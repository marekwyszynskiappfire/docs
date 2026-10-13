"""Post-plan guards for Importer execute (redaction IQ-17, Xray idempotency)."""

from __future__ import annotations

import os
from typing import Any

_GUARD_BLOCKER_IDS = frozenset({"export_preflight_redaction", "xray_idempotency"})


def redaction_preflight_warnings(warnings: list[str]) -> list[str]:
    """Subset of export preflight that hard-blocks execute by default."""
    blocked: list[str] = []
    for w in warnings:
        lower = w.lower()
        if "possible email" in lower or "sensitive url" in lower:
            blocked.append(w)
    return blocked


def finalize_import_plan_execute_readiness(
    plan: dict[str, Any],
    *,
    idempotency_acknowledged: bool = False,
) -> None:
    """Mutate plan credentials.execute_ready after idempotency + redaction checks."""
    creds = plan.setdefault("credentials", {})
    other_blockers = [
        b for b in (plan.get("execute_blockers") or []) if b not in _GUARD_BLOCKER_IDS
    ]
    guard_blockers: list[str] = []

    export_warnings = plan.get("export_preflight_warnings") or []
    redaction_hits = redaction_preflight_warnings(export_warnings)
    allow_redaction = os.environ.get("STUDIO_IMPORTER_ALLOW_REDACTION_EXECUTE", "").lower() in (
        "1",
        "true",
        "yes",
    )
    if redaction_hits:
        plan["export_preflight_redaction"] = redaction_hits
        if not allow_redaction:
            guard_blockers.append("export_preflight_redaction")

    idem = list(plan.get("idempotency_warnings") or [])
    plan["idempotency"] = {
        "requires_acknowledgement": bool(idem),
        "warnings": idem,
        "acknowledged": idempotency_acknowledged,
    }
    if idem and not idempotency_acknowledged:
        guard_blockers.append("xray_idempotency")

    plan["execute_blockers"] = other_blockers + guard_blockers
    if guard_blockers:
        creds["execute_ready"] = False


def assert_execute_allowed(plan: dict[str, Any], *, idempotency_acknowledged: bool) -> None:
    """Raise ValueError when execute must not proceed."""
    finalize_import_plan_execute_readiness(plan, idempotency_acknowledged=idempotency_acknowledged)
    blockers = plan.get("execute_blockers") or []
    if "export_preflight_redaction" in blockers:
        raise ValueError(
            "Export preflight redaction (email/sensitive URL) — fix tests or set "
            "STUDIO_IMPORTER_ALLOW_REDACTION_EXECUTE=1 for emergency override"
        )
    if "xray_idempotency" in blockers:
        raise ValueError(
            "Tests already have Xray keys in Studio — acknowledge idempotency warning or clear keys"
        )
