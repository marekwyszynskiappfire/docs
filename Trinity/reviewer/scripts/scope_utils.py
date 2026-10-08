"""Resolve epic keys from portfolio run-config scope (no live Jira in v1 Studio)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

EPIC_KEY_RE = re.compile(r"^[A-Z][A-Z0-9]+-\d+$")
BROWSE_RE = re.compile(r"/browse/([A-Z][A-Z0-9]+-\d+)", re.I)
FILTER_ID_RE = re.compile(r"(?:filter=|/filter/)(\d+)", re.I)
KEY_TOKEN_RE = re.compile(r"\b([A-Z][A-Z0-9]+-\d+)\b")

MAX_RESOLVED_KEYS = 200
WARN_RESOLVED_KEYS = 100


def filter_id_from_url(url: str) -> str | None:
    m = FILTER_ID_RE.search(url)
    return m.group(1) if m else None


def parse_pasted_keys(text: str) -> tuple[list[str], str | None]:
    """Parse epic keys from pasted text (CSV, lines, Jira export, browse URLs)."""
    seen: set[str] = set()
    keys: list[str] = []
    for line in text.replace(",", "\n").split("\n"):
        for m in KEY_TOKEN_RE.finditer(line.upper()):
            k = m.group(1)
            if k not in seen:
                seen.add(k)
                keys.append(k)
    if not keys:
        return [], "No epic keys found in pasted text"
    note = None
    if len(keys) > MAX_RESOLVED_KEYS:
        keys = keys[:MAX_RESOLVED_KEYS]
        note = f"Truncated to {MAX_RESOLVED_KEYS} keys"
    elif len(keys) > WARN_RESOLVED_KEYS:
        note = f"{len(keys)} epics in scope (>{WARN_RESOLVED_KEYS}); consider narrowing JQL"
    return keys, note


def epic_keys_from_scope(scope: dict[str, Any]) -> tuple[list[str], str | None]:
    kind = scope.get("kind") or ""
    value = (scope.get("value") or "").strip()
    if not value:
        return [], "Scope value is empty"

    if kind == "epic_keys":
        keys = []
        for part in value.replace("\n", ",").split(","):
            k = part.strip().upper()
            if k:
                if not EPIC_KEY_RE.match(k):
                    return [], f"Invalid epic key: {k}"
                keys.append(k)
        return keys, None

    if kind == "epic_url":
        m = BROWSE_RE.search(value)
        if m:
            return [m.group(1).upper()], None
        if EPIC_KEY_RE.match(value.upper()):
            return [value.upper()], None
        return [], "Could not parse epic key from epic_url"

    return (
        [],
        f"Scope kind '{kind}' needs resolved_epic_keys (resolve in Cursor, paste in Studio)",
    )


def epic_keys_for_config(config: dict[str, Any]) -> tuple[list[str], str | None]:
    resolved = config.get("resolved_epic_keys") or []
    if resolved:
        keys = [str(k).upper() for k in resolved if EPIC_KEY_RE.match(str(k).upper())]
        if keys:
            return keys, None
    return epic_keys_from_scope(config.get("scope") or {})


def new_epics_for_config(config: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    keys, note = epic_keys_for_config(config)
    portfolio_id = config.get("portfolio_id") or ""
    artifacts = config.get("artifacts_dir") or "Trinity/reviewer/runs"
    base = repo_root / artifacts / portfolio_id

    already: list[str] = []
    new: list[str] = []
    for k in keys:
        payload = base / k / "review-payload.json"
        if payload.is_file():
            already.append(k)
        else:
            new.append(k)

    rel_folder = f"{artifacts}/{portfolio_id}"
    scope = config.get("scope") or {}
    return {
        "portfolio_id": portfolio_id,
        "run_folder": rel_folder,
        "epics_in_scope": keys,
        "already_scanned": already,
        "new_epics": new,
        "scope_resolution_note": note,
        "resolved_at": config.get("resolved_at"),
        "resolved_source": config.get("resolved_source"),
        "scope_kind": scope.get("kind"),
        "error": note if note and not keys else None,
    }


def resolve_scope_inline(config: dict[str, Any]) -> tuple[list[str], str | None]:
    """Resolve without Jira — only epic_keys / epic_url scope kinds."""
    scope = config.get("scope") or {}
    kind = scope.get("kind")
    if kind in ("epic_keys", "epic_url"):
        return epic_keys_from_scope(scope)
    value = (scope.get("value") or "").strip()
    if kind == "jql":
        return (
            [],
            "Run this JQL in Cursor (Atlassian MCP), epics only, then paste keys in Studio. "
            "Keep scope.value as source_jql for Creator handoff.",
        )
    if kind == "filter_url":
        fid = filter_id_from_url(value)
        extra = f" Filter id {fid}." if fid else ""
        return (
            [],
            "Open filter in Jira or fetch filter JQL via MCP in Cursor, run search (Epic only), "
            f"then paste epic keys in Studio.{extra}",
        )
    return [], f"Unsupported scope kind: {kind}"
