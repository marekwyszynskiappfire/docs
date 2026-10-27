"""Workspace state and guidance for one pipeline run.

All "what do I do now?" logic lives here so the UI renders one consistent answer.
"""

from __future__ import annotations

from typing import Any

from coverage_profile import coerce_profile_id, is_coverage_stale, public_profile, public_profiles, profile_by_id, resolve_profile_id
from cursor_handoff import list_handoffs, suite_path_for
from db import row_to_dict
from review_payload_fields import testability_verdict
from run_config import portfolio_id_for_source
from run_report import _latest_payloads_for_units

STAGES: list[dict[str, str]] = [
    {
        "id": "review",
        "title": "Assess testability",
        "description": (
            "Read each Epic's verdict and blocker questions. "
            "Approve the review when the verdict is right."
        ),
        "done_when": "Every testable Epic has an approved review.",
    },
    {
        "id": "draft",
        "title": "Draft tests",
        "description": (
            "Set coverage depth, then paste one Creator prompt per Epic into Cursor. "
            "Studio imports the suite when the file appears."
        ),
        "done_when": "Every approved Epic has imported test cases.",
    },
    {
        "id": "test_review",
        "title": "Review tests",
        "description": "Open each test, then approve or reject it. A rejection needs a reason.",
        "done_when": "No test is pending.",
    },
    {
        "id": "import",
        "title": "Import to Xray",
        "description": (
            "Choose approved tests for Xray, then preview the import plan on this page. "
            "A dry-run is shown before anything is written, and a production target asks you to confirm."
        ),
        "done_when": "Every chosen test has an Xray key.",
    },
]
STAGE_INDEX = {stage["id"]: index for index, stage in enumerate(STAGES)}
DONE_INDEX = len(STAGES)


def _creator_run_for_unit(conn: Any, unit_id: str) -> Any:
    return conn.execute(
        """
        SELECT * FROM creator_run
        WHERE review_unit_id = ?
        ORDER BY updated_at DESC
        LIMIT 1
        """,
        (unit_id,),
    ).fetchone()


def _test_counts(conn: Any, creator_run_id: str | None) -> dict[str, int]:
    counts = {"total": 0, "pending": 0, "approved": 0, "rejected": 0, "marked": 0, "in_xray": 0}
    if not creator_run_id:
        return counts
    rows = conn.execute(
        """
        SELECT human_review_status, marked_for_xray_import, xray_test_key
        FROM test_case_row WHERE creator_run_id = ?
        """,
        (creator_run_id,),
    ).fetchall()
    for row in rows:
        counts["total"] += 1
        status = row["human_review_status"]
        if status in {"pending", "edited"}:
            counts["pending"] += 1
        elif status == "approved":
            counts["approved"] += 1
            if row["marked_for_xray_import"]:
                counts["marked"] += 1
                if row["xray_test_key"]:
                    counts["in_xray"] += 1
        elif status == "rejected":
            counts["rejected"] += 1
    return counts


def _epic_stage(epic: dict[str, Any]) -> str:
    if epic["verdict"] == "not_testable_yet":
        return "blocked"
    if not epic["approved"]:
        return "review"
    handoff = epic["creator_handoff"]
    if handoff and handoff["status"] == "stale_output":
        return "draft"
    tests = epic["tests"]
    if tests["total"] == 0:
        return "draft"
    if tests["pending"]:
        return "test_review"
    if tests["approved"] == 0:
        return "done"
    if tests["marked"] == 0 or tests["in_xray"] < tests["marked"]:
        if epic["creator_run_status"] == "imported":
            return "done"
        return "import"
    return "done"


def _action_for(epic: dict[str, Any], workspace_path: str) -> dict[str, Any]:
    key = epic["jira_key"]
    stage = epic["stage"]
    handoff = epic["creator_handoff"]
    base = {"epic_key": key, "unit_id": epic["unit_id"], "current_stage": stage}
    if stage == "review":
        return {
            **base,
            "title": f"Assess testability for {key}",
            "reason": (
                f"Verdict: {epic['verdict'].replace('_', ' ')}. "
                "Check the blocker questions, then approve the review."
            ),
            "completion_signal": f"{key} shows Review approved.",
            "primary": {"kind": "approve_review", "label": f"Approve {key} review"},
        }
    if stage == "draft":
        if handoff is None:
            return {
                **base,
                "title": f"Draft tests for {key}",
                "reason": "The review is approved. Studio will prepare the Creator prompt for Cursor.",
                "completion_signal": "A Creator prompt appears below.",
                "primary": {"kind": "prepare_creator", "label": "Prepare Creator prompt"},
            }
        if handoff["status"] == "stale_output" and is_coverage_stale(handoff.get("error")):
            return {
                **base,
                "title": f"Coverage depth changed for {key}",
                "reason": handoff["error"],
                "completion_signal": f"{key} lists tests for the new coverage depth.",
                "primary": {
                    "kind": "copy_prompt",
                    "label": "Run Creator in Cursor",
                    "handoff_id": handoff["id"],
                },
                "cursor_prompt": _prompt(handoff),
            }
        if handoff["status"] == "stale_output":
            return {
                **base,
                "title": f"Import the updated suite for {key}",
                "reason": "The suite file changed after Studio imported it.",
                "completion_signal": f"{key} shows the updated tests.",
                "primary": {
                    "kind": "accept_changes",
                    "label": "Import updated suite",
                    "handoff_id": handoff["id"],
                },
            }
        if handoff["status"] == "invalid_output":
            return {
                **base,
                "title": f"Fix the suite file for {key}",
                "reason": handoff["error"] or "The suite file could not be read.",
                "completion_signal": "Studio imports the corrected file automatically.",
                "primary": {
                    "kind": "copy_prompt",
                    "label": "Retry Creator in Cursor",
                    "handoff_id": handoff["id"],
                },
                "cursor_prompt": _prompt(handoff),
            }
        return {
            **base,
            "title": f"Run Creator in Cursor for {key}",
            "reason": (
                f"Studio is watching {suite_path_for(key)} and imports it automatically. "
                "No file yet just means Cursor has not finished."
            ),
            "completion_signal": f"{key} lists its test cases.",
            "primary": {
                "kind": "copy_prompt",
                "label": "Run Creator in Cursor",
                "handoff_id": handoff["id"],
            },
            "cursor_prompt": _prompt(handoff),
        }
    if stage == "test_review":
        pending = epic["tests"]["pending"]
        return {
            **base,
            "title": f"Review {pending} test case{'s' if pending != 1 else ''} for {key}",
            "reason": "Approve or reject each drafted test. Only approved tests can go to Xray.",
            "completion_signal": f"No pending tests remain for {key}.",
            "primary": {"kind": "review_tests", "label": "Review the tests"},
        }
    if stage == "import":
        if epic["tests"]["marked"] == 0:
            return {
                **base,
                "title": f"Choose which approved tests for {key} go to Xray",
                "reason": "Tick Send to Xray on each approved test you want imported.",
                "completion_signal": "At least one test is chosen.",
                "primary": {"kind": "review_tests", "label": "Review the tests"},
            }
        return {
            **base,
            "title": f"Plan the Xray import for {key}",
            "reason": (
                f"{epic['tests']['marked']} test(s) chosen. Preview the plan on this page. "
                "Nothing is written to Xray until you confirm the plan."
            ),
            "completion_signal": "Every chosen test has an Xray key.",
            "primary": {"kind": "open_importer", "label": "Plan Xray import"},
        }
    return {
        **base,
        "title": "Nothing left to do",
        "reason": "Every Epic is done or not testable yet.",
        "completion_signal": "",
        "primary": {"kind": "none", "label": ""},
        "workspace_path": workspace_path,
    }


def _prompt(handoff: dict[str, Any] | None) -> dict[str, Any] | None:
    if not handoff:
        return None
    return {
        "handoff_id": handoff["id"],
        "status": handoff["status"],
        "prompt_version": handoff["prompt_version"],
        "text": handoff["prompt_text"],
    }


def _epics(
    conn: Any, pipeline_run_id: str, handoffs: list[dict[str, Any]], portfolio_profile: str
) -> list[dict[str, Any]]:
    units = [
        row_to_dict(row)
        for row in conn.execute(
            "SELECT * FROM review_unit WHERE pipeline_run_id = ? ORDER BY jira_key",
            (pipeline_run_id,),
        ).fetchall()
    ]
    payloads = _latest_payloads_for_units(conn, [unit["id"] for unit in units])
    by_key = {item["epic_key"]: item for item in handoffs if item["stage"] == "creator_draft"}
    epics: list[dict[str, Any]] = []
    for unit in units:
        payload = payloads.get(unit["id"]) or {}
        creator = _creator_run_for_unit(conn, unit["id"])
        questions = [
            q
            for q in payload.get("questions") or []
            if isinstance(q, dict) and (q.get("status") or "open") == "open"
        ]
        classifications = payload.get("classifications") or {}
        readiness = classifications.get("readiness") or {}
        epic = {
            "unit_id": unit["id"],
            "jira_key": unit["jira_key"],
            "summary": unit["summary"],
            "qa_planning_fit": unit["qa_planning_fit"],
            "gate_status": unit["gate_status"],
            "verdict": testability_verdict(payload, unit["qa_planning_fit"]),
            "testability_reasons": [
                reason
                for reason in (payload.get("report") or {}).get("testability_reasons") or []
                if isinstance(reason, str) and reason.strip()
            ][:3],
            "readiness_label": readiness.get("human_label"),
            "readiness_line": (payload.get("report") or {}).get("readiness_line"),
            "blocker_questions": [
                {
                    "question_id": q.get("question_id"),
                    "question": q.get("question"),
                    "context": q.get("context"),
                    "owner_hint": q.get("owner_hint"),
                    "priority": q.get("priority"),
                }
                for q in questions
                if q.get("priority") == "High"
            ],
            "other_question_count": sum(1 for q in questions if q.get("priority") != "High"),
            "approved": bool(unit["approved_revision_id"]),
            "coverage_profile": unit["coverage_profile"] or None,
            "effective_coverage_profile": public_profile(
                profile_by_id(resolve_profile_id(unit["coverage_profile"], portfolio_profile))
            ),
            "creator_run_id": creator["id"] if creator else None,
            "creator_run_status": creator["status"] if creator else None,
            "tests": _test_counts(conn, creator["id"] if creator else None),
            "creator_handoff": by_key.get(unit["jira_key"]),
        }
        epic["stage"] = _epic_stage(epic)
        epics.append(epic)
    return epics


def _portfolio_actions(epics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Batch steps that only appear when at least two Epics share them."""
    actions: list[dict[str, Any]] = []
    draftable = [
        epic for epic in epics if epic["stage"] == "draft" and not epic["creator_handoff"]
    ]
    if len(draftable) >= 2:
        actions.append(
            {
                "kind": "prepare_creator_batch",
                "label": f"Prepare Creator prompts for {len(draftable)} Epics",
                "epic_keys": [epic["jira_key"] for epic in draftable],
                "unit_ids": [epic["unit_id"] for epic in draftable],
            }
        )
    copyable = [
        epic
        for epic in epics
        if epic["stage"] == "draft"
        and epic["creator_handoff"]
        and epic["creator_handoff"]["status"]
        in {"awaiting_cursor", "output_detected", "invalid_output"}
    ]
    if len(copyable) >= 2:
        actions.append(
            {
                "kind": "copy_creator_prompts",
                "label": f"Prepare Creator handoffs for {len(copyable)} Epics",
                "epic_keys": [epic["jira_key"] for epic in copyable],
                "handoff_ids": [epic["creator_handoff"]["id"] for epic in copyable],
            }
        )
    reviewable = [
        epic for epic in epics if epic["stage"] == "test_review" and epic["tests"]["pending"] > 0
    ]
    if len(reviewable) >= 2:
        pending = sum(epic["tests"]["pending"] for epic in reviewable)
        actions.append(
            {
                "kind": "review_selected_tests",
                "label": f"{pending} tests to review across {len(reviewable)} Epics",
                "epic_keys": [epic["jira_key"] for epic in reviewable],
            }
        )
    importable = [
        epic for epic in epics if epic["stage"] == "import" and epic["tests"]["marked"] > 0
    ]
    if len(importable) >= 2:
        actions.append(
            {
                "kind": "preview_import_plans",
                "label": f"Preview Xray plans for {len(importable)} Epics",
                "epic_keys": [epic["jira_key"] for epic in importable],
            }
        )
    return actions


def portfolio_guidance(conn: Any, pipeline_run_id: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    handoffs = list_handoffs(conn, pipeline_run_id)
    run = conn.execute(
        "SELECT coverage_profile FROM pipeline_run WHERE id = ?",
        (pipeline_run_id,),
    ).fetchone()
    portfolio_profile = coerce_profile_id(run["coverage_profile"] if run else None)
    epics = _epics(conn, pipeline_run_id, handoffs, portfolio_profile)
    workspace_path = f"/workspace/{pipeline_run_id}"
    active = [epic for epic in epics if epic["stage"] in STAGE_INDEX]
    if active:
        target = min(active, key=lambda epic: STAGE_INDEX[epic["stage"]])
        action = _action_for(target, workspace_path)
    elif epics and all(epic["stage"] == "blocked" for epic in epics):
        first = epics[0]
        action = {
            "epic_key": first["jira_key"],
            "unit_id": first["unit_id"],
            "current_stage": "review",
            "title": "No Epic is testable yet",
            "reason": "Send the blocker questions to the owners. Rescan in Cursor once they answer.",
            "completion_signal": "A rescan changes at least one verdict.",
            "primary": {
                "kind": "open_unit",
                "label": f"Open {first['jira_key']} questions",
                "path": f"/units/{first['unit_id']}",
            },
        }
    else:
        action = {
            "epic_key": None,
            "unit_id": None,
            "current_stage": "done",
            "title": "Nothing left to do",
            "reason": "Every Epic is done or not testable yet.",
            "completion_signal": "",
            "primary": {"kind": "none", "label": ""},
        }
    action.setdefault("cursor_prompt", None)
    return epics, action


def _stage_status(epics: list[dict[str, Any]], current: str) -> list[dict[str, Any]]:
    tracked = [epic for epic in epics if epic["stage"] != "blocked"]
    current_index = STAGE_INDEX.get(current, DONE_INDEX)
    out = []
    for index, stage in enumerate(STAGES):
        if tracked and all(
            STAGE_INDEX.get(epic["stage"], DONE_INDEX) > index for epic in tracked
        ):
            status = "complete"
        elif index == current_index:
            status = "current"
        else:
            status = "upcoming"
        out.append({**stage, "status": status})
    return out


def workspace_summary(conn: Any, pipeline_run_id: str) -> dict[str, Any]:
    run = conn.execute(
        "SELECT * FROM pipeline_run WHERE id = ?",
        (pipeline_run_id,),
    ).fetchone()
    if run is None:
        raise KeyError(pipeline_run_id)
    portfolio_profile = coerce_profile_id(run["coverage_profile"])
    epics, action = portfolio_guidance(conn, pipeline_run_id)
    handoffs = list_handoffs(conn, pipeline_run_id)
    review = next((item for item in handoffs if item["stage"] == "review"), None)
    return {
        "pipeline_run_id": pipeline_run_id,
        "label": run["label"],
        "portfolio_id": portfolio_id_for_source(run["source_path"]),
        "workspace_path": f"/workspace/{pipeline_run_id}",
        "coverage_profile": portfolio_profile,
        "coverage_profiles": public_profiles(),
        "stages": _stage_status(epics, action["current_stage"]),
        "next_action": action,
        "portfolio_actions": _portfolio_actions(epics),
        "review_prompt": _prompt(review),
        "epics": [
            {
                **{key: value for key, value in epic.items() if key != "creator_handoff"},
                "creator_handoff": (
                    {
                        "id": epic["creator_handoff"]["id"],
                        "status": epic["creator_handoff"]["status"],
                        "error": epic["creator_handoff"]["error"],
                        "expected_path": suite_path_for(epic["jira_key"]),
                        "prompt": epic["creator_handoff"]["prompt_text"],
                    }
                    if epic["creator_handoff"]
                    else None
                ),
            }
            for epic in epics
        ],
        "watch_handoff_ids": [
            epic["creator_handoff"]["id"]
            for epic in epics
            if epic["creator_handoff"] and _watching(epic["creator_handoff"])
        ],
    }


def _watching(handoff: dict[str, Any]) -> bool:
    if handoff["status"] in {"awaiting_cursor", "output_detected", "invalid_output"}:
        return True
    return handoff["status"] == "stale_output" and is_coverage_stale(handoff.get("error"))
