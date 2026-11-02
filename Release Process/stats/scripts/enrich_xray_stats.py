#!/usr/bin/env python3
"""Fill Xray test-run stats into existing Release Process/stats/data/*.json."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "Release Process" / "stats" / "data"
GATHER_PATH = ROOT / "Release Process" / "stats" / "scripts" / "gather_release_stats.py"
XRAY_NOTE_PREFIX = "Test-run counts were not loaded"


def load_gather():
    spec = importlib.util.spec_from_file_location("gather", GATHER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sync_metrics(report: dict) -> None:
    stats = (report.get("test_run") or {}).get("stats") or {}
    timing = stats.get("timing") or {}
    report["metrics"].update({
        "tests_total": stats.get("total"),
        "tests_executed": stats.get("executed"),
        "tests_passed": stats.get("passed"),
        "tests_failed": stats.get("failed"),
        "tests_skipped": stats.get("skipped"),
        "tests_todo": stats.get("todo"),
        "test_run_duration_days": timing.get("duration_days"),
        "test_run_first_status_change": timing.get("first_status_change"),
        "test_run_last_status_change": timing.get("last_status_change"),
        "qa_engineers_count": (stats.get("qa_engineers") or {}).get("count"),
    })


def enrich_report(report: dict, token: str, execution_key: str | None) -> None:
    gather = load_gather()
    if execution_key and report.get("test_run_candidates"):
        match = next((c for c in report["test_run_candidates"] if c["key"] == execution_key), None)
        if match:
            match["stats"] = gather.xray_counts(token, match["key"], match.get("created"))
            match["failed_tests"] = gather.xray_failed_tests(token, match["key"])
            match["failed_tests_source"] = (
                "getTestExecution.testRuns latest status per test (FAILED/FAIL)"
            )
            report["test_run"] = match
            report["test_run_candidates"] = [
                c for c in report["test_run_candidates"] if c["key"] != execution_key
            ]
            found = set(match.get("defect_keys") or [])
            for bug in report["bugs"]["issues"]:
                bug["found_by_test_run"] = bug["key"] in found
            report["metrics"]["bugs_found_by_test_run"] = len(found)
            report["bugs"]["found_by_test_run"] = report["metrics"]["bugs_found_by_test_run"]
            report["notes"] = [
                n for n in report.get("notes") or []
                if "Several Major Release Test Runs" not in n
            ]
            report["notes"].append(f"Test run selected with --execution {execution_key}.")

    run = report.get("test_run")
    if run and run.get("key"):
        run["stats"] = gather.xray_counts(token, run["key"], run.get("created"))
        run["failed_tests"] = gather.xray_failed_tests(token, run["key"])
        run["failed_tests_source"] = "getTestExecution.testRuns latest status per test (FAILED/FAIL)"
        sync_metrics(report)

    for cand in report.get("test_run_candidates") or []:
        if cand.get("key"):
            cand["stats"] = gather.xray_counts(token, cand["key"], cand.get("created"))

    report["notes"] = [
        n for n in report.get("notes") or []
        if not n.startswith(XRAY_NOTE_PREFIX)
    ]
    report["gathered_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    _sync_bug_jql_slices(report, gather)


def _sync_bug_jql_slices(report: dict, gather) -> None:
    bugs_block = report.get("bugs") or {}
    base = bugs_block.get("jql")
    issues = bugs_block.get("issues") or []
    run = report.get("test_run") or {}
    slices = gather.build_bug_jql_slices(
        base,
        issues,
        run.get("key"),
        run.get("defect_keys"),
    )
    bugs_block["test_run"] = slices["test_run"]
    bugs_block["other"] = slices["other"]
    report["metrics"]["bugs_found_by_test_run"] = slices["test_run"]["count"]
    report["metrics"]["bugs_other_since_cutoff"] = slices["other"]["count"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("versions", nargs="*", help="Versions to enrich (default: all JSON in data/)")
    parser.add_argument("--execution", action="append", default=[], metavar="VERSION=KEY")
    args = parser.parse_args()
    overrides = {}
    for item in args.execution:
        if "=" not in item:
            raise SystemExit(f"--execution must look like 8.75=TC-6504, got {item}")
        version, key = item.split("=", 1)
        overrides[version] = key

    gather = load_gather()
    gather.load_env(gather.ENV_PATH)
    gather.load_env(gather.PRODUCTION_ENV_PATH, override={"XRAY_CLIENT_ID", "XRAY_CLIENT_SECRET"})
    token = gather.xray_token()

    paths = sorted(DATA_DIR.glob("*.json"))
    if args.versions:
        paths = [DATA_DIR / f"{v}.json" for v in args.versions]
    for path in paths:
        if not path.is_file():
            print(f"skip missing {path.name}", file=sys.stderr)
            continue
        report = json.loads(path.read_text())
        version = report.get("version") or path.stem
        enrich_report(report, token, overrides.get(version))
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        m = report["metrics"]
        key = (report.get("test_run") or {}).get("key") or "NONE"
        print(
            f"{version}: {key} tests={m.get('tests_total')} "
            f"passed={m.get('tests_passed')} failed={m.get('tests_failed')} skipped={m.get('tests_skipped')}"
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
