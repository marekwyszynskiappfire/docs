"""Xray importer plan, execute, and persist."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from api_models import ImporterExecuteBody, ImporterPlanBody, ImporterRecordResultsBody
from creator_export import build_importer_payload, write_handoff_payload
from creator_importer_config import importer_defaults_for_handoff
from cursor_agent_runner import launch_agent
from db import db
from importer_execute import run_batch_execute
from importer_handoff import build_importer_cursor_prompt, build_pm_safe_summary
from importer_execute_guard import assert_execute_allowed, finalize_import_plan_execute_readiness
from importer_idempotency import attach_existing_xray_keys
from importer_jira import list_jira_projects
from importer_persist import apply_xray_reports, load_reports_from_path, resolve_report_path
from importer_plan import build_import_plan, load_handoff_payload
from importer_registry import get_jira_instance, list_jira_instances, list_mapping_files
from run_management import resolve_creator_run_id
from personas import docs_repo_root
from studio_env import importer_credential_scope
from studio_paths import EXPORT_ROOT
from telemetry import record_event

router = APIRouter(tags=["importer"])


@router.get("/api/importer/instances")
def importer_instances() -> dict[str, Any]:
    return {"instances": list_jira_instances()}


@router.get("/api/importer/mappings")
def importer_mappings() -> dict[str, Any]:
    return {"mappings": list_mapping_files()}


@router.get("/api/importer/jira-projects")
def importer_jira_projects(
    jira_instance_id: str,
    mapping_path: str | None = None,
    query: str = "",
) -> dict[str, Any]:
    with importer_credential_scope(jira_instance_id):
        return list_jira_projects(
            jira_instance_id,
            mapping_path=mapping_path,
            query=query,
        )


@router.get("/api/importer/credentials")
def importer_credentials() -> dict[str, Any]:
    scripts = Path(__file__).resolve().parents[3] / "importer" / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from xray_graphql_import import credentials_status as creds  # noqa: E402

    status = creds()
    jira_base = os.environ.get("JIRA_BASE_URL", "").strip()
    return {
        **status,
        "jira_base_url_set": bool(jira_base),
        "jira_base_url_host": jira_base.replace("https://", "").split("/")[0] if jira_base else None,
        "loaded_from_dotenv": (Path(__file__).resolve().parents[2] / ".env").is_file(),
    }


def _stamp_existing_xray_keys(handoff: dict[str, Any], plan: dict[str, Any]) -> None:
    """Copy Studio's known Xray keys onto the payload the CLI will read."""
    by_draft = {
        entry.get("draft_id"): entry.get("existing_xray_test_key")
        for entry in plan.get("tests") or []
        if entry.get("draft_id") and entry.get("existing_xray_test_key")
    }
    if not by_draft:
        return
    for test in handoff.get("tests") or []:
        key = by_draft.get(test.get("draft_id"))
        if key:
            test["existing_xray_test_key"] = key


def _resolve_creator_run_id_param(raw: str | None) -> str | None:
    if not raw or not str(raw).strip():
        return None
    with db() as conn:
        try:
            return resolve_creator_run_id(conn, str(raw).strip())
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
        except KeyError as exc:
            raise HTTPException(404, str(exc)) from exc


def _resolve_importer_handoff(body: ImporterPlanBody) -> tuple[dict[str, Any], str | None]:
    """Current approvals win over a saved importer-payload.json for a known Creator run."""
    creator_run_id = _resolve_creator_run_id_param(body.creator_run_id)
    if creator_run_id:
        with db() as conn:
            try:
                handoff = build_importer_payload(conn, creator_run_id)
            except KeyError:
                handoff = None
        if handoff is not None:
            if body.payload_path:
                handoff["ignored_payload_path"] = body.payload_path
            return handoff, creator_run_id
    if body.payload_path:
        path = Path(body.payload_path)
        if not path.is_absolute():
            path = (docs_repo_root() / path).resolve()
        handoff = load_handoff_payload(path)
        if not creator_run_id:
            creator_run_id = handoff.get("creator_run_id")
        return handoff, creator_run_id
    if creator_run_id:
        raise HTTPException(404, "Creator run not found")
    raise HTTPException(400, "Provide payload_path or creator_run_id")


@router.post("/api/importer/plan")
def importer_plan(body: ImporterPlanBody) -> dict[str, Any]:
    try:
        handoff, creator_run_id = _resolve_importer_handoff(body)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from None
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from None
    try:
        with importer_credential_scope(body.jira_instance_id):
            return _plan_with_credentials(body, handoff, creator_run_id)
    except KeyError as exc:
        raise HTTPException(400, str(exc)) from None
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from None


def _plan_with_credentials(
    body: ImporterPlanBody, handoff: dict[str, Any], creator_run_id: str | None
) -> dict[str, Any]:
    plan = build_import_plan(
        jira_instance_id=body.jira_instance_id,
        mapping_path=body.mapping_path,
        folder_path=body.folder_path,
        create_folder_if_missing=body.create_folder_if_missing,
        handoff=handoff,
        project_key_override=body.project_key_override,
        skip_requirement_link=body.skip_requirement_link,
        reviewer_gate_acknowledged=body.reviewer_gate_acknowledged,
        jira_instance_id_for_resolve=body.jira_instance_id,
    )
    plan["pm_safe_summary"] = build_pm_safe_summary(plan)
    if creator_run_id:
        plan["resolved_creator_run_id"] = creator_run_id
    with db() as conn:
        attach_existing_xray_keys(conn, creator_run_id, plan)
    _stamp_existing_xray_keys(handoff, plan)
    finalize_import_plan_execute_readiness(
        plan, idempotency_acknowledged=body.idempotency_acknowledged
    )
    if creator_run_id:
        written = write_handoff_payload(handoff, creator_run_id, EXPORT_ROOT)
        plan.setdefault("handoff", {})["payload_path"] = str(written)
    plan["cursor_prompt"] = build_importer_cursor_prompt(
        plan,
        payload_path=body.payload_path,
        creator_run_id=creator_run_id,
        mapping_path=body.mapping_path,
        skip_requirement_link=body.skip_requirement_link,
    )
    with db() as conn:
        record_event(
            conn,
            "importer_plan",
            "creator_run",
            creator_run_id,
            None,
            {
                "jira_instance_id": body.jira_instance_id,
                "valid_count": plan.get("valid_count"),
                "invalid_count": plan.get("invalid_count"),
                "project_key": plan.get("project_key"),
                "folder_path": body.folder_path,
            },
        )
    return plan


def _assert_production_execute_confirm(jira_instance_id: str, production_confirm: str | None) -> None:
    instance = get_jira_instance(jira_instance_id)
    if instance.get("risk_tier") == "production" and (production_confirm or "").strip() != "PRODUCTION":
        raise HTTPException(
            400,
            "Production instance: set production_confirm to PRODUCTION before execute",
        )


@router.post("/api/importer/launch-cursor")
def importer_launch_cursor(body: ImporterExecuteBody) -> dict[str, Any]:
    """Recompute the safe plan, then launch its server-owned Importer prompt."""
    _assert_production_execute_confirm(body.jira_instance_id, body.production_confirm)
    plan = importer_plan(body)
    if not plan.get("credentials", {}).get("execute_ready"):
        blockers = plan.get("execute_blockers") or ["Importer plan is not execute-ready"]
        raise HTTPException(400, "; ".join(str(item) for item in blockers))
    creator_run_id = plan.get("resolved_creator_run_id")
    pipeline_run_id = None
    if creator_run_id:
        with db() as conn:
            row = conn.execute(
                "SELECT pipeline_run_id FROM creator_run WHERE id = ?", (creator_run_id,)
            ).fetchone()
            pipeline_run_id = row["pipeline_run_id"] if row else None
    try:
        return launch_agent(
            stage="importer",
            prompt_text=plan["cursor_prompt"],
            pipeline_run_id=pipeline_run_id,
            creator_run_id=creator_run_id,
        )
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(503, str(exc)) from exc


@router.post("/api/importer/execute")
def importer_execute(body: ImporterExecuteBody) -> dict[str, Any]:
    _assert_production_execute_confirm(body.jira_instance_id, body.production_confirm)
    try:
        handoff, creator_run_id = _resolve_importer_handoff(body)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from None
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from None

    try:
        with importer_credential_scope(body.jira_instance_id):
            return _execute_with_credentials(body, handoff, creator_run_id)
    except KeyError as exc:
        raise HTTPException(400, str(exc)) from None
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from None
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001 — surface Xray/Jira errors to operator
        raise HTTPException(500, str(exc)) from exc


def _execute_with_credentials(
    body: ImporterExecuteBody, handoff: dict[str, Any], creator_run_id: str | None
) -> dict[str, Any]:
    plan = build_import_plan(
        jira_instance_id=body.jira_instance_id,
        mapping_path=body.mapping_path,
        folder_path=body.folder_path,
        create_folder_if_missing=body.create_folder_if_missing,
        handoff=handoff,
        project_key_override=body.project_key_override,
        skip_requirement_link=body.skip_requirement_link,
        reviewer_gate_acknowledged=body.reviewer_gate_acknowledged,
        jira_instance_id_for_resolve=body.jira_instance_id,
    )
    with db() as conn:
        attach_existing_xray_keys(conn, creator_run_id, plan)
    _stamp_existing_xray_keys(handoff, plan)
    try:
        assert_execute_allowed(
            plan, idempotency_acknowledged=body.idempotency_acknowledged
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    if not plan.get("credentials", {}).get("execute_ready"):
        blockers = plan.get("execute_blockers") or [
            "Import plan is not execute-ready — fix validation, credentials, gate acknowledgement, or mapping conflict"
        ]
        raise HTTPException(400, "; ".join(str(item) for item in blockers))
    map_path = body.mapping_path or plan["mapping"]["path"]
    if body.payload_path:
        batch_path = Path(body.payload_path)
        if not batch_path.is_absolute():
            batch_path = (docs_repo_root() / batch_path).resolve()
    elif creator_run_id:
        batch_path = EXPORT_ROOT / "creator" / creator_run_id / "importer-payload.json"
    else:
        raise HTTPException(400, "payload_path or creator_run_id required for execute")

    summary = run_batch_execute(
        plan=plan,
        handoff=handoff,
        batch_path=batch_path,
        mapping_path=map_path,
        skip_requirement_link=body.skip_requirement_link,
    )
    persist: dict[str, Any] | None = None
    if creator_run_id and summary.get("report_dir"):
        with db() as conn:
            persist = apply_xray_reports(conn, creator_run_id, Path(summary["report_dir"]))
            record_event(
                conn,
                "importer_execute",
                "creator_run",
                creator_run_id,
                None,
                {
                    "created": summary.get("created"),
                    "failed": summary.get("failed"),
                    "report_dir": summary.get("report_dir"),
                },
            )
    return {**summary, "persist": persist, "plan_summary": plan.get("summary")}


@router.get("/api/importer/defaults")
def importer_defaults(
    creator_run_id: str | None = None,
    payload_path: str | None = None,
) -> dict[str, Any]:
    try:
        handoff, _resolved = _resolve_importer_handoff(
            ImporterPlanBody(
                jira_instance_id="appfire-production",
                folder_path="/",
                creator_run_id=creator_run_id,
                payload_path=payload_path,
            )
        )
    except HTTPException:
        raise
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(400, str(exc)) from exc
    return importer_defaults_for_handoff(handoff)


@router.post("/api/importer/record-results")
def importer_record_results(body: ImporterRecordResultsBody) -> dict[str, Any]:
    """Persist Xray keys from import report JSON (file, folder, or inline list)."""
    reports: list[dict[str, Any]] = []
    if body.report_path:
        try:
            path = resolve_report_path(body.report_path)
            reports = load_reports_from_path(path)
        except FileNotFoundError as exc:
            raise HTTPException(404, str(exc)) from exc
    if body.results:
        for item in body.results:
            reports.append(
                {
                    "draft_id": item.get("draft_id"),
                    "xray_key": item.get("xray_test_key") or item.get("xray_key"),
                    "errors": item.get("errors"),
                }
            )
    if not reports:
        raise HTTPException(400, "Provide report_path or results")
    with db() as conn:
        run = conn.execute(
            "SELECT id FROM creator_run WHERE id = ?", (body.creator_run_id,)
        ).fetchone()
        if not run:
            raise HTTPException(404, "Creator run not found")
        return apply_xray_reports(conn, body.creator_run_id, reports)
