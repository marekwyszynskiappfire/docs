#!/usr/bin/env python3
"""Merge Jira search API page JSON files into issues list for xray_graphql_export."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("pages_dir", type=Path, help="Directory with page-*.json from Jira search")
    p.add_argument("-o", "--out", type=Path, required=True)
    args = p.parse_args()

    issues: list[dict[str, str]] = []
    seen: set[str] = set()
    for path in sorted(args.pages_dir.glob("page-*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        block = data.get("data") or data
        for item in block.get("issues") or []:
            key = item.get("key")
            if not key or key in seen:
                continue
            seen.add(key)
            issues.append({"key": key, "id": item.get("id", "")})

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"issues": issues}, indent=2) + "\n", encoding="utf-8")
    print(f"Merged {len(issues)} issues → {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
