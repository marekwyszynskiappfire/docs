"""PQ-06 — surface Reviewer context_loaded failures across Studio runs."""

from __future__ import annotations

import json
from typing import Any

ALERT_STATUSES = frozenset({"failed", "unavailable"})


def _latest_payload(conn: Any, unit_id: str) -> dict[str, Any] | None:
    row = conn.execute(
        """
        SELECT payload_json FROM review_payload_revision
        WHERE review_unit_id = ? ORDER BY revision DESC LIMIT 1
        """,
        (unit_id,),
    ).fetchone()
    if not row:
        return None
    return json.loads(row["payload_json"])


def build_context_loaded_alerts(conn: Any, limit: int = 50) -> dict[str, Any]:
    alerts: list[dict[str, Any]] = []
    units = conn.execute(
        """
        SELECT u.id AS unit_id, u.jira_key, u.pipeline_run_id, r.label AS run_label
        FROM review_unit u
        JOIN pipeline_run r ON r.id = u.pipeline_run_id
        ORDER BY u.updated_at DESC
        """
    ).fetchall()
    for unit in units:
        payload = _latest_payload(conn, unit["unit_id"])
        if not payload:
            continue
        for entry in payload.get("context_loaded") or []:
            if not isinstance(entry, dict):
                continue
            status = (entry.get("status") or "").strip().lower()
            if status not in ALERT_STATUSES:
                continue
            alerts.append(
                {
                    "pipeline_run_id": unit["pipeline_run_id"],
                    "run_label": unit["run_label"],
                    "unit_id": unit["unit_id"],
                    "jira_key": unit["jira_key"],
                    "source": entry.get("source") or entry.get("type") or "source",
                    "source_type": entry.get("type"),
                    "status": status,
                    "detail": entry.get("detail") or entry.get("reason"),
                }
            )
            if len(alerts) >= limit:
                break
        if len(alerts) >= limit:
            break
    return {
        "alert_count": len(alerts),
        "alerts": alerts,
        "statuses_flagged": sorted(ALERT_STATUSES),
    }
