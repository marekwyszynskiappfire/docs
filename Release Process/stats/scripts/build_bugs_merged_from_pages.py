#!/usr/bin/env python3
"""Build bugs_merged.json from bugs_page_*.json (MCP searchJiraIssuesUsingJql shape)."""

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


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: build_bugs_merged_from_pages.py VERSION", file=sys.stderr)
        return 2
    version = sys.argv[1]
    vdir = FETCH / version
    merged: list[dict] = []
    seen: set[str] = set()
    pages = sorted(vdir.glob("bugs_page_*.json"))
    if not pages:
        print(f"{version}: no bugs_page_*.json", file=sys.stderr)
        return 1
    for path in pages:
        payload = json.loads(path.read_text())
        data = payload.get("data") or payload
        for issue in data.get("issues") or []:
            row = append.slim(issue)
            if row["key"] not in seen:
                merged.append(row)
                seen.add(row["key"])
    out = vdir / "bugs_merged.json"
    out.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n")
    print(f"{version}: pages={len(pages)} merged={len(merged)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
