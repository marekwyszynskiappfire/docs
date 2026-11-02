#!/usr/bin/env python3
"""Build bugs_merged.json from MCP getJiraIssue payloads (stdin JSON array or file)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
APPEND = ROOT / "Release Process" / "stats" / "scripts" / "append_mcp_bugs.py"
FETCH = ROOT / "Release Process" / "stats" / "mcp_import" / "_fetch"

spec = importlib.util.spec_from_file_location("append", APPEND)
append = importlib.util.module_from_spec(spec)
spec.loader.exec_module(append)


def slim_issue(issue: dict) -> dict:
    return append.slim(issue)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: write_bugs_merged_from_issues.py VERSION", file=sys.stderr)
        return 2
    version = sys.argv[1]
    raw = sys.stdin.read().strip()
    if not raw:
        print("empty stdin", file=sys.stderr)
        return 1
    data = json.loads(raw)
    if isinstance(data, dict) and "issues" in data:
        issues = data["issues"]
    elif isinstance(data, list):
        issues = data
    else:
        issue = data.get("data") or data
        if isinstance(issue, dict) and issue.get("key"):
            issues = [issue]
        else:
            issues = issue.get("issues") or []
    merged = [slim_issue(i) for i in issues]
    vdir = FETCH / version
    vdir.mkdir(parents=True, exist_ok=True)
    out = vdir / "bugs_merged.json"
    out.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n")
    print(f"{version}: merged={len(merged)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
