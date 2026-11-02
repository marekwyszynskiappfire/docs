"""Usage Scorecard Google Sheet integration."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from db import db, utc_now
from run_report import persist_pipeline_run_report
from scorecard_config import SCORECARD_SPREADSHEET_URL
from scorecard_row import build_scorecard_row
from scorecard_sheets import is_configured, next_run_id, public_config, push_row

router = APIRouter(tags=["scorecard"])


@router.get("/api/scorecard/config")
def scorecard_config() -> dict[str, Any]:
    """Baked spreadsheet URL and whether Sheets credentials are present."""
    return public_config()


@router.get("/api/runs/{run_id}/scorecard/preview")
def scorecard_preview(run_id: str) -> dict[str, Any]:
    with db() as conn:
        run = conn.execute(
            "SELECT id, scorecard_external_run_id FROM pipeline_run WHERE id = ?",
            (run_id,),
        ).fetchone()
        if not run:
            raise HTTPException(404, "Run not found")
        report = persist_pipeline_run_report(conn, run_id)
        external = run["scorecard_external_run_id"]
        built = build_scorecard_row(
            conn,
            pipeline_run_id=run_id,
            report=report,
            external_run_id=external or None,
        )
        if not external:
            built["proposed_run_id"] = next_run_id(built["tab"], built["run_prefix"]) if is_configured() else None
            preview_values = list(built["values"])
            if built["proposed_run_id"]:
                preview_values[0] = built["proposed_run_id"]
            built["preview_values"] = preview_values
        else:
            built["proposed_run_id"] = external
            built["preview_values"] = built["values"]
    return {
        "spreadsheet_url": SCORECARD_SPREADSHEET_URL,
        "configured": is_configured(),
        **built,
    }


@router.post("/api/runs/{run_id}/scorecard/push")
def scorecard_push(run_id: str) -> dict[str, Any]:
    if not is_configured():
        raise HTTPException(
            503,
            "Scorecard credentials not configured (TRINITY_SCORECARD_CREDENTIALS or "
            "GOOGLE_APPLICATION_CREDENTIALS).",
        )
    with db() as conn:
        run = conn.execute(
            "SELECT id, scorecard_external_run_id FROM pipeline_run WHERE id = ?",
            (run_id,),
        ).fetchone()
        if not run:
            raise HTTPException(404, "Run not found")
        report = persist_pipeline_run_report(conn, run_id)
        external = (run["scorecard_external_run_id"] or "").strip() or None
        built = build_scorecard_row(
            conn,
            pipeline_run_id=run_id,
            report=report,
            external_run_id=external,
        )
        values = list(built["values"])
        if not external:
            external = next_run_id(built["tab"], built["run_prefix"])
            values[0] = external
        else:
            values[0] = external

        try:
            result = push_row(built["tab"], values, existing_run_id=external)
        except Exception as exc:
            raise HTTPException(502, f"Google Sheets API failed: {exc}") from exc

        pushed_at = utc_now()
        conn.execute(
            """
            UPDATE pipeline_run
            SET scorecard_external_run_id = ?, scorecard_pushed_at = ?, updated_at = ?
            WHERE id = ?
            """,
            (external, pushed_at, pushed_at, run_id),
        )

    return {
        "pipeline_run_id": run_id,
        "spreadsheet_url": SCORECARD_SPREADSHEET_URL,
        "tab": built["tab"],
        "external_run_id": external,
        "row_number": result["row_number"],
        "action": result["action"],
        "pushed_at": pushed_at,
        "fields": built["fields"],
    }
