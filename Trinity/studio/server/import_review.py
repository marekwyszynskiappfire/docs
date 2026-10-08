"""Import Reviewer run folders into QA Studio."""

from __future__ import annotations

import json
import re
import uuid
from pathlib import Path
from typing import Any

from creator_export import automation_candidate_flag, automation_fit_value
from db import db, init_db, log_event, utc_now

EPIC_DIR_RE = re.compile(r"^[A-Z][A-Z0-9]+-\d+$")


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _qa_planning_fit(payload: dict[str, Any]) -> str | None:
    for req in payload.get("requirements") or []:
        fit = req.get("qa_planning_fit")
        if fit:
            return fit
    return None


def import_reviewer_run(run_dir: Path, run_id: str | None = None) -> dict[str, Any]:
    init_db()
    run_dir = run_dir.resolve()
    if not run_dir.is_dir():
        raise FileNotFoundError(run_dir)

    pipeline_id = run_id or run_dir.name
    handoff_path = run_dir / "portfolio" / "data" / "creator-handoff.json"
    handoff_json = None
    trigger_value = pipeline_id
    if handoff_path.is_file():
        handoff = _read_json(handoff_path)
        handoff_json = json.dumps(handoff)
        trigger_value = handoff.get("source_jql") or handoff.get("creator_jql") or pipeline_id

    epic_dirs = sorted(
        p for p in run_dir.iterdir() if p.is_dir() and EPIC_DIR_RE.match(p.name)
    )
    if not epic_dirs:
        raise ValueError(f"No epic folders under {run_dir}")

    excluded: set[str] = set()
    if handoff_path.is_file():
        handoff = json.loads(handoff_json or "{}")
        excluded = set(handoff.get("excluded_by_default") or [])
        excluded |= set(handoff.get("excluded_epics") or [])
        excluded |= set(handoff.get("excluded_from_creator") or [])

    imported_units = 0
    now = utc_now()

    with db() as conn:
        existing = conn.execute(
            "SELECT id FROM pipeline_run WHERE id = ?", (pipeline_id,)
        ).fetchone()
        if existing:
            conn.execute(
                """
                UPDATE pipeline_run
                SET label = ?, trigger_type = ?, trigger_value = ?, source_path = ?,
                    creator_handoff_json = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    pipeline_id,
                    "reviewer_folder",
                    trigger_value,
                    str(run_dir),
                    handoff_json,
                    now,
                    pipeline_id,
                ),
            )
        else:
            conn.execute(
                """
                INSERT INTO pipeline_run (id, label, trigger_type, trigger_value, source_path,
                  product_id, status, creator_handoff_json, created_at, updated_at)
                VALUES (?, ?, 'reviewer_folder', ?, ?, NULL, 'active', ?, ?, ?)
                """,
                (pipeline_id, pipeline_id, trigger_value, str(run_dir), handoff_json, now, now),
            )

        for epic_dir in epic_dirs:
            payload_path = epic_dir / "review-payload.json"
            if not payload_path.is_file():
                continue
            payload = _read_json(payload_path)
            jira_key = epic_dir.name
            unit_id = f"{pipeline_id}:{jira_key}"
            summary = (payload.get("requirements") or [{}])[0].get("summary")
            gate = (payload.get("gate") or {}).get("status")
            fit = _qa_planning_fit(payload)
            include = 0 if jira_key in excluded or fit == "not_fit" else 1

            conn.execute(
                """
                INSERT INTO review_unit (id, pipeline_run_id, jira_key, scope_type, summary, gate_status,
                  qa_planning_fit, include_in_creator, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(pipeline_run_id, jira_key) DO UPDATE SET
                  summary = excluded.summary,
                  gate_status = excluded.gate_status,
                  qa_planning_fit = excluded.qa_planning_fit,
                  include_in_creator = excluded.include_in_creator,
                  updated_at = excluded.updated_at
                """,
                (
                    unit_id,
                    pipeline_id,
                    jira_key,
                    (payload.get("scope") or {}).get("type"),
                    summary,
                    gate,
                    fit,
                    include,
                    now,
                    now,
                ),
            )

            max_rev = conn.execute(
                "SELECT COALESCE(MAX(revision), 0) FROM review_payload_revision WHERE review_unit_id = ?",
                (unit_id,),
            ).fetchone()[0]
            new_rev = max_rev + 1
            conn.execute(
                """
                INSERT INTO review_payload_revision (review_unit_id, revision, payload_json, source, created_at, created_by)
                VALUES (?, ?, ?, 'import', ?, 'importer')
                """,
                (unit_id, new_rev, json.dumps(payload, ensure_ascii=False), now),
            )
            imported_units += 1

        log_event(
            conn,
            "review_run_imported",
            "pipeline_run",
            pipeline_id,
            pipeline_id,
            {"units": imported_units, "path": str(run_dir)},
        )

    return {
        "pipeline_run_id": pipeline_id,
        "units_imported": imported_units,
        "source_path": str(run_dir),
    }


def import_test_case_batch(batch_path: Path, creator_run_id: str | None = None) -> dict[str, Any]:
    init_db()
    batch_path = batch_path.resolve()
    batch = _read_json(batch_path)
    run_id = creator_run_id or batch.get("run_id") or f"creator-{uuid.uuid4().hex[:8]}"
    now = utc_now()
    tests = batch.get("tests") or []

    with db() as conn:
        conn.execute(
            """
            INSERT INTO creator_run (id, pipeline_run_id, review_unit_id, label, source_path, status, created_at, updated_at)
            VALUES (?, NULL, NULL, ?, ?, 'draft', ?, ?)
            ON CONFLICT(id) DO UPDATE SET source_path = excluded.source_path, updated_at = excluded.updated_at
            """,
            (run_id, run_id, str(batch_path), now, now),
        )
        max_rev = conn.execute(
            "SELECT COALESCE(MAX(revision), 0) FROM test_case_batch_revision WHERE creator_run_id = ?",
            (run_id,),
        ).fetchone()[0]
        rev = max_rev + 1
        conn.execute(
            """
            INSERT INTO test_case_batch_revision (creator_run_id, revision, batch_json, source, created_at, created_by)
            VALUES (?, ?, ?, 'import', ?, 'importer')
            """,
            (run_id, rev, json.dumps(batch, ensure_ascii=False), now),
        )
        for idx, tc in enumerate(tests):
            draft_id = tc.get("draft_id") or f"TC-{idx + 1:03d}"
            row_id = f"{run_id}:{draft_id}"
            conn.execute(
                """
                INSERT INTO test_case_row (id, creator_run_id, draft_id, title, execution_tier, test_type,
                  human_review_status, automation_candidate, automation_fit, marked_for_xray_import, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?, 0, ?)
                ON CONFLICT(creator_run_id, draft_id) DO UPDATE SET
                  title = excluded.title,
                  execution_tier = excluded.execution_tier,
                  test_type = excluded.test_type,
                  automation_candidate = excluded.automation_candidate,
                  automation_fit = excluded.automation_fit,
                  updated_at = excluded.updated_at
                """,
                (
                    row_id,
                    run_id,
                    draft_id,
                    tc.get("title") or draft_id,
                    tc.get("execution_tier"),
                    tc.get("test_type"),
                    automation_candidate_flag(tc),
                    automation_fit_value(tc),
                    now,
                ),
            )
            conn.execute(
                """
                INSERT INTO test_case_revision (test_case_row_id, revision, case_json, source, created_at, created_by)
                VALUES (?, 1, ?, 'import', ?, 'importer')
                ON CONFLICT(test_case_row_id, revision) DO UPDATE SET case_json = excluded.case_json
                """,
                (row_id, json.dumps(tc, ensure_ascii=False), now),
            )

        log_event(conn, "creator_batch_imported", "creator_run", run_id, None, {"tests": len(tests)})

    return {"creator_run_id": run_id, "tests_imported": len(tests)}
