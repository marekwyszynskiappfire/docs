import json
from urllib.error import HTTPError
from io import BytesIO

from db import db
from telemetry import (
    flush_outbox,
    operator_id,
    operator_name,
    record_event,
    resolve_product,
)


def test_operator_identity_prefers_explicit_env(studio_db, monkeypatch):
    monkeypatch.setenv("TRINITY_OPERATOR_ID", "jane@appfire.com")
    monkeypatch.setenv("TRINITY_OPERATOR_NAME", "Jane Operator")
    monkeypatch.setenv("JIRA_EMAIL", "ignored@appfire.com")
    assert operator_id() == "jane@appfire.com"
    assert operator_name() == "Jane Operator"


def test_record_event_includes_operator_and_product(studio_db, monkeypatch):
    monkeypatch.setenv("TRINITY_OPERATOR_ID", "marek.wyszynski@appfire.com")
    monkeypatch.setenv("TRINITY_OPERATOR_NAME", "Marek Wyszynski")
    now = "2026-10-19T10:00:00+00:00"
    with db() as conn:
        conn.execute(
            """
            INSERT INTO pipeline_run (
              id, label, trigger_type, trigger_value, product_id, created_at, updated_at
            ) VALUES ('pr-tel', 'BP run', 'reviewer_folder', 'x', 'bigpicture', ?, ?)
            """,
            (now, now),
        )
        envelope = record_event(
            conn,
            "review_unit_approved",
            "review_unit",
            "pr-tel:ONE-1",
            "pr-tel",
            {"revision": 1},
        )
        pending = conn.execute(
            "SELECT event_json FROM telemetry_outbox WHERE sent_at IS NULL"
        ).fetchone()
    assert envelope["operator_id"] == "marek.wyszynski@appfire.com"
    assert envelope["operator_name"] == "Marek Wyszynski"
    assert envelope["product_id"] == "bigpicture"
    assert envelope["product_name"] == "BigPicture"
    stored = json.loads(pending["event_json"])
    assert stored["operator_name"] == "Marek Wyszynski"
    assert stored["product_id"] == "bigpicture"


def test_resolve_product_from_handoff_json(studio_db):
    now = "2026-10-19T10:00:00+00:00"
    with db() as conn:
        conn.execute(
            """
            INSERT INTO pipeline_run (
              id, label, trigger_type, trigger_value, creator_handoff_json, created_at, updated_at
            ) VALUES ('pr-h', 'H', 'reviewer_folder', 'x', ?, ?, ?)
            """,
            (json.dumps({"product_id": "bigpicture"}), now, now),
        )
        pid, pname = resolve_product(conn, "pr-h", {})
    assert pid == "bigpicture"
    assert pname == "BigPicture"


def test_flush_sends_batch(studio_db, monkeypatch):
    calls = []

    class DummyResp:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def fake_urlopen(req, timeout=30):
        calls.append(json.loads(req.data.decode("utf-8")))
        return DummyResp()

    monkeypatch.setenv("TRINITY_TELEMETRY_URL", "http://127.0.0.1:8787/v1/events")
    monkeypatch.setenv("TRINITY_TELEMETRY_API_KEY", "test-key")
    monkeypatch.setattr("telemetry.urllib.request.urlopen", fake_urlopen)

    with db() as conn:
        result = record_event(
            conn, "review_run_imported", "pipeline_run", "pr-x", "pr-x", {"units": 1}
        )
        pending = conn.execute(
            "SELECT COUNT(*) FROM telemetry_outbox WHERE sent_at IS NULL"
        ).fetchone()[0]
    assert result["event_type"] == "review_run_imported"
    assert pending == 0
    assert calls
    assert "events" in calls[0]
    assert calls[0]["events"][0]["event_type"] == "review_run_imported"


def test_flush_records_error(studio_db, monkeypatch):
    def fake_urlopen(req, timeout=30):
        raise HTTPError("http://x", 500, "nope", hdrs=None, fp=BytesIO())

    monkeypatch.setenv("TRINITY_TELEMETRY_URL", "http://127.0.0.1:9/v1/events")
    monkeypatch.setattr("telemetry.urllib.request.urlopen", fake_urlopen)
    with db() as conn:
        record_event(conn, "review_run_imported", "pipeline_run", "pr-y", "pr-y", {})
        # URL is set so record_event already tried flush; pending should remain
        pending = conn.execute(
            "SELECT COUNT(*) FROM telemetry_outbox WHERE sent_at IS NULL"
        ).fetchone()[0]
    assert pending >= 1


def test_flush_retries_pending_event(studio_db, monkeypatch):
    attempts = []

    class DummyResp:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def fail(req, timeout=30):
        attempts.append("failed")
        raise HTTPError("http://x", 500, "nope", hdrs=None, fp=BytesIO())

    def succeed(req, timeout=30):
        attempts.append("sent")
        return DummyResp()

    monkeypatch.setenv("TRINITY_TELEMETRY_URL", "http://127.0.0.1:8787/v1/events")
    monkeypatch.setattr("telemetry.urllib.request.urlopen", fail)
    with db() as conn:
        record_event(conn, "review_run_imported", "pipeline_run", "pr-retry", "pr-retry", {})
        assert conn.execute(
            "SELECT COUNT(*) FROM telemetry_outbox WHERE sent_at IS NULL"
        ).fetchone()[0] == 1

        monkeypatch.setattr("telemetry.urllib.request.urlopen", succeed)
        result = flush_outbox(conn)
        assert result == {"flushed": 1, "failed": 0, "pending": 0}

    assert attempts == ["failed", "sent"]
