"""Portfolio rollup, context_loaded alerts, HTML review reports, child inventory."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from context_loaded_alerts import build_context_loaded_alerts
from db import db
from epic_child_inventory import build_run_child_inventory
from portfolio_rollup import build_portfolio_rollup
from reviewer_reports import (
    epic_report_for_unit,
    list_run_review_reports,
    portfolio_report_for_run,
)

router = APIRouter(tags=["reviewer-insights"])


@router.get("/api/context-loaded-alerts")
def api_context_loaded_alerts(limit: int = 50) -> dict[str, Any]:
    cap = min(max(limit, 1), 200)
    with db() as conn:
        return build_context_loaded_alerts(conn, limit=cap)


@router.get("/api/portfolio-rollup")
def api_portfolio_rollup() -> dict[str, Any]:
    with db() as conn:
        return build_portfolio_rollup(conn)


@router.get("/api/runs/{run_id}/review-reports")
def api_run_review_reports(run_id: str) -> dict[str, Any]:
    with db() as conn:
        try:
            return list_run_review_reports(conn, run_id)
        except KeyError:
            raise HTTPException(404, "Run not found") from None


@router.get("/api/runs/{run_id}/portfolio-report.html")
def api_portfolio_report_html(run_id: str) -> FileResponse:
    with db() as conn:
        try:
            path = portfolio_report_for_run(conn, run_id)
        except KeyError:
            raise HTTPException(404, "Run not found") from None
        except FileNotFoundError as exc:
            raise HTTPException(404, str(exc)) from exc
    return FileResponse(path, media_type="text/html")


@router.get("/api/units/{unit_id}/review-report.html")
def api_unit_review_report_html(unit_id: str) -> FileResponse:
    with db() as conn:
        try:
            path = epic_report_for_unit(conn, unit_id)
        except KeyError:
            raise HTTPException(404, "Unit not found") from None
        except FileNotFoundError as exc:
            raise HTTPException(404, str(exc)) from exc
    return FileResponse(path, media_type="text/html")


@router.get("/api/runs/{run_id}/child-inventory")
def api_run_child_inventory(run_id: str) -> dict[str, Any]:
    with db() as conn:
        run = conn.execute("SELECT id FROM pipeline_run WHERE id = ?", (run_id,)).fetchone()
        if not run:
            raise HTTPException(404, "Run not found")
        return build_run_child_inventory(conn, run_id)
