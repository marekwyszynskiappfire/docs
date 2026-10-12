"""Creator product config → Importer defaults (RQ-01 / CQ-03)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CONFIG_DIR = Path(__file__).resolve().parents[2] / "creator" / "config"


def load_creator_product_config(product_id: str | None) -> dict[str, Any]:
    pid = (product_id or "default").strip() or "default"
    path = CONFIG_DIR / f"{pid}.json"
    if not path.is_file():
        path = CONFIG_DIR / "default.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _first_requirement_key(handoff: dict[str, Any]) -> str | None:
    for test in handoff.get("tests") or []:
        keys = test.get("linked_requirement_keys") or []
        if keys:
            return str(keys[0])
    return None


def resolve_folder_template(template: str, requirement_key: str | None) -> str:
    key = requirement_key or "UNKNOWN"
    return template.replace("{requirement_key}", key).replace("{jira_key}", key)


def importer_defaults_for_handoff(handoff: dict[str, Any]) -> dict[str, Any]:
    product_id = handoff.get("product_id")
    cfg = load_creator_product_config(product_id)
    imp = cfg.get("importer") or {}
    req_key = _first_requirement_key(handoff)
    folder_template = imp.get("default_folder_template") or "/TC Importer/{requirement_key}"
    return {
        "product_id": cfg.get("product", {}).get("id") or product_id or "default",
        "default_jira_project_key": imp.get("default_jira_project_key") or "TC",
        "default_folder_template": folder_template,
        "suggested_folder_path": resolve_folder_template(folder_template, req_key),
        "default_mapping_id": imp.get("default_mapping_id"),
        "primary_requirement_key": req_key,
        "config_path": str(CONFIG_DIR / f"{cfg.get('product', {}).get('id', 'default')}.json"),
    }
