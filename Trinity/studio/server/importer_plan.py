"""Build Trinity Importer dry-run plans from Studio handoff payloads."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_TRINITY = Path(__file__).resolve().parents[2]
_SHARED = _TRINITY / "shared"
if str(_SHARED) not in sys.path:
    sys.path.insert(0, str(_SHARED))

from validate_for_xray import (  # noqa: E402
    enrich_test_for_xray_import,
    test_type_xray_coercion,
    validate_test,
)

from creator_importer_config import importer_defaults_for_handoff
from importer_jira import resolve_project_by_key
from importer_registry import (
    default_mapping_path_for_instance,
    get_jira_instance,
    mapping_summary,
    resolve_mapping_path,
)
from creator_coverage import format_coverage_matrix_for_prompt
from importer_review_gate import assess_reviewer_gate, load_review_payload

_SCRIPTS = Path(__file__).resolve().parents[2] / "importer" / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from xray_graphql_import import (  # noqa: E402
    build_create_variables,
    credentials_status,
    folder_plan_for_target,
    load_config,
    normalize_folder_path,
)


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
    reviewer_gate_acknowledged: bool = False,
    jira_instance_id_for_resolve: str | None = None,
) -> dict[str, Any]:
    instance = get_jira_instance(jira_instance_id)
    map_path = resolve_mapping_path(mapping_path) if mapping_path else default_mapping_path_for_instance(
        jira_instance_id
    )
    config = load_config(map_path)
    batch = handoff_to_batch(handoff)
    project_key = project_key_override or config["project"]["key"]
    resolve_id = jira_instance_id_for_resolve or jira_instance_id
    project_resolution: dict[str, Any] = {"project_key": project_key}
    resolved = resolve_project_by_key(resolve_id, project_key, mapping_path=str(map_path))
    if resolved.get("status") == "ok" and resolved.get("project_id"):
        project_resolution = {
            **project_resolution,
            "project_id": resolved["project_id"],
            "project_name": resolved.get("project_name"),
            "mapping_file_project_id": resolved.get("mapping_file_project_id"),
            "mapping_conflict": resolved.get("mapping_conflict"),
            "resolved_via": "jira_rest",
        }
        config = json.loads(json.dumps(config))
        config.setdefault("project", {})["id"] = resolved["project_id"]
        config["project"]["key"] = resolved.get("project_key") or project_key
    elif resolved.get("status") != "ok":
        project_resolution["resolve_error"] = resolved.get("message") or resolved.get("status")

    review_ref = batch.get("review_ref")
    review_payload = load_review_payload(review_ref)
    reviewer_gate = assess_reviewer_gate(review_payload)
    if review_ref:
        reviewer_gate["review_ref_path"] = review_ref

    normalized_folder = normalize_folder_path(folder_path)
    folder_plan = folder_plan_for_target(
        config,
        normalized_folder,
        create_if_missing=create_folder_if_missing,
    )
    if project_resolution.get("mapping_conflict"):
        folder_plan.setdefault("warnings", []).append(
            f"Resolved project id {project_resolution.get('project_id')} does not match mapping file "
            f"project.id ({project_resolution.get('mapping_file_project_id')}). "
            "createFolder will use the resolved id; update the mapping file to avoid confusion."
        )
    creds = credentials_status()

    raw_tests = handoff.get("tests") or []
    raw_by_draft = {t.get("draft_id"): t for t in raw_tests if t.get("draft_id")}

    tests_out: list[dict[str, Any]] = []
    valid = 0
    invalid = 0
    for test in batch["tests"]:
        draft_id = test.get("draft_id", "?")
        raw = raw_by_draft.get(draft_id) or test
        enriched = enrich_test_for_xray_import(dict(raw))
        errors = validate_test(enriched)
        entry: dict[str, Any] = {
            "draft_id": draft_id,
            "title": test.get("title"),
            "step_count": len(test.get("steps") or []),
            "linked_requirement_keys": test.get("linked_requirement_keys") or [],
            "validation_errors": errors,
            "action": "would_create" if not errors else "blocked_validation",
            "xray_test_type": enriched.get("test_type") or "Manual",
        }
        coercion = test_type_xray_coercion(raw)
        if coercion:
            entry["test_type_coercion"] = coercion
        if not errors:
            valid += 1
            variables = build_create_variables(
                enriched,
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

    gate_blocks_execute = (
        reviewer_gate.get("requires_acknowledgement") and not reviewer_gate_acknowledged
    )
    if gate_blocks_execute:
        folder_plan.setdefault("warnings", []).append(
            "Reviewer gate: acknowledge the warning in Studio before execute (IQ-16 soft gate)."
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
        and not gate_blocks_execute
        and not project_resolution.get("mapping_conflict")
    )

    importer_defaults = importer_defaults_for_handoff(handoff)
    coverage_report = handoff.get("coverage_report")
    coverage_matrix_markdown = format_coverage_matrix_for_prompt(coverage_report)
    export_warnings = []
    try:
        from validate_for_xray import export_preflight_warnings

        export_warnings = export_preflight_warnings(handoff)
    except ImportError:
        pass

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
        "project_resolution": project_resolution,
        "reviewer_gate": reviewer_gate,
        "reviewer_gate_acknowledged": reviewer_gate_acknowledged,
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
            "review_ref": batch.get("review_ref"),
            "product_id": handoff.get("product_id"),
        },
        "importer_defaults": importer_defaults,
        "export_preflight_warnings": export_warnings,
        "coverage_matrix_markdown": coverage_matrix_markdown,
        "tests": tests_out,
        "summary": {
            "total": len(tests_out),
            "valid": valid,
            "invalid": invalid,
            "action": "would_import_batch" if invalid == 0 else "fix_validation_first",
        },
    }
