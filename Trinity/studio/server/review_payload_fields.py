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


TESTABILITY_VERDICTS = ("testable_now", "testable_with_clarifications", "not_testable_yet")


def testability_verdict(payload: dict[str, Any] | None, qa_planning_fit: str | None) -> str:
    """Explicit report.testability_verdict wins; otherwise derive from fit, blockers, and open High questions."""
    report = (payload or {}).get("report")
    if isinstance(report, dict) and report.get("testability_verdict") in TESTABILITY_VERDICTS:
        return str(report["testability_verdict"])
    if qa_planning_fit == "not_fit":
        return "not_testable_yet"
    if not payload:
        return "testable_with_clarifications"
    for finding in payload.get("findings") or []:
        if isinstance(finding, dict) and finding.get("blocks_test_generation"):
            return "not_testable_yet"
    for question in payload.get("questions") or []:
        if (
            isinstance(question, dict)
            and question.get("priority") == "High"
            and (question.get("status") or "open") == "open"
        ):
            return "testable_with_clarifications"
    return "testable_now"


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
