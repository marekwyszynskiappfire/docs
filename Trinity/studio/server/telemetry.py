"""Local metrics + optional BigQuery ingest (best-effort, non-blocking)."""

from __future__ import annotations

import json
import os
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
    return (
        os.environ.get("TRINITY_OPERATOR_ID", "").strip()
        or os.environ.get("JIRA_EMAIL", "").strip()
        or "unknown"
    )


def trinity_version() -> str:
    return trinity_release_version()


def _envelope(
    event_type: str,
    entity_type: str,
    entity_id: str | None,
    pipeline_run_id: str | None,
    payload: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "event_id": str(uuid.uuid4()),
        "event_time": utc_now(),
        "event_type": event_type,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "pipeline_run_id": pipeline_run_id,
        "operator_id": operator_id(),
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


def record_event(
    conn: Any,
    event_type: str,
    entity_type: str,
    entity_id: str | None = None,
    pipeline_run_id: str | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Write metric_event + telemetry_outbox; optionally try one flush."""
    log_event(conn, event_type, entity_type, entity_id, pipeline_run_id, payload)
    envelope = _envelope(event_type, entity_type, entity_id, pipeline_run_id, payload)
    _insert_outbox(conn, envelope)
    _try_flush_pending(conn, max_rows=5)
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
    flushed = 0
    failed = 0
    api_key = _telemetry_api_key()
    for row in rows:
        event = json.loads(row["event_json"])
        body = json.dumps({"events": [event]}).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status >= 400:
                    raise urllib.error.HTTPError(url, resp.status, resp.reason, resp.headers, None)
            conn.execute(
                "UPDATE telemetry_outbox SET sent_at = ?, last_error = NULL WHERE id = ?",
                (utc_now(), row["id"]),
            )
            flushed += 1
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            failed += 1
            conn.execute(
                "UPDATE telemetry_outbox SET last_error = ? WHERE id = ?",
                (str(exc)[:500], row["id"]),
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
