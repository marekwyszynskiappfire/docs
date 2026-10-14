"""Portfolio-level readiness rollup for Studio Dashboard (PQ-01)."""

from __future__ import annotations

import json
from typing import Any

from db import utc_now
from review_payload_fields import gate_status_from_payload, qa_planning_fit_from_payload


def _inc(bucket: dict[str, int], key: str) -> None:
    k = (key or "unknown").strip() or "unknown"
    bucket[k] = bucket.get(k, 0) + 1


def _open_counts_from_payload(payload: dict[str, Any]) -> tuple[int, int]:
    findings = 0
    questions = 0
    for f in payload.get("findings") or []:
        if f.get("status", "open") == "open":
            findings += 1
    for q in payload.get("questions") or []:
        if q.get("status", "open") == "open":
            questions += 1
    return findings, questions


def _latest_payload(conn: Any, unit_id: str) -> dict[str, Any] | None:
    row = conn.execute(
        """
        SELECT payload_json FROM review_payload_revision
        WHERE review_unit_id = ?
        ORDER BY revision DESC LIMIT 1
        """,
        (unit_id,),
    ).fetchone()
    if not row:
        return None
    return json.loads(row["payload_json"])


def build_portfolio_rollup(conn: Any) -> dict[str, Any]:
    global_gate: dict[str, int] = {}
    global_fit: dict[str, int] = {}
    runs_out: list[dict[str, Any]] = []

    for run in conn.execute(
        "SELECT * FROM pipeline_run ORDER BY updated_at DESC"
    ).fetchall():
        run_id = run["id"]
        units = conn.execute(
            "SELECT * FROM review_unit WHERE pipeline_run_id = ?",
            (run_id,),
        ).fetchall()
        gate_mix: dict[str, int] = {}
        fit_mix: dict[str, int] = {}
        approved = 0
        in_creator = 0
        open_findings = 0
        open_questions = 0
        for u in units:
            payload = _latest_payload(conn, u["id"])
            gate = gate_status_from_payload(payload) or u["gate_status"]
            fit = qa_planning_fit_from_payload(payload) or u["qa_planning_fit"]
            _inc(gate_mix, gate)
            _inc(global_gate, gate)
            _inc(fit_mix, fit)
            _inc(global_fit, fit)
            if u["approved_revision_id"]:
                approved += 1
            if u["include_in_creator"]:
                in_creator += 1
            if payload:
                f, q = _open_counts_from_payload(payload)
                open_findings += f
                open_questions += q

        creator_runs = conn.execute(
            "SELECT COUNT(*) FROM creator_run WHERE pipeline_run_id = ?",
            (run_id,),
        ).fetchone()[0]
        test_row = conn.execute(
            """
            SELECT
              COUNT(*) AS total,
              SUM(CASE WHEN t.human_review_status = 'approved' THEN 1 ELSE 0 END) AS approved
            FROM test_case_row t
            INNER JOIN creator_run c ON c.id = t.creator_run_id
            WHERE c.pipeline_run_id = ?
            """,
            (run_id,),
        ).fetchone()
        runs_out.append(
            {
                "id": run_id,
                "label": run["label"],
                "updated_at": run["updated_at"],
                "unit_count": len(units),
                "units_approved": approved,
                "units_in_creator": in_creator,
                "gate_mix": gate_mix,
                "fit_mix": fit_mix,
                "open_findings_latest": open_findings,
                "open_questions_latest": open_questions,
                "creator_runs": creator_runs,
                "test_cases": test_row["total"] or 0,
                "test_cases_approved": test_row["approved"] or 0,
            }
        )

    return {
        "generated_at": utc_now(),
        "global": {
            "gate_mix": global_gate,
            "fit_mix": global_fit,
            "pipeline_runs": len(runs_out),
        },
        "runs": runs_out,
    }
