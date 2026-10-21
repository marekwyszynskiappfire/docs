"""Personas, Reviewer run configs, and import endpoints."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from api_models import (
    ImportBatchBody,
    ImportManifestBody,
    ImportRunBody,
    PasteResolvedKeysBody,
    RestorePersonaBody,
    SavePersonaBody,
)
from import_review import import_reviewer_run, import_test_case_batch
from pipeline_manifest import import_pipeline_manifest
from personas import PersonaConflict, list_persona_files, list_revisions, read_persona, restore_revision, write_persona
from run_config import (
    list_new_epics,
    list_run_configs,
    paste_resolved_keys,
    read_run_config,
    resolve_scope_attempt,
    resolve_scope_prompt,
    write_run_config,
)
from studio_paths import DOCS_REPO_ROOT

router = APIRouter(tags=["personas-config"])


@router.get("/api/personas")
def api_list_personas() -> list[dict[str, str]]:
    return list_persona_files()


@router.get("/api/personas/{filename}")
def api_get_persona(filename: str) -> dict[str, str]:
    try:
        return read_persona(filename)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e


@router.put("/api/personas/{filename}")
def api_put_persona(filename: str, body: SavePersonaBody) -> dict[str, Any]:
    try:
        return write_persona(filename, body.content, body.expected_sha256)
    except PersonaConflict as e:
        raise HTTPException(
            409,
            {"message": "This persona changed after you opened it.", "content": e.content, "content_sha256": e.content_sha256},
        ) from e
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e


@router.get("/api/personas/{filename}/revisions")
def api_list_persona_revisions(filename: str) -> list[dict[str, str | int]]:
    try:
        return list_revisions(filename)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@router.post("/api/personas/{filename}/revisions/{revision_id}/restore")
def api_restore_persona(filename: str, revision_id: int, body: RestorePersonaBody) -> dict[str, str]:
    try:
        return restore_revision(filename, revision_id, body.expected_sha256)
    except PersonaConflict as e:
        raise HTTPException(
            409,
            {"message": "This persona changed after you opened it.", "content": e.content, "content_sha256": e.content_sha256},
        ) from e
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e


@router.get("/api/reviewer-run-configs")
def api_list_run_configs() -> list[dict[str, Any]]:
    return list_run_configs()


@router.get("/api/reviewer-run-configs/{portfolio_id}")
def api_get_run_config(portfolio_id: str) -> dict[str, Any]:
    try:
        return read_run_config(portfolio_id)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e


@router.get("/api/reviewer-run-configs/{portfolio_id}/resolve-scope-prompt")
def api_resolve_scope_prompt(portfolio_id: str) -> dict[str, str]:
    try:
        return resolve_scope_prompt(portfolio_id)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e


@router.post("/api/reviewer-run-configs/{portfolio_id}/resolve-scope")
def api_resolve_scope(portfolio_id: str) -> dict[str, Any]:
    try:
        return resolve_scope_attempt(portfolio_id)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e


@router.post("/api/reviewer-run-configs/{portfolio_id}/resolved-keys")
def api_paste_resolved_keys(portfolio_id: str, body: PasteResolvedKeysBody) -> dict[str, Any]:
    try:
        out = paste_resolved_keys(portfolio_id, body.keys_text)
        warning = out.pop("_warning", None)
        resp = {"config": out, "resolved_count": len(out.get("resolved_epic_keys") or [])}
        if warning:
            resp["warning"] = warning
        return resp
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e


@router.delete("/api/reviewer-run-configs/{portfolio_id}/resolved-keys")
def api_clear_resolved_keys(portfolio_id: str) -> dict[str, Any]:
    try:
        config = read_run_config(portfolio_id)
        config.pop("resolved_epic_keys", None)
        config.pop("resolved_at", None)
        config.pop("resolved_source", None)
        return write_run_config(portfolio_id, config)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e


@router.get("/api/reviewer-run-configs/{portfolio_id}/new-epics")
def api_new_epics(portfolio_id: str) -> dict[str, Any]:
    try:
        return list_new_epics(portfolio_id)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e


@router.put("/api/reviewer-run-configs/{portfolio_id}")
def api_put_run_config(portfolio_id: str, body: dict[str, Any]) -> dict[str, Any]:
    try:
        return write_run_config(portfolio_id, body)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except RuntimeError as e:
        raise HTTPException(500, str(e)) from e


@router.post("/api/import/pipeline-manifest")
def api_import_manifest(body: ImportManifestBody) -> dict[str, Any]:
    try:
        return import_pipeline_manifest(body.path, dry_run=body.dry_run)
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(400, str(e)) from e


@router.post("/api/import/reviewer-run")
def api_import_run(body: ImportRunBody) -> dict[str, Any]:
    path = Path(body.path).expanduser()
    if not path.is_absolute():
        path = (DOCS_REPO_ROOT / path).resolve()
    try:
        return import_reviewer_run(path, run_id=body.run_id)
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(400, str(e)) from e


@router.post("/api/import/test-case-batch")
def api_import_batch(body: ImportBatchBody) -> dict[str, Any]:
    path = Path(body.path).expanduser()
    if not path.is_absolute():
        path = (DOCS_REPO_ROOT / path).resolve()
    try:
        return import_test_case_batch(path, body.creator_run_id)
    except FileNotFoundError as e:
        raise HTTPException(400, str(e)) from e
