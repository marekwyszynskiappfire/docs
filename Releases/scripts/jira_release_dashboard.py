#!/usr/bin/env python3
"""Create or update a Jira release dashboard from a JSON manifest.

Dry-run is the default. Pass --execute to write to Jira.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

FILTER_RESULTS_URI = (
    "rest/gadgets/1.0/g/com.atlassian.jira.gadgets:"
    "filter-results-gadget/gadgets/filter-results-gadget.xml"
)


def load_env(path: Path | None) -> None:
    if not path:
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key, value.strip().strip("\"'"))


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def validate_manifest(data: dict[str, Any]) -> None:
    dashboard = data.get("dashboard")
    releases = data.get("releases")
    if not isinstance(dashboard, dict) or not dashboard.get("name"):
        raise ValueError("dashboard.name is required")
    if not isinstance(releases, list) or not releases:
        raise ValueError("releases must be a non-empty array")

    seen_versions: set[str] = set()
    seen_filters: set[str] = set()
    for index, release in enumerate(releases):
        if not isinstance(release, dict):
            raise ValueError(f"releases[{index}] must be an object")
        required = ("version", "test_execution_key", "filter_name", "gadget_title", "jql")
        missing = [key for key in required if not release.get(key)]
        if missing:
            raise ValueError(f"releases[{index}] missing: {', '.join(missing)}")
        version = str(release["version"])
        if version in seen_versions:
            raise ValueError(f"duplicate release version: {version}")
        seen_versions.add(version)
        filter_name = str(release["filter_name"])
        if filter_name in seen_filters:
            raise ValueError(f"duplicate filter name: {filter_name}")
        seen_filters.add(filter_name)
        if release.get("xray_execution_verified") is not True:
            raise ValueError(
                f"{version}: xray_execution_verified must be true before dashboard creation"
            )


class Jira:
    def __init__(self, base_url: str, email: str, token: str, insecure: bool = False):
        self.base_url = base_url.rstrip("/")
        basic = base64.b64encode(f"{email}:{token}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {basic}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self.context = ssl._create_unverified_context() if insecure else ssl.create_default_context()

    def request(
        self, method: str, endpoint: str, body: dict[str, Any] | None = None
    ) -> Any:
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(
            f"{self.base_url}{endpoint}",
            data=data,
            headers=self.headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(request, context=self.context, timeout=60) as response:
                raw = response.read().decode()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as error:
            detail = error.read().decode(errors="replace")
            raise RuntimeError(
                f"{method} {endpoint} failed ({error.code}): {detail[:1000]}"
            ) from error

    def search_filters(self, name: str) -> list[dict[str, Any]]:
        query = urllib.parse.urlencode(
            {"filterName": name, "expand": "jql,owner,description", "maxResults": 100}
        )
        result = self.request("GET", f"/rest/api/3/filter/search?{query}")
        return [
            item
            for item in (result or {}).get("values", [])
            if item.get("name") == name
        ]

    def search_dashboards(self, name: str) -> list[dict[str, Any]]:
        query = urllib.parse.urlencode({"dashboardName": name, "maxResults": 100})
        result = self.request("GET", f"/rest/api/3/dashboard/search?{query}")
        return [
            item
            for item in (result or {}).get("values", [])
            if item.get("name") == name
        ]


def one_exact(items: list[dict[str, Any]], object_name: str) -> dict[str, Any] | None:
    if len(items) > 1:
        ids = ", ".join(str(item.get("id")) for item in items)
        raise RuntimeError(f"multiple exact-name {object_name} objects found: {ids}")
    return items[0] if items else None


def ensure_filter(
    jira: Jira,
    release: dict[str, Any],
    state_entry: dict[str, Any],
    share: str,
) -> str:
    filter_id = state_entry.get("filter_id")
    existing = None
    if filter_id:
        existing = jira.request("GET", f"/rest/api/3/filter/{filter_id}")
    else:
        existing = one_exact(
            jira.search_filters(str(release["filter_name"])), "filter"
        )
        filter_id = existing.get("id") if existing else None

    payload = {
        "name": release["filter_name"],
        "description": release.get(
            "filter_description",
            f"Bugs for {release['test_execution_key']} release {release['version']}.",
        ),
        "jql": release["jql"],
        "favourite": False,
    }
    if filter_id:
        result = jira.request("PUT", f"/rest/api/3/filter/{filter_id}", payload)
    else:
        result = jira.request("POST", "/rest/api/3/filter", payload)
        filter_id = result["id"]

    permissions = jira.request("GET", f"/rest/api/3/filter/{filter_id}/permission") or []
    shared = any(item.get("type") in {"loggedin", "authenticated"} for item in permissions)
    if share == "authenticated" and not shared:
        jira.request(
            "POST",
            f"/rest/api/3/filter/{filter_id}/permission",
            {"type": "authenticated"},
        )
    return str(filter_id)


def ensure_dashboard(
    jira: Jira, config: dict[str, Any], state: dict[str, Any]
) -> str:
    dashboard_id = state.get("dashboard_id")
    if dashboard_id:
        jira.request("GET", f"/rest/api/3/dashboard/{dashboard_id}")
    else:
        existing = one_exact(
            jira.search_dashboards(str(config["name"])), "dashboard"
        )
        dashboard_id = existing.get("id") if existing else None

    payload = {
        "name": config["name"],
        "description": config.get("description", ""),
        "sharePermissions": [{"type": "authenticated"}]
        if config.get("share", "authenticated") == "authenticated"
        else [],
    }
    if dashboard_id:
        jira.request("PUT", f"/rest/api/3/dashboard/{dashboard_id}", payload)
    else:
        result = jira.request("POST", "/rest/api/3/dashboard", payload)
        dashboard_id = result["id"]
    return str(dashboard_id)


def ensure_gadget(
    jira: Jira,
    dashboard_id: str,
    release: dict[str, Any],
    filter_id: str,
    state_entry: dict[str, Any],
    index: int,
    dashboard_columns: int,
    gadget_defaults: dict[str, Any],
) -> str:
    gadget_id = state_entry.get("gadget_id")
    gadgets = (
        jira.request("GET", f"/rest/api/3/dashboard/{dashboard_id}/gadget") or {}
    ).get("gadgets", [])
    if gadget_id and not any(str(item.get("id")) == str(gadget_id) for item in gadgets):
        gadget_id = None
    if not gadget_id:
        matches = [
            item for item in gadgets if item.get("title") == release["gadget_title"]
        ]
        existing = one_exact(matches, "gadget")
        gadget_id = existing.get("id") if existing else None

    position = {
        "column": index % dashboard_columns,
        "row": index // dashboard_columns,
    }
    gadget_payload = {
        "title": release["gadget_title"],
        "color": release.get("color", "blue"),
        "position": position,
    }
    if gadget_id:
        jira.request(
            "PUT",
            f"/rest/api/3/dashboard/{dashboard_id}/gadget/{gadget_id}",
            gadget_payload,
        )
    else:
        result = jira.request(
            "POST",
            f"/rest/api/3/dashboard/{dashboard_id}/gadget",
            {**gadget_payload, "uri": FILTER_RESULTS_URI},
        )
        gadget_id = result["id"]

    columns = gadget_defaults.get(
        "columns",
        ["issuetype", "issuekey", "summary", "priority", "status", "assignee"],
    )
    config = {
        "filterId": str(filter_id),
        "num": str(gadget_defaults.get("max_results", 20)),
        "columnNames": "|".join(columns),
        "refresh": str(gadget_defaults.get("refresh", False)).lower(),
        "isConfigured": "true",
    }
    jira.request(
        "PUT",
        f"/rest/api/3/dashboard/{dashboard_id}/items/{gadget_id}/properties/config",
        config,
    )
    return str(gadget_id)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--state", type=Path)
    args = parser.parse_args()

    manifest = load_json(args.manifest)
    validate_manifest(manifest)
    state_path = args.state or args.manifest.with_name("dashboard-state.json")
    state = load_json(state_path) if state_path.exists() else {"releases": {}}

    print(f"Dashboard: {manifest['dashboard']['name']}")
    print(f"Mode: {'EXECUTE' if args.execute else 'DRY RUN'}")
    for release in manifest["releases"]:
        print(
            f"- {release['version']}: {release['test_execution_key']} "
            f"-> {release['filter_name']}"
        )
    if not args.execute:
        print("No Jira changes made. Re-run with --execute.")
        return 0

    load_env(args.env_file)
    required = ("JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN")
    missing = [key for key in required if not os.environ.get(key)]
    if missing:
        raise RuntimeError(f"missing environment variables: {', '.join(missing)}")

    jira = Jira(
        os.environ["JIRA_BASE_URL"],
        os.environ["JIRA_EMAIL"],
        os.environ["JIRA_API_TOKEN"],
        os.environ.get("JIRA_INSECURE_SSL") == "1",
    )
    dashboard = manifest["dashboard"]
    dashboard_id = ensure_dashboard(jira, dashboard, state)
    state["dashboard_id"] = dashboard_id
    state["dashboard_url"] = f"{jira.base_url}/jira/dashboards/{dashboard_id}"
    releases_state = state.setdefault("releases", {})

    for index, release in enumerate(manifest["releases"]):
        version = str(release["version"])
        entry = releases_state.setdefault(version, {})
        filter_id = ensure_filter(
            jira, release, entry, dashboard.get("share", "authenticated")
        )
        entry["filter_id"] = filter_id
        gadget_id = ensure_gadget(
            jira,
            dashboard_id,
            release,
            filter_id,
            entry,
            index,
            int(dashboard.get("columns", 2)),
            manifest.get("gadget", {}),
        )
        entry.update(
            {
                "gadget_id": gadget_id,
                "test_execution_key": release["test_execution_key"],
                "filter_url": f"{jira.base_url}/issues/?filter={filter_id}",
            }
        )
        state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        print(f"Updated {version}: filter={filter_id}, gadget={gadget_id}")

    print(f"Dashboard: {state['dashboard_url']}")
    print(f"State: {state_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
