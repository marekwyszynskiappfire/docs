import json
import uuid
from pathlib import Path

from db import db, utc_now

REPO = Path(__file__).resolve().parents[3]
DEMO_BATCH = REPO / "Trinity/creator/samples/demo-story.suite.json"
CREATOR_ROOT = REPO / "Trinity/creator"


def test_build_suite_report_from_batch(tmp_path):
    import sys

    sys.path.insert(0, str(CREATOR_ROOT))
    from suite_report.build import build_report_payload, write_suite_report

    batch = json.loads(DEMO_BATCH.read_text(encoding="utf-8"))
    payload = build_report_payload(run_id="demo", batch=batch)
    assert len(payload["rows"]) == len(batch["tests"])
    index = write_suite_report(tmp_path / "suite-report", payload)
    assert index.is_file()
    data_js = tmp_path / "suite-report" / "data" / "report-data.js"
    assert "window.REPORT_DATA" in data_js.read_text(encoding="utf-8")


def test_studio_export_suite_report(client):
    batch = json.loads(DEMO_BATCH.read_text(encoding="utf-8"))
    run_id = f"suite-{uuid.uuid4().hex[:8]}"
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
            INSERT INTO test_case_batch_revision
              (creator_run_id, revision, batch_json, source, created_at, created_by)
            VALUES (?, 1, ?, 'import', ?, 'test')
            """,
            (run_id, json.dumps(batch), now),
        )
    r = client.post(f"/api/creator-runs/{run_id}/export-suite-report")
    assert r.status_code == 200
    body = r.json()
    assert body["test_count"] == len(batch["tests"])
    assert body["profile"] == "B"
    assert Path(body["absolute_path"]).is_file()
