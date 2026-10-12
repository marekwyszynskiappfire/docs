"""Reviewer readiness assessment for Importer soft-gate (IQ-16)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_review_payload(review_ref: str | None) -> dict[str, Any] | None:
    if not review_ref or not str(review_ref).strip():
        return None
    path = Path(review_ref)
    if not path.is_absolute():
        path = (_repo_root() / review_ref).resolve()
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def assess_reviewer_gate(payload: dict[str, Any] | None) -> dict[str, Any]:
    if not payload:
        return {
            "linked": False,
            "requires_acknowledgement": False,
            "level": "none",
            "messages": [],
            "gate_status": None,
            "readiness_value": None,
        }

    gate = payload.get("gate") or {}
    gate_status = gate.get("status")
    critical = int(gate.get("critical_unresolved_count") or 0)
    readiness = (payload.get("classification") or {}).get("readiness") or payload.get("readiness") or {}
    readiness_value = readiness.get("value")
    readiness_label = readiness.get("human_label")

    open_critical = 0
    for f in payload.get("findings") or []:
        if f.get("status", "open") != "open":
            continue
        if f.get("severity") == "CRITICAL" or f.get("blocks_test_generation"):
            open_critical += 1

    messages: list[str] = []
    level = "clear"
    requires = False

    if gate_status == "BLOCKED" or critical > 0 or open_critical > 0:
        level = "block"
        requires = True
        messages.append(
            f"Reviewer gate is {gate_status or 'BLOCKED'} with "
            f"{max(critical, open_critical)} unresolved Critical blocker(s)."
        )
    elif gate_status == "PASS_WITH_WARNINGS":
        level = "warn"
        requires = True
        high = int(gate.get("high_unresolved_count") or 0)
        messages.append(
            f"Reviewer gate is PASS_WITH_WARNINGS ({high} High finding(s) may still be open)."
        )
    elif gate_status and gate_status != "PASS":
        level = "warn"
        requires = True
        messages.append(f"Reviewer gate status is {gate_status}.")

    if readiness_value and readiness_value not in ("ok", "ready_to_build_tests"):
        if level == "clear":
            level = "warn"
            requires = True
        messages.append(
            f"Readiness is {readiness_value}"
            + (f" ({readiness_label})" if readiness_label else "")
            + "."
        )

    report = payload.get("report") or {}
    if report.get("readiness_line") and requires:
        messages.append(report["readiness_line"])

    return {
        "linked": True,
        "requires_acknowledgement": requires,
        "level": level,
        "messages": messages,
        "gate_status": gate_status,
        "readiness_value": readiness_value,
        "requirement_key": (payload.get("scope") or {}).get("jira_key")
        or payload.get("requirement_key"),
    }
