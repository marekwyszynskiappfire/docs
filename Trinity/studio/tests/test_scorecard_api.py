from scorecard_config import SCORECARD_SPREADSHEET_URL


def test_scorecard_config_endpoint(client):
    r = client.get("/api/scorecard/config")
    assert r.status_code == 200
    body = r.json()
    assert body["spreadsheet_url"] == SCORECARD_SPREADSHEET_URL
    assert body["spreadsheet_id"]
    assert isinstance(body["configured"], bool)


def test_scorecard_push_requires_credentials(client, studio_db, monkeypatch):
    monkeypatch.setattr("routers.scorecard.is_configured", lambda: False)
    from db import db, utc_now

    run_id = "pr-scorecard-push"
    now = utc_now()
    with db() as conn:
        conn.execute(
            """
            INSERT INTO pipeline_run (id, label, trigger_type, trigger_value, created_at, updated_at)
            VALUES (?, 'x', 'reviewer_folder', 'x', ?, ?)
            """,
            (run_id, now, now),
        )
    r = client.post(f"/api/runs/{run_id}/scorecard/push")
    assert r.status_code == 503


def test_health_lists_usage_scorecard(client):
    r = client.get("/api/health")
    assert "usage_scorecard_sheets" in r.json()["features"]
