"""Import Reviewer run folders into QA Studio."""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from pathlib import Path
from typing import Any

from creator_export import automation_candidate_flag, automation_fit_value
from db import db, init_db, utc_now
from review_payload_fields import qa_planning_fit_from_payload
from studio_paths import DOCS_REPO_ROOT
from telemetry import operator_id, operator_name, record_event

EPIC_DIR_RE = re.compile(r"^[A-Z][A-Z0-9]+-\d+$")


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def epic_key_from_payload(payload: dict[str, Any]) -> str | None:
    """Jira key for the reviewed epic (folder name should match)."""
    scope = payload.get("scope") or {}
    if isinstance(scope, dict):
        if (scope.get("type") or "").lower() == "epic" and scope.get("value"):
            return str(scope["value"]).strip()
        if scope.get("jira_key"):
            return str(scope["jira_key"]).strip()
    keys = payload.get("requirement_keys") or []
    if keys:
        return str(keys[0]).strip()
    reqs = payload.get("requirements") or []
    if reqs and isinstance(reqs[0], dict) and reqs[0].get("jira_key"):
        return str(reqs[0]["jira_key"]).strip()
    return None


def _creator_pipeline_link(
    conn: Any, batch: dict[str, Any]
) -> tuple[str | None, str | None]:
    """Resolve Creator batch → Reviewer pipeline using explicit IDs or review_ref."""
    explicit_pipeline = str(batch.get("pipeline_run_id") or "").strip()
    explicit_unit = str(batch.get("review_unit_id") or "").strip()
    if explicit_pipeline:
        row = conn.execute(
            "SELECT id FROM pipeline_run WHERE id = ?", (explicit_pipeline,)
        ).fetchone()
        if row:
            return explicit_pipeline, explicit_unit or None

    review_ref = str(batch.get("review_ref") or "").strip()
    if not review_ref:
        return None, None
    ref_path = Path(review_ref)
    if not ref_path.is_absolute():
        ref_path = (DOCS_REPO_ROOT / ref_path).resolve()
    epic_key = ref_path.parent.name
    if not EPIC_DIR_RE.match(epic_key):
        return None, None

    candidates = conn.execute(
        """
        SELECT u.id AS unit_id, u.pipeline_run_id, p.source_path, p.updated_at
        FROM review_unit u
        JOIN pipeline_run p ON p.id = u.pipeline_run_id
        WHERE u.jira_key = ?
        ORDER BY p.updated_at DESC
        """,
        (epic_key,),
    ).fetchall()
    for candidate in candidates:
        source = candidate["source_path"]
        if not source:
            continue
        try:
            ref_path.relative_to(Path(source).resolve())
            return candidate["pipeline_run_id"], candidate["unit_id"]
        except ValueError:
            continue
    if len(candidates) == 1:
        return candidates[0]["pipeline_run_id"], candidates[0]["unit_id"]
    return None, None


def repair_creator_pipeline_links(conn: Any) -> int:
    """Backfill legacy Creator rows from their latest batch review_ref."""
    rows = conn.execute(
        """
        SELECT cr.id, rev.batch_json
        FROM creator_run cr
        JOIN test_case_batch_revision rev ON rev.creator_run_id = cr.id
        JOIN (
          SELECT creator_run_id, MAX(revision) AS latest_revision
          FROM test_case_batch_revision
          GROUP BY creator_run_id
        ) latest
          ON latest.creator_run_id = rev.creator_run_id
         AND latest.latest_revision = rev.revision
        WHERE cr.pipeline_run_id IS NULL OR cr.review_unit_id IS NULL
        """
    ).fetchall()
    repaired = 0
    for row in rows:
        try:
            batch = json.loads(row["batch_json"])
        except (TypeError, json.JSONDecodeError):
            continue
        pipeline_id, unit_id = _creator_pipeline_link(conn, batch)
        if not pipeline_id:
            continue
        conn.execute(
            """
            UPDATE creator_run
            SET pipeline_run_id = COALESCE(pipeline_run_id, ?),
                review_unit_id = COALESCE(review_unit_id, ?)
            WHERE id = ?
            """,
            (pipeline_id, unit_id, row["id"]),
        )
        product_id = batch.get("product_id")
        if product_id:
            conn.execute(
                """
                UPDATE pipeline_run SET product_id = COALESCE(product_id, ?)
                WHERE id = ?
                """,
                (product_id, pipeline_id),
            )
        repaired += 1
    return repaired


def repair_pipeline_products(conn: Any) -> int:
    """Backfill legacy run products from their Reviewer run configuration."""
    repaired = 0
    rows = conn.execute(
        "SELECT id, source_path FROM pipeline_run WHERE product_id IS NULL"
    ).fetchall()
    for row in rows:
        if not row["source_path"]:
            continue
        run_name = Path(row["source_path"]).name
        config = (
            DOCS_REPO_ROOT
            / "Trinity"
            / "reviewer"
            / "config"
            / "runs"
            / f"{run_name}.json"
        )
        if not config.is_file():
            continue
        try:
            product_id = _read_json(config).get("product_id")
        except (OSError, json.JSONDecodeError):
            continue
        if not product_id:
            continue
        conn.execute(
            "UPDATE pipeline_run SET product_id = ? WHERE id = ?",
            (product_id, row["id"]),
        )
        repaired += 1
    return repaired


def import_reviewer_run(
    run_dir: Path,
    run_id: str | None = None,
    unchanged_hashes: dict[str, str] | None = None,
) -> dict[str, Any]:
    init_db()
    run_dir = run_dir.resolve()
    if not run_dir.is_dir():
        raise FileNotFoundError(run_dir)

    run_dir_str = str(run_dir)
    handoff_path = run_dir / "portfolio" / "data" / "creator-handoff.json"
    handoff_json = None
    product_id = None
    default_label = run_dir.name
    trigger_value = default_label
    if handoff_path.is_file():
        handoff = _read_json(handoff_path)
        handoff_json = json.dumps(handoff)
        trigger_value = handoff.get("source_jql") or handoff.get("creator_jql") or default_label
        product_id = handoff.get("product_id")
    if not product_id:
        run_config = (
            DOCS_REPO_ROOT
            / "Trinity"
            / "reviewer"
            / "config"
            / "runs"
            / f"{run_dir.name}.json"
        )
        if run_config.is_file():
            product_id = _read_json(run_config).get("product_id")

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
    revisions_skipped = 0
    now = utc_now()
    pipeline_is_new = True
    run_operator_id = operator_id()
    run_operator_name = operator_name()

    with db() as conn:
        existing = None
        if run_id:
            existing = conn.execute(
                "SELECT id FROM pipeline_run WHERE id = ?", (run_id,)
            ).fetchone()
        if not existing:
            existing = conn.execute(
                "SELECT id FROM pipeline_run WHERE source_path = ?", (run_dir_str,)
            ).fetchone()
        pipeline_is_new = existing is None
        if existing:
            pipeline_id = existing["id"]
            conn.execute(
                """
                UPDATE pipeline_run
                SET trigger_type = ?, trigger_value = ?, source_path = ?,
                    product_id = COALESCE(?, product_id),
                    operator_id = COALESCE(operator_id, ?),
                    operator_name = COALESCE(operator_name, ?),
                    creator_handoff_json = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    "reviewer_folder",
                    trigger_value,
                    run_dir_str,
                    product_id,
                    run_operator_id,
                    run_operator_name,
                    handoff_json,
                    now,
                    pipeline_id,
                ),
            )
        else:
            pipeline_id = run_id or f"pr-{uuid.uuid4()}"
            conn.execute(
                """
                INSERT INTO pipeline_run (id, label, trigger_type, trigger_value, source_path,
                  product_id, operator_id, operator_name, status, creator_handoff_json,
                  created_at, updated_at)
                VALUES (?, ?, 'reviewer_folder', ?, ?, ?, ?, ?, 'active', ?, ?, ?)
                """,
                (
                    pipeline_id,
                    default_label,
                    trigger_value,
                    run_dir_str,
                    product_id,
                    run_operator_id,
                    run_operator_name,
                    handoff_json,
                    now,
                    now,
                ),
            )

        for epic_dir in epic_dirs:
            payload_path = epic_dir / "review-payload.json"
            if not payload_path.is_file():
                continue
            payload_digest = hashlib.sha256(payload_path.read_bytes()).hexdigest()
            payload = _read_json(payload_path)
            jira_key = epic_dir.name
            expected = epic_key_from_payload(payload)
            if expected and expected != jira_key:
                raise ValueError(
                    f"Epic folder {jira_key} does not match payload epic key {expected} "
                    f"in {payload_path.relative_to(run_dir)} — rename the folder or fix scope/requirement_keys."
                )
            unit_id = f"{pipeline_id}:{jira_key}"
            summary = (payload.get("requirements") or [{}])[0].get("summary")
            gate = (payload.get("gate") or {}).get("status")
            fit = qa_planning_fit_from_payload(payload)
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

            if unchanged_hashes and unchanged_hashes.get(jira_key) == payload_digest:
                revisions_skipped += 1
                continue

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

        record_event(
            conn,
            "review_run_imported",
            "pipeline_run",
            pipeline_id,
            pipeline_id,
            {
                "units": imported_units,
                "revisions_skipped": revisions_skipped,
                "path": str(run_dir),
            },
        )

    return {
        "pipeline_run_id": pipeline_id,
        "units_imported": imported_units,
        "revisions_skipped": revisions_skipped,
        "source_path": str(run_dir),
        "pipeline_is_new": pipeline_is_new,
        "import_kind": "new" if pipeline_is_new else "updated",
    }


def _upsert_imported_case(
    conn: Any, run_id: str, draft_id: str, tc: dict[str, Any], now: str
) -> None:
    """Insert or refresh one draft. Changed case text starts a new revision and drops approval."""
    row_id = f"{run_id}:{draft_id}"
    case_json = json.dumps(tc, ensure_ascii=False)
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
          import_status = CASE
            WHEN test_case_row.import_status = 'removed' THEN NULL
            ELSE test_case_row.import_status
          END,
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
    stored = conn.execute(
        "SELECT id FROM test_case_row WHERE creator_run_id = ? AND draft_id = ?",
        (run_id, draft_id),
    ).fetchone()
    stored_id = stored["id"]
    latest = conn.execute(
        """
        SELECT revision, case_json FROM test_case_revision
        WHERE test_case_row_id = ?
        ORDER BY revision DESC LIMIT 1
        """,
        (stored_id,),
    ).fetchone()
    if latest and latest["case_json"] == case_json:
        return
    next_rev = int(latest["revision"]) + 1 if latest else 1
    cur = conn.execute(
        """
        INSERT INTO test_case_revision (test_case_row_id, revision, case_json, source, created_at, created_by)
        VALUES (?, ?, ?, 'import', ?, 'importer')
        """,
        (stored_id, next_rev, case_json, now),
    )
    conn.execute(
        """
        UPDATE test_case_row
        SET human_review_status = 'pending',
            marked_for_xray_import = 0,
            current_revision_id = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (cur.lastrowid, now, stored_id),
    )


def import_test_case_batch(batch_path: Path, creator_run_id: str | None = None) -> dict[str, Any]:
    init_db()
    batch_path = batch_path.resolve()
    batch_path_str = str(batch_path)
    batch = _read_json(batch_path)
    default_label = (
        (batch.get("label") or batch.get("suite_name") or batch.get("run_id") or batch_path.stem)
    )
    now = utc_now()
    tests = batch.get("tests") or []

    with db() as conn:
        linked_pipeline_id, linked_unit_id = _creator_pipeline_link(conn, batch)
        batch_product_id = batch.get("product_id")
        if linked_pipeline_id and batch_product_id:
            conn.execute(
                """
                UPDATE pipeline_run SET product_id = COALESCE(product_id, ?)
                WHERE id = ?
                """,
                (batch_product_id, linked_pipeline_id),
            )
        existing = None
        explicit_id = creator_run_id or batch.get("run_id")
        if explicit_id:
            existing = conn.execute(
                "SELECT id FROM creator_run WHERE id = ?", (explicit_id,)
            ).fetchone()
        if not existing:
            existing = conn.execute(
                "SELECT id FROM creator_run WHERE source_path = ?", (batch_path_str,)
            ).fetchone()
        run_is_new = existing is None
        if existing:
            run_id = existing["id"]
            conn.execute(
                """
                UPDATE creator_run
                SET source_path = ?,
                    pipeline_run_id = COALESCE(?, pipeline_run_id),
                    review_unit_id = COALESCE(?, review_unit_id),
                    updated_at = ?
                WHERE id = ?
                """,
                (batch_path_str, linked_pipeline_id, linked_unit_id, now, run_id),
            )
        else:
            run_id = explicit_id or f"cr-{uuid.uuid4()}"
            conn.execute(
                """
                INSERT INTO creator_run (id, pipeline_run_id, review_unit_id, label, source_path, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 'draft', ?, ?)
                """,
                (
                    run_id,
                    linked_pipeline_id,
                    linked_unit_id,
                    default_label,
                    batch_path_str,
                    now,
                    now,
                ),
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
        seen_drafts: set[str] = set()
        for idx, tc in enumerate(tests):
            draft_id = tc.get("draft_id") or f"TC-{idx + 1:03d}"
            seen_drafts.add(draft_id)
            _upsert_imported_case(conn, run_id, draft_id, tc, now)
        conn.execute(
            f"""
            UPDATE test_case_row
            SET human_review_status = 'pending',
                marked_for_xray_import = 0,
                import_status = 'removed',
                updated_at = ?
            WHERE creator_run_id = ?
              AND draft_id NOT IN ({", ".join("?" for _ in seen_drafts) or "''"})
            """,
            (now, run_id, *seen_drafts),
        )

        record_event(
            conn,
            "creator_batch_imported",
            "creator_run",
            run_id,
            None,
            {
                "tests": len(tests),
                "batch_revision": rev,
                "run_is_new": run_is_new,
                "ai_generated_test_count": len(tests),
                "product_id": batch.get("product_id"),
            },
        )

    return {
        "creator_run_id": run_id,
        "tests_imported": len(tests),
        "batch_revision": rev,
        "run_is_new": run_is_new,
        "import_kind": "new" if run_is_new else "updated",
        "source_path": str(batch_path),
    }
