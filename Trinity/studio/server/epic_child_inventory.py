"""Extract epic child inventory from Reviewer payloads (RQ-02)."""

from __future__ import annotations

import json
from typing import Any


def children_from_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rollup = payload.get("rollup") or {}
    raw = rollup.get("epic_child_inventory") or []
    out: list[dict[str, Any]] = []
    for c in raw:
        if not isinstance(c, dict):
            continue
        out.append(
            {
                "key": c.get("key"),
                "type": c.get("type"),
                "status": c.get("status"),
                "summary": c.get("summary"),
            }
        )
    return out


def status_mix(children: list[dict[str, Any]]) -> dict[str, int]:
    mix: dict[str, int] = {}
    for c in children:
        st = (c.get("status") or "unknown").strip() or "unknown"
        mix[st] = mix.get(st, 0) + 1
    return mix


def build_run_child_inventory(conn: Any, run_id: str) -> dict[str, Any]:
    epics: list[dict[str, Any]] = []
    for unit in conn.execute(
        """
        SELECT id, jira_key FROM review_unit
        WHERE pipeline_run_id = ? ORDER BY jira_key
        """,
        (run_id,),
    ).fetchall():
        row = conn.execute(
            """
            SELECT payload_json FROM review_payload_revision
            WHERE review_unit_id = ?
            ORDER BY revision DESC LIMIT 1
            """,
            (unit["id"],),
        ).fetchone()
        if not row:
            epics.append(
                {
                    "unit_id": unit["id"],
                    "jira_key": unit["jira_key"],
                    "child_count": 0,
                    "status_mix": {},
                    "children": [],
                }
            )
            continue
        payload = json.loads(row["payload_json"])
        children = children_from_payload(payload)
        epics.append(
            {
                "unit_id": unit["id"],
                "jira_key": unit["jira_key"],
                "child_count": len(children),
                "status_mix": status_mix(children),
                "children": children,
            }
        )
    run_status_mix: dict[str, int] = {}
    total_children = 0
    for epic in epics:
        total_children += epic["child_count"]
        for st, n in epic["status_mix"].items():
            run_status_mix[st] = run_status_mix.get(st, 0) + n
    return {
        "pipeline_run_id": run_id,
        "total_children": total_children,
        "run_status_mix": run_status_mix,
        "epics": epics,
    }
