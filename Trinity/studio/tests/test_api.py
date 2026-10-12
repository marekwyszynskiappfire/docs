from db import db, utc_now


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "importer_plan" in body["features"]


def test_telemetry_rejection_reasons(client):
    r = client.get("/api/telemetry/rejection-reasons")
    assert r.status_code == 200
    reasons = r.json()["reasons"]
    assert len(reasons) >= 5
    assert reasons[0]["id"] and reasons[0]["label"]


def test_stats_empty_db(client):
    r = client.get("/api/stats")
    assert r.status_code == 200
    assert r.json()["test_cases"] == 0


def test_health_lists_importer_execute(client):
    r = client.get("/api/health")
    assert "importer_execute" in r.json()["features"]


def test_health_lists_creator_coverage(client):
    r = client.get("/api/health")
    assert "creator_coverage" in r.json()["features"]


def test_portfolio_rollup_empty(client):
    r = client.get("/api/portfolio-rollup")
    assert r.status_code == 200
    assert r.json()["runs"] == []


def test_health_lists_portfolio_rollup(client):
    r = client.get("/api/health")
    assert "portfolio_rollup" in r.json()["features"]


def test_creator_products_lists_requirements(client):
    r = client.get("/api/creator/products")
    assert r.status_code == 200
    ids = {p["product_id"] for p in r.json()["products"]}
    assert "requirements" in ids


def test_importer_execute_requires_production_confirm(client):
    r = client.post(
        "/api/importer/execute",
        json={
            "jira_instance_id": "appfire-production",
            "folder_path": "/TC/test",
            "creator_run_id": "missing",
        },
    )
    assert r.status_code == 400
    assert "PRODUCTION" in r.json()["detail"]


def test_importer_record_results_inline(client):
    run_id = "test-creator-run"
    now = utc_now()
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
              marked_for_xray_import, updated_at
            ) VALUES (?, ?, 'TC-001', 't', 'approved', 1, ?)
            """,
            (f"{run_id}:TC-001", run_id, now),
        )
    r = client.post(
        "/api/importer/record-results",
        json={
            "creator_run_id": run_id,
            "results": [{"draft_id": "TC-001", "xray_test_key": "TC-7000"}],
        },
    )
    assert r.status_code == 200
    assert r.json()["updated"] == 1
