"""Cursor session context and usage cost attribution."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from api_models import CursorSessionBody, CursorUsageBody
from cursor_cost import (
    CURSOR_STAGES,
    STAGE_LABELS,
    backfill_costs_from_admin_api,
    normalize_stage,
    read_cursor_session_file,
    record_cursor_usage,
    usage_summary_for_creator,
    usage_summary_for_pipeline,
    write_cursor_session_file,
)
from db import db
from studio_paths import STUDIO_DATA

router = APIRouter(tags=["cursor-usage"])


@router.get("/api/cursor-usage/stages")
def cursor_usage_stages() -> dict[str, Any]:
    return {
        "stages": [{"id": s, "label": STAGE_LABELS[s]} for s in CURSOR_STAGES if s != "unscoped"]
        + [{"id": "unscoped", "label": STAGE_LABELS["unscoped"]}],
    }


@router.post("/api/cursor-session")
def cursor_session_begin(body: CursorSessionBody) -> dict[str, Any]:
    """Write context for Cursor hooks (next Agent session in this repo)."""
    path = write_cursor_session_file(
        STUDIO_DATA,
        pipeline_run_id=body.pipeline_run_id,
        creator_run_id=body.creator_run_id,
        stage=body.stage,
    )
    return {
        "path": str(path),
        "stage": normalize_stage(body.stage),
        "pipeline_run_id": body.pipeline_run_id,
        "creator_run_id": body.creator_run_id,
    }


@router.get("/api/cursor-session")
def cursor_session_read() -> dict[str, Any]:
    data = read_cursor_session_file(STUDIO_DATA)
    if not data:
        return {"active": False}
    return {"active": True, **data}


@router.post("/api/cursor-usage")
def cursor_usage_record(body: CursorUsageBody) -> dict[str, Any]:
    session = read_cursor_session_file(STUDIO_DATA) or {}
    pipeline_run_id = body.pipeline_run_id or session.get("pipeline_run_id")
    creator_run_id = body.creator_run_id or session.get("creator_run_id")
    stage = body.stage or session.get("stage") or "unscoped"
    try:
        with db() as conn:
            return record_cursor_usage(
                conn,
                stage=stage,
                conversation_id=body.conversation_id,
                pipeline_run_id=pipeline_run_id,
                creator_run_id=creator_run_id,
                model=body.model,
                model_id=body.model_id,
                generation_id=body.generation_id,
                duration_ms=body.duration_ms,
                status=body.status,
                input_tokens=body.input_tokens,
                output_tokens=body.output_tokens,
                cost_cents=body.cost_cents,
                source=body.source,
                notes=body.notes,
            )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@router.get("/api/cursor-usage/summary")
def cursor_usage_summary(
    pipeline_run_id: str | None = None,
    creator_run_id: str | None = None,
    include_events: bool = False,
) -> dict[str, Any]:
    if not pipeline_run_id and not creator_run_id:
        raise HTTPException(400, "Provide pipeline_run_id or creator_run_id")
    with db() as conn:
        if creator_run_id and not pipeline_run_id:
            summary = usage_summary_for_creator(conn, creator_run_id)
        else:
            summary = usage_summary_for_pipeline(conn, pipeline_run_id or "")
    if not include_events:
        summary.pop("events", None)
    return summary


@router.post("/api/cursor-usage/backfill")
def cursor_usage_backfill(hours_back: int = 48) -> dict[str, Any]:
    with db() as conn:
        return backfill_costs_from_admin_api(conn, hours_back=min(max(hours_back, 1), 168))
