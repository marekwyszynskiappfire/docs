#!/usr/bin/env python3
"""Append slim bugs from an MCP searchJiraIssuesUsingJql JSON payload to _fetch/{version}/bugs_merged.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FETCH = ROOT / "Release Process" / "stats" / "mcp_import" / "_fetch"
SITE = "https://appfire.atlassian.net"


def slim(issue: dict) -> dict:
    key = issue["key"]
    fields = issue.get("fields") or {}
    priority = fields.get("priority") or {}
    status = fields.get("status") or {}
    created = fields.get("created") or ""
    return {
        "key": key,
        "summary": fields.get("summary"),
        "priority": priority.get("name") if isinstance(priority, dict) else priority or "None",
        "status": status.get("name") if isinstance(status, dict) else status,
        "created": created[:10] if created else "",
        "url": f"{SITE}/browse/{key}",
    }


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print("usage: append_mcp_bugs.py VERSION [mcp_search.json]", file=sys.stderr)
        return 2
    version = sys.argv[1]
    if len(sys.argv) == 3:
        payload = json.loads(Path(sys.argv[2]).read_text())
    else:
        payload = json.load(sys.stdin)
    data = payload.get("data") or payload
    issues = data.get("issues") or []
    out_dir = FETCH / version
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "bugs_merged.json"
    merged: list[dict] = []
    if out_path.is_file():
        merged = json.loads(out_path.read_text())
    seen = {b["key"] for b in merged}
    for issue in issues:
        row = slim(issue)
        if row["key"] not in seen:
            merged.append(row)
            seen.add(row["key"])
    out_path.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n")
    print(f"{version}: +{len(issues)} total={len(merged)} isLast={data.get('isLast')}")
    if data.get("nextPageToken"):
        print(f"nextPageToken={data['nextPageToken']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
