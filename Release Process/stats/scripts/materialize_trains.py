#!/usr/bin/env python3
"""Materialize release-stats JSON from MCP import stubs + Xray enrichment."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "Release Process" / "stats" / "trains_since_2025-10-01.json"
IMPORT_DIR = ROOT / "Release Process" / "stats" / "mcp_import"
DATA_DIR = ROOT / "Release Process" / "stats" / "data"
GATHER_PATH = ROOT / "Release Process" / "stats" / "scripts" / "gather_release_stats.py"


def load_gather():
    spec = importlib.util.spec_from_file_location("gather", GATHER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cloud_pattern(version: str) -> re.Pattern[str]:
    return re.compile(rf"^bigpicture-cloud-{re.escape(version)}\.", re.I)


def build_report(gather, entry: dict, imported: dict, token: str | None) -> dict:
    version = entry["version"]
    cutoff_date = entry["cutoff_date"]
    preprod_name = entry["preprod_name"]
    preprod_id = entry["preprod_id"]
    site = gather.site_url()

    cutoff = {
        "id": preprod_id,
        "name": preprod_name,
        "cutoff_date": cutoff_date,
        "released": bool(entry.get("preprod_released")),
    }
    preprod_versions = [cutoff]

    cloud_versions = imported.get("cloud_versions") or []
    if not cloud_versions:
        cloud_versions = [
            item
            for item in imported.get("cloud_versions_raw") or []
            if cloud_pattern(version).match(item.get("name") or "")
        ]
    for item in cloud_versions:
        item.setdefault("url", f"{site}/projects/ONE/versions/{item.get('id')}")

    released = [item for item in cloud_versions if item.get("released") and item.get("release_date")]
    first = min(released, key=lambda item: item["release_date"]) if released else None

    execution = imported.get("execution") or {}
    exec_key = entry["execution_key"]
    defect_keys = execution.get("defect_keys") or []
    test_run = {
        "key": exec_key,
        "summary": execution.get("summary") or entry.get("execution_summary") or exec_key,
        "status": execution.get("status"),
        "created": execution.get("created"),
        "url": execution.get("url") or gather.browse(exec_key),
        "defect_keys": defect_keys,
        "stats": None,
    }
    if token:
        test_run["stats"] = gather.xray_counts(token, exec_key, test_run.get("created"))

    found = set(defect_keys)
    bugs = []
    for bug in imported.get("bugs") or []:
        bugs.append({
            "key": bug["key"],
            "summary": bug.get("summary"),
            "priority": bug.get("priority") or "None",
            "status": bug.get("status"),
            "created": (bug.get("created") or "")[:10],
            "found_by_test_run": bug["key"] in found,
            "url": bug.get("url") or gather.browse(bug["key"]),
        })
    bugs = gather.supplement_linked_defects(bugs, defect_keys)
    cutoff_bugs = gather.cutoff_scope_bugs(bugs)

    bug_jql = (
        f'issuetype = Bug AND affectedVersion = "{preprod_name}" '
        f'AND created >= "{cutoff_date}" ORDER BY priority DESC, created ASC'
    )
    bug_slices = gather.build_bug_jql_slices(bug_jql, bugs, exec_key, defect_keys)

    priority_order = ["Highest", "High", "Medium", "Low", "Lowest"]
    by_priority: dict[str, int] = {}
    for bug in cutoff_bugs:
        by_priority[bug["priority"]] = by_priority.get(bug["priority"], 0) + 1
    ordered = [name for name in priority_order if name in by_priority]
    ordered += sorted(name for name in by_priority if name not in priority_order)

    stats = test_run.get("stats") or {}
    timing = stats.get("timing") or {}
    notes = []
    if entry.get("execution_note"):
        notes.append(entry["execution_note"])
    if not imported.get("bugs"):
        notes.append(
            "Cut-off bug query returned 0 issues in Jira for this preprod affectedVersion "
            "(only test-run-linked defects are in scope)."
        )

    metrics = {
        "version": version,
        "cutoff_date": cutoff_date,
        "release_date": first["release_date"] if first else None,
        "released": bool(first),
        "days_in_preprod": gather.days_between(cutoff_date, first["release_date"] if first else None),
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
        "bugs_total": len(cutoff_bugs),
        "bugs_found_by_test_run": len(defect_keys),
        "bugs_other_since_cutoff": bug_slices["other"]["count"],
        "bugs_by_priority": {name: by_priority[name] for name in ordered},
    }

    return {
        "schema_version": 1,
        "gathered_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "version": version,
        "site": site,
        "cutoff": cutoff,
        "preprod_versions": preprod_versions,
        "production": {
            "product": "bigpicture-cloud",
            "released": bool(first),
            "first_released": first,
            "versions": cloud_versions,
        },
        "test_run": test_run,
        "test_run_candidates": [],
        "bugs": {
            "jql": bug_jql,
            "url": gather.jql_url(bug_jql),
            "rule": "Affected Version is the preprod version, created on or after the cut-off date.",
            "by_priority": metrics["bugs_by_priority"],
            "found_by_test_run": metrics["bugs_found_by_test_run"],
            "test_run": bug_slices["test_run"],
            "other": bug_slices["other"],
            "issues": bugs,
        },
        "metrics": metrics,
        "notes": notes,
    }


def main() -> int:
    gather = load_gather()
    gather.load_env(gather.ENV_PATH)
    gather.load_env(gather.PRODUCTION_ENV_PATH, override={"XRAY_CLIENT_ID", "XRAY_CLIENT_SECRET"})
    try:
        token = gather.xray_token()
    except RuntimeError as exc:
        print(f"warning: {exc}", file=sys.stderr)
        token = None

    manifest = json.loads(MANIFEST.read_text())
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for entry in manifest:
        version = entry["version"]
        import_path = IMPORT_DIR / f"{version}.json"
        if not import_path.is_file():
            print(f"skip {version}: missing {import_path.relative_to(ROOT)}", file=sys.stderr)
            continue
        imported = json.loads(import_path.read_text())
        report = build_report(gather, entry, imported, token)
        out = DATA_DIR / f"{version}.json"
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        m = report["metrics"]
        print(
            f"{version}: {entry['execution_key']} bugs={m['bugs_total']} "
            f"qa={m.get('qa_engineers_count')} tests={m.get('tests_total')}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
