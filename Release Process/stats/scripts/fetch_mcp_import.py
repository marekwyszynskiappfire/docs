#!/usr/bin/env python3
"""Build mcp_import/*.json via Jira REST (same JQL/fields as MCP gather)."""

from __future__ import annotations

import importlib.util
import json
import sys
import urllib.parse
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "Release Process" / "stats" / "trains_since_2025-10-01.json"
IMPORT_DIR = ROOT / "Release Process" / "stats" / "mcp_import"
GATHER_PATH = ROOT / "Release Process" / "stats" / "scripts" / "gather_release_stats.py"
SITE = "https://appfire.atlassian.net"


def load_gather():
    spec = importlib.util.spec_from_file_location("gather", GATHER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.load_env(mod.ENV_PATH)
    mod.load_env(mod.PRODUCTION_ENV_PATH, override={"XRAY_CLIENT_ID", "XRAY_CLIENT_SECRET"})
    # MCP OAuth bearer is not accepted by appfire.atlassian.net REST; use API token.
    mod.jira_bearer_token = lambda: None  # type: ignore[method-assign]
    return mod


def defect_keys(issuelinks: list[dict] | None) -> list[str]:
    keys: list[str] = []
    for link in issuelinks or []:
        if (link.get("type") or {}).get("name") != "Defect":
            continue
        outward = link.get("outwardIssue")
        inward = link.get("inwardIssue")
        if outward and outward.get("key"):
            keys.append(outward["key"])
        if inward and inward.get("key"):
            keys.append(inward["key"])
    return keys


def map_bug(issue: dict) -> dict:
    f = issue.get("fields") or {}
    key = issue["key"]
    return {
        "key": key,
        "summary": f.get("summary"),
        "priority": (f.get("priority") or {}).get("name") or "None",
        "status": (f.get("status") or {}).get("name"),
        "created": (f.get("created") or "")[:10],
        "url": f"{SITE}/browse/{key}",
    }


def map_cloud(item: dict) -> dict:
    return {
        "id": str(item["id"]),
        "name": item["name"],
        "released": bool(item.get("released")),
        "release_date": item.get("releaseDate") or None,
    }


def list_cloud_versions(gather, version: str) -> list[dict]:
    found: list[dict] = []
    start = 0
    query = f"bigpicture-cloud-{version}"
    while True:
        page = gather.jira_get(
            f"/rest/api/3/project/ONE/version",
            {"query": query, "maxResults": 100, "startAt": start, "orderBy": "name"},
        )
        found.extend(page.get("values") or [])
        start += page.get("maxResults") or 100
        if page.get("isLast", True) or start >= (page.get("total") or 0):
            return [map_cloud(v) for v in found]
    return [map_cloud(v) for v in found]


def main() -> int:
    gather = load_gather()
    manifest = json.loads(MANIFEST.read_text())
    IMPORT_DIR.mkdir(parents=True, exist_ok=True)

    versions = sys.argv[1:] if len(sys.argv) > 1 else []
    if not versions:
        versions = [f"8.{i}" for i in range(62, 74)]

    wanted = set(versions)
    failures: list[str] = []

    for entry in manifest:
        version = entry["version"]
        if version not in wanted:
            continue
        exec_key = entry["execution_key"]
        try:
            exec_issue = gather.jira_get(
                f"/rest/api/3/issue/{urllib.parse.quote(exec_key)}",
                {"fields": "summary,status,created,issuelinks"},
            )
            ef = exec_issue["fields"]
            execution = {
                "summary": ef.get("summary"),
                "status": (ef.get("status") or {}).get("name"),
                "created": ef.get("created"),
                "url": f"{SITE}/browse/{exec_key}",
                "defect_keys": defect_keys(ef.get("issuelinks")),
            }
            bug_jql = (
                f'issuetype = Bug AND affectedVersion = "{entry["preprod_name"]}" '
                f'AND created >= "{entry["cutoff_date"]}" ORDER BY priority DESC, created ASC'
            )
            bugs = [
                map_bug(i)
                for i in gather.jira_search(
                    bug_jql, ["summary", "priority", "status", "created"]
                )
            ]
            cloud_versions = list_cloud_versions(gather, version)
            payload = {
                "execution": execution,
                "bugs": bugs,
                "cloud_versions": cloud_versions,
            }
            out = IMPORT_DIR / f"{version}.json"
            out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
            print(
                f"{version}: {exec_key} bugs={len(bugs)} "
                f"defects={len(execution['defect_keys'])} cloud={len(cloud_versions)}"
            )
        except Exception as exc:
            failures.append(f"{version}: {exc}")
            print(f"FAIL {version}: {exc}", file=sys.stderr)

    if failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
