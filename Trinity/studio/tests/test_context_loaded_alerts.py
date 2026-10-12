import json

from context_loaded_alerts import build_context_loaded_alerts


def test_context_loaded_alerts_flags_failed(studio_db):
    from db import db, utc_now

    now = utc_now()
    with db() as conn:
        conn.execute(
            """
            INSERT INTO pipeline_run (id, label, trigger_type, trigger_value, created_at, updated_at)
            VALUES ('pr-ctx', 'Ctx run', 'reviewer_folder', 'x', ?, ?)
            """,
            (now, now),
        )
        conn.execute(
            """
            INSERT INTO review_unit (id, pipeline_run_id, jira_key, include_in_creator, created_at, updated_at)
            VALUES ('pr-ctx:ONE-1', 'pr-ctx', 'ONE-1', 1, ?, ?)
            """,
            (now, now),
        )
        payload = {
            "context_loaded": [
                {"source": "Confluence", "type": "confluence", "status": "failed", "detail": "403"},
                {"source": "Jira", "type": "jira_issue", "status": "analyzed"},
            ]
        }
        conn.execute(
            """
            INSERT INTO review_payload_revision (review_unit_id, revision, payload_json, source, created_at)
            VALUES ('pr-ctx:ONE-1', 1, ?, 'import', ?)
            """,
            (json.dumps(payload), now),
        )
        out = build_context_loaded_alerts(conn)
    assert out["alert_count"] == 1
    assert out["alerts"][0]["status"] == "failed"
