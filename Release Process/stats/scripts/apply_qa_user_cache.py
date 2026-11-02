#!/usr/bin/env python3
"""Apply accountId -> displayName cache to test_run.stats.qa_engineers in data/*.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "Release Process" / "stats" / "data"
CACHE = ROOT / "Release Process" / "stats" / "data" / "qa_user_cache.json"


def main() -> int:
    if not CACHE.is_file():
        print(f"missing {CACHE}", file=sys.stderr)
        return 1
    cache: dict[str, str] = json.loads(CACHE.read_text())
    updated = 0
    for path in sorted(DATA.glob("8.*.json")):
        report = json.loads(path.read_text())
        run = report.get("test_run") or {}
        stats = run.get("stats") or {}
        qa = stats.get("qa_engineers") or {}
        ids = qa.get("account_ids") or []
        if not ids:
            continue
        names = [cache.get(aid, aid) for aid in ids]
        if names == qa.get("names"):
            continue
        qa["names"] = names
        stats["qa_engineers"] = qa
        run["stats"] = stats
        report["test_run"] = run
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        updated += 1
        print(f"{path.stem}: {qa['count']} names")
    print(f"updated {updated} releases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
