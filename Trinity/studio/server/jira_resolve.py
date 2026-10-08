"""Optional Jira REST epic resolution (server-side only)."""

from __future__ import annotations

import os
from typing import Any
import httpx

from jira_resolve_prompt import append_epic_issuetype, filter_id_from_url

MAX_KEYS = 200
WARN_KEYS = 100


def _client() -> tuple[str, httpx.BasicAuth, dict[str, str]]:
    base = os.environ["JIRA_BASE_URL"].rstrip("/")
    auth = httpx.BasicAuth(os.environ["JIRA_EMAIL"], os.environ["JIRA_API_TOKEN"])
    headers = {"Accept": "application/json"}
    return base, auth, headers


def _get_filter_jql(base: str, auth: httpx.BasicAuth, headers: dict[str, str], filter_id: str) -> str:
    url = f"{base}/rest/api/3/filter/{filter_id}"
    with httpx.Client(timeout=60.0) as client:
        r = client.get(url, auth=auth, headers=headers)
        if r.status_code >= 400:
            raise ValueError(f"Jira filter fetch failed ({r.status_code})")
        data = r.json()
    jql = data.get("jql") or data.get("query")
    if not jql:
        raise ValueError(f"Filter {filter_id} returned no JQL")
    return jql


def _search_epic_keys(base: str, auth: httpx.BasicAuth, headers: dict[str, str], jql: str) -> tuple[list[str], str | None]:
    jql = append_epic_issuetype(jql)
    keys: list[str] = []
    start_at = 0
    max_results = 50
    warning = None
    url = f"{base}/rest/api/3/search"

    with httpx.Client(timeout=120.0) as client:
        while True:
            params = {
                "jql": jql,
                "startAt": start_at,
                "maxResults": max_results,
                "fields": "key,issuetype",
            }
            r = client.get(url, auth=auth, headers=headers, params=params)
            if r.status_code >= 400:
                raise ValueError(f"Jira search failed ({r.status_code})")
            data = r.json()
            issues = data.get("issues") or []
            for issue in issues:
                key = issue.get("key")
                if key:
                    keys.append(key)
                if len(keys) >= MAX_KEYS:
                    return keys, f"Truncated to {MAX_KEYS} keys"
            total = data.get("total", 0)
            start_at += len(issues)
            if start_at >= total or not issues:
                break

    if len(keys) > WARN_KEYS:
        warning = f"{len(keys)} epics resolved (>{WARN_KEYS}); consider narrowing JQL"
    return keys, warning


def resolve_epic_keys_from_config(config: dict[str, Any]) -> tuple[list[str], str | None]:
    base, auth, headers = _client()
    scope = config.get("scope") or {}
    kind = scope.get("kind")
    value = (scope.get("value") or "").strip()

    if kind == "jql":
        jql = value
    elif kind == "filter_url":
        fid = filter_id_from_url(value)
        if not fid:
            raise ValueError("Could not parse filter id from URL")
        jql = _get_filter_jql(base, auth, headers, fid)
    else:
        raise ValueError(f"Jira REST resolve does not support scope kind {kind}")

    return _search_epic_keys(base, auth, headers, jql)
