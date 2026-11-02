#!/usr/bin/env python3
"""Merge MCP changelog dump files into changelogs.json (slim entries)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "Release Process" / "stats" / "data"
OUT = DATA / "changelogs.json"
FC = ROOT / "Release Process" / "stats" / "scripts" / "fetch_changelog_cache.py"


def load_fc():
    spec = importlib.util.spec_from_file_location("fc", FC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def keys_from_versions() -> list[str]:
    keys: set[str] = set()
    for v in ("8.74", "8.75", "8.76"):
        report = json.loads((DATA / f"{v}.json").read_text())
        keys.update((report.get("test_run") or {}).get("defect_keys") or [])
    return sorted(keys)


def main() -> int:
    dump_dir = Path(sys.argv[1])
    fc = load_fc()
    required = keys_from_versions()
    cache: dict[str, list] = {}

    for path in sorted(dump_dir.glob("*.json")):
        if path.name.startswith("cache_") or path.name.startswith("payload-"):
            continue
        key = path.stem.upper()
        if not key.startswith("ONE-"):
            continue
        payload = json.loads(path.read_text())
        values = fc.extract_values(payload)
        slim = [fc.slim_entry(v) for v in values]
        by_created = {e.get("created"): e for e in cache.get(key, []) if e.get("created")}
        for entry in slim:
            if entry.get("created"):
                by_created[entry["created"]] = entry
        cache[key] = sorted(by_created.values(), key=lambda e: e.get("created") or "")

    missing = [k for k in required if k not in cache]
    if missing:
        print("missing:", ", ".join(missing), file=sys.stderr)
        return 1

    OUT.write_text(json.dumps(cache, indent=2) + "\n")
    print(f"wrote {OUT} ({len(cache)} issues)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
