#!/usr/bin/env python3
"""Merge linked-defect Jira fields into release stats JSON (MCP cache or live Jira)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "Release Process" / "stats" / "data"
CACHE = DATA_DIR / "linked_defect_cache.json"
GATHER_PATH = ROOT / "Release Process" / "stats" / "scripts" / "gather_release_stats.py"


def load_gather():
    spec = importlib.util.spec_from_file_location("gather", GATHER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def row_from_cache(key: str, item: dict[str, Any], gather) -> dict[str, Any]:
    return {
        "key": key,
        "summary": item.get("summary"),
        "priority": item.get("priority") or "None",
        "status": item.get("status"),
        "created": (item.get("created") or "")[:10] if item.get("created") else None,
        "found_by_test_run": True,
        "outside_cutoff_query": True,
        "url": item.get("url") or gather.browse(key),
    }


def patch_release(release: dict[str, Any], cache: dict[str, Any], gather) -> int:
    bugs = release.get("bugs") or {}
    issues: list[dict[str, Any]] = list(bugs.get("issues") or [])
    by_key = {item["key"]: item for item in issues}
    defect_keys = (release.get("test_run") or {}).get("defect_keys") or []
    added = 0
    for key in defect_keys:
        if key in by_key:
            continue
        cached = cache.get(key)
        if not cached:
            continue
        row = row_from_cache(key, cached, gather)
        issues.append(row)
        by_key[key] = row
        added += 1
    if not added:
        return 0
    bugs["issues"] = issues
    cutoff = gather.cutoff_scope_bugs(issues)
    release["bugs"] = bugs
    release["metrics"]["bugs_total"] = len(cutoff)
    slices = gather.build_bug_jql_slices(
        bugs.get("jql"),
        issues,
        (release.get("test_run") or {}).get("key"),
        defect_keys,
    )
    release["bugs"]["other"] = slices["other"]
    release["metrics"]["bugs_other_since_cutoff"] = slices["other"]["count"]
    priority_order = ["Highest", "High", "Medium", "Low", "Lowest"]
    by_priority: dict[str, int] = {}
    for bug in cutoff:
        name = bug.get("priority") or "None"
        by_priority[name] = by_priority.get(name, 0) + 1
    ordered = [name for name in priority_order if name in by_priority]
    ordered += sorted(name for name in by_priority if name not in priority_order)
    release["bugs"]["by_priority"] = {name: by_priority[name] for name in ordered}
    release["metrics"]["bugs_by_priority"] = release["bugs"]["by_priority"]
    return added


def main() -> int:
    if not CACHE.is_file():
        print(f"Missing {CACHE.relative_to(ROOT)} — populate via MCP key lookup first.", file=sys.stderr)
        return 2
    cache = json.loads(CACHE.read_text())
    gather = load_gather()
    gather.load_env(gather.ENV_PATH)
    total = 0
    for path in sorted(DATA_DIR.glob("*.json")):
        if path.name in ("changelogs.json", "qa_user_cache.json", "linked_defect_cache.json"):
            continue
        release = json.loads(path.read_text())
        if release.get("schema_version") != 1:
            continue
        n = patch_release(release, cache, gather)
        if n:
            path.write_text(json.dumps(release, indent=2, ensure_ascii=False) + "\n")
            print(f"{path.stem}: +{n} linked defect rows")
            total += n
    print(f"Done. {total} rows added.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
