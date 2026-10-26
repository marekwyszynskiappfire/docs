"""One-click local Cursor SDK agent endpoints."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from cursor_agent_runner import (
    cancel_agent_run,
    get_agent_run,
    launch_agent,
    list_agent_runs,
    sdk_status,
)
from cursor_handoff import public_handoff
from db import db
from reviewer_agent_prompt import build_reviewer_agent_prompt
from run_config import read_run_config

router = APIRouter(tags=["cursor-agents"])


class LaunchReviewerBody(BaseModel):
    portfolio_id: str
    pipeline_run_id: str | None = None


class LaunchHandoffBody(BaseModel):
    pipeline_run_id: str
    handoff_id: str


@router.get("/api/cursor-agents/status")
def cursor_agents_status() -> dict[str, Any]:
    return sdk_status()


@router.get("/api/cursor-agent-runs")
def cursor_agent_runs(
    pipeline_run_id: str | None = None,
    stage: str | None = None,
    handoff_id: str | None = None,
    portfolio_id: str | None = None,
    creator_run_id: str | None = None,
    active_only: bool = False,
) -> list[dict[str, Any]]:
    return list_agent_runs(
        pipeline_run_id,
        stage=stage,
        handoff_id=handoff_id,
        portfolio_id=portfolio_id,
        creator_run_id=creator_run_id,
        active_only=active_only,
    )


@router.get("/api/cursor-agent-runs/{run_id}")
def cursor_agent_run(run_id: str) -> dict[str, Any]:
    try:
        return get_agent_run(run_id)
    except KeyError:
        raise HTTPException(404, "Cursor agent run not found") from None


@router.post("/api/cursor-agent-runs/{run_id}/cancel")
def cursor_agent_cancel(run_id: str) -> dict[str, Any]:
    try:
        return cancel_agent_run(run_id)
    except KeyError:
        raise HTTPException(404, "Cursor agent run not found") from None


@router.post("/api/cursor-agents/reviewer")
def launch_reviewer(body: LaunchReviewerBody) -> dict[str, Any]:
    try:
        config = read_run_config(body.portfolio_id)
    except FileNotFoundError:
        raise HTTPException(404, "Reviewer portfolio config not found") from None
    epic_keys: list[str] = []
    if body.pipeline_run_id:
        with db() as conn:
            run = conn.execute(
                "SELECT id FROM pipeline_run WHERE id = ?", (body.pipeline_run_id,)
            ).fetchone()
            if run is None:
                raise HTTPException(404, "Pipeline run not found")
            epic_keys = [
                row["jira_key"]
                for row in conn.execute(
                    "SELECT jira_key FROM review_unit WHERE pipeline_run_id = ? ORDER BY jira_key",
                    (body.pipeline_run_id,),
                ).fetchall()
            ]
    prompt = build_reviewer_agent_prompt(
        config,
        pipeline_run_id=body.pipeline_run_id,
        epic_keys=epic_keys,
    )
    try:
        return launch_agent(
            stage="reviewer",
            prompt_text=prompt,
            pipeline_run_id=body.pipeline_run_id,
            portfolio_id=body.portfolio_id,
        )
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(503, str(exc)) from exc


@router.post("/api/cursor-agents/handoff")
def launch_handoff(body: LaunchHandoffBody) -> dict[str, Any]:
    with db() as conn:
        row = conn.execute(
            """
            SELECT * FROM cursor_handoff
            WHERE id = ? AND pipeline_run_id = ?
            """,
            (body.handoff_id, body.pipeline_run_id),
        ).fetchone()
    if row is None:
        raise HTTPException(404, "Cursor handoff not found")
    handoff = public_handoff(row)
    stage: Literal["reviewer", "creator"] = (
        "creator" if handoff["stage"] == "creator_draft" else "reviewer"
    )
    try:
        return launch_agent(
            stage=stage,
            prompt_text=handoff["prompt_text"],
            pipeline_run_id=body.pipeline_run_id,
            creator_run_id=handoff["epic_key"] if stage == "creator" else None,
            handoff_id=body.handoff_id,
            epic_key=handoff["epic_key"] or None,
        )
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(503, str(exc)) from exc
