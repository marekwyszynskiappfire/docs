"""Trinity distribution version (single source: Trinity/VERSION)."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

_TRINITY_ROOT = Path(__file__).resolve().parents[2]
_VERSION_FILE = _TRINITY_ROOT / "VERSION"


@lru_cache(maxsize=1)
def trinity_release_version() -> str:
    override = os.environ.get("TRINITY_VERSION", "").strip()
    if override:
        return override
    if _VERSION_FILE.is_file():
        line = _VERSION_FILE.read_text(encoding="utf-8").strip().splitlines()[0].strip()
        if line:
            return line
    return "0.0.0-dev"


def trinity_git_revision() -> str | None:
    rev = os.environ.get("TRINITY_GIT_REVISION", "").strip()
    return rev or None
