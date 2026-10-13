"""Global Studio statistics."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter

from db import db

router = APIRouter(tags=["stats"])


@router.get("/api/stats")
def global_stats() -> dict[str, Any]:
    with db() as conn:
        runs = conn.execute("SELECT COUNT(*) FROM pipeline_run").fetchone()[0]
        units = conn.execute("SELECT COUNT(*) FROM review_unit").fetchone()[0]
        approved = conn.execute(
            "SELECT COUNT(*) FROM review_unit WHERE approved_revision_id IS NOT NULL"
        ).fetchone()[0]
        findings_open = 0
        questions_open = 0
        for row in conn.execute(
            """
            SELECT r.payload_json FROM review_payload_revision r
            INNER JOIN (
              SELECT review_unit_id, MAX(revision) AS mr FROM review_payload_revision GROUP BY review_unit_id
            ) latest ON latest.review_unit_id = r.review_unit_id AND latest.mr = r.revision
            """
        ):
            p = json.loads(row["payload_json"])
            for f in p.get("findings") or []:
                if f.get("status", "open") == "open":
                    findings_open += 1
            for q in p.get("questions") or []:
                if q.get("status", "open") == "open":
                    questions_open += 1
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
        "open_findings_latest": findings_open,
        "open_questions_latest": questions_open,
        "creator_runs": creator_runs,
        "test_cases": tests,
        "test_cases_approved": tests_approved,
        "test_cases_automation_candidate": automatable,
        "test_cases_imported_xray": imported_xray,
        "test_cases_ready_for_import": ready_import,
    }

