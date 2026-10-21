"""Workspace summary, Creator handoffs, and output checks."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from cursor_handoff import (
    check_handoff,
    ingest_creator_output,
    mark_copied,
    prepare_creator_handoff,
    set_epic_coverage,
    set_portfolio_coverage,
)
from db import db
from workspace_summary import portfolio_guidance, workspace_summary

router = APIRouter(tags=["workspace"])


class CheckHandoffBody(BaseModel):
    accept_changes: bool = False


class CoverageProfileBody(BaseModel):
    profile: str


class EpicCoverageBody(BaseModel):
    profile: str | None = None


def _handoff_row(conn: Any, run_id: str, handoff_id: str) -> Any:
    row = conn.execute(
        "SELECT id, stage FROM cursor_handoff WHERE id = ? AND pipeline_run_id = ?",
        (handoff_id, run_id),
    ).fetchone()
    if row is None:
        raise HTTPException(404, "Handoff not found")
    return row


@router.get("/api/workspace/{run_id}")
def api_workspace(run_id: str) -> dict[str, Any]:
    with db() as conn:
        try:
            return workspace_summary(conn, run_id)
        except KeyError:
            raise HTTPException(404, "Run not found") from None


@router.put("/api/workspace/{run_id}/coverage-profile")
def api_set_coverage_profile(run_id: str, body: CoverageProfileBody) -> dict[str, Any]:
    with db() as conn:
        try:
            return set_portfolio_coverage(conn, run_id, body.profile)
        except KeyError:
            raise HTTPException(404, "Run not found") from None
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc


@router.put("/api/workspace/{run_id}/units/{unit_id}/coverage-profile")
def api_set_epic_coverage(run_id: str, unit_id: str, body: EpicCoverageBody) -> dict[str, Any]:
    with db() as conn:
        try:
            return set_epic_coverage(conn, run_id, unit_id, body.profile or None)
        except KeyError:
            raise HTTPException(404, "Epic not found in this workspace") from None
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc


@router.post("/api/workspace/{run_id}/units/{unit_id}/prepare-creator")
def api_prepare_creator(run_id: str, unit_id: str) -> dict[str, Any]:
    with db() as conn:
        unit = conn.execute(
            "SELECT id FROM review_unit WHERE id = ? AND pipeline_run_id = ?",
            (unit_id, run_id),
        ).fetchone()
        if unit is None:
            raise HTTPException(404, "Epic not found in this workspace")
        try:
            return prepare_creator_handoff(conn, unit_id)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc


@router.post("/api/workspace/{run_id}/prepare-creator-batch")
def api_prepare_creator_batch(run_id: str) -> dict[str, Any]:
    """Prepare a Creator prompt for every approved Epic that does not have one yet."""
    with db() as conn:
        try:
            epics, _action = portfolio_guidance(conn, run_id)
        except KeyError:
            raise HTTPException(404, "Run not found") from None
        eligible = [
            epic for epic in epics if epic["stage"] == "draft" and not epic["creator_handoff"]
        ]
        prepared = []
        for epic in eligible:
            handoff = prepare_creator_handoff(conn, epic["unit_id"])
            prepared.append({"id": handoff["id"], "epic_key": epic["jira_key"]})
        return {"prepared": prepared}


@router.post("/api/workspace/{run_id}/handoffs/{handoff_id}/check")
def api_check_handoff(
    run_id: str, handoff_id: str, body: CheckHandoffBody | None = None
) -> dict[str, Any]:
    accept = bool(body and body.accept_changes)
    with db() as conn:
        row = _handoff_row(conn, run_id, handoff_id)
        if row["stage"] == "creator_draft":
            return ingest_creator_output(conn, handoff_id, accept_changes=accept)
        return check_handoff(conn, handoff_id)


@router.post("/api/workspace/{run_id}/handoffs/{handoff_id}/copied")
def api_mark_handoff_copied(run_id: str, handoff_id: str) -> dict[str, Any]:
    with db() as conn:
        _handoff_row(conn, run_id, handoff_id)
        return mark_copied(conn, handoff_id)
