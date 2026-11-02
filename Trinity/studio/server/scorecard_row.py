"""Map a pipeline run report to one Usage Scorecard row."""

from __future__ import annotations

from typing import Any

from coverage_profile import coerce_profile_id, profile_by_id
from scorecard_config import product_tab_config
from telemetry import operator_name


def _pct(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        return "—"
    return f"{100.0 * numerator / denominator:.1f}%"


def _minutes_from_phase(phases: list[dict[str, Any]], phase_key: str) -> int | None:
    for phase in phases:
        if phase.get("phase") != phase_key:
            continue
        seconds = phase.get("duration_seconds")
        if seconds is None:
            return None
        return max(0, int(round(float(seconds) / 60.0)))
    return None


def _sheet_coverage_label(profile_id: str) -> str:
    pid = coerce_profile_id(profile_id)
    label = profile_by_id(pid)["label"]
    if pid in ("balanced", "thorough"):
        return "Comprehensive"
    if pid in ("smoke", "core"):
        return "Standard"
    if pid == "edge":
        return "Exploratory"
    return label


def _infer_use_case(report: dict[str, Any]) -> str:
    summary = report.get("summary") or {}
    drafted = int(summary.get("test_cases_drafted_total") or 0)
    creator_runs = int(summary.get("creator_runs_linked") or 0)
    amended = int(summary.get("test_cases_amended_total") or 0)
    if creator_runs == 0 and drafted == 0:
        return "review"
    if amended > 0 and amended >= max(1, drafted // 2):
        return "modify"
    return "create"


def _tc_review_counts(conn: Any, pipeline_run_id: str) -> tuple[int, int, int]:
    rows = conn.execute(
        """
        SELECT t.human_review_status, COUNT(*) AS c
        FROM test_case_row t
        JOIN creator_run cr ON cr.id = t.creator_run_id
        WHERE cr.pipeline_run_id = ?
        GROUP BY t.human_review_status
        """,
        (pipeline_run_id,),
    ).fetchall()
    approved = rejected = pending = 0
    for row in rows:
        status = row["human_review_status"]
        count = int(row["c"])
        if status == "approved":
            approved = count
        elif status == "rejected":
            rejected = count
        elif status in ("pending", "edited"):
            pending += count
    return approved, rejected, pending


def build_scorecard_row(
    conn: Any,
    *,
    pipeline_run_id: str,
    report: dict[str, Any],
    external_run_id: str | None = None,
) -> dict[str, Any]:
    """Return tab metadata plus ordered cell values for the product sheet."""
    run = conn.execute(
        "SELECT product_id, operator_name, operator_id, coverage_profile FROM pipeline_run WHERE id = ?",
        (pipeline_run_id,),
    ).fetchone()
    if not run:
        raise KeyError(pipeline_run_id)

    product_cfg = product_tab_config(run["product_id"])
    summary = report.get("summary") or {}
    phases = report.get("phases") or []
    ctx = report.get("product_context") or {}

    epics_reviewed = int(summary.get("epics_reviewed") or 0)
    epics_approved = int(summary.get("epics_review_approved") or 0)
    if epics_approved == 0:
        epics_approved = int(summary.get("epics_selected_for_test_case_creation") or 0)

    tc_gen = int(summary.get("test_cases_drafted_total") or 0)
    tc_approved, tc_rejected, _tc_pending = _tc_review_counts(conn, pipeline_run_id)
    tc_decided = tc_approved + tc_rejected
    sent_xray = int(summary.get("test_cases_imported_to_xray_total") or 0)

    tc_time = _minutes_from_phase(phases, "test_case_human_review")
    total_time = _minutes_from_phase(phases, "overall")

    qa_user = (run["operator_name"] or ctx.get("operator_name") or "").strip()
    if not qa_user:
        qa_user = operator_name()

    row_id = external_run_id or ""
    values: list[Any] = [
        row_id,
        qa_user,
        product_cfg["product_label"],
        _infer_use_case(report),
        epics_reviewed,
        epics_approved,
        _pct(epics_approved, epics_reviewed),
        tc_gen,
        tc_approved,
        tc_rejected,
        _pct(tc_approved, tc_decided if tc_decided else tc_gen),
        sent_xray,
        tc_time if tc_time is not None else "",
        total_time if total_time is not None else "",
        _sheet_coverage_label(run["coverage_profile"] or "balanced"),
    ]

    return {
        "tab": product_cfg["tab"],
        "run_prefix": product_cfg["run_prefix"],
        "external_run_id": row_id,
        "values": values,
        "fields": {
            "run_id": row_id,
            "qa_user": qa_user,
            "product": product_cfg["product_label"],
            "use_case": values[3],
            "epics_reviewed": epics_reviewed,
            "epics_approved": epics_approved,
            "test_cases_generated": tc_gen,
            "test_cases_approved": tc_approved,
            "test_cases_rejected": tc_rejected,
            "sent_to_xray": sent_xray,
            "tc_review_minutes": tc_time,
            "total_process_minutes": total_time,
            "coverage_depth": values[14],
        },
    }
