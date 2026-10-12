"""Filesystem paths for Trinity Studio data and UI assets."""

from __future__ import annotations

from pathlib import Path

SERVER_DIR = Path(__file__).resolve().parent
STUDIO_ROOT = SERVER_DIR.parent
STUDIO_DATA = STUDIO_ROOT / "data"
EXPORT_ROOT = STUDIO_DATA / "exports"
STATIC_FALLBACK = SERVER_DIR / "static"
WEB_DIST = STUDIO_ROOT / "web" / "dist"
DOCS_REPO_ROOT = STUDIO_ROOT.parent.parent
