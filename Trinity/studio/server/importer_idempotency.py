"""POC idempotency hints when Studio already has Xray keys (grill G4)."""

from __future__ import annotations

from typing import Any


def attach_existing_xray_keys(conn: Any, creator_run_id: str | None, plan: dict[str, Any]) -> None:
    if not creator_run_id:
        return
    rows = conn.execute(
        """
        SELECT draft_id, xray_test_key FROM test_case_row
        WHERE creator_run_id = ? AND xray_test_key IS NOT NULL AND xray_test_key != ''
        """,
        (creator_run_id,),
    ).fetchall()
    if not rows:
        return
    key_by_draft = {r["draft_id"]: r["xray_test_key"] for r in rows}
    duplicates: list[str] = []
    for entry in plan.get("tests") or []:
        draft_id = entry.get("draft_id")
        if draft_id and draft_id in key_by_draft:
            entry["existing_xray_test_key"] = key_by_draft[draft_id]
            duplicates.append(f"{draft_id} → {key_by_draft[draft_id]}")
    if not duplicates:
        return
    msg = (
        "These drafts already have Xray keys in Studio — re-execute may create duplicates in Xray "
        f"(post-POC: block/skip): {', '.join(duplicates)}"
    )
    plan.setdefault("idempotency_warnings", []).append(msg)
    target = plan.get("target") or {}
    warnings = list(target.get("warnings") or [])
    warnings.append(msg)
    target["warnings"] = warnings
    plan["target"] = target
