"""Build Trinity Importer dry-run plans from Studio handoff payloads."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from importer_registry import (
    default_mapping_path_for_instance,
    get_jira_instance,
    mapping_summary,
    resolve_mapping_path,
)

_SCRIPTS = Path(__file__).resolve().parents[2] / "importer" / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from xray_graphql_import import (  # noqa: E402
    build_create_variables,
    credentials_status,
    folder_plan_for_target,
    load_config,
    normalize_folder_path,
    validate_test,
)


def enrich_test_for_xray_import(test: dict[str, Any]) -> dict[str, Any]:
    """Creator optional fields that legacy Xray import still requires."""
    out = dict(test)
    if not out.get("coverage_catalog_id"):
        linked_ac = out.get("linked_ac_ids") or []
        if linked_ac:
            out["coverage_catalog_id"] = str(linked_ac[0])
        else:
            out["coverage_catalog_id"] = "TRINITY-IMPORT"
    return out


def handoff_to_batch(handoff: dict[str, Any]) -> dict[str, Any]:
    raw_tests = handoff.get("tests") or []
    return {
        "run_id": handoff.get("creator_run_id") or handoff.get("source_batch_run_id"),
        "review_ref": handoff.get("review_ref"),
        "product_id": handoff.get("product_id"),
        "tests": [enrich_test_for_xray_import(t) for t in raw_tests],
    }


def load_handoff_payload(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("export_kind") != "creator_importer_handoff":
        raise ValueError("Expected export_kind creator_importer_handoff")
    if not data.get("tests"):
        raise ValueError("Handoff payload has no tests")
    return data


def build_import_plan(
    *,
    jira_instance_id: str,
    mapping_path: str | None,
    folder_path: str,
    create_folder_if_missing: bool,
    handoff: dict[str, Any],
    project_key_override: str | None = None,
    skip_requirement_link: bool = False,
) -> dict[str, Any]:
    instance = get_jira_instance(jira_instance_id)
    map_path = resolve_mapping_path(mapping_path) if mapping_path else default_mapping_path_for_instance(
        jira_instance_id
    )
    config = load_config(map_path)
    batch = handoff_to_batch(handoff)
    project_key = project_key_override or config["project"]["key"]
    normalized_folder = normalize_folder_path(folder_path)
    folder_plan = folder_plan_for_target(
        config,
        normalized_folder,
        create_if_missing=create_folder_if_missing,
    )
    creds = credentials_status()

    tests_out: list[dict[str, Any]] = []
    valid = 0
    invalid = 0
    for test in batch["tests"]:
        draft_id = test.get("draft_id", "?")
        errors = validate_test(test)
        entry: dict[str, Any] = {
            "draft_id": draft_id,
            "title": test.get("title"),
            "step_count": len(test.get("steps") or []),
            "linked_requirement_keys": test.get("linked_requirement_keys") or [],
            "validation_errors": errors,
            "action": "would_create" if not errors else "blocked_validation",
        }
        if not errors:
            valid += 1
            variables = build_create_variables(
                test,
                batch,
                config,
                project_key=project_key,
                folder_path=normalized_folder,
            )
            entry["graphql_preview"] = {
                "folderPath": variables.get("folderPath"),
                "step_count": len(variables.get("steps") or []),
                "summary": (variables.get("jira") or {}).get("fields", {}).get("summary"),
            }
        else:
            invalid += 1
        tests_out.append(entry)

    site_url = (config.get("jira") or {}).get("site_url") or instance.get("jira_site")
    if site_url and instance.get("jira_site") and site_url.rstrip("/") != instance["jira_site"].rstrip("/"):
        folder_plan.setdefault("warnings", []).append(
            f"Mapping jira.site_url ({site_url}) does not match selected instance ({instance['jira_site']}). "
            "Pick a mapping file for this instance."
        )

    execute_ready = (
        valid > 0
        and invalid == 0
        and creds["xray_client_id"]
        and creds["xray_client_secret"]
        and (skip_requirement_link or (creds["jira_email"] and creds["jira_api_token"]))
        and not (
            create_folder_if_missing
            and folder_plan.get("create_folder_if_missing")
            and not (config.get("project") or {}).get("id")
        )
    )

    return {
        "schema_version": "1.0",
        "mode": "dry_run_plan",
        "jira_instance": {
            "id": instance["id"],
            "label": instance.get("label"),
            "jira_site": instance.get("jira_site"),
            "risk_tier": instance.get("risk_tier"),
        },
        "mapping": mapping_summary(map_path),
        "target": folder_plan,
        "project_key": project_key,
        "skip_requirement_link": skip_requirement_link,
        "credentials": {
            **creds,
            "execute_ready": execute_ready,
            "credential_hint": instance.get("credential_hint"),
        },
        "handoff": {
            "creator_run_id": handoff.get("creator_run_id"),
            "test_count": len(batch["tests"]),
            "export_kind": handoff.get("export_kind"),
        },
        "tests": tests_out,
        "summary": {
            "total": len(tests_out),
            "valid": valid,
            "invalid": invalid,
            "action": "would_import_batch" if invalid == 0 else "fix_validation_first",
        },
    }
