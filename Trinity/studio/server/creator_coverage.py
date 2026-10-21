"""Epic coverage matrix from imported TestCaseDraft batch + Studio review state."""

from __future__ import annotations

import json
from typing import Any


def _latest_case_json_by_row(conn: Any, row_ids: list[str]) -> dict[str, dict[str, Any]]:
    if not row_ids:
        return {}
    placeholders = ",".join("?" * len(row_ids))
    rows = conn.execute(
        f"""
        SELECT r.test_case_row_id, r.case_json
        FROM test_case_revision r
        INNER JOIN (
          SELECT test_case_row_id, MAX(revision) AS max_rev
          FROM test_case_revision
          WHERE test_case_row_id IN ({placeholders})
          GROUP BY test_case_row_id
        ) latest
          ON latest.test_case_row_id = r.test_case_row_id AND latest.max_rev = r.revision
        """,
        row_ids,
    ).fetchall()
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        try:
            out[row["test_case_row_id"]] = json.loads(row["case_json"])
        except (TypeError, json.JSONDecodeError):
            out[row["test_case_row_id"]] = {}
    return out


def cq02_catalog_warnings(cases: dict[str, dict[str, Any]]) -> list[str]:
    """CQ-02: warn when coverage_catalog_id disagrees with linked_ac_ids."""
    warnings: list[str] = []
    for row_id, case in cases.items():
        catalog = case.get("coverage_catalog_id")
        if not catalog or not isinstance(catalog, str):
            continue
        linked = [str(x) for x in (case.get("linked_ac_ids") or []) if x]
        if not linked:
            continue
        if catalog not in linked:
            draft = case.get("draft_id") or row_id
            warnings.append(
                f"CQ-02: {draft} has coverage_catalog_id={catalog} not in linked_ac_ids={linked}"
            )
    return warnings


def _ac_to_drafts(
    tests: list[dict[str, Any]],
    cases: dict[str, dict[str, Any]],
    *,
    approved_only: bool,
) -> dict[str, list[str]]:
    ac_map: dict[str, list[str]] = {}
    for t in tests:
        if approved_only and t.get("human_review_status") != "approved":
            continue
        draft_id = t.get("draft_id") or ""
        case = cases.get(t["id"], {})
        linked = case.get("linked_ac_ids") or []
        catalog = case.get("coverage_catalog_id")
        if catalog and isinstance(catalog, str):
            linked = list(linked) + [catalog]
        for ac_id in linked:
            if not ac_id:
                continue
            ac_map.setdefault(str(ac_id), [])
            if draft_id and draft_id not in ac_map[str(ac_id)]:
                ac_map[str(ac_id)].append(draft_id)
    return ac_map


def load_latest_batch(conn: Any, creator_run_id: str) -> tuple[dict[str, Any] | None, int | None]:
    row = conn.execute(
        """
        SELECT batch_json, revision FROM test_case_batch_revision
        WHERE creator_run_id = ? ORDER BY revision DESC LIMIT 1
        """,
        (creator_run_id,),
    ).fetchone()
    if not row:
        return None, None
    return json.loads(row["batch_json"]), int(row["revision"])


def format_coverage_matrix_for_prompt(report: dict[str, Any] | None) -> str:
    """AQ-03: short markdown for the Importer Cursor handoff."""
    if not report:
        return "_No coverage_report in batch — matrix not included._"
    lines: list[str] = []
    matrix = report.get("matrix") or []
    if matrix:
        lines.append("| AC / goal | Batch status | Covered by |")
        lines.append("|-----------|--------------|------------|")
        for row in matrix[:20]:
            ac = row.get("ac_id") or "—"
            st = row.get("status") or "—"
            by = ", ".join(row.get("covered_by") or []) or "—"
            lines.append(f"| {ac} | {st} | {by} |")
        if len(matrix) > 20:
            lines.append(f"| … | | +{len(matrix) - 20} more rows |")
    uncovered = report.get("uncovered_ac_ids") or []
    goals = report.get("uncovered_goals") or []
    if uncovered:
        lines.append(f"\n**Uncovered AC ids:** {', '.join(uncovered)}")
    if goals:
        lines.append("\n**Uncovered goals:**")
        for g in goals[:8]:
            lines.append(f"- {g}")
    warnings = report.get("warnings") or []
    if warnings:
        lines.append("\n**Coverage warnings:**")
        for w in warnings[:5]:
            lines.append(f"- {w}")
    return "\n".join(lines) if lines else "_Empty coverage_report._"


def build_coverage_summary(
    conn: Any,
    creator_run_id: str,
    tests: list[dict[str, Any]],
) -> dict[str, Any]:
    batch, batch_revision = load_latest_batch(conn, creator_run_id)
    test_list = list(tests)
    row_ids = [t["id"] for t in test_list if t.get("id")]
    cases = _latest_case_json_by_row(conn, row_ids)
    approved_ac_map = _ac_to_drafts(test_list, cases, approved_only=True)
    all_ac_map = _ac_to_drafts(test_list, cases, approved_only=False)

    cq_warnings = cq02_catalog_warnings(cases)
    if not batch:
        orphan_approved = sorted(approved_ac_map.keys())
        return {
            "available": False,
            "batch_revision": None,
            "message": "No imported batch JSON — coverage matrix appears after TestCaseDraft import.",
            "approved_ac_ids": orphan_approved,
            "approved_ac_map": approved_ac_map,
            "gap_count": len(orphan_approved),
            "warnings": cq_warnings,
        }

    report = batch.get("coverage_report") or {}
    matrix_in = report.get("matrix") or []
    uncovered_ac_ids = list(report.get("uncovered_ac_ids") or [])
    uncovered_goals = list(report.get("uncovered_goals") or [])
    warnings = list(report.get("warnings") or [])
    warnings.extend(cq02_catalog_warnings(cases))

    matrix_rows: list[dict[str, Any]] = []
    matrix_ac_ids: set[str] = set()

    for item in matrix_in:
        ac_id = str(item.get("ac_id") or "")
        if ac_id:
            matrix_ac_ids.add(ac_id)
        batch_status = str(item.get("status") or "UNCOVERED")
        batch_covered_by = list(item.get("covered_by") or [])
        approved_by = approved_ac_map.get(ac_id, []) if ac_id else []
        all_by = all_ac_map.get(ac_id, []) if ac_id else []

        review_gap = False
        gap_reason: str | None = None
        if batch_status in ("UNCOVERED", "PARTIAL"):
            review_gap = True
            gap_reason = f"Batch marks {batch_status}"
        elif ac_id in uncovered_ac_ids:
            review_gap = True
            gap_reason = "Listed in uncovered_ac_ids"
        elif batch_status == "Covered" and not approved_by:
            review_gap = True
            gap_reason = "No approved test links this AC/goal id"
        elif batch_status == "Covered" and approved_by and set(approved_by) != set(batch_covered_by):
            # Soft signal only when batch claimed drafts differ from approved linkage
            if not set(batch_covered_by) & set(approved_by):
                review_gap = True
                gap_reason = "Approved tests do not match batch covered_by"

        matrix_rows.append(
            {
                "ac_id": ac_id,
                "jira_key": item.get("jira_key"),
                "batch_status": batch_status,
                "batch_covered_by": batch_covered_by,
                "approved_covered_by": approved_by,
                "draft_covered_by": all_by,
                "review_gap": review_gap,
                "gap_reason": gap_reason,
            }
        )

    for ac_id in uncovered_ac_ids:
        if ac_id not in matrix_ac_ids:
            matrix_rows.append(
                {
                    "ac_id": ac_id,
                    "jira_key": None,
                    "batch_status": "UNCOVERED",
                    "batch_covered_by": [],
                    "approved_covered_by": approved_ac_map.get(ac_id, []),
                    "draft_covered_by": all_ac_map.get(ac_id, []),
                    "review_gap": not approved_ac_map.get(ac_id),
                    "gap_reason": "uncovered_ac_ids (not in matrix[])",
                }
            )

    gap_count = sum(1 for r in matrix_rows if r["review_gap"]) + len(uncovered_goals)

    return {
        "available": True,
        "batch_revision": batch_revision,
        "source_requirement_keys": batch.get("source_requirement_keys") or [],
        "uncovered_ac_ids": uncovered_ac_ids,
        "uncovered_goals": uncovered_goals,
        "warnings": warnings,
        "catalog_coverage_pct": report.get("catalog_coverage_pct"),
        "catalog_coverage": report.get("catalog_coverage") or [],
        "matrix": matrix_rows,
        "gap_count": gap_count,
        "approved_ac_map": approved_ac_map,
    }
