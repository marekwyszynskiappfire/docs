"""Load Reviewer Jira wiki renderers (render_report.py)."""

from __future__ import annotations

import sys
from pathlib import Path

_REVIEWER_SCRIPTS = Path(__file__).resolve().parent.parent.parent / "reviewer" / "scripts"
if str(_REVIEWER_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_REVIEWER_SCRIPTS))

from render_report import render_jira_full, render_jira_short  # noqa: E402

__all__ = ["render_jira_full", "render_jira_short"]
