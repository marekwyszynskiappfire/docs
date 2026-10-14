"""Shared Reviewer payload field extraction for Studio."""

from __future__ import annotations

from typing import Any


def qa_planning_fit_from_payload(payload: dict[str, Any] | None) -> str | None:
    """Epic QA planning fit: prefer report.qa_planning_fit (Reviewer), then requirements[]."""
    if not payload:
        return None
    report = payload.get("report")
    if isinstance(report, dict):
        fit = report.get("qa_planning_fit")
        if fit:
            return str(fit).strip()
    for req in payload.get("requirements") or []:
        if not isinstance(req, dict):
            continue
        fit = req.get("qa_planning_fit")
        if fit:
            return str(fit).strip()
    return None


def gate_status_from_payload(payload: dict[str, Any] | None) -> str | None:
    if not payload:
        return None
    gate = payload.get("gate")
    if isinstance(gate, dict):
        status = gate.get("status")
        if status:
            return str(status).strip()
    report = payload.get("report")
    if isinstance(report, dict):
        status = report.get("gate_status")
        if status:
            return str(status).strip()
    return None


def apply_payload_fields_to_unit(unit: dict[str, Any], payload: dict[str, Any] | None) -> dict[str, Any]:
    """Overlay display fields from latest payload when DB columns are stale."""
    if not payload:
        return unit
    fit = qa_planning_fit_from_payload(payload)
    if fit:
        unit["qa_planning_fit"] = fit
    gate = gate_status_from_payload(payload)
    if gate:
        unit["gate_status"] = gate
    return unit
