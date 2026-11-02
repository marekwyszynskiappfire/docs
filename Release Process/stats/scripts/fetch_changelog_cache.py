#!/usr/bin/env python3
"""Build changelogs.json from per-issue JSON dumps (MCP listJiraIssueChangelogs pages).

Each input file is either:
  - raw MCP response: {"data": {"values": [...], "isLast": ..., "total": ...}}
  - paginated merge: {"values": [...]}
  - a list of changelog entries

Usage:
  python3 fetch_changelog_cache.py --merge /tmp/ONE-392073.json ...
  python3 fetch_changelog_cache.py --from-dir /tmp/release-changelogs
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "Release Process" / "stats" / "data"
DEFAULT_OUT = DATA_DIR / "changelogs.json"
KEY_RE = re.compile(r"(ONE-\d+)", re.I)


def extract_values(payload) -> list:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        if "data" in payload and isinstance(payload["data"], dict):
            payload = payload["data"]
        if "values" in payload:
            return payload["values"] or []
    return []


def issue_key_from_path(path: Path) -> str | None:
    match = KEY_RE.search(path.stem) or KEY_RE.search(path.name)
    return match.group(1).upper() if match else None


def slim_entry(entry: dict) -> dict:
    items = []
    for item in entry.get("items") or []:
        if not item:
            continue
        items.append({
            "field": item.get("field"),
            "fromString": item.get("fromString"),
            "toString": item.get("toString"),
        })
    return {"created": entry.get("created"), "items": items}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--merge", nargs="*", type=Path, help="Issue dump files to merge")
    parser.add_argument("--from-dir", type=Path, help="Directory of ONE-*.json pages")
    args = parser.parse_args()

    cache: dict[str, list] = {}
    if args.out.is_file():
        cache = json.loads(args.out.read_text())

    paths: list[Path] = list(args.merge or [])
    if args.from_dir:
        paths.extend(sorted(args.from_dir.glob("*.json")))

    for path in paths:
        key = issue_key_from_path(path)
        if not key:
            print(f"skip (no key): {path}")
            continue
        payload = json.loads(path.read_text())
        values = extract_values(payload)
        slim = [slim_entry(v) for v in values]
        existing = cache.get(key) or []
        by_created = {e.get("created"): e for e in existing if e.get("created")}
        for entry in slim:
            if entry.get("created"):
                by_created[entry["created"]] = entry
        cache[key] = sorted(by_created.values(), key=lambda e: e.get("created") or "")
        print(f"{key}: {len(cache[key])} entries")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(cache, indent=2) + "\n")
    print(f"wrote {args.out} ({len(cache)} issues)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
