#!/usr/bin/env python3
"""Write MCP fetch results into nested-rescan cache.

Input JSON (stdin or file): list of objects with pageId, title, version, markdown.

Usage:
  python3 save_confluence_cache_batch.py --run-dir PATH < batch.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nested_confluence_rescan import cache_write


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", type=Path, required=True)
    ap.add_argument("--input", type=Path, default=None)
    args = ap.parse_args()
    run_dir = args.run_dir.resolve()
    raw = args.input.read_text(encoding="utf-8") if args.input else sys.stdin.read()
    items = json.loads(raw)
    if isinstance(items, dict) and "items" in items:
        items = items["items"]
    for item in items:
        cache_write(
            run_dir,
            str(item["pageId"]),
            item.get("title") or f"page {item['pageId']}",
            int(item.get("version") or 1),
            item.get("markdown") or "",
        )
        print(item["pageId"])


if __name__ == "__main__":
    main()
