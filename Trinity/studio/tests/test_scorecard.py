"""Usage scorecard row mapping."""

from __future__ import annotations

import json
import uuid

from db import db, utc_now
from run_report import persist_pipeline_run_report
from scorecard_config import SCORECARD_SPREADSHEET_ID, SCORECARD_SPREADSHEET_URL
from scorecard_row import build_scorecard_row


def _seed_run(conn, run_id: str) -> None:
    now = utc_now()
    conn.execute(
        """
        INSERT INTO pipeline_run (
          id, label, trigger_type, trigger_value, product_id, operator_name,
          coverage_profile, created_at, updated_at
        ) VALUES (?, 'Pilot', 'reviewer_folder', 'project = ONE', 'bigpicture', 'Marek Wyszynski', 'balanced', ?, ?)
        """,
        (run_id, now, now),
    )
    unit_id = f"{run_id}:ONE-1"
    conn.execute(
        """
        INSERT INTO review_unit (
          id, pipeline_run_id, jira_key, qa_planning_fit, include_in_creator,
          gate_status, created_at, updated_at
        ) VALUES (?, ?, 'ONE-1', 'fit', 1, 'GREEN', ?, ?)
        """,
        (unit_id, run_id, now, now),
    )
    conn.execute(
        """
        INSERT INTO review_payload_revision (review_unit_id, revision, payload_json, source, created_at)
        VALUES (?, 1, ?, 'import', ?)
        """,
        (unit_id, json.dumps({"report": {"qa_planning_fit": "fit"}}), now),
    )
    cr_id = f"cr-{uuid.uuid4().hex[:8]}"
    conn.execute(
        """
        INSERT INTO creator_run (id, label, pipeline_run_id, status, created_at, updated_at)
        VALUES (?, 'suite', ?, 'draft', ?, ?)
        """,
        (cr_id, run_id, now, now),
    )
    conn.execute(
        """
        INSERT INTO test_case_row (
          id, creator_run_id, draft_id, title, human_review_status,
          marked_for_xray_import, xray_test_key, updated_at
        ) VALUES (?, ?, 'D1', 'Test 1', 'approved', 1, 'TC-9001', ?)
        """,
        (f"{cr_id}:D1", cr_id, now),
    )
    conn.execute(
        """
        INSERT INTO test_case_row (
          id, creator_run_id, draft_id, title, human_review_status,
          marked_for_xray_import, updated_at
        ) VALUES (?, ?, 'D2', 'Test 2', 'rejected', 0, ?)
        """,
        (f"{cr_id}:D2", cr_id, now),
    )


def test_scorecard_config_constants():
    assert SCORECARD_SPREADSHEET_ID == "123L4BTTTrgghlLHni-vqCAEiJperj-pu1tDKuEyg6oo"
    assert SCORECARD_SPREADSHEET_ID in SCORECARD_SPREADSHEET_URL


def test_build_scorecard_row(studio_db):
    run_id = f"pr-sc-{uuid.uuid4().hex[:8]}"
    with db() as conn:
        _seed_run(conn, run_id)
        report = persist_pipeline_run_report(conn, run_id)
        built = build_scorecard_row(
            conn,
            pipeline_run_id=run_id,
            report=report,
            external_run_id="BP-999",
        )
    assert built["tab"] == "BigPicture"
    assert built["values"][0] == "BP-999"
    assert built["values"][1] == "Marek Wyszynski"
    assert built["values"][3] == "create"
    assert built["fields"]["test_cases_approved"] == 1
    assert built["fields"]["test_cases_rejected"] == 1
    assert built["fields"]["coverage_depth"] == "Comprehensive"
