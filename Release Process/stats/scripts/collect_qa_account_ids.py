#!/usr/bin/env python3
"""Print sorted unique QA executor account IDs from release data JSON files."""

from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "data"


def main() -> int:
    ids: set[str] = set()
    for path in sorted(DATA.glob("8.*.json")):
        qa = ((json.loads(path.read_text()).get("test_run") or {}).get("stats") or {}).get(
            "qa_engineers"
        ) or {}
        ids.update(qa.get("account_ids") or [])
    for aid in sorted(ids):
        print(aid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
