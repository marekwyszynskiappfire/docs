"""Load Studio .env files and optional production credential overlay."""

from __future__ import annotations

import os
from pathlib import Path

from studio_paths import STUDIO_ROOT


def load_env_file(
    path: Path, *, keys_only: set[str] | None = None, override: bool = False
) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if not key:
            continue
        if keys_only is not None and key not in keys_only:
            continue
        if override or key not in os.environ:
            os.environ[key] = val


def load_dotenv() -> None:
    load_env_file(STUDIO_ROOT / ".env")


def apply_importer_credential_profile(jira_instance_id: str) -> None:
    """Overlay Xray (and site URL) from .env.production when targeting prod."""
    if jira_instance_id != "appfire-production":
        return
    prod_keys = {
        "XRAY_CLIENT_ID",
        "XRAY_CLIENT_SECRET",
        "JIRA_BASE_URL",
        "XRAY_INSECURE_SSL",
    }
    load_env_file(STUDIO_ROOT / ".env.production", keys_only=prod_keys, override=True)
