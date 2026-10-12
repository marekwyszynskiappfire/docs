"""Register modular API routers on the FastAPI app."""

from __future__ import annotations

from fastapi import FastAPI

from routers import cursor_usage, reviewer_insights, telemetry


def register_routers(app: FastAPI) -> None:
    for module in (reviewer_insights, cursor_usage, telemetry):
        app.include_router(module.router)
