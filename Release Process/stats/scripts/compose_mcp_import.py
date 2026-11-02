#!/usr/bin/env python3
"""Compose mcp_import/{version}.json from MCP JSON snapshots under mcp_import/_fetch/."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
FETCH = ROOT / "Release Process" / "stats" / "mcp_import" / "_fetch"
OUT = ROOT / "Release Process" / "stats" / "mcp_import"
SITE = "https://appfire.atlassian.net"


def defect_keys(issuelinks: list[dict] | None) -> list[str]:
    keys: list[str] = []
    for link in issuelinks or []:
        if (link.get("type") or {}).get("name") != "Defect":
            continue
        for side in ("outwardIssue", "inwardIssue"):
            issue = link.get(side)
            if issue and issue.get("key"):
                keys.append(issue["key"])
    return keys


def execution_from_issue(issue: dict, exec_key: str) -> dict:
    fields = issue.get("fields") or {}
    status = fields.get("status") or {}
    return {
        "summary": fields.get("summary"),
        "status": status.get("name") if isinstance(status, dict) else status,
        "created": fields.get("created"),
        "url": f"{SITE}/browse/{exec_key}",
        "defect_keys": defect_keys(fields.get("issuelinks")),
    }


def map_bug(issue: dict) -> dict:
    key = issue["key"]
    fields = issue.get("fields") or {}
    priority = fields.get("priority") or {}
    status = fields.get("status") or {}
    created = fields.get("created") or ""
    return {
        "key": key,
        "summary": fields.get("summary"),
        "priority": priority.get("name") if isinstance(priority, dict) else priority or "None",
        "status": status.get("name") if isinstance(status, dict) else status,
        "created": created[:10] if created else "",
        "url": f"{SITE}/browse/{key}",
    }


def map_cloud(item: dict) -> dict:
    return {
        "id": str(item["id"]),
        "name": item["name"],
        "released": bool(item.get("released")),
        "release_date": item.get("releaseDate") or None,
    }


def load_bugs(version_dir: Path) -> list[dict]:
    merged_path = version_dir / "bugs_merged.json"
    if merged_path.is_file():
        data = json.loads(merged_path.read_text())
        if isinstance(data, list) and data and "url" in data[0]:
            return data
    bugs_path = version_dir / "bugs.json"
    if bugs_path.is_file():
        data = json.loads(bugs_path.read_text())
        if isinstance(data, list):
            if data and "url" in data[0]:
                return data
            return [map_bug(i) for i in data]
        issues = data.get("issues") if isinstance(data, dict) else None
        if issues is not None:
            return [map_bug(i) for i in issues]
    merged: list[dict] = []
    for path in sorted(version_dir.glob("bugs_page_*.json")):
        page = json.loads(path.read_text())
        issues = page.get("issues") if isinstance(page, dict) else page
        if not isinstance(issues, list):
            continue
        merged.extend(map_bug(i) for i in issues)
    return merged


def compose(version: str, exec_key: str) -> dict:
    version_dir = FETCH / version
    meta_path = version_dir / "execution_meta.json"
    if meta_path.is_file():
        execution = json.loads(meta_path.read_text())
    else:
        exec_raw = json.loads((version_dir / "execution.json").read_text())
        issue = exec_raw.get("data") or exec_raw
        execution = execution_from_issue(issue, exec_key)
    cloud_raw = json.loads((version_dir / "cloud.json").read_text())
    cloud_data = cloud_raw.get("data") or cloud_raw
    values = cloud_data.get("values") or []
    return {
        "execution": execution,
        "bugs": load_bugs(version_dir),
        "cloud_versions": [map_cloud(v) for v in values],
    }


def main() -> int:
    manifest_path = ROOT / "Release Process" / "stats" / "trains_since_2025-10-01.json"
    manifest = {e["version"]: e for e in json.loads(manifest_path.read_text())}
    versions = sys.argv[1:] or [f"8.{i}" for i in range(62, 74)]
    OUT.mkdir(parents=True, exist_ok=True)
    ok: list[str] = []
    failures: list[str] = []
    for version in versions:
        entry = manifest.get(version)
        if not entry:
            failures.append(f"{version}: not in manifest")
            continue
        version_dir = FETCH / version
        if not (version_dir / "execution.json").is_file() and not (
            version_dir / "execution_meta.json"
        ).is_file():
            failures.append(f"{version}: missing _fetch/{version}/execution.json")
            continue
        try:
            payload = compose(version, entry["execution_key"])
            (OUT / f"{version}.json").write_text(
                json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
            )
            ok.append(
                f"{version}: bugs={len(payload['bugs'])} "
                f"defects={len(payload['execution']['defect_keys'])} "
                f"cloud={len(payload['cloud_versions'])}"
            )
        except Exception as exc:
            failures.append(f"{version}: {exc}")
    for line in ok:
        print(line)
    for line in failures:
        print(f"FAIL {line}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
