"""Cursor MCP instructions + optional Jira REST resolve for portfolio scope."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent.parent.parent / "reviewer" / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from scope_utils import filter_id_from_url  # noqa: E402


def jira_env_configured() -> bool:
    return all(
        os.environ.get(k, "").strip()
        for k in ("JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN")
    )


def effective_jql_from_config(config: dict[str, Any]) -> tuple[str | None, str | None]:
    scope = config.get("scope") or {}
    kind = scope.get("kind")
    value = (scope.get("value") or "").strip()
    if not value:
        return None, "Scope value is empty"
    if kind == "jql":
        return value, None
    if kind == "filter_url":
        fid = filter_id_from_url(value)
        if not fid:
            return None, "Could not parse filter id from URL"
        return None, f"filter_id:{fid}"
    return None, f"Scope kind {kind} does not use JQL resolve"


def append_epic_issuetype(jql: str) -> str:
    if re.search(r"\bissuetype\b", jql, re.I):
        return jql
    return f"{jql} AND issuetype = Epic"


def build_cursor_resolve_prompt(config: dict[str, Any]) -> str:
    scope = config.get("scope") or {}
    kind = scope.get("kind")
    value = (scope.get("value") or "").strip()
    portfolio_id = config.get("portfolio_id") or ""
    jql, note = effective_jql_from_config(config)

    lines = [
        "## Resolve epic keys in Cursor (Atlassian MCP)",
        "",
        f"Portfolio: `{portfolio_id}`",
        "",
        "1. Open this repo in **Cursor** with **Atlassian MCP** connected.",
        "2. Resolve scope to a JQL that returns **Epic** issues only.",
    ]

    if kind == "filter_url" and note and note.startswith("filter_id:"):
        fid = note.split(":", 1)[1]
        lines += [
            "",
            f"**Filter URL** — fetch filter **{fid}** (MCP or `GET /rest/api/3/filter/{fid}`) and read its **JQL**.",
            f"Filter link from config: `{value}`",
        ]
        jql_placeholder = append_epic_issuetype("(paste filter JQL after fetch)")
    elif jql:
        jql_placeholder = append_epic_issuetype(jql)
    else:
        jql_placeholder = append_epic_issuetype("(JQL from scope)")

    lines += [
        "",
        "3. Run **searchJiraIssuesUsingJql** with:",
        "",
        "```",
        jql_placeholder,
        "```",
        "",
        "4. **Paginate** until `isLast` / all pages fetched. Collect **Epic** keys only.",
        "5. If more than **100** epics, narrow JQL; Studio stores at most **200** keys.",
        "",
        "6. **Trinity Studio → Reviewer configs → Resolved epic keys** → paste → **Save pasted keys**.",
        "",
        f"Keep `scope.value` in config as **source_jql** for Creator handoff.",
        "",
        "---",
        "Optional: `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` in `Trinity/studio/.env` → **Resolve from scope** uses server REST.",
    ]
    return "\n".join(lines)


def try_jira_rest_resolve(config: dict[str, Any]) -> tuple[list[str], str | None]:
    from jira_resolve import resolve_epic_keys_from_config

    return resolve_epic_keys_from_config(config)
