"""Derive production release date from test-run bug Done transitions."""

from __future__ import annotations

import re
from datetime import date
from typing import Any

RELEASE_FIX_PRODUCT = "bigpicture-cloud"
DONE_STATUS = "Done"


def cloud_fix_pattern(version: str) -> re.Pattern[str]:
    return re.compile(rf"^{RELEASE_FIX_PRODUCT}-{re.escape(version)}\.")


def qualifying_done_events(
    issue_key: str,
    version: str,
    changelog_values: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return each status→Done while a bigpicture-cloud fix version is on the bug."""
    cloud_re = cloud_fix_pattern(version)
    fix_names: set[str] = set()
    events: list[dict[str, Any]] = []
    ordered = sorted(changelog_values, key=lambda entry: entry.get("created") or "")
    for entry in ordered:
        created = entry.get("created") or ""
        items = [item for item in (entry.get("items") or []) if item]
        for item in items:
            field = item.get("field") or ""
            if field in ("Fix Version", "fixVersions"):
                added = item.get("toString")
                removed = item.get("fromString")
                if added:
                    fix_names.add(added)
                if removed:
                    fix_names.discard(removed)
        for item in items:
            field = item.get("field") or ""
            if field == "status" and item.get("toString") == DONE_STATUS:
                matching = sorted(name for name in fix_names if cloud_re.match(name))
                if matching:
                    events.append({
                        "issue_key": issue_key,
                        "done_at": created[:10],
                        "done_at_iso": created,
                        "fix_versions": matching,
                        "url": f"https://appfire.atlassian.net/browse/{issue_key}",
                    })
    return events


def build_release_signal(
    version: str,
    defect_keys: list[str],
    changelogs_by_key: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    cloud_re = cloud_fix_pattern(version)
    all_events: list[dict[str, Any]] = []
    for key in defect_keys:
        values = changelogs_by_key.get(key) or []
        all_events.extend(qualifying_done_events(key, version, values))

    rule = (
        f"Earliest date a test-run-linked bug reached status {DONE_STATUS!r} "
        f"while Fix Version included {RELEASE_FIX_PRODUCT}-{version}.* "
        f"(changelog replay; status name must be exactly Done)."
    )
    if not all_events:
        return {
            "released": False,
            "release_date": None,
            "release_date_last": None,
            "trigger_issue": None,
            "qualifying_events": [],
            "rule": rule,
            "fix_version_pattern": cloud_re.pattern,
        }

    latest = max(all_events, key=lambda event: event["done_at_iso"])
    earliest = min(all_events, key=lambda event: event["done_at_iso"])
    return {
        "released": True,
        "release_date": earliest["done_at"],
        "release_date_last": latest["done_at"],
        "trigger_issue": earliest["issue_key"],
        "trigger_url": earliest["url"],
        "trigger_fix_versions": earliest["fix_versions"],
        "latest_issue": latest["issue_key"],
        "latest_url": latest["url"],
        "qualifying_events": all_events,
        "rule": rule,
        "fix_version_pattern": cloud_re.pattern,
    }


def earliest_cloud_fix_date(production: dict[str, Any], version: str) -> str | None:
    """Earliest Jira releaseDate on bigpicture-cloud-{version}.* (even if unreleased flag)."""
    cloud_re = cloud_fix_pattern(version)
    dated: list[str] = []
    for item in production.get("versions") or []:
        name = item.get("name") or ""
        if not cloud_re.match(name):
            continue
        raw = item.get("release_date")
        if raw:
            dated.append(str(raw)[:10])
    return min(dated) if dated else None


def apply_release_signal(report: dict[str, Any], signal: dict[str, Any]) -> None:
    """Apply changelog-derived signal; fall back to cloud fix-version dates."""
    production = report.get("production") or {}
    first = production.get("first_released") or {}
    version = report.get("version") or ""

    if not signal.get("released"):
        release_date = first.get("release_date") or earliest_cloud_fix_date(production, version)
        if release_date:
            signal = {
                **signal,
                "released": True,
                "release_date": release_date,
                "release_date_last": signal.get("release_date_last") or release_date,
                "release_date_source": (
                    "jira_first_released_cloud_fix"
                    if first.get("release_date")
                    else "jira_cloud_fix_version_release_date"
                ),
            }
            if not production.get("released"):
                production["released"] = True
                report["production"] = production

    report["production"]["release_signal"] = signal
    cutoff = report["metrics"].get("cutoff_date")
    release_date = signal.get("release_date")
    report["metrics"]["released"] = bool(signal.get("released"))
    report["metrics"]["release_date"] = release_date
    report["metrics"]["release_date_last"] = signal.get("release_date_last")
    report["metrics"]["days_in_preprod"] = None
    if cutoff and release_date:
        report["metrics"]["days_in_preprod"] = (
            date.fromisoformat(release_date) - date.fromisoformat(cutoff)
        ).days
