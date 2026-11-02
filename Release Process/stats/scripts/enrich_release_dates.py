#!/usr/bin/env python3
"""Compute release dates from test-run bug Done transitions."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "Release Process" / "stats" / "data"
CACHE = DATA_DIR / "changelogs.json"
GATHER = ROOT / "Release Process" / "stats" / "scripts" / "gather_release_stats.py"
SIGNAL = ROOT / "Release Process" / "stats" / "scripts" / "release_signal.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fetch_changelog_rest(gather_mod, issue_key: str) -> list[dict]:
    values: list[dict] = []
    start = 0
    while True:
        page = gather_mod.jira_get(
            f"/rest/api/3/issue/{issue_key}/changelog",
            {"startAt": start, "maxResults": 100},
        )
        values.extend(page.get("values") or [])
        if page.get("isLast", True):
            return values
        start += page.get("maxResults") or 100
        if start >= (page.get("total") or 0):
            return values


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("versions", nargs="*", help="e.g. 8.76 (default: all data/*.json)")
    parser.add_argument(
        "--cache",
        type=Path,
        default=CACHE,
        help="JSON map issueKey -> changelog values[] (from MCP listJiraIssueChangelogs)",
    )
    parser.add_argument("--write-cache", action="store_true", help="Refresh cache via Jira REST")
    args = parser.parse_args()

    gather = load_module(GATHER, "gather")
    signal_mod = load_module(SIGNAL, "release_signal")
    gather.load_env(gather.ENV_PATH)

    paths = sorted(DATA_DIR.glob("*.json"))
    if args.versions:
        paths = [DATA_DIR / f"{v}.json" for v in args.versions]
    paths = [p for p in paths if p.name != "changelogs.json"]

    cache: dict[str, list] = {}
    if args.cache.is_file():
        cache = json.loads(args.cache.read_text())

    keys: set[str] = set()
    for path in paths:
        if not path.is_file():
            continue
        report = json.loads(path.read_text())
        run = report.get("test_run") or {}
        keys.update(run.get("defect_keys") or [])

    if args.write_cache:
        for key in sorted(keys):
            try:
                cache[key] = fetch_changelog_rest(gather, key)
                print(f"cached {key} ({len(cache[key])} entries)")
            except RuntimeError as exc:
                print(f"skip {key}: {exc}", file=sys.stderr)
        args.cache.parent.mkdir(parents=True, exist_ok=True)
        args.cache.write_text(json.dumps(cache, indent=2) + "\n")
        return 0

    missing = sorted(k for k in keys if k not in cache)
    if missing:
        print(
            f"warning: missing changelogs for {len(missing)} issues "
            f"(first: {', '.join(missing[:5])})",
            file=sys.stderr,
        )

    for path in paths:
        report = json.loads(path.read_text())
        version = report["version"]
        defect_keys = (report.get("test_run") or {}).get("defect_keys") or []
        sig = signal_mod.build_release_signal(version, defect_keys, cache)
        signal_mod.apply_release_signal(report, sig)
        report["gathered_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        print(
            f"{version}: released={sig['released']} date={sig['release_date']} "
            f"trigger={sig.get('trigger_issue')} events={len(sig['qualifying_events'])}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
