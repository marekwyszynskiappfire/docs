"""Batch Xray import execute from Studio (IQ-10)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parents[2] / "importer" / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from xray_graphql_import import (  # noqa: E402
    authenticate,
    execute_create_folder,
    execute_single_test_import,
    load_config,
    normalize_folder_path,
)

from importer_plan import handoff_to_batch
from importer_registry import resolve_mapping_path


def config_from_plan(plan: dict[str, Any], mapping_path: str) -> dict[str, Any]:
    cfg = json.loads(json.dumps(load_config(resolve_mapping_path(mapping_path))))
    resolution = plan.get("project_resolution") or {}
    if resolution.get("project_id"):
        cfg.setdefault("project", {})["id"] = resolution["project_id"]
    if plan.get("project_key"):
        cfg.setdefault("project", {})["key"] = plan["project_key"]
    return cfg


def run_batch_execute(
    *,
    plan: dict[str, Any],
    handoff: dict[str, Any],
    batch_path: Path,
    mapping_path: str,
    skip_requirement_link: bool,
) -> dict[str, Any]:
    config = config_from_plan(plan, mapping_path)
    batch = handoff_to_batch(handoff)
    batch["run_id"] = batch.get("run_id") or handoff.get("creator_run_id")
    batch_path.parent.mkdir(parents=True, exist_ok=True)
    batch_path.write_text(json.dumps(batch, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    project_key = plan["project_key"]
    folder_path = normalize_folder_path(plan["target"]["folder_path"])
    run_dir = batch_path.parent / "xray-import-run"
    run_dir.mkdir(parents=True, exist_ok=True)

    draft_ids = [
        t["draft_id"]
        for t in plan.get("tests") or []
        if not t.get("validation_errors")
    ]
    if not draft_ids:
        return {
            "status": "failed",
            "message": "No valid tests in plan",
            "results": [],
            "report_dir": str(run_dir),
        }

    token = authenticate(config)
    folder_response: dict[str, Any] | None = None
    if plan.get("target", {}).get("create_folder_if_missing"):
        folder_response = execute_create_folder(config, folder_path, token)

    results: list[dict[str, Any]] = []
    for draft_id in draft_ids:
        safe_id = re.sub(r"[^\w-]", "_", draft_id)
        out_dir = run_dir / f"xray-import-{safe_id}"
        report = execute_single_test_import(
            config=config,
            batch=batch,
            draft_id=draft_id,
            project_key=project_key,
            folder_path=folder_path,
            output_dir=out_dir,
            skip_requirement_link=skip_requirement_link,
            token=token,
        )
        results.append(
            {
                "draft_id": draft_id,
                "action": report.get("action"),
                "xray_key": report.get("xray_key"),
                "errors": report.get("errors"),
                "report_dir": str(out_dir),
            }
        )

    created = sum(1 for r in results if r["action"] == "created")
    failed = len(results) - created
    return {
        "status": "completed" if failed == 0 else "partial",
        "created": created,
        "failed": failed,
        "total": len(results),
        "report_dir": str(run_dir),
        "create_folder_response": folder_response,
        "results": results,
    }
