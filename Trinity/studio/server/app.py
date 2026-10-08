"""QA Studio API."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Allow running as `python app.py` from server/
sys.path.insert(0, str(Path(__file__).resolve().parent))

from db import db, init_db, json_loads, log_event, row_to_dict, utc_now
from import_review import import_reviewer_run, import_test_case_batch
from personas import docs_repo_root, list_persona_files, read_persona, write_persona
from creator_handoff import build_creator_prompt, payload_readiness, review_ref_relative
from run_config import (
    list_new_epics,
    list_run_configs,
    paste_resolved_keys,
    read_run_config,
    resolve_scope_attempt,
    resolve_scope_prompt,
    write_run_config,
)

app = FastAPI(title="Trinity Studio", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EXPORT_ROOT = Path(__file__).resolve().parent.parent / "data" / "exports"


class ImportRunBody(BaseModel):
    path: str


class ImportBatchBody(BaseModel):
    path: str
    creator_run_id: str | None = None


class SavePayloadBody(BaseModel):
    payload: dict[str, Any]
    created_by: str = "human"


class UnitMetaBody(BaseModel):
    include_in_creator: bool | None = None
    qa_planning_fit: str | None = None


class SaveTestCaseBody(BaseModel):
    case: dict[str, Any]
    human_review_status: str | None = None
    created_by: str = "human"


class SavePersonaBody(BaseModel):
    content: str = Field(..., min_length=1)


class PasteResolvedKeysBody(BaseModel):
    keys_text: str = Field(..., min_length=1)


def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


@app.on_event("startup")
def _startup() -> None:
    _load_dotenv()
    init_db()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/personas")
def api_list_personas() -> list[dict[str, str]]:
    return list_persona_files()


@app.get("/api/personas/{filename}")
def api_get_persona(filename: str) -> dict[str, str]:
    try:
        return read_persona(filename)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e


@app.put("/api/personas/{filename}")
def api_put_persona(filename: str, body: SavePersonaBody) -> dict[str, Any]:
    try:
        return write_persona(filename, body.content)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@app.get("/api/reviewer-run-configs")
def api_list_run_configs() -> list[dict[str, Any]]:
    return list_run_configs()


@app.get("/api/reviewer-run-configs/{portfolio_id}")
def api_get_run_config(portfolio_id: str) -> dict[str, Any]:
    try:
        return read_run_config(portfolio_id)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e


@app.get("/api/reviewer-run-configs/{portfolio_id}/resolve-scope-prompt")
def api_resolve_scope_prompt(portfolio_id: str) -> dict[str, str]:
    try:
        return resolve_scope_prompt(portfolio_id)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e


@app.post("/api/reviewer-run-configs/{portfolio_id}/resolve-scope")
def api_resolve_scope(portfolio_id: str) -> dict[str, Any]:
    """Inline epic_keys/epic_url; JQL/filter via JIRA_* env or Cursor prompt payload."""
    try:
        return resolve_scope_attempt(portfolio_id)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e


@app.post("/api/reviewer-run-configs/{portfolio_id}/resolved-keys")
def api_paste_resolved_keys(portfolio_id: str, body: PasteResolvedKeysBody) -> dict[str, Any]:
    try:
        out = paste_resolved_keys(portfolio_id, body.keys_text)
        warning = out.pop("_warning", None)
        resp = {"config": out, "resolved_count": len(out.get("resolved_epic_keys") or [])}
        if warning:
            resp["warning"] = warning
        return resp
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e


@app.delete("/api/reviewer-run-configs/{portfolio_id}/resolved-keys")
def api_clear_resolved_keys(portfolio_id: str) -> dict[str, Any]:
    try:
        config = read_run_config(portfolio_id)
        config.pop("resolved_epic_keys", None)
        config.pop("resolved_at", None)
        config.pop("resolved_source", None)
        return write_run_config(portfolio_id, config)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e


@app.get("/api/reviewer-run-configs/{portfolio_id}/new-epics")
def api_new_epics(portfolio_id: str) -> dict[str, Any]:
    try:
        return list_new_epics(portfolio_id)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e


@app.put("/api/reviewer-run-configs/{portfolio_id}")
def api_put_run_config(portfolio_id: str, body: dict[str, Any]) -> dict[str, Any]:
    try:
        return write_run_config(portfolio_id, body)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except RuntimeError as e:
        raise HTTPException(500, str(e)) from e


@app.post("/api/import/reviewer-run")
def api_import_run(body: ImportRunBody) -> dict[str, Any]:
    path = Path(body.path).expanduser()
    if not path.is_absolute():
        # DOCS repo root: Trinity/studio/server → four levels up
        repo_root = Path(__file__).resolve().parent.parent.parent.parent
        path = (repo_root / path).resolve()
    try:
        return import_reviewer_run(path)
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(400, str(e)) from e


@app.post("/api/import/test-case-batch")
def api_import_batch(body: ImportBatchBody) -> dict[str, Any]:
    path = Path(body.path).expanduser()
    if not path.is_absolute():
        repo_root = Path(__file__).resolve().parent.parent.parent.parent
        path = (repo_root / path).resolve()
    try:
        return import_test_case_batch(path, body.creator_run_id)
    except FileNotFoundError as e:
        raise HTTPException(400, str(e)) from e


@app.get("/api/runs")
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


@app.get("/api/runs/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    with db() as conn:
        run = conn.execute("SELECT * FROM pipeline_run WHERE id = ?", (run_id,)).fetchone()
        if not run:
            raise HTTPException(404, "Run not found")
        units = conn.execute(
            "SELECT * FROM review_unit WHERE pipeline_run_id = ? ORDER BY jira_key",
            (run_id,),
        ).fetchall()
    out = row_to_dict(run)
    out["creator_handoff"] = json_loads(out.pop("creator_handoff_json", None))
    out["units"] = [row_to_dict(u) for u in units]
    return out


@app.get("/api/units/{unit_id}")
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


@app.put("/api/units/{unit_id}/payload")
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
        log_event(
            conn,
            "review_payload_saved",
            "review_unit",
            unit_id,
            unit["pipeline_run_id"],
            {"revision": new_rev},
        )
    return {"revision": new_rev}


@app.patch("/api/units/{unit_id}")
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


@app.post("/api/units/{unit_id}/approve")
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
        log_event(
            conn,
            "review_unit_approved",
            "review_unit",
            unit_id,
            unit["pipeline_run_id"],
            {"revision": rev["revision"]},
        )
    return {"approved_revision_id": rev["id"], "revision": rev["revision"]}


@app.post("/api/units/{unit_id}/export")
def export_unit(unit_id: str) -> dict[str, Any]:
    with db() as conn:
        unit = conn.execute("SELECT * FROM review_unit WHERE id = ?", (unit_id,)).fetchone()
        if not unit:
            raise HTTPException(404, "Unit not found")
        rev = None
        if unit["approved_revision_id"]:
            rev = conn.execute(
                "SELECT * FROM review_payload_revision WHERE id = ?",
                (unit["approved_revision_id"],),
            ).fetchone()
        if not rev:
            rev = _latest_revision(conn, unit_id)
        if not rev:
            raise HTTPException(400, "No payload")
        payload = json.loads(rev["payload_json"])
    meta = {
        "studio_run_id": unit["pipeline_run_id"],
        "studio_unit_id": unit_id,
        "approved_revision": rev["revision"],
        "exported_at": utc_now(),
    }
    payload["studio_export"] = meta

    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
    out_dir = EXPORT_ROOT / unit["pipeline_run_id"] / unit["jira_key"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "review-payload.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")

    rel = review_ref_relative(str(out_path))
    return {
        "path": str(out_path),
        "review_ref": rel,
        "jira_key": unit["jira_key"],
    }


@app.post("/api/units/{unit_id}/send-to-creator")
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
        unit_row = dict(unit)
    export = export_unit(unit_id)
    with db() as conn:
        rev_row = conn.execute(
            "SELECT payload_json FROM review_payload_revision WHERE id = ?",
            (unit_row["approved_revision_id"],),
        ).fetchone()
    if not rev_row:
        raise HTTPException(400, "Approved revision payload not found")
    payload = json.loads(rev_row["payload_json"])
    gate = (payload.get("gate") or {}).get("status")
    prompt = build_creator_prompt(
        review_ref=export["review_ref"],
        jira_key=unit_row["jira_key"],
        creator_run_id=unit_row["jira_key"],
        gate_status=gate,
        readiness_label=payload_readiness(payload),
        qa_planning_fit=unit_row["qa_planning_fit"],
        pipeline_run_id=unit_row["pipeline_run_id"],
    )
    return {
        "review_ref": export["review_ref"],
        "creator_run_id": unit_row["jira_key"],
        "prompt": prompt,
        "suite_payload_hint": f"Trinity/creator/artifacts/{unit_meta['jira_key']}/suite-payload.json",
        "creator_studio_path": "/creator",
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


@app.get("/api/runs/{run_id}/creator-handoff")
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


@app.get("/api/stats")
def global_stats() -> dict[str, Any]:
    with db() as conn:
        runs = conn.execute("SELECT COUNT(*) FROM pipeline_run").fetchone()[0]
        units = conn.execute("SELECT COUNT(*) FROM review_unit").fetchone()[0]
        approved = conn.execute(
            "SELECT COUNT(*) FROM review_unit WHERE approved_revision_id IS NOT NULL"
        ).fetchone()[0]
        findings_open = 0
        questions_open = 0
        for row in conn.execute(
            """
            SELECT r.payload_json FROM review_payload_revision r
            INNER JOIN (
              SELECT review_unit_id, MAX(revision) AS mr FROM review_payload_revision GROUP BY review_unit_id
            ) latest ON latest.review_unit_id = r.review_unit_id AND latest.mr = r.revision
            """
        ):
            p = json.loads(row["payload_json"])
            for f in p.get("findings") or []:
                if f.get("status", "open") == "open":
                    findings_open += 1
            for q in p.get("questions") or []:
                if q.get("status", "open") == "open":
                    questions_open += 1
        creator_runs = conn.execute("SELECT COUNT(*) FROM creator_run").fetchone()[0]
        tests = conn.execute("SELECT COUNT(*) FROM test_case_row").fetchone()[0]
        tests_approved = conn.execute(
            "SELECT COUNT(*) FROM test_case_row WHERE human_review_status = 'approved'"
        ).fetchone()[0]
        automatable = conn.execute(
            "SELECT COUNT(*) FROM test_case_row WHERE automation_candidate = 1"
        ).fetchone()[0]
        imported_xray = conn.execute(
            "SELECT COUNT(*) FROM test_case_row WHERE xray_test_key IS NOT NULL"
        ).fetchone()[0]
    return {
        "pipeline_runs": runs,
        "review_units": units,
        "review_units_approved": approved,
        "open_findings_latest": findings_open,
        "open_questions_latest": questions_open,
        "creator_runs": creator_runs,
        "test_cases": tests,
        "test_cases_approved": tests_approved,
        "test_cases_automation_candidate": automatable,
        "test_cases_imported_xray": imported_xray,
    }


@app.get("/api/creator-runs")
def list_creator_runs() -> list[dict[str, Any]]:
    with db() as conn:
        rows = conn.execute(
            """
            SELECT c.*,
              (SELECT COUNT(*) FROM test_case_row t WHERE t.creator_run_id = c.id) AS test_count
            FROM creator_run c ORDER BY c.updated_at DESC
            """
        ).fetchall()
    return [row_to_dict(r) for r in rows]


@app.get("/api/creator-runs/{run_id}")
def get_creator_run(run_id: str) -> dict[str, Any]:
    with db() as conn:
        run = conn.execute("SELECT * FROM creator_run WHERE id = ?", (run_id,)).fetchone()
        if not run:
            raise HTTPException(404, "Creator run not found")
        tests = conn.execute(
            "SELECT * FROM test_case_row WHERE creator_run_id = ? ORDER BY draft_id",
            (run_id,),
        ).fetchall()
    return {"run": row_to_dict(run), "tests": [row_to_dict(t) for t in tests]}


@app.get("/api/tests/{test_id}")
def get_test(test_id: str) -> dict[str, Any]:
    with db() as conn:
        row = conn.execute("SELECT * FROM test_case_row WHERE id = ?", (test_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Test not found")
        rev = conn.execute(
            """
            SELECT * FROM test_case_revision WHERE test_case_row_id = ?
            ORDER BY revision DESC LIMIT 1
            """,
            (test_id,),
        ).fetchone()
    return {"test": row_to_dict(row), "case": json.loads(rev["case_json"]) if rev else None}


@app.put("/api/tests/{test_id}")
def save_test(test_id: str, body: SaveTestCaseBody) -> dict[str, Any]:
    now = utc_now()
    status = body.human_review_status or "edited"
    with db() as conn:
        row = conn.execute("SELECT * FROM test_case_row WHERE id = ?", (test_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Test not found")
        max_rev = conn.execute(
            "SELECT COALESCE(MAX(revision), 0) FROM test_case_revision WHERE test_case_row_id = ?",
            (test_id,),
        ).fetchone()[0]
        new_rev = max_rev + 1
        conn.execute(
            """
            INSERT INTO test_case_revision (test_case_row_id, revision, case_json, source, created_at, created_by)
            VALUES (?, ?, ?, 'human', ?, ?)
            """,
            (test_id, new_rev, json.dumps(body.case, ensure_ascii=False), now, body.created_by),
        )
        auto = 1 if (body.case.get("test_type") or "").lower() in ("cucumber", "generic") else 0
        conn.execute(
            """
            UPDATE test_case_row SET title = ?, execution_tier = ?, test_type = ?,
              human_review_status = ?, automation_candidate = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                body.case.get("title") or row["title"],
                body.case.get("execution_tier"),
                body.case.get("test_type"),
                status,
                auto,
                now,
                test_id,
            ),
        )
    return {"revision": new_rev}


STATIC_FALLBACK = Path(__file__).resolve().parent / "static"
WEB_DIST = Path(__file__).resolve().parent.parent / "web" / "dist"


def _ui_index() -> FileResponse:
    return FileResponse(
        STATIC_FALLBACK / "index.html",
        headers={"Cache-Control": "no-cache"},
    )


@app.get("/")
def root_ui():
    """Built-in UI — no npm. Set QA_STUDIO_REACT=1 to serve web/dist instead."""
    use_react = os.environ.get("QA_STUDIO_REACT", "").lower() in ("1", "true", "yes")
    if use_react and WEB_DIST.is_dir() and (WEB_DIST / "index.html").is_file():
        return FileResponse(WEB_DIST / "index.html")
    return _ui_index()


@app.get("/static/{filename}")
def static_asset(filename: str):
    if "/" in filename or filename.startswith("."):
        raise HTTPException(status_code=404, detail="Not found")
    path = STATIC_FALLBACK / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(path)


if WEB_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=WEB_DIST / "assets"), name="assets")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("QA_STUDIO_PORT", "8765"))
    uvicorn.run("app:app", host="127.0.0.1", port=port, reload=False)
