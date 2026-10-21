"""Register modular API routers on the FastAPI app."""

from __future__ import annotations

from fastapi import FastAPI

from routers import (
    creator,
    cursor_agents,
    cursor_usage,
    importer,
    jira_epic_comments,
    personas_config,
    review_runs,
    reviewer_insights,
    stats,
    telemetry,
    workspace,
)


def register_routers(app: FastAPI) -> None:
    for module in (
        review_runs,
        stats,
        creator,
        importer,
        reviewer_insights,
        cursor_agents,
        cursor_usage,
        telemetry,
        jira_epic_comments,
        personas_config,
        workspace,
    ):
        app.include_router(module.router)
