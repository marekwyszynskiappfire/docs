"""QA Studio API."""

from __future__ import annotations

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Allow running as `python app.py` from server/
sys.path.insert(0, str(Path(__file__).resolve().parent))

from db import init_db
from routers import register_routers
from studio_env import load_dotenv
from studio_paths import STATIC_FALLBACK, WEB_DIST
from trinity_release import trinity_git_revision, trinity_release_version


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    load_dotenv()
    init_db()
    yield


app = FastAPI(title="Trinity Studio", version=trinity_release_version(), lifespan=_lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_routers(app)


@app.get("/api/health")
def health() -> dict[str, Any]:
    version = trinity_release_version()
    body: dict[str, Any] = {
        "status": "ok",
        "trinity_version": version,
        "studio_version": version,
        "features": [
            "importer_plan",
            "importer_execute",
            "creator_coverage",
            "creator_golden",
            "creator_suite_report",
            "portfolio_rollup",
            "cursor_cost",
            "reviewer_html_reports",
            "context_loaded_alerts",
            "jira_epic_comments",
            "pipeline_run_statistics",
        ],
    }
    rev = trinity_git_revision()
    if rev:
        body["git_revision"] = rev
    return body


def _ui_index() -> FileResponse:
    return FileResponse(
        STATIC_FALLBACK / "index.html",
        headers={"Cache-Control": "no-cache"},
    )


@app.get("/")
def root_ui():
    """Prefer built React app when web/dist exists; legacy static fallback is deprecated."""
    force_legacy = os.environ.get("QA_STUDIO_LEGACY_STATIC", "").lower() in ("1", "true", "yes")
    use_react = (
        not force_legacy
        and WEB_DIST.is_dir()
        and (WEB_DIST / "index.html").is_file()
    ) or os.environ.get("QA_STUDIO_REACT", "").lower() in ("1", "true", "yes")
    if use_react:
        return FileResponse(WEB_DIST / "index.html")
    return _ui_index()


@app.get("/static/{filename}")
def static_asset(filename: str):
    if "/" in filename or filename.startswith("."):
        raise HTTPException(status_code=404, detail="Not found")
    path = STATIC_FALLBACK / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(path)


if WEB_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=WEB_DIST / "assets"), name="assets")

    @app.get("/{spa_path:path}")
    def spa_ui(spa_path: str):
        """React Router paths (e.g. /statistics, /runs/…) when UI is served from :8765."""
        if spa_path == "api" or spa_path.startswith("api/") or spa_path.startswith("assets/"):
            raise HTTPException(status_code=404, detail="Not found")
        force_legacy = os.environ.get("QA_STUDIO_LEGACY_STATIC", "").lower() in (
            "1",
            "true",
            "yes",
        )
        if force_legacy:
            raise HTTPException(status_code=404, detail="Not found")
        if (WEB_DIST / "index.html").is_file():
            return FileResponse(WEB_DIST / "index.html", headers={"Cache-Control": "no-cache"})
        raise HTTPException(status_code=404, detail="Not found")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("QA_STUDIO_PORT", "8765"))
    uvicorn.run("app:app", host="127.0.0.1", port=port, reload=False)
