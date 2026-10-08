"""Load Trinity Importer instance registry and Jira/Xray mapping files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

IMPORTER_ROOT = Path(__file__).resolve().parents[2] / "importer"
INSTANCES_PATH = IMPORTER_ROOT / "config" / "instances.json"
MAPPINGS_DIR = IMPORTER_ROOT / "config" / "mappings"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def list_jira_instances() -> list[dict[str, Any]]:
    data = _load_json(INSTANCES_PATH)
    return list(data.get("instances", []))


def get_jira_instance(instance_id: str) -> dict[str, Any]:
    for row in list_jira_instances():
        if row.get("id") == instance_id:
            return row
    raise KeyError(f"Unknown jira instance: {instance_id}")


def list_mapping_files() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not MAPPINGS_DIR.is_dir():
        return rows
    for path in sorted(MAPPINGS_DIR.glob("*.json")):
        try:
            meta = _load_json(path)
        except json.JSONDecodeError:
            meta = {}
        repo_root = IMPORTER_ROOT.parent.parent
        rows.append(
            {
                "id": path.stem,
                "path": str(path.relative_to(repo_root)),
                "absolute_path": str(path.resolve()),
                "environment": meta.get("environment"),
                "project_key": (meta.get("project") or {}).get("key"),
                "default_folder": (meta.get("defaults") or {}).get("folder_path"),
                "jira_site": (meta.get("jira") or {}).get("site_url"),
            }
        )
    return rows


def resolve_mapping_path(mapping_path: str) -> Path:
    raw = Path(mapping_path)
    if raw.is_absolute():
        path = raw
    else:
        repo_root = IMPORTER_ROOT.parent.parent
        path = (repo_root / raw).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Mapping file not found: {path}")
    return path


def default_mapping_path_for_instance(instance_id: str) -> Path:
    inst = get_jira_instance(instance_id)
    rel = inst.get("default_mapping", "")
    path = (IMPORTER_ROOT / "config" / rel).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Default mapping for {instance_id} not found: {path}")
    return path


def mapping_summary(path: Path) -> dict[str, Any]:
    data = _load_json(path)
    return {
        "path": str(path),
        "version": data.get("version"),
        "environment": data.get("environment"),
        "project_key": (data.get("project") or {}).get("key"),
        "project_id": (data.get("project") or {}).get("id"),
        "default_folder_path": (data.get("defaults") or {}).get("folder_path"),
        "jira_site": (data.get("jira") or {}).get("site_url"),
    }
