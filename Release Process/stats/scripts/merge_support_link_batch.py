#!/usr/bin/env python3
"""Merge issuelink search results into support_links_cache.json."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CACHE = ROOT / "Release Process/stats/data/support_links_cache.json"
VERSIONS_CACHE = ROOT / "Release Process/stats/data/affected_versions_cache.json"
GATHER = ROOT / "Release Process/stats/scripts/gather_release_stats.py"


def load_gather():
    spec = importlib.util.spec_from_file_location("gather", GATHER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    gather = load_gather()
    if len(sys.argv) > 1:
        raw = Path(sys.argv[1]).read_text()
    else:
        raw = sys.stdin.read()
    wrap = json.loads(raw)
    if wrap.get("error"):
        print(f"skip error payload: {wrap.get('message')}", file=sys.stderr)
        return 1
    data = wrap.get("data") or wrap
    cache: dict[str, list[str]] = {}
    if CACHE.is_file():
        cache = json.loads(CACHE.read_text())
    vcache: dict[str, list[str]] = {}
    if VERSIONS_CACHE.is_file():
        vcache = json.loads(VERSIONS_CACHE.read_text())
    for issue in data.get("issues") or []:
        key = issue.get("key")
        if not key:
            continue
        fields = issue.get("fields") or {}
        links = fields.get("issuelinks")
        cache[key] = gather.support_keys_from_issuelinks(links)
        vcache[key] = gather.affected_version_names_from_fields(fields)
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, indent=2, ensure_ascii=False) + "\n")
    VERSIONS_CACHE.write_text(json.dumps(vcache, indent=2, ensure_ascii=False) + "\n")
    print(f"cache size {len(cache)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
