from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "bq_ingest.py"
SPEC = importlib.util.spec_from_file_location("bq_ingest", SCRIPT)
assert SPEC and SPEC.loader
bq_ingest = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bq_ingest)


class QueryResult:
    def __init__(self, rows=()):
        self.rows = rows

    def result(self):
        return self.rows


class FakeBigQueryClient:
    def __init__(self):
        self.queries = []
        self.inserted = []

    def query(self, sql, job_config=None):
        self.queries.append((sql, job_config))
        return QueryResult()

    def insert_rows_json(self, table, rows):
        self.inserted.append((table, rows))
        return []


def test_snapshot_event_inserts_event_and_upserts_current_report(monkeypatch):
    client = FakeBigQueryClient()
    monkeypatch.setattr(bq_ingest, "_client", lambda: (client, object()))
    monkeypatch.setattr(
        bq_ingest,
        "_table_ids",
        lambda: ("qa-coe.trinity.telemetry_events", "qa-coe.trinity.pipeline_run_reports"),
    )
    event = {
        "event_id": "event-1",
        "event_time": "2026-10-21T12:00:00+00:00",
        "event_type": bq_ingest.REPORT_SNAPSHOT_EVENT,
        "pipeline_run_id": "run-1",
        "operator_id": "operator@appfire.com",
        "operator_name": "Operator",
        "product_id": "bigpicture",
        "product_name": "BigPicture",
        "payload": {},
        "report": {
            "pipeline_run_id": "run-1",
            "pipeline_label": "Release gate",
            "schema_version": 1,
            "computed_at": "2026-10-21T12:00:00+00:00",
            "product_context": {"product_id": "bigpicture"},
            "summary": {"tests_drafted": 3},
        },
    }

    result = bq_ingest.ingest_events([event])

    assert result == {"inserted": 1, "duplicates": 0, "reports_upserted": 1}
    assert client.inserted[0][0] == "qa-coe.trinity.telemetry_events"
    merge_sql = client.queries[1][0]
    assert "MERGE `qa-coe.trinity.pipeline_run_reports`" in merge_sql
    assert "WHEN MATCHED THEN UPDATE" in merge_sql
    assert "WHEN NOT MATCHED THEN INSERT" in merge_sql
