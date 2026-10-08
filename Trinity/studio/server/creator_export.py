"""Build Importer-ready payload from approved, import-marked Creator tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from db import utc_now


def automation_candidate_flag(tc: dict[str, Any]) -> int:
    if tc.get("automation_candidate") is not None:
        return 1 if tc.get("automation_candidate") else 0
    fit = tc.get("automation_fit")
    if fit == "full":
        return 1
    if fit == "partial":
        return 1
    return 0


def automation_fit_value(tc: dict[str, Any]) -> str | None:
    fit = tc.get("automation_fit")
    if fit in ("full", "partial", "manual_only"):
        return fit
    return None


def validate_import_mark(status: str, marked: bool) -> None:
    if marked and status != "approved":
        raise ValueError("marked_for_xray_import requires human_review_status approved")


def build_importer_payload(conn: Any, creator_run_id: str) -> dict[str, Any]:
    run = conn.execute("SELECT * FROM creator_run WHERE id = ?", (creator_run_id,)).fetchone()
    if not run:
        raise KeyError("creator run not found")

    batch_row = conn.execute(
        """
        SELECT batch_json FROM test_case_batch_revision
        WHERE creator_run_id = ? ORDER BY revision DESC LIMIT 1
        """,
        (creator_run_id,),
    ).fetchone()
    batch_meta: dict[str, Any] = {}
    if batch_row:
        try:
            batch_meta = json.loads(batch_row["batch_json"])
        except json.JSONDecodeError:
            batch_meta = {}

    rows = conn.execute(
        """
        SELECT * FROM test_case_row
        WHERE creator_run_id = ? AND human_review_status = 'approved' AND marked_for_xray_import = 1
        ORDER BY draft_id
        """,
        (creator_run_id,),
    ).fetchall()

    tests: list[dict[str, Any]] = []
    for row in rows:
        rev = conn.execute(
            """
            SELECT case_json FROM test_case_revision
            WHERE test_case_row_id = ? ORDER BY revision DESC LIMIT 1
            """,
            (row["id"],),
        ).fetchone()
        if not rev:
            continue
        case = json.loads(rev["case_json"])
        if not case.get("coverage_catalog_id"):
            linked_ac = case.get("linked_ac_ids") or []
            case["coverage_catalog_id"] = str(linked_ac[0]) if linked_ac else "TRINITY-IMPORT"
        tests.append(case)

    return {
        "schema_version": "1.0",
        "export_kind": "creator_importer_handoff",
        "creator_run_id": creator_run_id,
        "exported_at": utc_now(),
        "source_batch_run_id": batch_meta.get("run_id"),
        "review_ref": batch_meta.get("review_ref"),
        "product_id": batch_meta.get("product_id"),
        "suite_mode": batch_meta.get("suite_mode"),
        "test_count": len(tests),
        "tests": tests,
    }


def write_importer_export(conn: Any, creator_run_id: str, export_root: Path) -> Path:
    payload = build_importer_payload(conn, creator_run_id)
    out_dir = export_root / "creator" / creator_run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "importer-payload.json"
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out_path
