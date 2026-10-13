"""Minimal Jira REST client for Studio (issue comments)."""

from __future__ import annotations

import os
import re
from typing import Any

import httpx

from jira_wiki_adf import wiki_to_adf_document

SENSITIVE_PATTERNS = [
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),
    re.compile(r"xox[baprs]-[a-zA-Z0-9-]{10,}"),
    re.compile(r"(?i)api[_-]?key\s*[:=]\s*\S+"),
    re.compile(r"(?i)bearer\s+[a-zA-Z0-9._-]{20,}"),
]


def jira_configured() -> dict[str, Any]:
    base = os.environ.get("JIRA_BASE_URL", "").strip().rstrip("/")
    email = os.environ.get("JIRA_EMAIL", "").strip()
    token = os.environ.get("JIRA_API_TOKEN", "").strip()
    return {
        "configured": bool(base and email and token),
        "jira_base_url_set": bool(base),
        "jira_email_set": bool(email),
        "jira_token_set": bool(token),
        "jira_base_url_host": base.replace("https://", "").split("/")[0] if base else None,
    }


def scan_redaction_warnings(text: str) -> list[str]:
    warnings: list[str] = []
    for pat in SENSITIVE_PATTERNS:
        if pat.search(text):
            warnings.append(f"Possible secret pattern matched: {pat.pattern[:40]}…")
    return warnings


def post_issue_comment(
    issue_key: str,
    wiki_body: str,
    *,
    http_client: httpx.Client | None = None,
) -> dict[str, Any]:
    cfg = jira_configured()
    if not cfg["configured"]:
        raise RuntimeError("JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN are required")
    base = os.environ.get("JIRA_BASE_URL", "").strip().rstrip("/")
    email = os.environ.get("JIRA_EMAIL", "").strip()
    token = os.environ.get("JIRA_API_TOKEN", "").strip()
    url = f"{base}/rest/api/3/issue/{issue_key}/comment"
    payload = {"body": wiki_to_adf_document(wiki_body)}
    owns_client = http_client is None
    client = http_client or httpx.Client(timeout=60.0)
    try:
        resp = client.post(
            url,
            json=payload,
            auth=(email, token),
            headers={"Accept": "application/json"},
        )
    finally:
        if owns_client:
            client.close()
    if resp.status_code >= 400:
        detail = resp.text[:500]
        raise RuntimeError(f"Jira comment failed HTTP {resp.status_code}: {detail}")
    data = resp.json()
    return {
        "id": str(data.get("id", "")),
        "self": data.get("self"),
        "issue_key": issue_key,
    }
