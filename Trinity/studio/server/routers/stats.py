"""Global Studio statistics and per-run E2E reports."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, HTTPException

from db import db, utc_now
from run_report import compare_pipeline_runs, persist_pipeline_run_report
from studio_stats import count_open_questions_and_findings
router = APIRouter(tags=["stats"])


@router.get("/api/stats")
def global_stats() -> dict[str, Any]:
    with db() as conn:
        runs = conn.execute("SELECT COUNT(*) FROM pipeline_run").fetchone()[0]
        units = conn.execute("SELECT COUNT(*) FROM review_unit").fetchone()[0]
        approved = conn.execute(
            "SELECT COUNT(*) FROM review_unit WHERE approved_revision_id IS NOT NULL"
        ).fetchone()[0]
        open_qf = count_open_questions_and_findings(conn)
        creator_runs = conn.execute("SELECT COUNT(*) FROM creator_run").fetchone()[0]
        tests = conn.execute("SELECT COUNT(*) FROM test_case_row").fetchone()[0]
        tests_approved = conn.execute(
            "SELECT COUNT(*) FROM test_case_row WHERE human_review_status = 'approved'"
        ).fetchone()[0]
        automatable = conn.execute(
            "SELECT COUNT(*) FROM test_case_row WHERE automation_candidate = 1"
        ).fetchone()[0]
        imported_xray = conn.execute(
            "SELECT COUNT(*) FROM test_case_row WHERE xray_test_key IS NOT NULL"
        ).fetchone()[0]
        ready_import = conn.execute(
            """
            SELECT COUNT(*) FROM test_case_row
            WHERE human_review_status = 'approved' AND marked_for_xray_import = 1
            """
        ).fetchone()[0]
    return {
        "pipeline_runs": runs,
        "review_units": units,
        "review_units_approved": approved,
        "open_findings_latest": open_qf["open_findings_latest"],
        "open_questions_latest": open_qf["open_questions_latest"],
        "open_qf_counts_capped": open_qf["open_qf_counts_capped"],
        "open_qf_unit_cap": open_qf["open_qf_unit_cap"],
        "creator_runs": creator_runs,
        "test_cases": tests,
        "test_cases_approved": tests_approved,
        "test_cases_automation_candidate": automatable,
        "test_cases_imported_xray": imported_xray,
        "test_cases_ready_for_import": ready_import,
    }


@router.get("/api/runs/{run_id}/statistics")
def pipeline_run_statistics(run_id: str, refresh: bool = True) -> dict[str, Any]:
    with db() as conn:
        run = conn.execute("SELECT id FROM pipeline_run WHERE id = ?", (run_id,)).fetchone()
        if not run:
            raise HTTPException(404, "Run not found")
        if refresh:
            report = persist_pipeline_run_report(conn, run_id)
        else:
            row = conn.execute(
                "SELECT report_json FROM pipeline_run_report WHERE pipeline_run_id = ?",
                (run_id,),
            ).fetchone()
            if not row:
                report = persist_pipeline_run_report(conn, run_id)
            else:
                report = json.loads(row["report_json"])
    return report


@router.get("/api/statistics/compare")
def statistics_compare(runs: str) -> dict[str, Any]:
    """Compare 2–5 pipeline runs. Query: runs=id1,id2[,id3…] (first id = baseline for deltas)."""
    run_ids = [part.strip() for part in runs.split(",") if part.strip()]
    if len(run_ids) < 2:
        raise HTTPException(400, "Provide at least two run ids: runs=id1,id2")
    try:
        with db() as conn:
            return compare_pipeline_runs(conn, run_ids)
    except KeyError as exc:
        raise HTTPException(404, f"Run not found: {exc.args[0]}") from exc
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@router.get("/api/runs/{run_id}/statistics/export")
def pipeline_run_statistics_export(run_id: str) -> dict[str, Any]:
    """BigQuery-shaped bundle for a single pipeline run (local archive)."""
    with db() as conn:
        run = conn.execute("SELECT id FROM pipeline_run WHERE id = ?", (run_id,)).fetchone()
        if not run:
            raise HTTPException(404, "Run not found")
        report = persist_pipeline_run_report(conn, run_id)
    return {
        "exported_at": utc_now(),
        "export_kind": "pipeline_run_statistics",
        "report": report,
    }

