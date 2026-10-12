"""Build Creator Profile B suite report (data + folder)."""

from __future__ import annotations

import html
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = REPO_ROOT / "creator" / "suite-report-template"


def _escape_script_json(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, ensure_ascii=True, indent=2)
    return raw.replace("</", "<\\/")


def steps_to_html(steps: list[dict[str, Any]]) -> tuple[str, str]:
    if not steps:
        return "", ""
    plain_parts: list[str] = []
    rows: list[str] = []
    for s in steps:
        n = s.get("step") or s.get("number") or len(rows) + 1
        action = s.get("action") or s.get("step") or ""
        if isinstance(action, int):
            action = s.get("action", "")
        expected = s.get("result") or s.get("expected_result") or ""
        data = s.get("data") or s.get("test_data") or ""
        plain_parts.append(f"{n} {action} {expected}")
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(n))}</td>"
            f"<td>{html.escape(str(action))}</td>"
            f"<td>{html.escape(str(data)) if data else '—'}</td>"
            f"<td>{html.escape(str(expected))}</td>"
            "</tr>"
        )
    table = (
        '<table class="step-table"><thead><tr>'
        "<th>#</th><th>Action</th><th>Data</th><th>Expected</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )
    return table, " ".join(plain_parts)


def row_from_case(
    case: dict[str, Any],
    studio: dict[str, Any] | None = None,
) -> dict[str, Any]:
    studio = studio or {}
    steps = case.get("steps") or []
    steps_html, steps_plain = steps_to_html(steps)
    draft_id = case.get("draft_id") or studio.get("draft_id") or "TC-?"
    review = studio.get("human_review_status") or "batch"
    marked = bool(studio.get("marked_for_xray_import"))
    approved = review == "approved"
    tier = case.get("execution_tier") or ""
    return {
        "draft_id": draft_id,
        "title": case.get("title") or draft_id,
        "execution_tier": tier,
        "test_pattern": case.get("test_pattern") or "",
        "test_type": case.get("test_type") or "",
        "human_review_status": review,
        "automation_fit": case.get("automation_fit") or studio.get("automation_fit") or "",
        "automation_candidate": bool(
            case.get("automation_candidate") or studio.get("automation_candidate")
        ),
        "deferrable": bool(case.get("deferrable")),
        "marked_for_xray_import": marked,
        "import_ready": approved and marked,
        "xray_test_key": studio.get("xray_test_key"),
        "linked_requirement_keys": list(case.get("linked_requirement_keys") or []),
        "linked_ac_ids": list(case.get("linked_ac_ids") or []),
        "step_count": len(steps),
        "steps_html": steps_html,
        "steps_plain": steps_plain,
        "sortValues": {
            "draft_id": draft_id,
            "title": case.get("title") or "",
            "execution_tier": tier,
            "test_pattern": case.get("test_pattern") or "",
            "human_review_status": review,
            "step_count": str(len(steps)).zfill(4),
        },
    }


def build_report_payload(
    *,
    run_id: str,
    batch: dict[str, Any],
    studio_by_draft: dict[str, dict[str, Any]] | None = None,
    coverage_gap_count: int | None = None,
) -> dict[str, Any]:
    studio_by_draft = studio_by_draft or {}
    tests = batch.get("tests") or []
    rows = []
    for tc in tests:
        draft_id = tc.get("draft_id") or ""
        rows.append(row_from_case(tc, studio_by_draft.get(draft_id)))

    req_keys = batch.get("source_requirement_keys") or []
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    gap_note = ""
    if coverage_gap_count is not None and coverage_gap_count > 0:
        gap_note = f" Coverage review: {coverage_gap_count} matrix gap(s) in Studio."

    return {
        "meta": {
            "title": f"Test suite — {run_id}",
            "subtitle": f"Generated {generated} · {len(rows)} tests · requirements: {', '.join(req_keys) or '—'}",
            "noteHtml": (
                "Interactive Profile B suite report for Creator batches. "
                "Filter by tier, pattern, review status, and automation. "
                "Step tables below match the filtered rows."
                + html.escape(gap_note)
            ),
            "run_id": run_id,
            "generated": generated,
        },
        "filters": [
            {"id": "tier-p0", "label": "P0 Critical", "shortLabel": "P0"},
            {"id": "tier-p1", "label": "P1 Mandatory", "shortLabel": "P1"},
            {"id": "pattern-journey", "label": "Journey tests", "shortLabel": "Journey"},
            {"id": "review-approved", "label": "Approved in Studio", "shortLabel": "Approved"},
            {"id": "review-pending", "label": "Pending review", "shortLabel": "Pending"},
            {"id": "automation-candidate", "label": "Automation candidate", "shortLabel": "Auto cand."},
            {"id": "import-ready", "label": "Ready for Xray import", "shortLabel": "Import ready"},
            {"id": "deferrable", "label": "Deferrable", "shortLabel": "Deferrable"},
        ],
        "stats": [
            {"key": "tests", "label": "Tests visible"},
            {"key": "journeys", "label": "Journeys"},
            {"key": "approved", "label": "Approved"},
            {"key": "importReady", "label": "Import ready"},
            {"key": "steps", "label": "Total steps"},
        ],
        "columns": [
            {"key": "draft_id", "label": "ID"},
            {"key": "title", "label": "Title"},
            {"key": "execution_tier", "label": "Tier"},
            {"key": "test_pattern", "label": "Pattern"},
            {"key": "human_review_status", "label": "Review"},
            {"key": "automation_fit", "label": "Automation"},
            {"key": "linked_requirement_keys", "label": "Requirements"},
            {"key": "linked_ac_ids", "label": "AC / goals"},
            {"key": "step_count", "label": "Steps"},
            {"key": "xray", "label": "Xray"},
        ],
        "rows": rows,
    }


def write_report_data_js(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = _escape_script_json(payload)
    path.write_text(f"window.REPORT_DATA = {body};\n", encoding="utf-8")


def write_suite_report(out_dir: Path, payload: dict[str, Any]) -> Path:
    if not TEMPLATE_DIR.is_dir():
        raise FileNotFoundError(f"Suite template missing: {TEMPLATE_DIR}")
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TEMPLATE_DIR / "index.html", out_dir / "index.html")
    shutil.copy2(TEMPLATE_DIR / "README.md", out_dir / "README.md")
    shutil.copytree(TEMPLATE_DIR / "assets", out_dir / "assets", dirs_exist_ok=True)
    write_report_data_js(out_dir / "data" / "report-data.js", payload)
    return out_dir / "index.html"
