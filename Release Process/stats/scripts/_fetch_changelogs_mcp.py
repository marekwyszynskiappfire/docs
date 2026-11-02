#!/usr/bin/env python3
"""Fetch changelogs via Atlassian MCP listJiraIssueChangelogs and write slim cache.

Requires Cursor agent with plugin-atlassian-atlassian MCP. This script is invoked
by the agent after MCP pages are saved under --dump-dir as ONE-*.json files.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import importlib.util

ROOT = Path(__file__).resolve().parents[3]
FC_PATH = ROOT / "Release Process" / "stats" / "scripts" / "fetch_changelog_cache.py"
_spec = importlib.util.spec_from_file_location("fetch_changelog_cache", FC_PATH)
fc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fc)
DATA = ROOT / "Release Process" / "stats" / "data"
DEFAULT_OUT = DATA / "changelogs.json"
KEY_RE = re.compile(r"(ONE-\d+)", re.I)


def keys_from_versions(data_dir: Path, versions: list[str]) -> list[str]:
    keys: set[str] = set()
    for v in versions:
        path = data_dir / f"{v}.json"
        report = json.loads(path.read_text())
        keys.update((report.get("test_run") or {}).get("defect_keys") or [])
    return sorted(keys)


def merge_dump_dir(dump_dir: Path, out: Path, required: list[str]) -> None:
    cache: dict[str, list] = {}
    if out.is_file():
        cache = json.loads(out.read_text())

    for path in sorted(dump_dir.glob("*.json")):
        match = KEY_RE.search(path.stem)
        if not match:
            continue
        key = match.group(1).upper()
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
        raise SystemExit(f"missing changelogs for {len(missing)} keys: {', '.join(missing[:8])}")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(cache, indent=2) + "\n")
    print(f"wrote {out} ({len(cache)} issues)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dump-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("versions", nargs="*", default=["8.74", "8.75", "8.76"])
    args = parser.parse_args()
    required = keys_from_versions(DATA, args.versions)
    merge_dump_dir(args.dump_dir, args.out, required)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
