#!/usr/bin/env python3
"""Paginate bug JQL via Atlassian MCP (mcp-remote stdio); save pages and bugs_merged."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "Release Process/stats/trains_since_2025-10-01.json"
FETCH = ROOT / "Release Process/stats/mcp_import/_fetch"
SAVE = ROOT / "Release Process/stats/scripts/save_mcp_bug_page.py"
BUILD = ROOT / "Release Process/stats/scripts/build_bugs_merged_from_pages.py"
CLOUD_ID = "8e83c2b4-97ae-4335-8a8f-bbdff09d62dd"
MCP_CMD = [
    "/usr/local/bin/mcp-remote",
    "https://mcp.atlassian.com/v2/mcp",
    "30899",
    "--resource",
    "https://appfire.atlassian.net/",
]


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


def fetch_version(proc, req_id: int, version: str, jql: str) -> tuple[int, int, int]:
    vdir = FETCH / version
    vdir.mkdir(parents=True, exist_ok=True)
    merged = vdir / "bugs_merged.json"
    if merged.is_file():
        merged.unlink()
    for p in vdir.glob("bugs_page_*.json"):
        p.unlink()

    token = None
    page = 0
    while True:
        args = {
            "cloudId": CLOUD_ID,
            "jql": jql,
            "maxResults": 100,
            "fields": ["summary", "priority", "status", "created"],
            "view": "evidence",
        }
        if token:
            args["nextPageToken"] = token
        wrap = call_tool(proc, "searchJiraIssuesUsingJql", args, req_id)
        req_id += 1
        page_path = vdir / f"bugs_page_{page:03d}.json"
        page_path.write_text(json.dumps(wrap, indent=2, ensure_ascii=False) + "\n")
        subprocess.run([sys.executable, str(SAVE), version, str(page), str(page_path)], check=True)
        data = wrap.get("data") or wrap
        if data.get("isLast", True):
            break
        token = data.get("nextPageToken")
        if not token:
            break
        page += 1
    subprocess.run([sys.executable, str(BUILD), version], check=True)
    count = len(json.loads((vdir / "bugs_merged.json").read_text()))
    return page + 1, count, req_id


def main() -> int:
    versions = sys.argv[1:] or [f"8.{i}" for i in range(66, 74)]
    manifest = {e["version"]: e for e in json.loads(MANIFEST.read_text())}
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
        proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        proc.stdin.flush()
        req_id = 2
        for version in versions:
            entry = manifest[version]
            jql = (
                f'issuetype = Bug AND affectedVersion = "{entry["preprod_name"]}" '
                f'AND created >= "{entry["cutoff_date"]}" ORDER BY priority DESC, created ASC'
            )
            pages, count, req_id = fetch_version(proc, req_id, version, jql)
            print(f"{version}: pages={pages} merged={count}")
    finally:
        proc.stdin.close()
        proc.wait(timeout=10)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
