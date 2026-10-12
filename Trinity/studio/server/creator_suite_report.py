"""Studio export: Creator run → Profile B suite-report folder."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT / "Trinity" / "creator") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "Trinity" / "creator"))

from suite_report.build import build_report_payload, write_suite_report  # noqa: E402

from creator_coverage import build_coverage_summary, load_latest_batch


def _studio_map(conn: Any, creator_run_id: str) -> dict[str, dict[str, Any]]:
    rows = conn.execute(
        "SELECT * FROM test_case_row WHERE creator_run_id = ?",
        (creator_run_id,),
    ).fetchall()
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        out[row["draft_id"]] = dict(row)
    return out


def export_suite_report_for_run(
    conn: Any,
    creator_run_id: str,
    export_root: Path,
) -> tuple[Path, int]:
    batch, _rev = load_latest_batch(conn, creator_run_id)
    if not batch:
        raise ValueError("No batch JSON for this Creator run — import a TestCaseDraft batch first.")

    studio = _studio_map(conn, creator_run_id)
    test_dicts = [dict(r) for r in conn.execute(
        "SELECT * FROM test_case_row WHERE creator_run_id = ?",
        (creator_run_id,),
    ).fetchall()]
    coverage = build_coverage_summary(conn, creator_run_id, test_dicts)
    gap_count = coverage.get("gap_count") if coverage.get("available") else None

    payload = build_report_payload(
        run_id=creator_run_id,
        batch=batch,
        studio_by_draft=studio,
        coverage_gap_count=gap_count,
    )
    out_dir = export_root / "creator" / creator_run_id / "suite-report"
    index = write_suite_report(out_dir, payload)
    return index, len(payload["rows"])
