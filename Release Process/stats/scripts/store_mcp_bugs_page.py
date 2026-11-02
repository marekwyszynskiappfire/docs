#!/usr/bin/env python3
"""Store MCP searchJiraIssuesUsingJql payload as slim bugs_merged.json (single page, isLast=true)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
APPEND = ROOT / "Release Process" / "stats" / "scripts" / "append_mcp_bugs.py"

spec = importlib.util.spec_from_file_location("append", APPEND)
append = importlib.util.module_from_spec(spec)
spec.loader.exec_module(append)


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: store_mcp_bugs_page.py VERSION mcp.json", file=sys.stderr)
        return 2
    version, path = sys.argv[1], Path(sys.argv[2])
    payload = json.loads(path.read_text())
    data = payload.get("data") or payload
    if not data.get("isLast", True):
        print(f"warning: {version} page is not last — use append_mcp_bugs for pagination", file=sys.stderr)
    out_dir = append.FETCH / version
    out_dir.mkdir(parents=True, exist_ok=True)
    merged_path = out_dir / "bugs_merged.json"
    merged: list[dict] = []
    if merged_path.is_file():
        merged = json.loads(merged_path.read_text())
    seen = {b["key"] for b in merged}
    for issue in data.get("issues") or []:
        row = append.slim(issue)
        if row["key"] not in seen:
            merged.append(row)
            seen.add(row["key"])
    merged_path.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n")
    print(f"{version}: stored {len(merged)} bugs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
