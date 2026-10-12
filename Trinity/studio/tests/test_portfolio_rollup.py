import json
from pathlib import Path

from db import db, utc_now
from epic_child_inventory import build_run_child_inventory
from portfolio_rollup import build_portfolio_rollup


def test_portfolio_rollup_and_child_inventory(studio_db):
    run_id = "rollup-run"
    unit_id = f"{run_id}:DEMO-4500"
    now = utc_now()
    payload_path = (
        Path(__file__).resolve().parents[2]
        / "reviewer"
        / "samples"
        / "demo-epic.payload.json"
    )
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    with db() as conn:
        conn.execute(
            """
            INSERT INTO pipeline_run (id, label, trigger_type, trigger_value, created_at, updated_at)
            VALUES (?, ?, 'reviewer_folder', 'demo', ?, ?)
            """,
            (run_id, "Demo", now, now),
        )
        conn.execute(
            """
            INSERT INTO review_unit (
              id, pipeline_run_id, jira_key, summary, gate_status, qa_planning_fit,
              include_in_creator, created_at, updated_at
            ) VALUES (?, ?, 'DEMO-4500', 'OKR', 'PASS', 'fit', 1, ?, ?)
            """,
            (unit_id, run_id, now, now),
        )
        conn.execute(
            """
            INSERT INTO review_payload_revision (
              review_unit_id, revision, payload_json, source, created_at
            ) VALUES (?, 1, ?, 'import', ?)
            """,
            (unit_id, json.dumps(payload), now),
        )
        rollup = build_portfolio_rollup(conn)
        inv = build_run_child_inventory(conn, run_id)
    assert rollup["runs"][0]["unit_count"] == 1
    assert rollup["global"]["gate_mix"].get("PASS") == 1
    assert inv["epics"][0]["child_count"] >= 1
    assert inv["epics"][0]["children"][0]["key"]
