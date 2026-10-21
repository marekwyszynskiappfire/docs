"""Local metrics + optional BigQuery ingest (best-effort, non-blocking)."""

from __future__ import annotations

import json
import os
import pwd
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any

from db import get_db_path, log_event, utc_now
from trinity_release import trinity_release_version

# Rejection categories (aligned with METRICS.md / scorecard)
REJECTION_REASONS: tuple[str, ...] = (
    "granularity_too_high",
    "granularity_too_low",
    "duplicate",
    "missing_scenarios",
    "wrong_assumptions",
    "weak_steps_or_expected",
    "requirements_mismatch",
    "maintainability",
    "other",
)

REJECTION_REASON_LABELS: dict[str, str] = {
    "granularity_too_high": "Granularity too high",
    "granularity_too_low": "Granularity too low",
    "duplicate": "Duplicate",
    "missing_scenarios": "Missing scenarios",
    "wrong_assumptions": "Incorrect assumptions",
    "weak_steps_or_expected": "Weak steps or expected results",
    "requirements_mismatch": "Does not match requirements",
    "maintainability": "Maintainability concerns",
    "other": "Other",
}

REPORT_SNAPSHOT_EVENT = "pipeline_run_report_snapshot"


def _install_id_path() -> Path:
    return get_db_path().parent / ".telemetry_install_id"


def studio_install_id() -> str:
    path = _install_id_path()
    if path.is_file():
        return path.read_text(encoding="utf-8").strip()
    value = str(uuid.uuid4())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")
    return value


def operator_id() -> str:
    """Login of the human operator (Jira email), never the GCP service account."""
    return (
        os.environ.get("TRINITY_OPERATOR_ID", "").strip()
        or os.environ.get("JIRA_EMAIL", "").strip()
        or "unknown"
    )


def operator_name() -> str:
    """Display name of the human who is running Studio."""
    explicit = os.environ.get("TRINITY_OPERATOR_NAME", "").strip()
    if explicit:
        return explicit
    try:
        gecos = pwd.getpwuid(os.getuid()).pw_gecos.split(",")[0].strip()
        if gecos:
            return gecos
    except (KeyError, OSError, AttributeError):
        pass
    login = operator_id()
    if login and login != "unknown" and "@" in login:
        return login.split("@", 1)[0]
    return login or "unknown"


def trinity_version() -> str:
    return trinity_release_version()


def _product_label(product_id: str | None) -> tuple[str | None, str | None]:
    if not product_id:
        return None, None
    try:
        from creator_importer_config import load_creator_product_config

        cfg = load_creator_product_config(product_id)
        product = cfg.get("product") or {}
        pid = str(product.get("id") or product_id)
        name = str(product.get("name") or pid)
        return pid, name
    except Exception:
        return product_id, product_id


def resolve_pipeline_run_id(
    conn: Any,
    pipeline_run_id: str | None,
    entity_type: str,
    entity_id: str | None,
) -> str | None:
    if pipeline_run_id:
        return pipeline_run_id
    if not entity_id:
        return None
    if entity_type == "creator_run":
        row = conn.execute(
            "SELECT pipeline_run_id FROM creator_run WHERE id = ?", (entity_id,)
        ).fetchone()
        return row["pipeline_run_id"] if row else None
    if entity_type == "review_unit":
        row = conn.execute(
            "SELECT pipeline_run_id FROM review_unit WHERE id = ?", (entity_id,)
        ).fetchone()
        return row["pipeline_run_id"] if row else None
    if entity_type == "test_case":
        row = conn.execute(
            """
            SELECT cr.pipeline_run_id
            FROM test_case_row t
            JOIN creator_run cr ON cr.id = t.creator_run_id
            WHERE t.id = ?
            """,
            (entity_id,),
        ).fetchone()
        return row["pipeline_run_id"] if row else None
    return None


def resolve_product(conn: Any, pipeline_run_id: str | None, payload: dict[str, Any] | None) -> tuple[str | None, str | None]:
    raw = (payload or {}).get("product_id")
    if pipeline_run_id:
        row = conn.execute(
            "SELECT product_id, creator_handoff_json FROM pipeline_run WHERE id = ?",
            (pipeline_run_id,),
        ).fetchone()
        if row:
            raw = raw or row["product_id"]
            if not raw and row["creator_handoff_json"]:
                try:
                    handoff = json.loads(row["creator_handoff_json"])
                    if isinstance(handoff, dict):
                        raw = handoff.get("product_id")
                except json.JSONDecodeError:
                    pass
    if not raw and (payload or {}).get("creator_run_id"):
        creator_id = str(payload["creator_run_id"])
        batch = conn.execute(
            """
            SELECT batch_json FROM test_case_batch_revision
            WHERE creator_run_id = ? ORDER BY revision DESC LIMIT 1
            """,
            (creator_id,),
        ).fetchone()
        if batch and batch["batch_json"]:
            try:
                data = json.loads(batch["batch_json"])
                if isinstance(data, dict):
                    raw = data.get("product_id")
            except json.JSONDecodeError:
                pass
    return _product_label(str(raw) if raw else None)


def _envelope(
    event_type: str,
    entity_type: str,
    entity_id: str | None,
    pipeline_run_id: str | None,
    payload: dict[str, Any] | None,
    *,
    product_id: str | None = None,
    product_name: str | None = None,
    event_operator_id: str | None = None,
    event_operator_name: str | None = None,
    event_id: str | None = None,
) -> dict[str, Any]:
    return {
        "event_id": event_id or str(uuid.uuid4()),
        "event_time": utc_now(),
        "event_type": event_type,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "pipeline_run_id": pipeline_run_id,
        "operator_id": event_operator_id or operator_id(),
        "operator_name": event_operator_name or operator_name(),
        "product_id": product_id,
        "product_name": product_name,
        "studio_install_id": studio_install_id(),
        "trinity_version": trinity_version(),
        "payload": payload or {},
    }


def _insert_outbox(conn: Any, envelope: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT INTO telemetry_outbox (event_json, created_at, sent_at, last_error)
        VALUES (?, ?, NULL, NULL)
        """,
        (json.dumps(envelope, ensure_ascii=False), utc_now()),
    )


def queue_report_snapshot(conn: Any, report: dict[str, Any]) -> dict[str, Any] | None:
    """Queue a current-run statistics snapshot for BigQuery upsert. No-op without ingest URL."""
    if not _telemetry_url():
        return None
    run_id = report.get("pipeline_run_id")
    if not run_id:
        return None
    product_ctx = report.get("product_context") or {}
    product_id, product_name = _product_label(product_ctx.get("product_id"))
    slim = {
        "schema_version": report.get("schema_version"),
        "pipeline_label": report.get("pipeline_label"),
        "computed_at": report.get("computed_at"),
        "product_context": product_ctx,
        "summary": report.get("summary") or {},
    }
    envelope = _envelope(
        REPORT_SNAPSHOT_EVENT,
        "pipeline_run",
        str(run_id),
        str(run_id),
        slim,
        product_id=product_id,
        product_name=product_name,
        event_operator_id=product_ctx.get("operator_id"),
        event_operator_name=product_ctx.get("operator_name"),
    )
    envelope["report"] = report
    _insert_outbox(conn, envelope)
    return envelope


def sync_all_runs(conn: Any) -> dict[str, Any]:
    """Recompute every run snapshot, then flush all pending telemetry."""
    from import_review import repair_creator_pipeline_links, repair_pipeline_products

    creator_links_repaired = repair_creator_pipeline_links(conn)
    products_repaired = repair_pipeline_products(conn)
    conn.execute(
        """
        UPDATE pipeline_run
        SET operator_id = COALESCE(operator_id, ?),
            operator_name = COALESCE(operator_name, ?)
        WHERE operator_id IS NULL OR operator_name IS NULL
        """,
        (operator_id(), operator_name()),
    )
    run_ids = [
        row["id"]
        for row in conn.execute(
            "SELECT id FROM pipeline_run ORDER BY created_at ASC"
        ).fetchall()
    ]
    reports_queued = 0
    report_errors: list[dict[str, str]] = []
    if _telemetry_url():
        from run_report import persist_pipeline_run_report

        for run_id in run_ids:
            try:
                persist_pipeline_run_report(conn, run_id, flush_telemetry=False)
                reports_queued += 1
            except Exception as exc:
                report_errors.append(
                    {"pipeline_run_id": run_id, "error": str(exc)[:300]}
                )
    flush = flush_outbox(conn, limit=5000)
    return {
        "runs_seen": len(run_ids),
        "creator_links_repaired": creator_links_repaired,
        "products_repaired": products_repaired,
        "reports_queued": reports_queued,
        "report_errors": report_errors,
        **flush,
    }


def record_event(
    conn: Any,
    event_type: str,
    entity_type: str,
    entity_id: str | None = None,
    pipeline_run_id: str | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Write metric_event + telemetry_outbox; refresh run report; flush to ingest."""
    pipeline_run_id = resolve_pipeline_run_id(conn, pipeline_run_id, entity_type, entity_id)
    product_id, product_name = resolve_product(conn, pipeline_run_id, payload)
    log_event(conn, event_type, entity_type, entity_id, pipeline_run_id, payload)
    envelope = _envelope(
        event_type,
        entity_type,
        entity_id,
        pipeline_run_id,
        payload,
        product_id=product_id,
        product_name=product_name,
    )
    _insert_outbox(conn, envelope)
    if pipeline_run_id and event_type != REPORT_SNAPSHOT_EVENT:
        try:
            from run_report import persist_pipeline_run_report

            persist_pipeline_run_report(conn, pipeline_run_id)
        except Exception:
            _try_flush_pending(conn, max_rows=200)
    else:
        _try_flush_pending(conn, max_rows=200)
    return envelope


def validate_rejection_reason(reason: str | None, status: str) -> str | None:
    if status != "rejected":
        return None
    if not reason or reason not in REJECTION_REASONS:
        raise ValueError(
            f"rejection_reason required when rejecting; use one of: {', '.join(REJECTION_REASONS)}"
        )
    return reason


def _telemetry_url() -> str | None:
    url = os.environ.get("TRINITY_TELEMETRY_URL", "").strip()
    return url or None


def _telemetry_api_key() -> str | None:
    key = os.environ.get("TRINITY_TELEMETRY_API_KEY", "").strip()
    return key or None


def flush_outbox(conn: Any, limit: int = 200) -> dict[str, Any]:
    """POST pending outbox rows to TRINITY_TELEMETRY_URL. No-op if URL unset."""
    url = _telemetry_url()
    if not url:
        pending = conn.execute(
            "SELECT COUNT(*) FROM telemetry_outbox WHERE sent_at IS NULL"
        ).fetchone()[0]
        return {"flushed": 0, "failed": 0, "pending": pending, "skipped": "no_url"}

    rows = conn.execute(
        """
        SELECT id, event_json FROM telemetry_outbox
        WHERE sent_at IS NULL
        ORDER BY id ASC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    if not rows:
        pending = conn.execute(
            "SELECT COUNT(*) FROM telemetry_outbox WHERE sent_at IS NULL"
        ).fetchone()[0]
        return {"flushed": 0, "failed": 0, "pending": pending}

    events: list[dict[str, Any]] = []
    row_ids: list[int] = []
    for row in rows:
        event = json.loads(row["event_json"])
        run_id = resolve_pipeline_run_id(
            conn,
            event.get("pipeline_run_id"),
            str(event.get("entity_type") or ""),
            event.get("entity_id"),
        )
        product_id, product_name = resolve_product(
            conn, run_id, event.get("payload")
        )
        event["pipeline_run_id"] = run_id
        event["operator_id"] = event.get("operator_id") or operator_id()
        event["operator_name"] = event.get("operator_name") or operator_name()
        event["product_id"] = event.get("product_id") or product_id
        event["product_name"] = event.get("product_name") or product_name
        events.append(event)
        row_ids.append(row["id"])

    body = json.dumps({"events": events}).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    api_key = _telemetry_api_key()
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    flushed = 0
    failed = 0
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            if resp.status >= 400:
                raise urllib.error.HTTPError(url, resp.status, resp.reason, resp.headers, None)
        now = utc_now()
        for row_id in row_ids:
            conn.execute(
                "UPDATE telemetry_outbox SET sent_at = ?, last_error = NULL WHERE id = ?",
                (now, row_id),
            )
        flushed = len(row_ids)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        failed = len(row_ids)
        err = str(exc)[:500]
        for row_id in row_ids:
            conn.execute(
                "UPDATE telemetry_outbox SET last_error = ? WHERE id = ?",
                (err, row_id),
            )
    pending = conn.execute(
        "SELECT COUNT(*) FROM telemetry_outbox WHERE sent_at IS NULL"
    ).fetchone()[0]
    return {"flushed": flushed, "failed": failed, "pending": pending}


def _try_flush_pending(conn: Any, max_rows: int) -> None:
    if not _telemetry_url():
        return
    try:
        flush_outbox(conn, limit=max_rows)
    except Exception:
        pass


def operator_review_summary(conn: Any) -> dict[str, Any]:
    total = conn.execute("SELECT COUNT(*) FROM test_case_row").fetchone()[0]
    approved = conn.execute(
        "SELECT COUNT(*) FROM test_case_row WHERE human_review_status = 'approved'"
    ).fetchone()[0]
    rejected = conn.execute(
        "SELECT COUNT(*) FROM test_case_row WHERE human_review_status = 'rejected'"
    ).fetchone()[0]
    pending = total - approved - rejected
    acceptance_rate = round(approved / total, 4) if total else None

    reasons: list[dict[str, Any]] = []
    for row in conn.execute(
        """
        SELECT rejection_reason, COUNT(*) AS n
        FROM test_case_row
        WHERE human_review_status = 'rejected' AND rejection_reason IS NOT NULL
        GROUP BY rejection_reason
        ORDER BY n DESC
        """
    ):
        reasons.append(
            {
                "reason": row["rejection_reason"],
                "label": REJECTION_REASON_LABELS.get(row["rejection_reason"], row["rejection_reason"]),
                "count": row["n"],
            }
        )

    events = conn.execute("SELECT COUNT(*) FROM metric_event").fetchone()[0]
    outbox_pending = conn.execute(
        "SELECT COUNT(*) FROM telemetry_outbox WHERE sent_at IS NULL"
    ).fetchone()[0]

    return {
        "operator_id": operator_id(),
        "operator_name": operator_name(),
        "studio_install_id": studio_install_id(),
        "test_cases_total": total,
        "test_cases_approved": approved,
        "test_cases_rejected": rejected,
        "test_cases_pending_or_edited": pending,
        "acceptance_rate": acceptance_rate,
        "rejection_reasons": reasons,
        "metric_events_total": events,
        "telemetry_outbox_pending": outbox_pending,
        "bigquery_configured": bool(_telemetry_url()),
    }


def mateusz_summary(conn: Any) -> dict[str, Any]:
    """Deprecated alias — use operator_review_summary."""
    return operator_review_summary(conn)
