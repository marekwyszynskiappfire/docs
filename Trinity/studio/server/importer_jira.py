"""Jira project discovery for Importer target selection."""

from __future__ import annotations

import json
import os
from typing import Any

import httpx

from importer_registry import default_mapping_path_for_instance, get_jira_instance, resolve_mapping_path


def jira_site_for_instance(instance_id: str, mapping_path: str | None) -> str:
    inst = get_jira_instance(instance_id)
    path = resolve_mapping_path(mapping_path) if mapping_path else default_mapping_path_for_instance(instance_id)
    cfg = json.loads(path.read_text(encoding="utf-8"))
    site = (cfg.get("jira") or {}).get("site_url") or inst.get("jira_site") or ""
    return site.rstrip("/")


def list_jira_projects(
    instance_id: str,
    *,
    mapping_path: str | None = None,
    query: str = "",
    max_results: int = 50,
) -> dict[str, Any]:
    email = os.environ.get("JIRA_EMAIL", "").strip()
    token = os.environ.get("JIRA_API_TOKEN", "").strip()
    if not email or not token:
        return {
            "status": "credentials_missing",
            "projects": [],
            "message": "Set JIRA_EMAIL and JIRA_API_TOKEN in Trinity/studio/.env",
        }
    base = jira_site_for_instance(instance_id, mapping_path)
    if not base:
        return {"status": "error", "projects": [], "message": "No Jira site URL for instance"}

    params: dict[str, Any] = {"maxResults": min(max_results, 100)}
    if query.strip():
        params["query"] = query.strip()
    url = f"{base}/rest/api/3/project/search"
    try:
        resp = httpx.get(url, params=params, auth=(email, token), timeout=45.0)
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as exc:
        return {"status": "error", "projects": [], "message": str(exc)}

    projects = [
        {
            "key": row.get("key"),
            "id": row.get("id"),
            "name": row.get("name"),
            "projectTypeKey": row.get("projectTypeKey"),
        }
        for row in data.get("values", [])
        if row.get("key")
    ]
    return {
        "status": "ok",
        "jira_site": base,
        "projects": projects,
        "total": data.get("total", len(projects)),
    }


def resolve_project_by_key(
    instance_id: str,
    project_key: str,
    *,
    mapping_path: str | None = None,
) -> dict[str, Any]:
    """Resolve numeric Jira project id for a key (IQ-01)."""
    key = project_key.strip().upper()
    if not key:
        return {"status": "error", "message": "Empty project key"}

    email = os.environ.get("JIRA_EMAIL", "").strip()
    token = os.environ.get("JIRA_API_TOKEN", "").strip()
    if not email or not token:
        return {
            "status": "credentials_missing",
            "message": "Set JIRA_EMAIL and JIRA_API_TOKEN in Trinity/studio/.env",
        }

    base = jira_site_for_instance(instance_id, mapping_path)
    url = f"{base}/rest/api/3/project/{key}"
    try:
        resp = httpx.get(url, auth=(email, token), timeout=45.0)
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as exc:
        return {"status": "error", "message": str(exc), "project_key": key}

    map_path = resolve_mapping_path(mapping_path) if mapping_path else default_mapping_path_for_instance(
        instance_id
    )
    cfg = json.loads(map_path.read_text(encoding="utf-8"))
    mapping_id = (cfg.get("project") or {}).get("id")
    resolved_id = str(data.get("id") or "")
    conflict = bool(mapping_id and resolved_id and str(mapping_id) != resolved_id)

    return {
        "status": "ok",
        "project_key": data.get("key") or key,
        "project_id": resolved_id,
        "project_name": data.get("name"),
        "mapping_file_project_id": str(mapping_id) if mapping_id else None,
        "mapping_conflict": conflict,
        "jira_site": base,
    }
