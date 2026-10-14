#!/usr/bin/env python3
"""Push maintained Trinity wiki pages from git markdown to Confluence (QACoE).

Uses Atlassian site API token:

  export ATLASSIAN_EMAIL='you@appfire.com'
  export ATLASSIAN_API_TOKEN='...'

  python3 Trinity/scripts/sync_confluence_from_git.py [--dry-run] [--page TITLE]

Page list: Trinity/confluence/page-map.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
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


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_page_map() -> dict:
    path = repo_root() / "Trinity/confluence/page-map.json"
    return json.loads(path.read_text(encoding="utf-8"))


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
    escaped = (
        markdown.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return f"<pre>{escaped}</pre>"


def rewrite_links_for_wiki(markdown: str, pages: list[dict]) -> str:
    """Turn relative .md links into Confluence URLs where we have a mapped page."""
    by_name: dict[str, str] = {}
    for p in pages:
        name = Path(p["git_path"]).name
        by_name[name] = p["web_url"]
        # Trinity/foo.md style
        rel = p["git_path"].replace("Trinity/", "")
        by_name[rel] = p["web_url"]

    def repl(match: re.Match[str]) -> str:
        text, target = match.group(1), match.group(2)
        if target.startswith("http") or target.startswith("#"):
            return match.group(0)
        clean = target.split("#")[0]
        anchor = ""
        if "#" in target:
            anchor = "#" + target.split("#", 1)[1]
        url = by_name.get(Path(clean).name) or by_name.get(clean)
        if url:
            return f"[{text}]({url}{anchor})"
        return match.group(0)

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", repl, markdown)


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
    parser.add_argument("--page", help="Sync only page title substring match")
    args = parser.parse_args()
    root = repo_root()
    page_map = load_page_map()
    pages = page_map["pages"]

    for entry in pages:
        title = entry["title"]
        if args.page and args.page.lower() not in title.lower():
            continue
        rel_path = entry["git_path"]
        page_id = entry["content_id"]
        md_path = root / rel_path
        if not md_path.is_file():
            print(f"Missing {md_path}", file=sys.stderr)
            sys.exit(1)
        raw = md_path.read_text(encoding="utf-8")
        wiki_md = rewrite_links_for_wiki(raw, pages)
        update_page(page_id, title, wiki_md, args.dry_run)


if __name__ == "__main__":
    main()
