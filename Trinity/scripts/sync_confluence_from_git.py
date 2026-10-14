#!/usr/bin/env python3
"""Push maintained Trinity wiki pages from git markdown to Confluence (QACoE).

Uses Atlassian MCP-compatible credentials (site-wide API token):

  export ATLASSIAN_EMAIL='you@appfire.com'
  export ATLASSIAN_API_TOKEN='...'

Optional: ATLASSIAN_CLOUD_ID (default appfire production).

  python3 Trinity/scripts/sync_confluence_from_git.py [--dry-run]

Parent index page (3750559869) contains Confluence page links — update its
*Last published* / *What changed* section manually or via MCP edits (markdown
full-replace is blocked).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import ssl
import urllib.error
import urllib.request
from pathlib import Path

try:
    import certifi

    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()

BASE = "https://appfire.atlassian.net/wiki"

PAGES: tuple[tuple[str, str, str], ...] = (
    ("3750592672", "Trinity/FIRST-RUN.md", "Trinity — First run playbook"),
    ("3750920216", "Trinity/ARCHITECTURE.md", "Trinity — Architecture"),
    ("3750658179", "Trinity/MANUAL.md", "Trinity — Operator manual"),
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def auth_header() -> str:
    email = os.environ.get("ATLASSIAN_EMAIL") or os.environ.get("JIRA_EMAIL")
    token = os.environ.get("ATLASSIAN_API_TOKEN") or os.environ.get("JIRA_API_TOKEN")
    if not email or not token:
        print(
            "Set ATLASSIAN_EMAIL and ATLASSIAN_API_TOKEN (or JIRA_EMAIL / JIRA_API_TOKEN).",
            file=sys.stderr,
        )
        sys.exit(1)
    import base64

    raw = f"{email}:{token}".encode()
    return "Basic " + base64.b64encode(raw).decode("ascii")


def http_json(method: str, url: str, payload: dict | None = None) -> dict:
    data = None
    headers = {"Accept": "application/json", "Authorization": auth_header()}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120, context=SSL_CONTEXT) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {url} -> {e.code}: {err[:800]}") from e


def get_page(page_id: str) -> dict:
    return http_json("GET", f"{BASE}/api/v2/pages/{page_id}?body-format=storage")


def convert_markdown(markdown: str) -> str:
    try:
        out = http_json(
            "POST",
            f"{BASE}/rest/api/contentbody/convert/to",
            {"value": markdown, "representation": "markdown"},
        )
        if isinstance(out, dict) and out.get("value"):
            return out["value"]
    except RuntimeError:
        pass
    # Fallback: escaped preformatted (operators still have git as source of truth)
    escaped = (
        markdown.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return f"<pre>{escaped}</pre>"


def update_page(page_id: str, title: str, markdown: str, dry_run: bool) -> None:
    current = get_page(page_id)
    version = current["version"]["number"]
    storage = convert_markdown(markdown)
    payload = {
        "id": page_id,
        "status": "current",
        "title": title,
        "body": {"representation": "storage", "value": storage},
        "version": {"number": version + 1, "message": "Sync from git (sync_confluence_from_git.py)"},
    }
    if dry_run:
        print(f"[dry-run] {page_id} {title} v{version + 1} ({len(markdown)} chars markdown)")
        return
    http_json("PUT", f"{BASE}/api/v2/pages/{page_id}", payload)
    print(f"Updated {page_id} ({title}) -> v{version + 1}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = repo_root()
    for page_id, rel_path, title in PAGES:
        md_path = root / rel_path
        if not md_path.is_file():
            print(f"Missing {md_path}", file=sys.stderr)
            sys.exit(1)
        update_page(page_id, title, md_path.read_text(encoding="utf-8"), args.dry_run)


if __name__ == "__main__":
    main()
