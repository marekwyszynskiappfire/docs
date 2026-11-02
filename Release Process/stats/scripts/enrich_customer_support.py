#!/usr/bin/env python3
"""Fetch issuelinks via Atlassian MCP and mark customer-reported (SUPPORT-linked) bugs per train."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "Release Process/stats/data"
CACHE = DATA / "support_links_cache.json"
VERSIONS_CACHE = DATA / "affected_versions_cache.json"
GATHER = ROOT / "Release Process/stats/scripts/gather_release_stats.py"
CLOUD_ID = "8e83c2b4-97ae-4335-8a8f-bbdff09d62dd"
MCP_CMD = [
    "/usr/local/bin/mcp-remote",
    "https://mcp.atlassian.com/v2/mcp",
    "30899",
    "--resource",
    "https://appfire.atlassian.net/",
]
BATCH = 40


def load_gather():
    spec = importlib.util.spec_from_file_location("gather", GATHER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rpc(proc, method: str, params: dict | None = None, req_id: int = 1) -> dict:
    msg = {"jsonrpc": "2.0", "id": req_id, "method": method}
    if params is not None:
        msg["params"] = params
    proc.stdin.write(json.dumps(msg) + "\n")
    proc.stdin.flush()
    while True:
        line = proc.stdout.readline()
        if not line:
            raise RuntimeError("mcp-remote closed stdout")
        payload = json.loads(line)
        if payload.get("id") == req_id:
            if payload.get("error"):
                raise RuntimeError(payload["error"])
            return payload.get("result") or {}


def call_tool(proc, name: str, arguments: dict, req_id: int) -> dict:
    result = rpc(proc, "tools/call", {"name": name, "arguments": arguments}, req_id)
    content = result.get("content") or []
    for block in content:
        if block.get("type") == "text":
            return json.loads(block["text"])
    raise RuntimeError(f"no text in tool result for {name}")


def fetch_links(
    proc, req_id: int, keys: list[str]
) -> tuple[dict[str, list[str]], dict[str, list[str]], int]:
    gather = load_gather()
    out: dict[str, list[str]] = {}
    versions: dict[str, list[str]] = {}
    for start in range(0, len(keys), BATCH):
        chunk = keys[start : start + BATCH]
        jql = f"key in ({', '.join(chunk)})"
        wrap = call_tool(
            proc,
            "searchJiraIssuesUsingJql",
            {
                "cloudId": CLOUD_ID,
                "jql": jql,
                "maxResults": 100,
                "fields": ["issuelinks", "versions"],
                "view": "full",
            },
            req_id,
        )
        req_id += 1
        data = wrap.get("data") or wrap
        for issue in data.get("issues") or []:
            key = issue["key"]
            fields = issue.get("fields") or {}
            links = fields.get("issuelinks")
            out[key] = gather.support_keys_from_issuelinks(links)
            versions[key] = gather.affected_version_names_from_fields(fields)
    return out, versions, req_id


def all_bug_keys() -> list[str]:
    keys: set[str] = set()
    for path in sorted(DATA.glob("8.*.json")):
        report = json.loads(path.read_text())
        for bug in (report.get("bugs") or {}).get("issues") or []:
            keys.add(bug["key"])
    return sorted(keys)


def apply_reports(
    support_by_bug: dict[str, list[str]],
    affected_versions_by_key: dict[str, list[str]] | None = None,
) -> None:
    gather = load_gather()
    for path in sorted(DATA.glob("8.*.json")):
        report = json.loads(path.read_text())
        gather.apply_customer_reported_block(
            report, support_by_bug, affected_versions_by_key
        )
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        print(
            f"{path.stem}: customer_reported={report['metrics'].get('bugs_customer_reported', 0)}"
        )


def main() -> int:
    gather = load_gather()
    cache: dict[str, list[str]] = {}
    if CACHE.is_file():
        cache = json.loads(CACHE.read_text())
    versions_cache: dict[str, list[str]] = {}
    if VERSIONS_CACHE.is_file():
        versions_cache = json.loads(VERSIONS_CACHE.read_text())

    keys = all_bug_keys()
    missing = [k for k in keys if k not in cache]
    if missing and "--apply-only" not in sys.argv:
        proc = subprocess.Popen(
            MCP_CMD,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            rpc(
                proc,
                "initialize",
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "release-stats", "version": "1.0"},
                },
                1,
            )
            proc.stdin.write(
                json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n"
            )
            proc.stdin.flush()
            fetched, fetched_versions, _ = fetch_links(proc, 2, missing)
            cache.update(fetched)
            versions_cache.update(fetched_versions)
            CACHE.write_text(json.dumps(cache, indent=2, ensure_ascii=False) + "\n")
            VERSIONS_CACHE.write_text(
                json.dumps(versions_cache, indent=2, ensure_ascii=False) + "\n"
            )
            print(f"cached {len(fetched)} bug link sets ({len(cache)} total)")
        finally:
            proc.stdin.close()
            proc.wait(timeout=120)
    elif missing:
        print(f"warning: {len(missing)} keys missing from cache; run without --apply-only", file=sys.stderr)

    apply_reports(cache, versions_cache)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
