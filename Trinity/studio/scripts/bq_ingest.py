#!/usr/bin/env python3
"""Local Trinity → BigQuery ingest. Binds 127.0.0.1 only.

The GCP service account is the writer. Operator identity and product come from
each Studio event envelope, not from the key file.
"""

from __future__ import annotations

import argparse
import json
import os
import hmac
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

REPORT_SNAPSHOT_EVENT = "pipeline_run_report_snapshot"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _client():
    from google.cloud import bigquery

    project = os.environ.get("BQ_PROJECT", "qa-coe").strip() or "qa-coe"
    return bigquery.Client(project=project), bigquery


def _table_ids() -> tuple[str, str]:
    project = os.environ.get("BQ_PROJECT", "qa-coe").strip() or "qa-coe"
    dataset = os.environ.get("BQ_DATASET", "trinity").strip() or "trinity"
    return f"{project}.{dataset}.telemetry_events", f"{project}.{dataset}.pipeline_run_reports"


def ensure_schema() -> None:
    """Create/upgrade BigQuery tables and Looker-friendly views idempotently."""
    client, _bq = _client()
    events_table, reports_table = _table_ids()
    project, dataset, _ = events_table.split(".", 2)
    statements = [
        f"""
        CREATE TABLE IF NOT EXISTS `{events_table}` (
          event_id STRING NOT NULL,
          event_time TIMESTAMP NOT NULL,
          event_type STRING NOT NULL,
          entity_type STRING,
          entity_id STRING,
          pipeline_run_id STRING,
          operator_id STRING,
          operator_name STRING,
          product_id STRING,
          product_name STRING,
          studio_install_id STRING,
          trinity_version STRING,
          payload JSON,
          ingested_at TIMESTAMP NOT NULL
        )
        PARTITION BY DATE(event_time)
        CLUSTER BY pipeline_run_id, event_type, entity_type
        OPTIONS(description = 'Raw telemetry events uploaded by Trinity Studio')
        """,
        f"""
        CREATE TABLE IF NOT EXISTS `{reports_table}` (
          pipeline_run_id STRING NOT NULL,
          pipeline_label STRING,
          schema_version INT64 NOT NULL,
          computed_at TIMESTAMP NOT NULL,
          product_id STRING,
          product_name STRING,
          operator_id STRING,
          operator_name STRING,
          report JSON NOT NULL,
          ingested_at TIMESTAMP NOT NULL
        )
        PARTITION BY DATE(computed_at)
        CLUSTER BY product_id, pipeline_run_id
        OPTIONS(description = 'Current per-run Trinity statistics for reporting')
        """,
    ]
    event_columns = {
        "operator_name": "STRING",
        "product_id": "STRING",
        "product_name": "STRING",
    }
    report_columns = {
        "operator_id": "STRING",
        "operator_name": "STRING",
        "product_name": "STRING",
    }
    for name, kind in event_columns.items():
        statements.append(
            f"ALTER TABLE `{events_table}` ADD COLUMN IF NOT EXISTS {name} {kind}"
        )
    for name, kind in report_columns.items():
        statements.append(
            f"ALTER TABLE `{reports_table}` ADD COLUMN IF NOT EXISTS {name} {kind}"
        )
    statements.extend(
        [
            f"""
            CREATE OR REPLACE VIEW `{project}.{dataset}.v_run_summary` AS
            SELECT
              pipeline_run_id,
              pipeline_label,
              operator_id,
              operator_name,
              product_id,
              product_name,
              computed_at,
              ingested_at,
              SAFE_CAST(JSON_VALUE(report, '$.summary.epics_reviewed') AS INT64)
                AS epics_reviewed,
              SAFE_CAST(JSON_VALUE(report, '$.summary.issues_spotted_findings_total') AS INT64)
                AS findings_total,
              SAFE_CAST(JSON_VALUE(report, '$.summary.epics_tc_creation_ready') AS INT64)
                AS epics_ready,
              SAFE_CAST(JSON_VALUE(report, '$.summary.epics_tc_creation_ready_with_reservations') AS INT64)
                AS epics_ready_with_reservations,
              SAFE_CAST(JSON_VALUE(report, '$.summary.epics_tc_creation_not_ready') AS INT64)
                AS epics_not_ready,
              SAFE_CAST(JSON_VALUE(report, '$.summary.test_cases_drafted_total') AS INT64)
                AS test_cases_drafted,
              SAFE_CAST(JSON_VALUE(report, '$.summary.test_cases_amended_total') AS INT64)
                AS test_cases_amended,
              SAFE_CAST(JSON_VALUE(report, '$.summary.test_cases_sent_to_import_total') AS INT64)
                AS test_cases_sent_to_import,
              SAFE_CAST(JSON_VALUE(report, '$.summary.test_cases_imported_to_xray_total') AS INT64)
                AS test_cases_imported_to_xray,
              SAFE_CAST((
                SELECT JSON_VALUE(phase, '$.duration_seconds')
                FROM UNNEST(JSON_QUERY_ARRAY(report, '$.phases')) phase
                WHERE JSON_VALUE(phase, '$.phase') = 'overall'
                LIMIT 1
              ) AS FLOAT64) AS overall_duration_seconds
            FROM `{reports_table}`
            """,
            f"""
            CREATE OR REPLACE VIEW `{project}.{dataset}.v_run_phases` AS
            SELECT
              r.pipeline_run_id,
              r.pipeline_label,
              r.operator_id,
              r.operator_name,
              r.product_id,
              r.product_name,
              r.computed_at,
              JSON_VALUE(phase, '$.phase') AS phase,
              JSON_VALUE(phase, '$.label') AS phase_label,
              TIMESTAMP(JSON_VALUE(phase, '$.started_at')) AS started_at,
              TIMESTAMP(JSON_VALUE(phase, '$.ended_at')) AS ended_at,
              SAFE_CAST(JSON_VALUE(phase, '$.duration_seconds') AS FLOAT64)
                AS duration_seconds,
              JSON_VALUE(phase, '$.notes') AS notes
            FROM `{reports_table}` r,
            UNNEST(JSON_QUERY_ARRAY(r.report, '$.phases')) phase
            """,
            f"""
            CREATE OR REPLACE VIEW `{project}.{dataset}.v_run_epics` AS
            SELECT
              r.pipeline_run_id,
              r.pipeline_label,
              r.operator_id,
              r.operator_name,
              r.product_id,
              r.product_name,
              r.computed_at,
              JSON_VALUE(epic, '$.jira_key') AS jira_key,
              JSON_VALUE(epic, '$.summary') AS epic_summary,
              JSON_VALUE(epic, '$.gate_status') AS gate_status,
              JSON_VALUE(epic, '$.qa_planning_fit') AS qa_planning_fit,
              JSON_VALUE(epic, '$.tc_creation_readiness') AS tc_creation_readiness,
              SAFE_CAST(JSON_VALUE(epic, '$.findings_total') AS INT64)
                AS findings_total,
              SAFE_CAST(JSON_VALUE(epic, '$.questions_total') AS INT64)
                AS questions_total,
              SAFE_CAST(JSON_VALUE(epic, '$.test_cases_drafted') AS INT64)
                AS test_cases_drafted,
              SAFE_CAST(JSON_VALUE(epic, '$.test_cases_sent_to_import') AS INT64)
                AS test_cases_sent_to_import,
              SAFE_CAST(JSON_VALUE(epic, '$.test_cases_xray_imported') AS INT64)
                AS test_cases_xray_imported
            FROM `{reports_table}` r,
            UNNEST(JSON_QUERY_ARRAY(r.report, '$.epics')) epic
            """,
            f"""
            CREATE OR REPLACE VIEW `{project}.{dataset}.v_event_details` AS
            SELECT
              event_id,
              event_time,
              event_type,
              entity_type,
              entity_id,
              pipeline_run_id,
              operator_id,
              operator_name,
              product_id,
              product_name,
              trinity_version,
              JSON_VALUE(payload, '$.human_review_status') AS human_review_status,
              JSON_VALUE(payload, '$.rejection_reason') AS rejection_reason,
              SAFE_CAST(JSON_VALUE(payload, '$.ai_generated_test_count') AS INT64)
                AS ai_generated_test_count,
              ingested_at
            FROM `{events_table}`
            """
        ]
    )
    for statement in statements:
        client.query(statement).result()


def _api_key() -> str:
    return os.environ.get("TRINITY_TELEMETRY_API_KEY", "").strip()


def _authorized(handler: BaseHTTPRequestHandler) -> bool:
    expected = _api_key()
    if not expected:
        return True
    got = handler.headers.get("Authorization", "")
    prefix = "Bearer "
    if not got.startswith(prefix):
        return False
    token = got[len(prefix) :].strip()
    return hmac.compare_digest(token, expected)


def _parse_ts(value: Any) -> str | None:
    if not value:
        return None
    text = str(value).replace("Z", "+00:00")
    datetime.fromisoformat(text)  # validate
    return text


def _event_row(event: dict[str, Any]) -> dict[str, Any]:
    payload = event.get("payload")
    if payload is not None and not isinstance(payload, (dict, list)):
        payload = {"value": payload}
    return {
        "event_id": str(event["event_id"]),
        "event_time": _parse_ts(event.get("event_time")) or _now(),
        "event_type": str(event["event_type"]),
        "entity_type": event.get("entity_type"),
        "entity_id": event.get("entity_id"),
        "pipeline_run_id": event.get("pipeline_run_id"),
        "operator_id": event.get("operator_id"),
        "operator_name": event.get("operator_name"),
        "product_id": event.get("product_id"),
        "product_name": event.get("product_name"),
        "studio_install_id": event.get("studio_install_id"),
        "trinity_version": event.get("trinity_version"),
        "payload": json.dumps(payload if payload is not None else {}),
        "ingested_at": _now(),
    }


def ingest_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    from google.cloud.bigquery import ArrayQueryParameter, QueryJobConfig, ScalarQueryParameter

    client, _bq = _client()
    events_table, reports_table = _table_ids()
    rows = [_event_row(e) for e in events]
    ids = [r["event_id"] for r in rows]
    existing: set[str] = set()
    if ids:
        job = client.query(
            f"SELECT event_id FROM `{events_table}` WHERE event_id IN UNNEST(@ids)",
            job_config=QueryJobConfig(
                query_parameters=[ArrayQueryParameter("ids", "STRING", ids)]
            ),
        )
        existing = {row.event_id for row in job.result()}
    new_rows = [r for r in rows if r["event_id"] not in existing]
    inserted = 0
    if new_rows:
        errors = client.insert_rows_json(events_table, new_rows)
        if errors:
            raise RuntimeError(f"insert_rows_json failed: {errors}")
        inserted = len(new_rows)

    reports_upserted = 0
    for event in events:
        if event.get("event_type") != REPORT_SNAPSHOT_EVENT:
            continue
        report = event.get("report")
        if not isinstance(report, dict):
            report = event.get("payload") if isinstance(event.get("payload"), dict) else None
        if not report:
            continue
        run_id = str(report.get("pipeline_run_id") or event.get("pipeline_run_id") or "")
        if not run_id:
            continue
        product_ctx = report.get("product_context") or {}
        product_id = event.get("product_id") or product_ctx.get("product_id")
        merge = f"""
        MERGE `{reports_table}` T
        USING (
          SELECT
            @pipeline_run_id AS pipeline_run_id,
            @pipeline_label AS pipeline_label,
            @schema_version AS schema_version,
            TIMESTAMP(@computed_at) AS computed_at,
            @product_id AS product_id,
            @product_name AS product_name,
            @operator_id AS operator_id,
            @operator_name AS operator_name,
            PARSE_JSON(@report_json) AS report,
            CURRENT_TIMESTAMP() AS ingested_at
        ) S
        ON T.pipeline_run_id = S.pipeline_run_id
        WHEN MATCHED THEN UPDATE SET
          pipeline_label = S.pipeline_label,
          schema_version = S.schema_version,
          computed_at = S.computed_at,
          product_id = S.product_id,
          product_name = S.product_name,
          operator_id = S.operator_id,
          operator_name = S.operator_name,
          report = S.report,
          ingested_at = S.ingested_at
        WHEN NOT MATCHED THEN INSERT (
          pipeline_run_id, pipeline_label, schema_version, computed_at,
          product_id, product_name, operator_id, operator_name, report, ingested_at
        ) VALUES (
          S.pipeline_run_id, S.pipeline_label, S.schema_version, S.computed_at,
          S.product_id, S.product_name, S.operator_id, S.operator_name, S.report, S.ingested_at
        )
        """
        computed = report.get("computed_at") or event.get("event_time") or _now()
        client.query(
            merge,
            job_config=QueryJobConfig(
                query_parameters=[
                    ScalarQueryParameter("pipeline_run_id", "STRING", run_id),
                    ScalarQueryParameter("pipeline_label", "STRING", report.get("pipeline_label")),
                    ScalarQueryParameter("schema_version", "INT64", int(report.get("schema_version") or 0)),
                    ScalarQueryParameter("computed_at", "STRING", str(computed).replace("Z", "+00:00")),
                    ScalarQueryParameter("product_id", "STRING", product_id),
                    ScalarQueryParameter("product_name", "STRING", event.get("product_name")),
                    ScalarQueryParameter("operator_id", "STRING", event.get("operator_id")),
                    ScalarQueryParameter("operator_name", "STRING", event.get("operator_name")),
                    ScalarQueryParameter("report_json", "STRING", json.dumps(report, ensure_ascii=False)),
                ]
            ),
        ).result()
        reports_upserted += 1

    return {
        "inserted": inserted,
        "duplicates": len(rows) - inserted,
        "reports_upserted": reports_upserted,
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, code: int, body: dict[str, Any]) -> None:
        raw = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in ("/health", "/v1/health"):
            self._send(200, {"status": "ok"})
            return
        self._send(404, {"error": "not_found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path not in ("/v1/events", "/events"):
            self._send(404, {"error": "not_found"})
            return
        if not _authorized(self):
            self._send(401, {"error": "unauthorized"})
            return
        length = int(self.headers.get("Content-Length") or "0")
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._send(400, {"error": "invalid_json"})
            return
        events = body.get("events") if isinstance(body, dict) else None
        if not isinstance(events, list) or not events:
            self._send(400, {"error": "events_required"})
            return
        try:
            result = ingest_events(events)
        except Exception as exc:
            self._send(500, {"error": "ingest_failed", "detail": str(exc)[:500]})
            return
        self._send(200, result)


def main() -> None:
    parser = argparse.ArgumentParser(description="Trinity BigQuery ingest")
    parser.add_argument(
        "--setup-only",
        action="store_true",
        help="Create/upgrade tables and reporting views, then exit",
    )
    args = parser.parse_args()
    ensure_schema()
    if args.setup_only:
        events_table, reports_table = _table_ids()
        print(f"BigQuery schema ready: {events_table}, {reports_table}")
        return
    host = os.environ.get("TRINITY_INGEST_HOST", "127.0.0.1")
    port = int(os.environ.get("TRINITY_INGEST_PORT", "8787"))
    events_table, reports_table = _table_ids()
    print(f"Trinity BigQuery ingest on http://{host}:{port}/v1/events", flush=True)
    print(f"  events  {events_table}", flush=True)
    print(f"  reports {reports_table}", flush=True)
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
