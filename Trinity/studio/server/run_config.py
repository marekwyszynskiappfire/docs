"""Portfolio run configs under Trinity/reviewer/config/runs/."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone

import httpx
from pathlib import Path
from typing import Any

from personas import docs_repo_root

import sys

_REVIEWER_SCRIPTS = docs_repo_root() / "Trinity" / "reviewer" / "scripts"
if str(_REVIEWER_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_REVIEWER_SCRIPTS))

from scope_utils import (  # noqa: E402
    new_epics_for_config,
    parse_pasted_keys,
    resolve_scope_inline,
)

PORTFOLIO_ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{2,127}$")


def runs_config_dir() -> Path:
    return docs_repo_root() / "Trinity" / "reviewer" / "config" / "runs"


def schema_path() -> Path:
    return docs_repo_root() / "Trinity" / "reviewer" / "schemas" / "run-config.schema.json"


def validate_portfolio_id(portfolio_id: str) -> str:
    if not portfolio_id or portfolio_id != Path(portfolio_id).name:
        raise ValueError("Invalid portfolio_id")
    if ".." in portfolio_id or "/" in portfolio_id:
        raise ValueError("Invalid portfolio_id")
    if not PORTFOLIO_ID_RE.match(portfolio_id):
        raise ValueError(
            "portfolio_id must be 3–128 chars: letters, numbers, dot, underscore, hyphen"
        )
    return portfolio_id


def _load_schema() -> dict[str, Any]:
    with schema_path().open(encoding="utf-8") as f:
        return json.load(f)


def validate_run_config(data: dict[str, Any]) -> None:
    try:
        import jsonschema
        from jsonschema import ValidationError
    except ImportError as e:
        raise RuntimeError("jsonschema package required; pip install jsonschema") from e
    schema = _load_schema()
    try:
        jsonschema.Draft202012Validator(schema).validate(data)
    except ValidationError as e:
        raise ValueError(f"Schema validation failed: {e.message}") from e


def list_run_configs() -> list[dict[str, Any]]:
    root = runs_config_dir()
    if not root.is_dir():
        return []
    items: list[dict[str, Any]] = []
    for path in sorted(root.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            items.append(
                {
                    "portfolio_id": path.stem,
                    "label": path.stem,
                    "invalid": True,
                }
            )
            continue
        items.append(
            {
                "portfolio_id": data.get("portfolio_id") or path.stem,
                "label": data.get("label") or path.stem,
                "updated_at": data.get("updated_at"),
            }
        )
    return items


def list_new_epics(portfolio_id: str) -> dict[str, Any]:
    config = read_run_config(portfolio_id)
    return new_epics_for_config(config, docs_repo_root())


def apply_resolved_keys(
    portfolio_id: str, keys: list[str], source: str = "paste"
) -> dict[str, Any]:
    config = read_run_config(portfolio_id)
    config["resolved_epic_keys"] = keys
    config["resolved_source"] = source
    config["resolved_at"] = (
        datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    )
    return write_run_config(portfolio_id, config)


def paste_resolved_keys(portfolio_id: str, keys_text: str) -> dict[str, Any]:
    keys, note = parse_pasted_keys(keys_text)
    if not keys:
        raise ValueError(note or "No keys parsed")
    out = apply_resolved_keys(portfolio_id, keys, source="paste")
    if note:
        out["_warning"] = note
    return out


def resolve_scope_attempt(portfolio_id: str) -> dict[str, Any]:
    from jira_resolve_prompt import (
        build_cursor_resolve_prompt,
        jira_env_configured,
        try_jira_rest_resolve,
    )

    config = read_run_config(portfolio_id)
    scope_kind = (config.get("scope") or {}).get("kind")

    keys, err = resolve_scope_inline(config)
    if keys:
        out = apply_resolved_keys(portfolio_id, keys, source="scope_inline")
        return {"status": "resolved", "config": out}

    if scope_kind in ("jql", "filter_url") and jira_env_configured():
        try:
            keys, warn = try_jira_rest_resolve(config)
            if keys:
                out = apply_resolved_keys(portfolio_id, keys, source="jira_rest")
                resp: dict[str, Any] = {"status": "resolved", "config": out}
                if warn:
                    resp["warning"] = warn
                return resp
        except (ValueError, OSError, httpx.HTTPError) as e:
            return {
                "status": "cursor",
                "prompt": build_cursor_resolve_prompt(config),
                "message": f"Jira REST failed: {e}. Use Cursor MCP or fix .env.",
            }

    return {
        "status": "cursor",
        "prompt": build_cursor_resolve_prompt(config),
        "message": err or "Resolve epic keys in Cursor, then paste in Studio.",
    }


def resolve_scope_prompt(portfolio_id: str) -> dict[str, str]:
    from jira_resolve_prompt import build_cursor_resolve_prompt

    config = read_run_config(portfolio_id)
    return {"prompt": build_cursor_resolve_prompt(config)}


def read_run_config(portfolio_id: str) -> dict[str, Any]:
    pid = validate_portfolio_id(portfolio_id)
    path = runs_config_dir() / f"{pid}.json"
    if not path.is_file():
        raise FileNotFoundError(pid)
    data = json.loads(path.read_text(encoding="utf-8"))
    return data


def write_run_config(portfolio_id: str, data: dict[str, Any]) -> dict[str, Any]:
    pid = validate_portfolio_id(portfolio_id)
    if data.get("portfolio_id") and data["portfolio_id"] != pid:
        raise ValueError("portfolio_id in body must match URL")
    data = dict(data)
    data["portfolio_id"] = pid
    data.setdefault("config_version", "1.0")
    data.setdefault("planning_dates", "jira_due_then_end")
    data.setdefault("artifacts_dir", "Trinity/reviewer/runs")
    data.setdefault("jira_comment_policy", "generate_review_before_post")
    data.setdefault("creator_handoff_exclude_not_fit", True)

    root = runs_config_dir()
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{pid}.json"
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    if path.is_file():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
            data.setdefault("created_at", existing.get("created_at") or now)
        except json.JSONDecodeError:
            data.setdefault("created_at", now)
    else:
        data.setdefault("created_at", now)
    data["updated_at"] = now

    validate_run_config(data)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return data
