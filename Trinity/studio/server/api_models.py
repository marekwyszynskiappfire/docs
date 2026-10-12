"""Pydantic request/response bodies for Studio API routes."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ImportRunBody(BaseModel):
    path: str
    run_id: str | None = None


class RunLabelBody(BaseModel):
    label: str = Field(..., min_length=1, max_length=240)


class ImportBatchBody(BaseModel):
    path: str
    creator_run_id: str | None = None


class ImporterPlanBody(BaseModel):
    jira_instance_id: str
    folder_path: str
    create_folder_if_missing: bool = False
    mapping_path: str | None = None
    project_key_override: str | None = None
    payload_path: str | None = None
    creator_run_id: str | None = None
    skip_requirement_link: bool = False
    reviewer_gate_acknowledged: bool = False


class ImporterExecuteBody(ImporterPlanBody):
    production_confirm: str | None = None


class SavePayloadBody(BaseModel):
    payload: dict[str, Any]
    created_by: str = "human"


class UnitMetaBody(BaseModel):
    include_in_creator: bool | None = None
    qa_planning_fit: str | None = None


class SaveTestCaseBody(BaseModel):
    case: dict[str, Any]
    human_review_status: str | None = None
    marked_for_xray_import: bool | None = None
    rejection_reason: str | None = None
    created_by: str = "human"


class PatchTestBody(BaseModel):
    human_review_status: str | None = None
    marked_for_xray_import: bool | None = None
    rejection_reason: str | None = None


class BulkTestsBody(BaseModel):
    test_ids: list[str] = Field(..., min_length=1)
    human_review_status: str | None = None
    marked_for_xray_import: bool | None = None
    rejection_reason: str | None = None


class SavePersonaBody(BaseModel):
    content: str = Field(..., min_length=1)


class PasteResolvedKeysBody(BaseModel):
    keys_text: str = Field(..., min_length=1)


class ImporterRecordResultsBody(BaseModel):
    creator_run_id: str = Field(..., min_length=1)
    report_path: str | None = None
    results: list[dict[str, Any]] | None = None


class CursorSessionBody(BaseModel):
    stage: str = Field(..., min_length=1)
    pipeline_run_id: str | None = None
    creator_run_id: str | None = None


class CursorUsageBody(BaseModel):
    stage: str = Field(..., min_length=1)
    conversation_id: str | None = None
    pipeline_run_id: str | None = None
    creator_run_id: str | None = None
    generation_id: str | None = None
    model: str | None = None
    model_id: str | None = None
    duration_ms: int | None = None
    status: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_cents: int | None = None
    source: str = "cursor_hook"
    notes: str | None = None
