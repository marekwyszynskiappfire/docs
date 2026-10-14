"""Per-pipeline E2E statistics for Studio Statistics tab and BigQuery export."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from db import utc_now
from jira_epic_comment import _collect_epic_feedback_items
from review_payload_fields import qa_planning_fit_from_payload

REPORT_SCHEMA_VERSION = 2
EPIC_DIR_RE = re.compile(r"^[A-Z][A-Z0-9]+-\d+$")

TC_CREATION_READY = frozenset({"fit", "good"})
TC_CREATION_RESERVATIONS = frozenset({"provisional", "ready_with_clarifications"})
TC_CREATION_NOT_READY = frozenset(
    {"not_fit", "needs_clarification_before_scope_lock", "cannot_plan_scope_yet"}
)

COMPARE_METRIC_KEYS: tuple[tuple[str, str], ...] = (
    ("epics_reviewed", "Epics reviewed"),
    ("epics_tc_creation_ready", "Ready for TC creation"),
    ("epics_tc_creation_ready_with_reservations", "Ready with reservations"),
    ("epics_tc_creation_not_ready", "Not ready for TC creation"),
    ("epics_tc_creation_unknown", "TC readiness unknown"),
    ("issues_spotted_findings_total", "Findings spotted"),
    ("epics_selected_for_test_case_creation", "Epics selected for Creator"),
    ("epics_review_approved", "Epics review-approved"),
    ("test_cases_drafted_total", "Test cases drafted"),
    ("test_cases_sent_to_import_total", "Test cases sent to import"),
    ("test_cases_imported_to_xray_total", "Test cases in Xray"),
)


def tc_creation_readiness_bucket(qa_planning_fit: str | None) -> str:
    """ready | ready_with_reservations | not_ready | unknown"""
    raw = (qa_planning_fit or "").strip().lower()
    if not raw:
        return "unknown"
    if raw in TC_CREATION_NOT_READY:
        return "not_ready"
    if raw in TC_CREATION_RESERVATIONS:
        return "ready_with_reservations"
    if raw in TC_CREATION_READY:
        return "ready"
    if (
        "not_fit" in raw
        or raw.startswith("cannot_")
        or raw.startswith("needs_clarification")
    ):
        return "not_ready"
    if raw == "provisional" or raw.startswith("ready_with_clarif"):
        return "ready_with_reservations"
    return "unknown"


def _tc_readiness_counts_from_fits(fits: list[str | None]) -> dict[str, int]:
    counts = {
        "ready": 0,
        "ready_with_reservations": 0,
        "not_ready": 0,
        "unknown": 0,
    }
    mix: dict[str, int] = {}
    for fit in fits:
        bucket = tc_creation_readiness_bucket(fit)
        counts[bucket] += 1
        key = (fit or "unset").strip() or "unset"
        mix[key] = mix.get(key, 0) + 1
    return {
        "epics_tc_creation_ready": counts["ready"],
        "epics_tc_creation_ready_with_reservations": counts["ready_with_reservations"],
        "epics_tc_creation_not_ready": counts["not_ready"],
        "epics_tc_creation_unknown": counts["unknown"],
        "epics_tc_creation_mix": mix,
    }

_EMPTY_TC = {
    "test_cases_drafted": 0,
    "test_cases_amended": 0,
    "test_cases_sent_to_import": 0,
    "test_cases_xray_imported": 0,
}


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _duration_seconds(start: datetime | None, end: datetime | None) -> float | None:
    if not start or not end:
        return None
    delta = end - start
    return max(0.0, delta.total_seconds())


def _phase_row(
    key: str,
    label: str,
    started_at: str | None,
    ended_at: str | None,
    notes: str | None = None,
) -> dict[str, Any]:
    start_dt = _parse_ts(started_at)
    end_dt = _parse_ts(ended_at)
    return {
        "phase": key,
        "label": label,
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_seconds": _duration_seconds(start_dt, end_dt),
        "notes": notes,
    }


def _latest_payloads_for_units(conn: Any, unit_ids: list[str]) -> dict[str, dict[str, Any]]:
    if not unit_ids:
        return {}
    placeholders = ",".join("?" * len(unit_ids))
    rows = conn.execute(
        f"""
        SELECT r.review_unit_id, r.payload_json
        FROM review_payload_revision r
        INNER JOIN (
          SELECT review_unit_id, MAX(revision) AS mr
          FROM review_payload_revision
          WHERE review_unit_id IN ({placeholders})
          GROUP BY review_unit_id
        ) latest ON latest.review_unit_id = r.review_unit_id AND latest.mr = r.revision
        """,
        unit_ids,
    ).fetchall()
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        out[row["review_unit_id"]] = json.loads(row["payload_json"])
    return out


def _payloads_at_revisions(
    conn: Any, pairs: list[tuple[str, int]]
) -> dict[tuple[str, int], dict[str, Any]]:
    if not pairs:
        return {}
    out: dict[tuple[str, int], dict[str, Any]] = {}
    for unit_id, revision in pairs:
        row = conn.execute(
            """
            SELECT payload_json FROM review_payload_revision
            WHERE review_unit_id = ? AND revision = ?
            """,
            (unit_id, revision),
        ).fetchone()
        if row:
            out[(unit_id, revision)] = json.loads(row["payload_json"])
    return out


def _studio_decisions(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    studio = payload.get("studio_qa") or {}
    if not isinstance(studio, dict):
        return {}
    return dict(studio.get("decisions") or {})


def _feedback_counts(payload: dict[str, Any]) -> dict[str, int]:
    decisions = _studio_decisions(payload)
    suggested_marked = 0
    new_marked = 0
    added_ids = {
        str(q.get("question_id"))
        for q in (payload.get("studio_qa") or {}).get("added_questions") or []
        if isinstance(q, dict) and q.get("question_id")
    }

    def marked(item_id: str) -> bool:
        d = decisions.get(item_id) or {}
        if d.get("validity") == "invalid":
            return False
        return bool(d.get("send_to_epic"))

    for q in payload.get("questions") or []:
        if not isinstance(q, dict):
            continue
        qid = q.get("question_id")
        if qid and marked(str(qid)):
            suggested_marked += 1
    for qid in added_ids:
        if marked(qid):
            new_marked += 1
    return {
        "questions_marked_suggested": suggested_marked,
        "questions_marked_new": new_marked,
        "feedback_items_marked_total": len(_collect_epic_feedback_items(payload)),
    }


def _count_posted_questions(payload: dict[str, Any]) -> tuple[int, int]:
    added_ids = {
        str(q.get("question_id"))
        for q in (payload.get("studio_qa") or {}).get("added_questions") or []
        if isinstance(q, dict) and q.get("question_id")
    }
    suggested = 0
    new_q = 0
    for item in _collect_epic_feedback_items(payload):
        if item.get("type") != "question":
            continue
        iid = str(item.get("id"))
        if iid in added_ids or item.get("origin") == "qa_studio":
            new_q += 1
        else:
            suggested += 1
    return suggested, new_q


def _posted_feedback_counts(
    posts: list[Any],
    payloads_by_revision: dict[tuple[str, int], dict[str, Any]],
    unit_id: str,
) -> dict[str, int]:
    """Count posted questions once per payload revision (ignore duplicate posts of same revision)."""
    suggested = 0
    new_q = 0
    seen_revisions: set[int] = set()
    for post in posts:
        rev = post["payload_revision_id"]
        if rev is None:
            continue
        rev_int = int(rev)
        if rev_int in seen_revisions:
            continue
        seen_revisions.add(rev_int)
        payload = payloads_by_revision.get((unit_id, rev_int))
        if not payload:
            continue
        s, n = _count_posted_questions(payload)
        suggested += s
        new_q += n
    return {
        "questions_posted_suggested": suggested,
        "questions_posted_new": new_q,
        "jira_comment_posts_success": len(posts),
    }


def _finding_counts(payload: dict[str, Any]) -> dict[str, int]:
    total = 0
    open_n = 0
    for f in payload.get("findings") or []:
        if not isinstance(f, dict):
            continue
        total += 1
        if (f.get("status") or "open") == "open":
            open_n += 1
    return {"findings_total": total, "findings_open": open_n}


def _question_counts(payload: dict[str, Any]) -> dict[str, int]:
    total = 0
    open_n = 0
    for q in payload.get("questions") or []:
        if not isinstance(q, dict):
            continue
        total += 1
        if (q.get("status") or "open") == "open":
            open_n += 1
    studio = payload.get("studio_qa") or {}
    added = studio.get("added_questions") if isinstance(studio, dict) else []
    added_n = len([q for q in (added or []) if isinstance(q, dict)])
    return {
        "questions_total": total,
        "questions_open": open_n,
        "questions_added_in_studio": added_n,
    }


def _creator_runs_for_pipeline(conn: Any, run_id: str) -> list[Any]:
    units = conn.execute(
        "SELECT id, jira_key FROM review_unit WHERE pipeline_run_id = ?",
        (run_id,),
    ).fetchall()
    unit_ids = [u["id"] for u in units]
    jira_keys = [u["jira_key"] for u in units]
    if not unit_ids:
        return []
    placeholders = ",".join("?" * len(unit_ids))
    query = f"""
        SELECT * FROM creator_run
        WHERE pipeline_run_id = ?
        OR review_unit_id IN ({placeholders})
    """
    params: list[Any] = [run_id, *unit_ids]
    if jira_keys:
        query += f" OR id IN ({','.join('?' * len(jira_keys))})"
        params.extend(jira_keys)
    rows = conn.execute(query, params).fetchall()
    seen: set[str] = set()
    unique: list[Any] = []
    for row in rows:
        if row["id"] not in seen:
            seen.add(row["id"])
            unique.append(row)
    return unique


def _creator_runs_for_epic(
    cr_by_unit: dict[str, list[Any]],
    cr_by_jira_key: dict[str, list[Any]],
    unit_id: str,
    jira_key: str,
) -> list[Any]:
    """Epic-scoped creator runs only (never attribute pipeline-wide runs to every epic)."""
    merged: list[Any] = []
    seen: set[str] = set()
    for cr in cr_by_unit.get(unit_id, []) + cr_by_jira_key.get(jira_key, []):
        if cr["id"] not in seen:
            seen.add(cr["id"])
            merged.append(cr)
    return merged


def _index_creator_runs(
    creator_runs: list[Any], unit_ids: set[str], jira_keys: set[str]
) -> tuple[dict[str, list[Any]], dict[str, list[Any]]]:
    by_unit: dict[str, list[Any]] = {}
    by_key: dict[str, list[Any]] = {}
    for cr in creator_runs:
        uid = cr["review_unit_id"]
        if uid and uid in unit_ids:
            by_unit.setdefault(uid, []).append(cr)
        elif cr["id"] in jira_keys:
            by_key.setdefault(cr["id"], []).append(cr)
    return by_unit, by_key


def _merge_tc_stats(target: dict[str, int], add: dict[str, int]) -> dict[str, int]:
    for key in _EMPTY_TC:
        target[key] = target.get(key, 0) + add.get(key, 0)
    return target


def _test_case_stats_batch(conn: Any, creator_run_ids: list[str]) -> dict[str, dict[str, int]]:
    if not creator_run_ids:
        return {}
    placeholders = ",".join("?" * len(creator_run_ids))
    rows = conn.execute(
        f"""
        SELECT id, creator_run_id, human_review_status, marked_for_xray_import, xray_test_key
        FROM test_case_row WHERE creator_run_id IN ({placeholders})
        """,
        creator_run_ids,
    ).fetchall()
    row_ids = [r["id"] for r in rows]
    human_by_row: dict[str, int] = {}
    if row_ids:
        row_ph = ",".join("?" * len(row_ids))
        for rev in conn.execute(
            f"""
            SELECT test_case_row_id, COUNT(*) AS n
            FROM test_case_revision
            WHERE test_case_row_id IN ({row_ph}) AND source = 'human'
            GROUP BY test_case_row_id
            """,
            row_ids,
        ):
            human_by_row[rev["test_case_row_id"]] = rev["n"]

    out: dict[str, dict[str, int]] = {cid: dict(_EMPTY_TC) for cid in creator_run_ids}
    for row in rows:
        cid = row["creator_run_id"]
        stats = out[cid]
        stats["test_cases_drafted"] += 1
        if human_by_row.get(row["id"], 0) > 0 or row["human_review_status"] == "edited":
            stats["test_cases_amended"] += 1
        if row["human_review_status"] == "approved" and row["marked_for_xray_import"]:
            stats["test_cases_sent_to_import"] += 1
        if row["xray_test_key"]:
            stats["test_cases_xray_imported"] += 1
    return out


def _xray_keys_for_runs(conn: Any, creator_run_ids: list[str]) -> dict[str, list[str]]:
    if not creator_run_ids:
        return {}
    placeholders = ",".join("?" * len(creator_run_ids))
    out: dict[str, list[str]] = {cid: [] for cid in creator_run_ids}
    for row in conn.execute(
        f"""
        SELECT creator_run_id, xray_test_key FROM test_case_row
        WHERE creator_run_id IN ({placeholders}) AND xray_test_key IS NOT NULL
        """,
        creator_run_ids,
    ):
        out[row["creator_run_id"]].append(row["xray_test_key"])
    return out


def _jira_posts_by_unit(conn: Any, unit_ids: list[str]) -> dict[str, list[Any]]:
    if not unit_ids:
        return {}
    placeholders = ",".join("?" * len(unit_ids))
    rows = conn.execute(
        f"""
        SELECT review_unit_id, payload_revision_id, id
        FROM jira_comment_post
        WHERE review_unit_id IN ({placeholders}) AND jira_comment_id IS NOT NULL
        ORDER BY id ASC
        """,
        unit_ids,
    ).fetchall()
    grouped: dict[str, list[Any]] = {uid: [] for uid in unit_ids}
    for row in rows:
        grouped[row["review_unit_id"]].append(row)
    return grouped


def _event_times(
    conn: Any,
    run_id: str,
    event_types: tuple[str, ...],
    entity_ids: tuple[str, ...] = (),
) -> list[str]:
    if not event_types:
        return []
    in_clause = ",".join("?" * len(event_types))
    params: list[Any] = [*event_types, run_id]
    entity_clause = ""
    if entity_ids:
        entity_clause = f" OR entity_id IN ({','.join('?' * len(entity_ids))})"
        params.extend(entity_ids)
    rows = conn.execute(
        f"""
        SELECT created_at FROM metric_event
        WHERE event_type IN ({in_clause})
          AND (pipeline_run_id = ?{entity_clause})
        ORDER BY created_at ASC
        """,
        tuple(params),
    ).fetchall()
    return [r["created_at"] for r in rows]


def _folder_payload_time_bounds(source_path: str | None) -> tuple[str | None, str | None]:
    if not source_path:
        return None, None
    root = Path(source_path)
    if not root.is_dir():
        return None, None
    earliest: datetime | None = None
    latest: datetime | None = None
    for child in root.iterdir():
        if not child.is_dir() or not EPIC_DIR_RE.match(child.name):
            continue
        path = child / "review-payload.json"
        if not path.is_file():
            continue
        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        except OSError:
            continue
        if earliest is None or mtime < earliest:
            earliest = mtime
        if latest is None or mtime > latest:
            latest = mtime
    return (
        earliest.isoformat() if earliest else None,
        latest.isoformat() if latest else None,
    )


def _reviewer_gather_bounds(
    run_row: Any, handoff: dict[str, Any] | None, first_studio_import: str | None
) -> tuple[str | None, str | None]:
    folder_start, folder_end = _folder_payload_time_bounds(run_row["source_path"])
    candidates_start: list[datetime] = []
    candidates_end: list[datetime] = []
    for raw in (folder_start, run_row["created_at"]):
        dt = _parse_ts(raw)
        if dt:
            candidates_start.append(dt)
    if handoff and handoff.get("generated_at"):
        dt = _parse_ts(str(handoff["generated_at"]))
        if dt:
            candidates_end.append(dt)
    if folder_end:
        dt = _parse_ts(folder_end)
        if dt:
            candidates_end.append(dt)
    if first_studio_import:
        dt = _parse_ts(first_studio_import)
        if dt:
            candidates_end.append(dt)
    start = min(candidates_start).isoformat() if candidates_start else run_row["created_at"]
    end = max(candidates_end).isoformat() if candidates_end else first_studio_import
    return start, end


def _product_context(run_row: Any, handoff: dict[str, Any] | None) -> dict[str, Any]:
    ctx: dict[str, Any] = {
        "product_id": run_row["product_id"],
        "trigger_type": run_row["trigger_type"],
        "trigger_value": run_row["trigger_value"],
        "source_path": run_row["source_path"],
        "jira_projects": [],
        "reviewer_run_id": None,
    }
    if handoff:
        ctx["reviewer_run_id"] = handoff.get("run_id")
        ctx["source_jql"] = handoff.get("source_jql")
        ctx["creator_jql"] = handoff.get("creator_jql")
    jql = (handoff or {}).get("source_jql") or run_row["trigger_value"] or ""
    m = re.search(r"project\s*=\s*(\w+)", str(jql), re.I)
    if m:
        ctx["jira_projects"] = [m.group(1).upper()]
    return ctx


def _epic_label_for_creator_run(conn: Any, cr: Any, jira_keys: set[str]) -> str:
    if cr["review_unit_id"]:
        row = conn.execute(
            "SELECT jira_key FROM review_unit WHERE id = ?", (cr["review_unit_id"],)
        ).fetchone()
        if row:
            return row["jira_key"]
    if cr["id"] in jira_keys:
        return cr["id"]
    return cr["id"]


def compute_pipeline_run_report(conn: Any, run_id: str) -> dict[str, Any]:
    run = conn.execute("SELECT * FROM pipeline_run WHERE id = ?", (run_id,)).fetchone()
    if not run:
        raise KeyError(run_id)

    handoff = None
    if run["creator_handoff_json"]:
        handoff = json.loads(run["creator_handoff_json"])

    units = conn.execute(
        "SELECT * FROM review_unit WHERE pipeline_run_id = ? ORDER BY jira_key",
        (run_id,),
    ).fetchall()
    unit_ids = [u["id"] for u in units]
    jira_keys = {u["jira_key"] for u in units}
    payloads_by_unit = _latest_payloads_for_units(conn, unit_ids)
    posts_by_unit = _jira_posts_by_unit(conn, unit_ids)

    revision_pairs: list[tuple[str, int]] = []
    for uid, posts in posts_by_unit.items():
        for post in posts:
            if post["payload_revision_id"] is not None:
                revision_pairs.append((uid, int(post["payload_revision_id"])))
    payloads_by_revision = _payloads_at_revisions(conn, revision_pairs)

    creator_runs = _creator_runs_for_pipeline(conn, run_id)
    cr_by_unit, cr_by_key = _index_creator_runs(creator_runs, set(unit_ids), jira_keys)
    all_cr_ids = [cr["id"] for cr in creator_runs]
    tc_stats_by_run = _test_case_stats_batch(conn, all_cr_ids)
    xray_by_run = _xray_keys_for_runs(conn, all_cr_ids)

    epics_reviewed = len(units)
    findings_total = 0
    findings_open = 0
    questions_total = 0
    unit_fits: list[str | None] = []
    selected_creator = 0
    approved_units = 0
    questions_marked_suggested = 0
    questions_marked_new = 0
    questions_posted_suggested = 0
    questions_posted_new = 0
    jira_posts = 0
    epic_rows: list[dict[str, Any]] = []

    for u in units:
        payload = payloads_by_unit.get(u["id"])
        fc = {"findings_total": 0, "findings_open": 0}
        qc = {"questions_total": 0, "questions_open": 0, "questions_added_in_studio": 0}
        fb = {"questions_marked_suggested": 0, "questions_marked_new": 0, "feedback_items_marked_total": 0}
        posted = {"questions_posted_suggested": 0, "questions_posted_new": 0, "jira_comment_posts_success": 0}
        if payload:
            fc = _finding_counts(payload)
            qc = _question_counts(payload)
            fb = _feedback_counts(payload)
            posted = _posted_feedback_counts(
                posts_by_unit.get(u["id"], []), payloads_by_revision, u["id"]
            )

        findings_total += fc["findings_total"]
        findings_open += fc["findings_open"]
        questions_total += qc["questions_total"] + qc["questions_added_in_studio"]
        questions_marked_suggested += fb["questions_marked_suggested"]
        questions_marked_new += fb["questions_marked_new"]
        questions_posted_suggested += posted["questions_posted_suggested"]
        questions_posted_new += posted["questions_posted_new"]
        jira_posts += posted["jira_comment_posts_success"]

        fit = qa_planning_fit_from_payload(payload) or u["qa_planning_fit"]
        unit_fits.append(fit)
        readiness_bucket = tc_creation_readiness_bucket(fit)
        not_ready = readiness_bucket == "not_ready"
        if u["include_in_creator"]:
            selected_creator += 1
        if u["approved_revision_id"]:
            approved_units += 1

        epic_crs = _creator_runs_for_epic(cr_by_unit, cr_by_key, u["id"], u["jira_key"])
        tc_stats = dict(_EMPTY_TC)
        xray_keys: list[str] = []
        for cr in epic_crs:
            _merge_tc_stats(tc_stats, tc_stats_by_run.get(cr["id"], _EMPTY_TC))
            xray_keys.extend(xray_by_run.get(cr["id"], []))

        epic_rows.append(
            {
                "unit_id": u["id"],
                "jira_key": u["jira_key"],
                "summary": u["summary"],
                "gate_status": u["gate_status"]
                or ((payload.get("gate") or {}).get("status") if payload else None),
                "qa_planning_fit": fit,
                "tc_creation_readiness": readiness_bucket,
                "not_ready_for_test_design": not_ready,
                "include_in_creator": bool(u["include_in_creator"]),
                "review_approved": bool(u["approved_revision_id"]),
                **fc,
                **qc,
                **fb,
                **posted,
                **tc_stats,
                "xray_test_keys": sorted(set(xray_keys)),
            }
        )

    tc_drafted = 0
    tc_amended = 0
    tc_sent = 0
    tc_xray = 0
    per_epic_tc: dict[str, int] = {}
    for cr in creator_runs:
        stats = tc_stats_by_run.get(cr["id"], _EMPTY_TC)
        tc_drafted += stats["test_cases_drafted"]
        tc_amended += stats["test_cases_amended"]
        tc_sent += stats["test_cases_sent_to_import"]
        tc_xray += stats["test_cases_xray_imported"]
        label = _epic_label_for_creator_run(conn, cr, jira_keys)
        per_epic_tc[label] = per_epic_tc.get(label, 0) + stats["test_cases_drafted"]

    entity_ids = tuple(all_cr_ids)
    import_times = _event_times(conn, run_id, ("review_run_imported",))
    review_end_times = _event_times(conn, run_id, ("review_unit_approved",))
    jira_times = _event_times(
        conn, run_id, ("jira_comment_post_success", "jira_comment_preview")
    )
    creator_times = _event_times(conn, run_id, ("creator_batch_imported",), entity_ids)
    review_tc_times = _event_times(conn, run_id, ("test_case_review",), entity_ids)
    importer_times = _event_times(
        conn,
        run_id,
        ("importer_plan", "importer_execute", "creator_importer_export"),
        entity_ids,
    )
    xray_times = _event_times(conn, run_id, ("xray_import_persisted",), entity_ids)

    gather_start, gather_end = _reviewer_gather_bounds(
        run, handoff, import_times[0] if import_times else None
    )
    review_start = import_times[0] if import_times else gather_end
    review_end = review_end_times[-1] if review_end_times else None
    feedback_start = jira_times[0] if jira_times else None
    feedback_end = jira_times[-1] if jira_times else None
    creator_start = creator_times[0] if creator_times else review_end
    creator_end = creator_times[-1] if creator_times else None
    tc_review_start = review_tc_times[0] if review_tc_times else creator_end
    tc_review_end = review_tc_times[-1] if review_tc_times else None
    importer_start = importer_times[0] if importer_times else tc_review_end
    importer_end = xray_times[-1] if xray_times else (importer_times[-1] if importer_times else None)

    overall_start = gather_start
    overall_end = importer_end or tc_review_end or review_end or utc_now()

    phases = [
        _phase_row(
            "reviewer_gather",
            "Reviewer (Cursor gather → run folder)",
            gather_start,
            gather_end,
            "Start from portfolio handoff timestamp or epic review-payload mtimes under source_path.",
        ),
        _phase_row(
            "review_in_studio",
            "Human review in Studio (edit + approve)",
            review_start,
            review_end,
        ),
        _phase_row(
            "epic_feedback_jira",
            "Epic feedback (Jira comments)",
            feedback_start,
            feedback_end,
            None if jira_times else "No Jira comment activity recorded for this run.",
        ),
        _phase_row(
            "creator_drafting",
            "Creator (import suite into Studio)",
            creator_start,
            creator_end,
        ),
        _phase_row(
            "test_case_human_review",
            "Test case human review",
            tc_review_start,
            tc_review_end,
        ),
        _phase_row(
            "importer_xray",
            "Importer → Xray",
            importer_start,
            importer_end,
        ),
        _phase_row("overall", "Overall E2E", overall_start, overall_end),
    ]

    readiness = _tc_readiness_counts_from_fits(unit_fits)
    summary = {
        "epics_reviewed": epics_reviewed,
        "issues_spotted_findings_total": findings_total,
        "issues_spotted_findings_open": findings_open,
        "epics_not_ready_for_test_design": readiness["epics_tc_creation_not_ready"],
        **readiness,
        "questions_marked_for_epic_suggested": questions_marked_suggested,
        "questions_marked_for_epic_new": questions_marked_new,
        "questions_posted_to_epic_suggested": questions_posted_suggested,
        "questions_posted_to_epic_new": questions_posted_new,
        "jira_comment_posts_success": jira_posts,
        "epics_selected_for_test_case_creation": selected_creator,
        "epics_review_approved": approved_units,
        "test_cases_drafted_total": tc_drafted,
        "test_cases_amended_total": tc_amended,
        "test_cases_sent_to_import_total": tc_sent,
        "test_cases_imported_to_xray_total": tc_xray,
        "creator_runs_linked": len(creator_runs),
    }

    report = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "pipeline_run_id": run_id,
        "pipeline_label": run["label"],
        "computed_at": utc_now(),
        "product_context": _product_context(run, handoff),
        "summary": summary,
        "test_cases_per_epic_drafted": per_epic_tc,
        "phases": phases,
        "epics": epic_rows,
    }
    return report


def compare_pipeline_runs(conn: Any, run_ids: list[str]) -> dict[str, Any]:
    if len(run_ids) < 2:
        raise ValueError("At least two pipeline runs are required for comparison")
    if len(run_ids) > 5:
        raise ValueError("At most five pipeline runs can be compared at once")
    unique_ids: list[str] = []
    seen: set[str] = set()
    for rid in run_ids:
        rid = rid.strip()
        if not rid or rid in seen:
            continue
        seen.add(rid)
        unique_ids.append(rid)
    if len(unique_ids) < 2:
        raise ValueError("At least two distinct pipeline runs are required")

    run_cards: list[dict[str, Any]] = []
    for rid in unique_ids:
        row = conn.execute(
            "SELECT id, label FROM pipeline_run WHERE id = ?", (rid,)
        ).fetchone()
        if not row:
            raise KeyError(rid)
        report = persist_pipeline_run_report(conn, rid)
        run_cards.append(
            {
                "pipeline_run_id": rid,
                "pipeline_label": report["pipeline_label"],
                "computed_at": report["computed_at"],
                "summary": report["summary"],
                "overall_duration_seconds": next(
                    (
                        p.get("duration_seconds")
                        for p in report["phases"]
                        if p.get("phase") == "overall"
                    ),
                    None,
                ),
            }
        )

    metric_rows: list[dict[str, Any]] = []
    for key, label in COMPARE_METRIC_KEYS:
        if key == "epics_tc_creation_mix":
            continue
        values: dict[str, int | float | None] = {}
        for card in run_cards:
            raw = card["summary"].get(key)
            values[card["pipeline_run_id"]] = raw if isinstance(raw, (int, float)) else None
        nums = [v for v in values.values() if isinstance(v, (int, float))]
        metric_rows.append(
            {
                "key": key,
                "label": label,
                "values": values,
                "min": min(nums) if nums else None,
                "max": max(nums) if nums else None,
            }
        )

    baseline_id = unique_ids[0]
    deltas: list[dict[str, Any]] = []
    for row in metric_rows:
        base_val = row["values"].get(baseline_id)
        if not isinstance(base_val, (int, float)):
            continue
        for rid in unique_ids[1:]:
            other = row["values"].get(rid)
            if not isinstance(other, (int, float)):
                continue
            deltas.append(
                {
                    "metric": row["key"],
                    "label": row["label"],
                    "baseline_run_id": baseline_id,
                    "other_run_id": rid,
                    "baseline": base_val,
                    "other": other,
                    "delta": other - base_val,
                }
            )

    return {
        "compared_at": utc_now(),
        "baseline_run_id": baseline_id,
        "runs": run_cards,
        "metrics": metric_rows,
        "deltas_from_baseline": deltas,
    }


def persist_pipeline_run_report(conn: Any, run_id: str) -> dict[str, Any]:
    report = compute_pipeline_run_report(conn, run_id)
    conn.execute(
        """
        INSERT INTO pipeline_run_report (pipeline_run_id, schema_version, report_json, computed_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(pipeline_run_id) DO UPDATE SET
          schema_version = excluded.schema_version,
          report_json = excluded.report_json,
          computed_at = excluded.computed_at
        """,
        (
            run_id,
            REPORT_SCHEMA_VERSION,
            json.dumps(report, ensure_ascii=False),
            report["computed_at"],
        ),
    )
    return report
