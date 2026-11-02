#!/usr/bin/env python3
"""Inventory or merge hand-enriched train JSON after gather_release_stats overwrites the file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "Release Process" / "stats" / "data"


def _has(obj: dict[str, Any] | None, *path: str) -> bool:
    cur: Any = obj
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return False
        cur = cur[key]
    if cur is None:
        return False
    if isinstance(cur, (list, dict, str)) and len(cur) == 0:
        return False
    return True


def inventory(report: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Gaps vs a complete train (8.76 reference). Returns (required, optional)."""
    required: list[str] = []
    optional: list[str] = []
    metrics = report.get("metrics") or {}

    if not report.get("cutoff", {}).get("name"):
        required.append("cutoff.preprod name (gather or materialize_trains)")
    if not report.get("test_run", {}).get("key"):
        required.append("test_run.key (gather or --execution VERSION=TC-XXXX)")
    elif not _has(report, "test_run", "stats", "total"):
        required.append("test_run.stats / metrics.tests_* (enrich_xray_stats.py)")
    elif _has(report, "test_run", "stats", "total") and "failed_tests" not in (report.get("test_run") or {}):
        optional.append("test_run.failed_tests[] with Xray Testing Board URLs (enrich_xray_stats.py)")
    if not report.get("bugs", {}).get("issues"):
        required.append("bugs.issues (gather or MCP import)")
    if metrics.get("tests_total") is None and _has(report, "test_run", "stats", "total"):
        required.append("metrics.tests_* sync (re-run enrich_xray_stats or gather)")
    if metrics.get("released") and metrics.get("release_date") is None:
        required.append("metrics.release_date (enrich_release_dates.py + changelogs)")
    elif not metrics.get("released") and not _has(report, "production", "release_signal"):
        optional.append("production.release_signal (when train not released yet — OK)")

    if not _has(report, "bugs", "customer_reported", "issues"):
        optional.append("bugs.customer_reported (enrich_customer_support.py + MCP issuelinks)")

    ki = report.get("known_issues") or {}
    if not ki.get("jql"):
        optional.append("known_issues.jql (gather when preprod exists)")
    elif ki.get("issue_count_verified") is None:
        optional.append("known_issues.issue_count_verified (Jira MCP on known_issues.jql)")
    if ki.get("jql") and not _has(ki, "breakdown"):
        optional.append("known_issues.breakdown[] (post-release Git + Jira; see skill reference)")
    else:
        for group in ki.get("breakdown") or []:
            gid = group.get("id") or group.get("title") or "?"
            if not _has(group, "issues"):
                optional.append(f"known_issues.breakdown[{gid}].issues[] (Jira MCP rows)")

    return required, optional


def merge_enrichments(
    previous: dict[str, Any],
    fresh: dict[str, Any],
    *,
    refresh_known_breakdown: bool = False,
) -> dict[str, Any]:
    merged = json.loads(json.dumps(fresh))
    prev_ki = previous.get("known_issues") or {}
    ki = merged.setdefault("known_issues", {})
    if not refresh_known_breakdown:
        for key in (
            "breakdown",
            "issue_count_verified",
            "breakdown_verified_at",
            "breakdown_source",
        ):
            if prev_ki.get(key) and not ki.get(key):
                ki[key] = prev_ki[key]

    prev_bugs = previous.get("bugs") or {}
    new_bugs = merged.setdefault("bugs", {})
    prev_cr = prev_bugs.get("customer_reported")
    new_cr = new_bugs.get("customer_reported")
    if prev_cr and prev_cr.get("issues") and not (new_cr or {}).get("issues"):
        new_bugs["customer_reported"] = prev_cr
        if prev_cr.get("count") is not None:
            merged.setdefault("metrics", {})["bugs_customer_reported"] = prev_cr["count"]

    prev_prod = previous.get("production") or {}
    new_prod = merged.setdefault("production", {})
    if prev_prod.get("release_signal") and not new_prod.get("release_signal"):
        new_prod["release_signal"] = prev_prod["release_signal"]
    prev_metrics = previous.get("metrics") or {}
    new_metrics = merged.setdefault("metrics", {})
    if prev_metrics.get("release_date") and not new_metrics.get("release_date"):
        new_metrics["release_date"] = prev_metrics["release_date"]
        new_metrics["released"] = prev_metrics.get("released", new_metrics.get("released"))
        new_metrics["days_in_preprod"] = prev_metrics.get(
            "days_in_preprod", new_metrics.get("days_in_preprod")
        )

    prev_tr = previous.get("test_run") or {}
    new_tr = merged.get("test_run") or {}
    if prev_tr.get("stats") and not (new_tr or {}).get("stats"):
        if new_tr:
            new_tr["stats"] = prev_tr["stats"]
        else:
            merged["test_run"] = prev_tr
        ps = prev_tr["stats"]
        for field, metric_key in (
            ("total", "tests_total"),
            ("executed", "tests_executed"),
            ("passed", "tests_passed"),
            ("failed", "tests_failed"),
            ("skipped", "tests_skipped"),
            ("todo", "tests_todo"),
        ):
            if ps.get(field) is not None and new_metrics.get(metric_key) is None:
                new_metrics[metric_key] = ps[field]
        timing = ps.get("timing") or {}
        for tkey, mkey in (
            ("duration_days", "test_run_duration_days"),
            ("first_status_change", "test_run_first_status_change"),
            ("last_status_change", "test_run_last_status_change"),
        ):
            if timing.get(tkey) and not new_metrics.get(mkey):
                new_metrics[mkey] = timing[tkey]
        qe = ps.get("qa_engineers") or {}
        if qe.get("count") is not None and new_metrics.get("qa_engineers_count") is None:
            new_metrics["qa_engineers_count"] = qe["count"]
        if prev_tr.get("failed_tests") is not None and new_tr.get("failed_tests") is None:
            new_tr["failed_tests"] = prev_tr["failed_tests"]
            if prev_tr.get("failed_tests_source") and not new_tr.get("failed_tests_source"):
                new_tr["failed_tests_source"] = prev_tr["failed_tests_source"]

    return merged


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="Train token, e.g. 8.77")
    parser.add_argument(
        "--previous",
        type=Path,
        help="JSON snapshot before gather (default: data/.preserve/{version}.json)",
    )
    parser.add_argument(
        "--refresh-known-breakdown",
        action="store_true",
        help="Do not restore known_issues.breakdown* from previous file",
    )
    parser.add_argument(
        "--inventory",
        action="store_true",
        help="Print missing enrichments for current file and exit",
    )
    parser.add_argument("--write", action="store_true", help="Write merged JSON back to data/{version}.json")
    args = parser.parse_args()

    path = DATA_DIR / f"{args.version}.json"
    if not path.is_file():
        print(f"Missing {path}", file=sys.stderr)
        return 1

    report = json.loads(path.read_text())
    if args.inventory:
        required, optional = inventory(report)
        if not required and not optional:
            print(f"{args.version}: complete (reference checklist)")
            return 0
        if required:
            print(f"{args.version}: required for canvas / comparison column:")
            for line in required:
                print(f"  - {line}")
        if optional:
            print(f"{args.version}: optional enrichments:")
            for line in optional:
                print(f"  - {line}")
        return 0

    prev_path = args.previous or (DATA_DIR / ".preserve" / f"{args.version}.json")
    if not prev_path.is_file():
        print(f"No previous snapshot at {prev_path}; nothing to merge.", file=sys.stderr)
        return 1

    previous = json.loads(prev_path.read_text())
    merged = merge_enrichments(
        previous,
        report,
        refresh_known_breakdown=args.refresh_known_breakdown,
    )
    if args.write:
        path.write_text(json.dumps(merged, indent=2) + "\n")
        print(f"Merged enrichments into {path}")
    else:
        print(json.dumps(merged, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
