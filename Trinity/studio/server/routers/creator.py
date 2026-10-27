"""Creator runs, golden corpora, and test case review."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, HTTPException

from api_models import BulkTestsBody, PatchTestBody, RunLabelBody, SaveTestCaseBody
from creator_coverage import build_coverage_summary
from creator_export import automation_candidate_flag, automation_fit_value, validate_import_mark
from creator_golden import golden_info_for_product, list_creator_products, list_golden_corpora
from creator_suite_report import export_suite_report_for_run
from creator_export import build_importer_payload, write_importer_export
from db import db, row_to_dict, utc_now
from run_management import delete_creator_run, rename_creator_run
from studio_paths import EXPORT_ROOT
from personas import docs_repo_root
from telemetry import record_event, validate_rejection_reason

router = APIRouter(tags=["creator"])


@router.get("/api/creator/golden-corpora")
def api_golden_corpora() -> dict[str, Any]:
    return {"corpora": list_golden_corpora()}


@router.get("/api/creator/products")
def api_creator_products() -> dict[str, Any]:
    return {"products": list_creator_products()}


@router.get("/api/creator/products/{product_id}/golden")
def api_product_golden(product_id: str) -> dict[str, Any]:
    return golden_info_for_product(product_id)


@router.get("/api/creator-runs")
def list_creator_runs() -> list[dict[str, Any]]:
    with db() as conn:
        rows = conn.execute(
            """
            SELECT c.*,
              (SELECT COUNT(*) FROM test_case_row t WHERE t.creator_run_id = c.id) AS test_count,
              (SELECT COALESCE(MAX(revision), 0) FROM test_case_batch_revision b WHERE b.creator_run_id = c.id) AS batch_revision
            FROM creator_run c ORDER BY c.updated_at DESC
            """
        ).fetchall()
    return [row_to_dict(r) for r in rows]


@router.get("/api/creator-runs/{run_id}")
def get_creator_run(run_id: str) -> dict[str, Any]:
    with db() as conn:
        run = conn.execute("SELECT * FROM creator_run WHERE id = ?", (run_id,)).fetchone()
        if not run:
            raise HTTPException(404, "Creator run not found")
        tests = conn.execute(
            "SELECT * FROM test_case_row WHERE creator_run_id = ? ORDER BY draft_id",
            (run_id,),
        ).fetchall()
        ready = sum(
            1
            for t in tests
            if t["human_review_status"] == "approved" and t["marked_for_xray_import"]
        )
        test_dicts = [row_to_dict(t) for t in tests]
        coverage = build_coverage_summary(conn, run_id, test_dicts)
    return {
        "run": row_to_dict(run),
        "tests": test_dicts,
        "summary": {
            "total": len(tests),
            "approved": sum(1 for t in tests if t["human_review_status"] == "approved"),
            "rejected": sum(1 for t in tests if t["human_review_status"] == "rejected"),
            "ready_for_import": ready,
        },
        "coverage": coverage,
    }


@router.patch("/api/creator-runs/{run_id}")
def api_patch_creator_run(run_id: str, body: RunLabelBody) -> dict[str, Any]:
    try:
        with db() as conn:
            return rename_creator_run(conn, run_id, body.label)
    except KeyError:
        raise HTTPException(404, "Creator run not found") from None
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@router.delete("/api/creator-runs/{run_id}")
def api_delete_creator_run(run_id: str) -> dict[str, Any]:
    try:
        with db() as conn:
            return delete_creator_run(conn, run_id)
    except KeyError:
        raise HTTPException(404, "Creator run not found") from None


@router.get("/api/tests/{test_id}")
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
        run = conn.execute(
            """
            SELECT cr.pipeline_run_id, ru.jira_key
            FROM creator_run cr
            LEFT JOIN review_unit ru ON ru.id = cr.review_unit_id
            WHERE cr.id = ?
            """,
            (row["creator_run_id"],),
        ).fetchone()
    test = row_to_dict(row) or {}
    if run:
        test["pipeline_run_id"] = run["pipeline_run_id"]
        test["jira_key"] = run["jira_key"]
    return {"test": test, "case": json.loads(rev["case_json"]) if rev else None}


def _emit_test_case_review(
    conn: Any,
    row: Any,
    status: str,
    rejection_reason: str | None,
    *,
    source: str = "studio",
) -> None:
    reason = validate_rejection_reason(rejection_reason, status)
    run = conn.execute(
        "SELECT pipeline_run_id FROM creator_run WHERE id = ?",
        (row["creator_run_id"],),
    ).fetchone()
    pipeline_run_id = run["pipeline_run_id"] if run else None
    record_event(
        conn,
        "test_case_review",
        "test_case",
        row["id"],
        pipeline_run_id,
        {
            "creator_run_id": row["creator_run_id"],
            "draft_id": row["draft_id"],
            "human_review_status": status,
            "rejection_reason": reason,
            "marked_for_xray_import": bool(row["marked_for_xray_import"]),
            "source": source,
        },
    )


def _resolve_test_row_update(
    row: Any,
    body_status: str | None,
    body_marked: bool | None,
    case: dict[str, Any],
) -> tuple[str, int, str | None, int]:
    status = body_status or row["human_review_status"] or "edited"
    if status == "pending":
        status = "edited"
    marked = (
        int(body_marked)
        if body_marked is not None
        else int(row["marked_for_xray_import"] or 0)
    )
    if status == "rejected":
        marked = 0
    try:
        validate_import_mark(status, bool(marked))
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    auto = automation_candidate_flag(case)
    fit = automation_fit_value(case)
    return status, auto, fit, marked


@router.put("/api/tests/{test_id}")
def save_test(test_id: str, body: SaveTestCaseBody) -> dict[str, Any]:
    now = utc_now()
    with db() as conn:
        row = conn.execute("SELECT * FROM test_case_row WHERE id = ?", (test_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Test not found")
        if body.human_review_status is not None:
            status_in = body.human_review_status
        elif row["human_review_status"] == "pending":
            status_in = "edited"
        else:
            status_in = row["human_review_status"]
        if status_in == "pending":
            status_in = "edited"
        status, auto, fit, marked = _resolve_test_row_update(
            row, status_in, body.marked_for_xray_import, body.case
        )
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
        rejection_reason: str | None = None
        if status == "rejected":
            rejection_reason = validate_rejection_reason(body.rejection_reason, status)
        elif status == "approved":
            rejection_reason = None
        else:
            rejection_reason = row["rejection_reason"]

        conn.execute(
            """
            UPDATE test_case_row SET title = ?, execution_tier = ?, test_type = ?,
              human_review_status = ?, automation_candidate = ?, automation_fit = ?,
              marked_for_xray_import = ?, rejection_reason = ?, current_revision_id = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                body.case.get("title") or row["title"],
                body.case.get("execution_tier"),
                body.case.get("test_type"),
                status,
                auto,
                fit,
                marked,
                rejection_reason,
                new_rev,
                now,
                test_id,
            ),
        )
        if body.human_review_status is not None and body.human_review_status != row["human_review_status"]:
            updated = conn.execute(
                "SELECT * FROM test_case_row WHERE id = ?", (test_id,)
            ).fetchone()
            _emit_test_case_review(conn, updated, status, rejection_reason)
    return {"revision": new_rev, "human_review_status": status, "marked_for_xray_import": bool(marked)}


@router.patch("/api/tests/{test_id}")
def patch_test(test_id: str, body: PatchTestBody) -> dict[str, Any]:
    now = utc_now()
    with db() as conn:
        row = conn.execute("SELECT * FROM test_case_row WHERE id = ?", (test_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Test not found")
        status = body.human_review_status or row["human_review_status"]
        marked = row["marked_for_xray_import"]
        if body.marked_for_xray_import is not None:
            marked = int(body.marked_for_xray_import)
        if body.human_review_status == "rejected":
            marked = 0
        try:
            validate_import_mark(status, bool(marked))
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
        rejection_reason: str | None = row["rejection_reason"]
        if body.human_review_status is not None:
            if status == "rejected":
                try:
                    rejection_reason = validate_rejection_reason(body.rejection_reason, status)
                except ValueError as exc:
                    raise HTTPException(400, str(exc)) from exc
            elif status == "approved":
                rejection_reason = None
        conn.execute(
            """
            UPDATE test_case_row SET human_review_status = ?, marked_for_xray_import = ?,
              rejection_reason = ?, updated_at = ?
            WHERE id = ?
            """,
            (status, marked, rejection_reason, now, test_id),
        )
        if body.human_review_status is not None and body.human_review_status != row["human_review_status"]:
            updated = conn.execute(
                "SELECT * FROM test_case_row WHERE id = ?", (test_id,)
            ).fetchone()
            _emit_test_case_review(conn, updated, status, rejection_reason)
    return {"human_review_status": status, "marked_for_xray_import": bool(marked)}


@router.post("/api/creator-runs/{run_id}/bulk-test-review")
def bulk_test_review(run_id: str, body: BulkTestsBody) -> dict[str, Any]:
    now = utc_now()
    updated = 0
    deferrable_marked: list[str] = []
    if body.human_review_status == "rejected":
        try:
            validate_rejection_reason(body.rejection_reason, "rejected")
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
    with db() as conn:
        for test_id in body.test_ids:
            row = conn.execute(
                "SELECT * FROM test_case_row WHERE id = ? AND creator_run_id = ?",
                (test_id, run_id),
            ).fetchone()
            if not row:
                continue
            status = body.human_review_status or row["human_review_status"]
            marked = row["marked_for_xray_import"]
            if body.marked_for_xray_import is not None:
                marked = int(body.marked_for_xray_import)
            if body.human_review_status == "rejected":
                marked = 0
            if body.marked_for_xray_import and body.human_review_status is None:
                status = row["human_review_status"]
                if status != "approved":
                    continue
            try:
                validate_import_mark(status, bool(marked))
            except ValueError:
                continue
            if marked:
                rev = conn.execute(
                    """
                    SELECT case_json FROM test_case_revision
                    WHERE test_case_row_id = ? ORDER BY revision DESC LIMIT 1
                    """,
                    (test_id,),
                ).fetchone()
                if rev:
                    try:
                        case = json.loads(rev["case_json"])
                        if case.get("deferrable"):
                            deferrable_marked.append(row["draft_id"])
                    except json.JSONDecodeError:
                        pass
            rejection_reason: str | None = row["rejection_reason"]
            if body.human_review_status == "rejected":
                rejection_reason = body.rejection_reason
            elif body.human_review_status == "approved":
                rejection_reason = None
            prev_status = row["human_review_status"]
            conn.execute(
                """
                UPDATE test_case_row SET human_review_status = ?, marked_for_xray_import = ?,
                  rejection_reason = ?, updated_at = ?
                WHERE id = ?
                """,
                (status, marked, rejection_reason, now, test_id),
            )
            if body.human_review_status is not None and body.human_review_status != prev_status:
                updated_row = conn.execute(
                    "SELECT * FROM test_case_row WHERE id = ?", (test_id,)
                ).fetchone()
                _emit_test_case_review(
                    conn, updated_row, status, rejection_reason, source="bulk"
                )
            updated += 1
    out: dict[str, Any] = {"updated": updated}
    if deferrable_marked:
        out["warnings"] = [
            f"Marked deferrable test(s) for Xray import: {', '.join(deferrable_marked)} (IQ-08 — review before execute)."
        ]
    return out


@router.post("/api/creator-runs/{run_id}/export-for-importer")
def export_creator_for_importer(run_id: str) -> dict[str, Any]:
    with db() as conn:
        try:
            payload = build_importer_payload(conn, run_id)
        except KeyError:
            raise HTTPException(404, "Creator run not found") from None
        if not payload["tests"]:
            raise HTTPException(
                400,
                "No tests approved and marked for Xray import",
            )
        out_path, export_warnings = write_importer_export(conn, run_id, EXPORT_ROOT)
        rel = out_path
        try:
            rel = out_path.resolve().relative_to(docs_repo_root().resolve())
        except ValueError:
            rel = out_path
        record_event(
            conn,
            "creator_importer_export",
            "creator_run",
            run_id,
            None,
            {"path": str(rel), "test_count": payload["test_count"]},
        )
    return {
        "path": str(rel),
        "absolute_path": str(out_path),
        "test_count": payload["test_count"],
        "export_preflight_warnings": export_warnings,
        "payload": payload,
    }


@router.post("/api/creator-runs/{run_id}/export-suite-report")
def export_creator_suite_report(run_id: str) -> dict[str, Any]:
    with db() as conn:
        run = conn.execute("SELECT id FROM creator_run WHERE id = ?", (run_id,)).fetchone()
        if not run:
            raise HTTPException(404, "Creator run not found")
        try:
            index_path, test_count = export_suite_report_for_run(conn, run_id, EXPORT_ROOT)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from None
        rel = index_path
        try:
            rel = index_path.resolve().relative_to(docs_repo_root().resolve())
        except ValueError:
            rel = index_path
        record_event(
            conn,
            "creator_suite_report_export",
            "creator_run",
            run_id,
            None,
            {"path": str(rel), "test_count": test_count},
        )
    return {
        "path": str(rel),
        "absolute_path": str(index_path),
        "index_html": str(index_path),
        "test_count": test_count,
        "profile": "B",
    }

