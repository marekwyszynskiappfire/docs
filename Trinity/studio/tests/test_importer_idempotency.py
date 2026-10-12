import uuid

from db import db, utc_now
from importer_idempotency import attach_existing_xray_keys


def test_attach_existing_xray_keys_warns():
    run_id = f"cr-idem-{uuid.uuid4().hex[:8]}"
    now = utc_now()
    plan = {"tests": [{"draft_id": "TC-001", "action": "would_create"}], "target": {"warnings": []}}
    with db() as conn:
        conn.execute(
            """
            INSERT INTO creator_run (id, label, status, created_at, updated_at)
            VALUES (?, ?, 'draft', ?, ?)
            """,
            (run_id, run_id, now, now),
        )
        conn.execute(
            """
            INSERT INTO test_case_row (
              id, creator_run_id, draft_id, title, human_review_status,
              marked_for_xray_import, xray_test_key, updated_at
            ) VALUES (?, ?, 'TC-001', 't', 'approved', 1, 'TC-9999', ?)
            """,
            (f"{run_id}:TC-001", run_id, now),
        )
        attach_existing_xray_keys(conn, run_id, plan)
    assert plan["tests"][0]["existing_xray_test_key"] == "TC-9999"
    assert plan["idempotency_warnings"]
