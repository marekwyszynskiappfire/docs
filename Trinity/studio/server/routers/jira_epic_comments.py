"""Jira epic comment preview and post."""

from __future__ import annotations

import json
import os
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from db import db
from jira_client import jira_configured
from jira_epic_comment import comment_history, post_comment, preview_comment
from telemetry import record_event

router = APIRouter(tags=["jira-epic-comments"])


class JiraCommentPostBody(BaseModel):
    variant: str = Field(default="auto")
    confirm_issue_key: str = Field(..., min_length=1)
    body: str | None = None
    preview_edited: bool = False
    production_confirm: str | None = None
    allow_duplicate: bool = False


def _load_unit_payload(conn: Any, unit_id: str) -> tuple[dict[str, Any], str, int | None]:
    unit = conn.execute("SELECT * FROM review_unit WHERE id = ?", (unit_id,)).fetchone()
    if not unit:
        raise HTTPException(404, "Unit not found")
    row = conn.execute(
        """
        SELECT revision, payload_json FROM review_payload_revision
        WHERE review_unit_id = ? ORDER BY revision DESC LIMIT 1
        """,
        (unit_id,),
    ).fetchone()
    if not row:
        raise HTTPException(404, "No payload for unit")
    payload = json.loads(row["payload_json"])
    return payload, unit["jira_key"], int(row["revision"])


def _assert_production_jira_confirm(production_confirm: str | None) -> None:
    base = os.environ.get("JIRA_BASE_URL", "").lower()
    if "appfire.atlassian.net" in base and (production_confirm or "").strip() != "PRODUCTION":
        raise HTTPException(
            400,
            "Production Jira host: set production_confirm to PRODUCTION before post",
        )


@router.get("/api/jira/status")
def jira_status() -> dict[str, Any]:
    return jira_configured()


@router.get("/api/units/{unit_id}/jira-comment/preview")
def jira_comment_preview(
    unit_id: str,
    variant: str = "auto",
    preview_edited: bool = False,
) -> dict[str, Any]:
    with db() as conn:
        unit = conn.execute(
            "SELECT pipeline_run_id FROM review_unit WHERE id = ?", (unit_id,)
        ).fetchone()
        payload, jira_key, revision = _load_unit_payload(conn, unit_id)
        out = preview_comment(
            conn, unit_id, payload, jira_key, variant, payload_revision_id=revision
        )
        out["jira_key"] = jira_key
        out["payload_revision_id"] = revision
        record_event(
            conn,
            "jira_comment_preview",
            "review_unit",
            unit_id,
            unit["pipeline_run_id"] if unit else None,
            {
                "variant": out.get("variant"),
                "epic_feedback_count": out.get("epic_feedback_count"),
                "blocker_count": len(out.get("blockers") or []),
                "preview_edited": preview_edited,
                "duplicate_warning": bool(out.get("duplicate_warning")),
            },
        )
        return out


@router.get("/api/units/{unit_id}/jira-comment/history")
def jira_comment_history(unit_id: str, limit: int = 10) -> dict[str, Any]:
    with db() as conn:
        unit = conn.execute("SELECT id FROM review_unit WHERE id = ?", (unit_id,)).fetchone()
        if not unit:
            raise HTTPException(404, "Unit not found")
        return {"posts": comment_history(conn, unit_id, limit=limit)}


@router.post("/api/units/{unit_id}/jira-comment/post")
def jira_comment_post(unit_id: str, body: JiraCommentPostBody) -> dict[str, Any]:
    if not jira_configured().get("configured"):
        raise HTTPException(503, "Jira credentials not configured — copy studio/.env.example")
    with db() as conn:
        payload, jira_key, revision = _load_unit_payload(conn, unit_id)
        if body.confirm_issue_key.strip() != jira_key:
            raise HTTPException(400, f"confirm_issue_key must be {jira_key}")
        _assert_production_jira_confirm(body.production_confirm)
        unit_row = conn.execute(
            "SELECT pipeline_run_id FROM review_unit WHERE id = ?", (unit_id,)
        ).fetchone()
        pipeline_run_id = unit_row["pipeline_run_id"] if unit_row else None
        try:
            result = post_comment(
                conn,
                unit_id=unit_id,
                jira_key=jira_key,
                payload=payload,
                variant=body.variant,
                body_override=body.body,
                preview_edited=body.preview_edited,
                payload_revision_id=revision,
                allow_duplicate=body.allow_duplicate,
            )
        except ValueError as exc:
            record_event(
                conn,
                "jira_comment_post_failure",
                "review_unit",
                unit_id,
                pipeline_run_id,
                {"http_status": 400, "error_class": "validation"},
            )
            raise HTTPException(400, str(exc)) from exc
        except RuntimeError as exc:
            record_event(
                conn,
                "jira_comment_post_failure",
                "review_unit",
                unit_id,
                pipeline_run_id,
                {"http_status": 502, "error_class": "jira_api"},
            )
            raise HTTPException(502, str(exc)) from exc
        record_event(
            conn,
            "jira_comment_post_success",
            "review_unit",
            unit_id,
            pipeline_run_id,
            {
                "variant": result.get("variant"),
                "preview_edited": result.get("preview_edited"),
                "jira_comment_id": result.get("jira_comment_id"),
            },
        )
        return result
