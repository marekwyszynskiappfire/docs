"""Duplicate Jira comment detection."""

from db import db, utc_now
from jira_epic_comment import find_recent_duplicate_post, post_comment, preview_comment, request_hash


def test_duplicate_blocks_second_post(studio_db):
    from pathlib import Path
    import json

    fixture = (
        Path(__file__).resolve().parents[1]
        / "fixtures/demo-reviewer-run/DEMO-4500/review-payload.json"
    )
    payload = json.loads(fixture.read_text(encoding="utf-8"))
    unit_id = "dup-unit"
    now = utc_now()
    with db() as conn:
        conn.execute(
            """
            INSERT INTO pipeline_run (id, label, trigger_type, trigger_value, created_at, updated_at)
            VALUES ('pr-dup', 't', 'reviewer_folder', 't', ?, ?)
            """,
            (now, now),
        )
        conn.execute(
            """
            INSERT INTO review_unit (id, pipeline_run_id, jira_key, include_in_creator, created_at, updated_at)
            VALUES (?, 'pr-dup', 'DEMO-4500', 1, ?, ?)
            """,
            (unit_id, now, now),
        )
        conn.execute(
            """
            INSERT INTO review_payload_revision (review_unit_id, revision, payload_json, source, created_at, created_by)
            VALUES (?, 1, ?, 'import', ?, 'test')
            """,
            (unit_id, json.dumps(payload), now),
        )
        preview = preview_comment(conn, unit_id, payload, "DEMO-4500", "full", payload_revision_id=1)
        body = (preview["body"] or "").strip()
        req_hash = request_hash(preview["variant"], body, 1)
        conn.execute(
            """
            INSERT INTO jira_comment_post (
              review_unit_id, jira_issue_key, variant, jira_comment_id, created_at, request_hash, preview_edited
            ) VALUES (?, 'DEMO-4500', 'full', '99', ?, ?, 0)
            """,
            (unit_id, now, req_hash),
        )
        assert find_recent_duplicate_post(conn, unit_id, req_hash) is not None
        try:
            post_comment(
                conn,
                unit_id=unit_id,
                jira_key="DEMO-4500",
                payload=payload,
                variant="full",
                body_override=body,
                preview_edited=False,
                payload_revision_id=1,
                allow_duplicate=False,
            )
            raised = False
        except ValueError as exc:
            raised = True
            assert "Duplicate" in str(exc)
        assert raised
