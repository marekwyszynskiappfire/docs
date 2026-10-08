#!/usr/bin/env python3
"""List epics in run-config scope that lack review-payload.json under the portfolio folder."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

from scope_utils import new_epics_for_config  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "config",
        help="Path to portfolio run-config JSON or portfolio_id (loads config/runs/{id}.json)",
    )
    p.add_argument("--json", action="store_true", help="Print JSON")
    args = p.parse_args()

    path = Path(args.config)
    if not path.is_file():
        path = SCRIPT_DIR.parent / "config" / "runs" / f"{path.name}.json"
    if not path.is_file() and path.suffix != ".json":
        path = path.with_suffix(".json")
    if not path.is_file():
        print(f"Config not found: {path}", file=sys.stderr)
        return 1

    config = json.loads(path.read_text(encoding="utf-8"))
    result = new_epics_for_config(config, REPO_ROOT)

    if args.json:
        print(json.dumps(result, indent=2))
        return 0 if not result.get("error") or result.get("epics_in_scope") else 1

    if result.get("error"):
        print(result["error"], file=sys.stderr)
    print(f"Portfolio folder: {result['run_folder']}")
    print(f"New epics ({len(result['new_epics'])}): {', '.join(result['new_epics']) or '—'}")
    print(f"Already scanned ({len(result['already_scanned'])}): {', '.join(result['already_scanned']) or '—'}")
    return 0 if result.get("epics_in_scope") else 1


if __name__ == "__main__":
    raise SystemExit(main())
