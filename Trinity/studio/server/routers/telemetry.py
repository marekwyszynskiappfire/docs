"""Local metrics summary, export bundle, and outbox flush."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from cursor_cost import cursor_usage_export_bundle
from db import db, row_to_dict, utc_now
from telemetry import (
    REJECTION_REASON_LABELS,
    REJECTION_REASONS,
    flush_outbox,
    operator_review_summary,
    sync_all_runs,
)

router = APIRouter(tags=["telemetry"])


@router.get("/api/telemetry/rejection-reasons")
def telemetry_rejection_reasons() -> dict[str, Any]:
    return {
        "reasons": [
            {"id": r, "label": REJECTION_REASON_LABELS[r]} for r in REJECTION_REASONS
        ]
    }


@router.get("/api/telemetry/summary")
def telemetry_summary() -> dict[str, Any]:
    with db() as conn:
        return operator_review_summary(conn)


@router.get("/api/telemetry/events")
def telemetry_events(limit: int = 500) -> dict[str, Any]:
    cap = min(max(limit, 1), 5000)
    with db() as conn:
        rows = conn.execute(
            """
            SELECT id, pipeline_run_id, entity_type, entity_id, event_type, payload_json, created_at
            FROM metric_event ORDER BY id DESC LIMIT ?
            """,
            (cap,),
        ).fetchall()
    return {"events": [row_to_dict(r) for r in rows]}


@router.get("/api/telemetry/export")
def telemetry_export() -> dict[str, Any]:
    """Single JSON bundle for scorecard / evidence (local; copy before BigQuery exists)."""
    with db() as conn:
        summary = operator_review_summary(conn)
        rows = conn.execute(
            """
            SELECT id, pipeline_run_id, entity_type, entity_id, event_type, payload_json, created_at
            FROM metric_event ORDER BY id ASC
            """
        ).fetchall()
        outbox_pending = conn.execute(
            "SELECT COUNT(*) FROM telemetry_outbox WHERE sent_at IS NULL"
        ).fetchone()[0]
        cursor_usage = cursor_usage_export_bundle(conn)
    return {
        "exported_at": utc_now(),
        "summary": summary,
        "cursor_usage": cursor_usage,
        "metric_events": [row_to_dict(r) for r in rows],
        "telemetry_outbox_pending": outbox_pending,
    }


@router.post("/api/telemetry/flush")
def telemetry_flush() -> dict[str, Any]:
    with db() as conn:
        return flush_outbox(conn)


@router.post("/api/telemetry/sync")
def telemetry_sync() -> dict[str, Any]:
    """Backfill all pending events and current run snapshots to configured ingest."""
    with db() as conn:
        return sync_all_runs(conn)
