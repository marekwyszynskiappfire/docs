"""Pipeline runs and review units."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

from api_models import RunLabelBody, SavePayloadBody, UnitMetaBody
from creator_handoff import build_creator_prompt, payload_readiness
from creator_importer_config import test_data_isolation_warning
from db import db, json_loads, row_to_dict, utc_now
from personas import docs_repo_root
from review_payload_fields import apply_payload_fields_to_unit
from review_unit_export import export_review_unit
from run_report import _latest_payloads_for_units
from run_management import delete_pipeline_run, rename_pipeline_run
from telemetry import record_event

router = APIRouter(tags=["review-runs"])

@router.get("/api/runs")
def list_runs() -> list[dict[str, Any]]:
    with db() as conn:
        rows = conn.execute(
            """
            SELECT r.*,
              (SELECT COUNT(*) FROM review_unit u WHERE u.pipeline_run_id = r.id) AS unit_count
            FROM pipeline_run r
            ORDER BY r.updated_at DESC
            """
        ).fetchall()
    return [row_to_dict(r) for r in rows]


@router.get("/api/runs/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    with db() as conn:
        run = conn.execute("SELECT * FROM pipeline_run WHERE id = ?", (run_id,)).fetchone()
        if not run:
            raise HTTPException(404, "Run not found")
        units = conn.execute(
            "SELECT * FROM review_unit WHERE pipeline_run_id = ? ORDER BY jira_key",
            (run_id,),
        ).fetchall()
        unit_dicts = [row_to_dict(u) for u in units]
        payloads = _latest_payloads_for_units(conn, [u["id"] for u in unit_dicts])
    out = row_to_dict(run)
    out["creator_handoff"] = json_loads(out.pop("creator_handoff_json", None))
    out["units"] = [
        apply_payload_fields_to_unit(u, payloads.get(u["id"])) for u in unit_dicts
    ]
    return out


@router.patch("/api/runs/{run_id}")
def api_patch_pipeline_run(run_id: str, body: RunLabelBody) -> dict[str, Any]:
    try:
        with db() as conn:
            return rename_pipeline_run(conn, run_id, body.label)
    except KeyError:
        raise HTTPException(404, "Run not found") from None
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@router.delete("/api/runs/{run_id}")
def api_delete_pipeline_run(run_id: str) -> dict[str, Any]:
    try:
        with db() as conn:
            return delete_pipeline_run(conn, run_id)
    except KeyError:
        raise HTTPException(404, "Run not found") from None


@router.get("/api/units/{unit_id}")
def get_unit(unit_id: str) -> dict[str, Any]:
    with db() as conn:
        unit = conn.execute("SELECT * FROM review_unit WHERE id = ?", (unit_id,)).fetchone()
        if not unit:
            raise HTTPException(404, "Unit not found")
        rev_row = _latest_revision(conn, unit_id)
    payload = json.loads(rev_row["payload_json"]) if rev_row else None
    return {
        "unit": row_to_dict(unit),
        "revision": rev_row["revision"] if rev_row else None,
        "approved_revision": unit["approved_revision_id"],
        "payload": payload,
    }


def _latest_revision(conn, unit_id: str):
    return conn.execute(
        """
        SELECT * FROM review_payload_revision
        WHERE review_unit_id = ?
        ORDER BY revision DESC LIMIT 1
        """,
        (unit_id,),
    ).fetchone()


@router.put("/api/units/{unit_id}/payload")
def save_unit_payload(unit_id: str, body: SavePayloadBody) -> dict[str, Any]:
    now = utc_now()
    with db() as conn:
        unit = conn.execute("SELECT * FROM review_unit WHERE id = ?", (unit_id,)).fetchone()
        if not unit:
            raise HTTPException(404, "Unit not found")
        max_rev = conn.execute(
            "SELECT COALESCE(MAX(revision), 0) FROM review_payload_revision WHERE review_unit_id = ?",
            (unit_id,),
        ).fetchone()[0]
        new_rev = max_rev + 1
        payload_json = json.dumps(body.payload, ensure_ascii=False)
        conn.execute(
            """
            INSERT INTO review_payload_revision (review_unit_id, revision, payload_json, source, created_at, created_by)
            VALUES (?, ?, ?, 'human', ?, ?)
            """,
            (unit_id, new_rev, payload_json, now, body.created_by),
        )
        gate = (body.payload.get("gate") or {}).get("status")
        summary = (body.payload.get("requirements") or [{}])[0].get("summary")
        conn.execute(
            "UPDATE review_unit SET gate_status = ?, summary = ?, updated_at = ? WHERE id = ?",
            (gate, summary, now, unit_id),
        )
        record_event(
            conn,
            "review_payload_saved",
            "review_unit",
            unit_id,
            unit["pipeline_run_id"],
            {"revision": new_rev},
        )
    return {"revision": new_rev}


@router.patch("/api/units/{unit_id}")
def patch_unit(unit_id: str, body: UnitMetaBody) -> dict[str, str]:
    with db() as conn:
        unit = conn.execute("SELECT id FROM review_unit WHERE id = ?", (unit_id,)).fetchone()
        if not unit:
            raise HTTPException(404, "Unit not found")
        if body.include_in_creator is not None:
            conn.execute(
                "UPDATE review_unit SET include_in_creator = ?, updated_at = ? WHERE id = ?",
                (1 if body.include_in_creator else 0, utc_now(), unit_id),
            )
        if body.qa_planning_fit is not None:
            conn.execute(
                "UPDATE review_unit SET qa_planning_fit = ?, updated_at = ? WHERE id = ?",
                (body.qa_planning_fit, utc_now(), unit_id),
            )
    return {"status": "ok"}


@router.post("/api/units/{unit_id}/approve")
def approve_unit(unit_id: str) -> dict[str, Any]:
    with db() as conn:
        unit = conn.execute("SELECT * FROM review_unit WHERE id = ?", (unit_id,)).fetchone()
        if not unit:
            raise HTTPException(404, "Unit not found")
        rev = _latest_revision(conn, unit_id)
        if not rev:
            raise HTTPException(400, "No payload to approve")
        conn.execute(
            "UPDATE review_unit SET approved_revision_id = ?, updated_at = ? WHERE id = ?",
            (rev["id"], utc_now(), unit_id),
        )
        record_event(
            conn,
            "review_unit_approved",
            "review_unit",
            unit_id,
            unit["pipeline_run_id"],
            {"revision": rev["revision"]},
        )
    return {"approved_revision_id": rev["id"], "revision": rev["revision"]}


@router.post("/api/units/{unit_id}/export")
def export_unit(unit_id: str) -> dict[str, Any]:
    with db() as conn:
        try:
            result = export_review_unit(conn, unit_id)
        except KeyError:
            raise HTTPException(404, "Unit not found") from None
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
    return {
        "path": result["path"],
        "review_ref": result["review_ref"],
        "jira_key": result["jira_key"],
    }


@router.post("/api/units/{unit_id}/send-to-creator")
def send_to_creator(unit_id: str) -> dict[str, Any]:
    with db() as conn:
        unit = conn.execute("SELECT * FROM review_unit WHERE id = ?", (unit_id,)).fetchone()
        if not unit:
            raise HTTPException(404, "Unit not found")
        if not unit["approved_revision_id"]:
            raise HTTPException(
                400,
                "Approve this unit before sending to Creator (Save → Approve & export).",
            )
        if unit["qa_planning_fit"] == "not_fit":
            raise HTTPException(
                400,
                "This epic is not suitable for test design (not_fit). Resolve scope before Creator.",
            )
        run_row = conn.execute(
            "SELECT product_id FROM pipeline_run WHERE id = ?",
            (unit["pipeline_run_id"],),
        ).fetchone()
        product_id = run_row["product_id"] if run_row else None
        try:
            export = export_review_unit(conn, unit_id)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
        payload = export["payload"]
        gate = (payload.get("gate") or {}).get("status")
        prompt = build_creator_prompt(
            review_ref=export["review_ref"],
            jira_key=unit["jira_key"],
            creator_run_id=unit["jira_key"],
            gate_status=gate,
            readiness_label=payload_readiness(payload),
            qa_planning_fit=unit["qa_planning_fit"],
            pipeline_run_id=unit["pipeline_run_id"],
        )
        warnings: list[str] = []
        iso_warn = test_data_isolation_warning(product_id)
        if iso_warn:
            warnings.append(iso_warn)
        return {
            "review_ref": export["review_ref"],
            "creator_run_id": unit["jira_key"],
            "prompt": prompt,
            "suite_payload_hint": f"Trinity/creator/artifacts/{unit['jira_key']}/suite-payload.json",
            "creator_studio_path": "/creator",
            "warnings": warnings,
        }


def _source_path_relative(source_path: str | None) -> str | None:
    if not source_path:
        return None
    p = Path(source_path)
    root = docs_repo_root()
    if p.is_absolute():
        try:
            return str(p.relative_to(root))
        except ValueError:
            return str(p)
    return source_path


@router.get("/api/runs/{run_id}/creator-handoff")
def build_creator_handoff(run_id: str) -> dict[str, Any]:
    with db() as conn:
        run = conn.execute("SELECT * FROM pipeline_run WHERE id = ?", (run_id,)).fetchone()
        if not run:
            raise HTTPException(404, "Run not found")
        included = [
            r["jira_key"]
            for r in conn.execute(
                """
                SELECT jira_key FROM review_unit
                WHERE pipeline_run_id = ? AND include_in_creator = 1
                ORDER BY jira_key
                """,
                (run_id,),
            ).fetchall()
        ]
        excluded_n = conn.execute(
            "SELECT COUNT(*) FROM review_unit WHERE pipeline_run_id = ? AND include_in_creator = 0",
            (run_id,),
        ).fetchone()[0]
    keys = included
    jql = f"key in ({', '.join(keys)}) ORDER BY key ASC" if keys else "key = IMPOSSIBLE-0"
    handoff = json_loads(run["creator_handoff_json"]) if run else None
    rel_source = _source_path_relative(run["source_path"])
    portfolio_report_path: str | None = None
    if rel_source:
        portfolio_index = docs_repo_root() / rel_source / "portfolio" / "index.html"
        if portfolio_index.is_file():
            portfolio_report_path = f"{rel_source}/portfolio/index.html"

    handoff_export: dict[str, Any] = {
        "schema_version": "1.0",
        "run_id": run_id,
        "generated_at": utc_now(),
        "source_path": rel_source,
        "source_jql": (handoff or {}).get("source_jql"),
        "creator_jql": jql,
        "included_epics": keys,
        "excluded_from_creator_count": excluded_n,
    }
    if handoff:
        merged = dict(handoff)
        merged.update(handoff_export)
        handoff_export = merged

    return {
        **handoff_export,
        "portfolio_report_path": portfolio_report_path,
        "handoff_export": handoff_export,
    }

