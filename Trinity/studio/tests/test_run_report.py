import json
import uuid

from db import db, init_db, utc_now
from run_report import (
    compare_pipeline_runs,
    compute_pipeline_run_report,
    persist_pipeline_run_report,
    tc_creation_readiness_bucket,
)


def _seed_minimal_pipeline(conn, run_id: str = "pr-stats-test") -> str:
    now = utc_now()
    conn.execute(
        """
        INSERT INTO pipeline_run (id, label, trigger_type, trigger_value, created_at, updated_at)
        VALUES (?, 'Stats test', 'reviewer_folder', 'project = ONE', ?, ?)
        """,
        (run_id, now, now),
    )
    unit_id = f"{run_id}:ONE-100"
    conn.execute(
        """
        INSERT INTO review_unit (
          id, pipeline_run_id, jira_key, qa_planning_fit, include_in_creator,
          gate_status, created_at, updated_at
        ) VALUES (?, ?, 'ONE-100', 'not_fit', 0, 'AMBER', ?, ?)
        """,
        (unit_id, run_id, now, now),
    )
    payload = {
        "report": {"qa_planning_fit": "provisional"},
        "findings": [{"finding_id": "F1", "status": "open"}, {"finding_id": "F2", "status": "closed"}],
        "questions": [{"question_id": "Q1", "status": "open"}],
        "studio_qa": {
            "decisions": {"Q1": {"send_to_epic": True}, "Q2": {"send_to_epic": True}},
            "added_questions": [{"question_id": "Q2", "question": "New?"}],
        },
    }
    conn.execute(
        """
        INSERT INTO review_payload_revision (review_unit_id, revision, payload_json, source, created_at)
        VALUES (?, 1, ?, 'import', ?)
        """,
        (unit_id, json.dumps(payload), now),
    )
    return run_id


def test_tc_creation_readiness_buckets():
    assert tc_creation_readiness_bucket("fit") == "ready"
    assert tc_creation_readiness_bucket("provisional") == "ready_with_reservations"
    assert tc_creation_readiness_bucket("not_fit") == "not_ready"
    assert tc_creation_readiness_bucket("needs_clarification") == "not_ready"
    assert tc_creation_readiness_bucket(None) == "unknown"


def test_compute_pipeline_run_report_counts(studio_db):
    with db() as conn:
        run_id = _seed_minimal_pipeline(conn, f"pr-stats-{uuid.uuid4().hex[:8]}")
        report = compute_pipeline_run_report(conn, run_id)
    assert report["summary"]["epics_reviewed"] == 1
    assert report["summary"]["issues_spotted_findings_total"] == 2
    assert report["summary"]["epics_tc_creation_ready_with_reservations"] == 1
    assert report["summary"]["epics_not_ready_for_test_design"] == 0
    assert report["summary"]["questions_marked_for_epic_suggested"] == 1
    assert report["summary"]["questions_marked_for_epic_new"] == 1


def test_persist_pipeline_run_report(studio_db):
    with db() as conn:
        run_id = _seed_minimal_pipeline(conn, f"pr-stats-persist-{uuid.uuid4().hex[:8]}")
        persist_pipeline_run_report(conn, run_id)
        row = conn.execute(
            "SELECT report_json FROM pipeline_run_report WHERE pipeline_run_id = ?",
            (run_id,),
        ).fetchone()
    assert row is not None
    saved = json.loads(row["report_json"])
    assert saved["pipeline_run_id"] == run_id


def test_epic_tc_stats_not_duplicated_across_epics(studio_db):
    now = utc_now()
    run_id = f"pr-dup-{uuid.uuid4().hex[:8]}"
    with db() as conn:
        conn.execute(
            """
            INSERT INTO pipeline_run (id, label, trigger_type, trigger_value, created_at, updated_at)
            VALUES (?, 'Dup', 'reviewer_folder', 'x', ?, ?)
            """,
            (run_id, now, now),
        )
        u1 = f"{run_id}:ONE-1"
        u2 = f"{run_id}:ONE-2"
        for uid, key in ((u1, "ONE-1"), (u2, "ONE-2")):
            conn.execute(
                """
                INSERT INTO review_unit (
                  id, pipeline_run_id, jira_key, include_in_creator, created_at, updated_at
                ) VALUES (?, ?, ?, 1, ?, ?)
                """,
                (uid, run_id, key, now, now),
            )
        conn.execute(
            """
            INSERT INTO creator_run (id, pipeline_run_id, label, status, created_at, updated_at)
            VALUES ('ONE-228469', ?, 'ONE-228469', 'draft', ?, ?)
            """,
            (run_id, now, now),
        )
        for i in range(3):
            row_id = f"tc-{i}"
            conn.execute(
                """
                INSERT INTO test_case_row (
                  id, creator_run_id, draft_id, title, human_review_status, updated_at
                ) VALUES (?, 'ONE-228469', ?, ?, 'approved', ?)
                """,
                (row_id, f"d{i}", f"T{i}", now),
            )
        report = compute_pipeline_run_report(conn, run_id)
    by_key = {e["jira_key"]: e for e in report["epics"]}
    assert by_key["ONE-1"]["test_cases_drafted"] == 0
    assert by_key["ONE-2"]["test_cases_drafted"] == 0
    assert report["summary"]["test_cases_drafted_total"] == 3


def test_posted_questions_deduped_per_revision(studio_db):
    now = utc_now()
    run_id = f"pr-post-{uuid.uuid4().hex[:8]}"
    unit_id = f"{run_id}:ONE-9"
    payload = {
        "questions": [{"question_id": "Q1", "status": "open"}],
        "studio_qa": {"decisions": {"Q1": {"send_to_epic": True}}},
    }
    with db() as conn:
        conn.execute(
            """
            INSERT INTO pipeline_run (id, label, trigger_type, trigger_value, created_at, updated_at)
            VALUES (?, 'Post', 'reviewer_folder', 'x', ?, ?)
            """,
            (run_id, now, now),
        )
        conn.execute(
            """
            INSERT INTO review_unit (id, pipeline_run_id, jira_key, created_at, updated_at)
            VALUES (?, ?, 'ONE-9', ?, ?)
            """,
            (unit_id, run_id, now, now),
        )
        conn.execute(
            """
            INSERT INTO review_payload_revision (review_unit_id, revision, payload_json, source, created_at)
            VALUES (?, 1, ?, 'import', ?)
            """,
            (unit_id, json.dumps(payload), now),
        )
        for _ in range(2):
            conn.execute(
                """
                INSERT INTO jira_comment_post (
                  review_unit_id, jira_issue_key, variant, jira_comment_id,
                  payload_revision_id, created_at
                ) VALUES (?, 'ONE-9', 'studio', '10001', 1, ?)
                """,
                (unit_id, now),
            )
        report = compute_pipeline_run_report(conn, run_id)
    epic = report["epics"][0]
    assert epic["jira_comment_posts_success"] == 2
    assert epic["questions_posted_suggested"] == 1


def test_compare_pipeline_runs(studio_db):
    now = utc_now()
    ids = [f"pr-cmp-{uuid.uuid4().hex[:6]}", f"pr-cmp-{uuid.uuid4().hex[:6]}"]
    with db() as conn:
        for i, run_id in enumerate(ids):
            conn.execute(
                """
                INSERT INTO pipeline_run (id, label, trigger_type, trigger_value, created_at, updated_at)
                VALUES (?, ?, 'reviewer_folder', 'x', ?, ?)
                """,
                (run_id, f"Run {i}", now, now),
            )
            conn.execute(
                """
                INSERT INTO review_unit (id, pipeline_run_id, jira_key, qa_planning_fit, created_at, updated_at)
                VALUES (?, ?, 'ONE-1', ?, ?, ?)
                """,
                (f"{run_id}:ONE-1", run_id, "fit" if i == 0 else "not_fit", now, now),
            )
        cmp = compare_pipeline_runs(conn, ids)
    assert len(cmp["runs"]) == 2
    assert cmp["runs"][0]["summary"]["epics_tc_creation_ready"] == 1
    assert cmp["runs"][1]["summary"]["epics_tc_creation_not_ready"] == 1
    assert any(d["delta"] == -1 for d in cmp["deltas_from_baseline"])


def test_statistics_api(client):
    run_id = "pr-stats-api"
    now = utc_now()
    with db() as conn:
        conn.execute(
            """
            INSERT INTO pipeline_run (id, label, trigger_type, trigger_value, created_at, updated_at)
            VALUES (?, 'API', 'reviewer_folder', 'x', ?, ?)
            """,
            (run_id, now, now),
        )
    r = client.get(f"/api/runs/{run_id}/statistics")
    assert r.status_code == 200
    body = r.json()
    assert body["pipeline_run_id"] == run_id
    assert "phases" in body
    exp = client.get(f"/api/runs/{run_id}/statistics/export")
    assert exp.status_code == 200
    assert exp.json()["export_kind"] == "pipeline_run_statistics"


def test_compare_statistics_api(client, studio_db):
    now = utc_now()
    a, b = "pr-cmp-api-a", "pr-cmp-api-b"
    with db() as conn:
        for run_id in (a, b):
            conn.execute(
                """
                INSERT INTO pipeline_run (id, label, trigger_type, trigger_value, created_at, updated_at)
                VALUES (?, 'x', 'reviewer_folder', 'x', ?, ?)
                """,
                (run_id, now, now),
            )
    r = client.get(f"/api/statistics/compare?runs={a},{b}")
    assert r.status_code == 200
    assert len(r.json()["runs"]) == 2
