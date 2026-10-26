#!/usr/bin/env python3
"""Harvest Jira evidence for full-fidelity Reviewer (REST mirrors MCP Jira reads).

Writes `_gather/epics/{KEY}.json` and initial `{KEY}/review-payload.json`.
Confluence bodies: fetch via Atlassian MCP → `_gather/nested-rescan/mcp/` then ingest-mcp.

Usage:
  JIRA_BASE_URL=https://appfire.atlassian.net python3 full_fidelity_epic_batch.py \\
    --run-dir Trinity/reviewer/runs/bp-q4-26-qa-8bd-testable \\
    --keys ONE-96543,ONE-232656
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

REPO = Path(__file__).resolve().parents[3]
REVIEWER = REPO / "Trinity" / "reviewer"

CONF_RE = re.compile(
    r"https?://[^/\s]+/wiki/[^\s\"')>]+|https?://[^/\s]+/wiki/x/[A-Za-z0-9]+"
)
FIGMA_RE = re.compile(r"https?://(?:www\.)?figma\.com/(?:design|file)/[^\s\"')>]+")
EXTERNAL_RE = [
    (re.compile(r"https?://docs\.google\.com/[^\s\"')>]+"), "google_doc"),
    (re.compile(r"https?://drive\.google\.com/[^\s\"')>]+"), "google_drive"),
    (re.compile(r"[^\s\"')>]+\.pdf(?:\?[^\s\"')>]*)?", re.I), "pdf"),
]


def load_env() -> None:
    env_path = REPO / "Trinity" / "studio" / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


def adf_to_text(node: Any) -> str:
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "".join(adf_to_text(n) for n in node)
    if not isinstance(node, dict):
        return ""
    t = node.get("type")
    if t == "text":
        return node.get("text", "")
    if t == "hardBreak":
        return "\n"
    return adf_to_text(node.get("content"))


def plain_description(fields: dict) -> str:
    desc = fields.get("description")
    if desc is None:
        return ""
    if isinstance(desc, str):
        return desc.strip()
    return adf_to_text(desc).strip()


def extract_urls(text: str) -> list[str]:
    if not text:
        return []
    found = set(CONF_RE.findall(text))
    found.update(FIGMA_RE.findall(text))
    for pat, _ in EXTERNAL_RE:
        found.update(pat.findall(text))
    return sorted(found)


def page_id_from_url(url: str) -> str | None:
    m = re.search(r"/pages/(\d+)|[?&]pageId=(\d+)", url)
    if m:
        return m.group(1) or m.group(2)
    return None


def fetch_issue(client: httpx.Client, base: str, auth: httpx.BasicAuth, key: str) -> dict:
    fields = (
        "summary,status,description,duedate,comment,issuelinks,issuetype,attachment,"
        "customfield_10901,customfield_10548,updated,priority,labels,components"
    )
    r = client.get(f"{base}/rest/api/3/issue/{key}", auth=auth, params={"fields": fields})
    r.raise_for_status()
    return r.json()


def fetch_children(client: httpx.Client, base: str, auth: httpx.BasicAuth, epic_key: str) -> list[dict]:
    jql = f'project = ONE AND (parent = {epic_key} OR "Epic Link" = {epic_key}) ORDER BY rank'
    out: list[dict] = []
    start = 0
    while True:
        r = client.get(
            f"{base}/rest/api/3/search/jql",
            auth=auth,
            params={
                "jql": jql,
                "startAt": start,
                "maxResults": 50,
                "fields": "summary,status,description,issuetype",
            },
        )
        if r.status_code == 410:
            r = client.get(
                f"{base}/rest/api/3/search",
                auth=auth,
                params={
                    "jql": jql,
                    "startAt": start,
                    "maxResults": 50,
                    "fields": "summary,status,description,issuetype",
                },
            )
        r.raise_for_status()
        data = r.json()
        for issue in data.get("issues", []):
            f = issue.get("fields", {})
            desc = plain_description(f)
            out.append(
                {
                    "key": issue["key"],
                    "type": (f.get("issuetype") or {}).get("name", "?"),
                    "status": (f.get("status") or {}).get("name", "?"),
                    "summary": f.get("summary", ""),
                    "description": desc,
                    "description_len": len(desc),
                }
            )
        if data.get("isLast", True) or not data.get("issues"):
            break
        start += len(data["issues"])
    return out


def fetch_remote_links(client: httpx.Client, base: str, auth: httpx.BasicAuth, key: str) -> list[dict]:
    r = client.get(f"{base}/rest/api/3/issue/{key}/remotelink", auth=auth)
    if r.status_code >= 400:
        return []
    links = []
    for item in r.json() or []:
        obj = item.get("object") or {}
        url = obj.get("url") or ""
        if url:
            links.append({"url": url, "title": obj.get("title") or url, "relationship": item.get("relationship")})
    return links


def fetch_comments(client: httpx.Client, base: str, auth: httpx.BasicAuth, key: str) -> dict:
    authors: list[str] = []
    bodies: list[str] = []
    start = 0
    total = 0
    while True:
        r = client.get(
            f"{base}/rest/api/3/issue/{key}/comment",
            auth=auth,
            params={"startAt": start, "maxResults": 100},
        )
        r.raise_for_status()
        data = r.json()
        total = data.get("total", 0)
        for c in data.get("comments") or []:
            author = (c.get("author") or {}).get("displayName", "?")
            created = (c.get("created") or "")[:10]
            authors.append(f"@{author}, {created}")
            bodies.append(plain_description({"description": c.get("body")}))
        if data.get("isLast", True) or not data.get("comments"):
            break
        start += len(data["comments"])
    return {"fetched": True, "count": total, "authors_dates": authors, "urls": extract_urls("\n".join(bodies))}


def fingerprint(epic_key: str, updated: str) -> str:
    return hashlib.sha256(f"{epic_key}:{updated}".encode()).hexdigest()[:16]


def build_harvest(
    epic_key: str,
    issue: dict,
    children: list[dict],
    epic_remotes: list[dict],
    child_remotes: dict[str, list[dict]],
    comments: dict,
) -> dict:
    fields = issue.get("fields", {})
    desc = plain_description(fields)
    epic_urls = extract_urls(desc)
    confluence_urls: set[str] = set()
    external: list[dict] = []
    figma: list[dict] = []

    def ingest_url(url: str, prov: str) -> None:
        if "figma.com" in url:
            figma.append({"url": url, "status": "not_applicable", "detail": f"Figma not fetched in harvest batch ({prov})"})
        elif "/wiki/" in url or "confluence" in url.lower():
            confluence_urls.add(url)
        else:
            kind = "other"
            for pat, k in EXTERNAL_RE:
                if pat.search(url):
                    kind = k
                    break
            external.append({"url": url, "kind": kind, "from": prov})

    for u in epic_urls:
        ingest_url(u, "epic description")
    for r in epic_remotes:
        ingest_url(r["url"], "epic remote link")
    for u in comments.get("urls") or []:
        ingest_url(u, "epic comment")

    child_url_rows: list[dict] = []
    for c in children:
        for u in extract_urls(c.get("description") or ""):
            child_url_rows.append({"child": c["key"], "url": u, "source": "description"})
            ingest_url(u, f"child {c['key']} description")
        for r in child_remotes.get(c["key"]) or []:
            child_url_rows.append({"child": c["key"], "url": r["url"], "source": "remote link"})
            ingest_url(r["url"], f"child {c['key']} remote link")

    attachments = fields.get("attachment") or []
    screenshots = []
    for a in attachments:
        mime = (a.get("mimeType") or "").lower()
        if mime.startswith("image/"):
            screenshots.append(
                {
                    "name": a.get("filename"),
                    "status": "failed",
                    "detail": "Epic attachment image not downloaded in batch harvest — run vision step or record failed.",
                }
            )
    if not screenshots:
        screenshots = [{"name": "epic attachments", "status": "not_applicable", "detail": "No image attachments on Epic."}]

    return {
        "epic_key": epic_key,
        "gathered_at": datetime.now(timezone.utc).isoformat(),
        "epic": {"description_urls": epic_urls, "description_len": len(desc)},
        "remote_links": epic_remotes,
        "comments": comments,
        "children": {
            "count": len(children),
            "described": sum(1 for c in children if c["description_len"] >= 40),
            "urls": child_url_rows,
            "remote_links_checked_for_children": True,
            "items": children,
        },
        "confluence_urls": sorted(confluence_urls),
        "external_urls": external,
        "figma": figma[:3],
        "screenshots": screenshots,
        "errors": [],
    }


def build_payload(epic_key: str, issue: dict, harvest: dict, run_id: str, base_url: str) -> dict[str, Any]:
    from portfolio_testing_sweep import build_payload as sweep_build  # noqa: PLC0415

    children = harvest["children"]["items"]
    child_rows = [
        {
            "key": c["key"],
            "type": c["type"],
            "status": c["status"],
            "summary": c["summary"],
            "description_len": c["description_len"],
        }
        for c in children
    ]
    remote_urls = [r["url"] for r in harvest.get("remote_links") or []]
    payload = sweep_build(epic_key, issue, child_rows, remote_urls, run_id)
    fields = issue.get("fields", {})
    payload["requirements"][0]["url"] = f"{base_url}/browse/{epic_key}"
    payload["requirements"][0]["description_excerpt"] = plain_description(fields)[:500]
    due = fields.get("duedate")
    end = fields.get("customfield_10548")
    if due:
        payload["requirements"][0]["planning_due_date"] = due
    if end:
        payload["requirements"][0]["planning_end_date"] = end
    if due or end:
        payload["requirements"][0]["planning_target_date"] = due or end
    payload["requirement_fingerprint"] = fingerprint(epic_key, fields.get("updated", run_id))
    payload["gather_mode"] = "rest_harvest"
    payload["report"]["handoff_note"] = (
        "REST harvest only. This is not a full Reviewer gather. "
        "Re-score findings after the Confluence merge."
    )
    payload["report"]["next_action"] = (
        "Run trinity-reviewer for a full gather before Creator. This file is a REST harvest."
    )
    st = (fields.get("status") or {}).get("name", "")
    cat = (fields.get("status") or {}).get("statusCategory", {}).get("key", "")
    payload.setdefault("scope", {})["lifecycle"] = "post_delivery" if cat == "done" else "pre_delivery"
    inv = payload.get("rollup", {}).get("epic_child_inventory") or []
    for row in inv:
        ck = row["key"]
        match = next((c for c in children if c["key"] == ck), None)
        if match:
            row["content_source"] = "description" if match["description_len"] >= 40 else "title_only"
    payload["rollup"]["epic_child_inventory"] = inv
    if "recommended_batch_keys" in payload.get("rollup", {}):
        del payload["rollup"]["recommended_batch_keys"]
    return payload


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", type=Path, required=True)
    ap.add_argument("--keys", required=True, help="Comma-separated epic keys")
    ap.add_argument("--run-id", default=datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M"))
    args = ap.parse_args()
    load_env()
    if not os.environ.get("JIRA_API_TOKEN"):
        sys.exit("Set JIRA_* in Trinity/studio/.env")
    base = os.environ.get("JIRA_BASE_URL", "https://appfire.atlassian.net").rstrip("/")
    if "sandbox" in base:
        base = "https://appfire.atlassian.net"
    auth = httpx.BasicAuth(os.environ["JIRA_EMAIL"], os.environ["JIRA_API_TOKEN"])
    run_dir = args.run_dir if args.run_dir.is_absolute() else REPO / args.run_dir
    gather_dir = run_dir / "_gather" / "epics"
    gather_dir.mkdir(parents=True, exist_ok=True)
    keys = [k.strip() for k in args.keys.split(",") if k.strip()]
    results: dict[str, str] = {}

    with httpx.Client(timeout=120.0) as client:
        for key in keys:
            epic_dir = run_dir / key
            epic_dir.mkdir(parents=True, exist_ok=True)
            try:
                issue = fetch_issue(client, base, auth, key)
                children = fetch_children(client, base, auth, key)
                epic_remotes = fetch_remote_links(client, base, auth, key)
                child_remotes: dict[str, list[dict]] = {}
                for c in children:
                    child_remotes[c["key"]] = fetch_remote_links(client, base, auth, c["key"])
                comments = fetch_comments(client, base, auth, key)
                harvest = build_harvest(key, issue, children, epic_remotes, child_remotes, comments)
                (gather_dir / f"{key}.json").write_text(json.dumps(harvest, indent=2), encoding="utf-8")
                payload = build_payload(key, issue, harvest, args.run_id, base)
                canonical = epic_dir / "review-payload.json"
                target = canonical
                if canonical.is_file():
                    try:
                        existing_mode = json.loads(canonical.read_text(encoding="utf-8")).get("gather_mode")
                    except (OSError, json.JSONDecodeError):
                        existing_mode = None
                    if existing_mode not in ("rest_sweep", "rest_harvest"):
                        target = epic_dir / "rest-sweep" / "review-payload.json"
                        target.parent.mkdir(parents=True, exist_ok=True)
                        print(f"KEEP {key} canonical review-payload.json")
                target.write_text(
                    json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
                )
                results[key] = "ok"
                print(f"OK {key} children={len(children)} conf_urls={len(harvest['confluence_urls'])}")
            except Exception as e:
                results[key] = f"fail: {e}"
                (epic_dir / "harvest-error.txt").write_text(str(e), encoding="utf-8")
                print(f"FAIL {key}: {e}", file=sys.stderr)

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
