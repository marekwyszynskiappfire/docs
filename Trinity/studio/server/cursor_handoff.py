"""Persisted Cursor handoffs and expected output state.

Studio can launch a stored handoff through the local Cursor SDK or let the
operator copy it as a recovery path. A missing file while status is
awaiting_cursor is waiting, not a failure.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any

from db import json_loads, row_to_dict, utc_now
from pipeline_manifest import file_sha256, resolve_repo_path

PROMPT_VERSION = "1"
STATUSES = (
    "awaiting_cursor",
    "output_detected",
    "invalid_output",
    "imported",
    "stale_output",
)


def studio_base_url() -> str:
    port = os.environ.get("QA_STUDIO_PORT", "8765")
    return f"http://127.0.0.1:{port}"


def build_review_prompt(
    manifest: dict[str, Any],
    manifest_path: str,
    pipeline_run_id: str,
) -> str:
    keys = ", ".join(epic["jira_key"] for epic in manifest["epics"])
    workspace_url = f"{studio_base_url()}/workspace/{pipeline_run_id}"
    return (
        "Run the trinity-reviewer skill as a rescan of this portfolio.\n\n"
        f"Portfolio: {manifest['portfolio_id']}\n"
        f"Pipeline run: {pipeline_run_id}\n"
        f"Epics: {keys}\n"
        f"Output root: {manifest['output_root']}\n"
        f"Product: {manifest['product_id']}\n"
        f"Persona: {manifest['persona_id']}\n\n"
        "Questions and Jira comments must be unanswered decisions. Each one names the missing "
        "fact, who answers it, and what test, scope boundary, or pass/fail criterion the answer "
        "changes. Drop nits, restatements, and anything the sources already answer.\n\n"
        "Write the updated payloads into the same output root, then regenerate the manifest "
        f"at {manifest_path} and open the workspace with open_workspace.py. "
        "Studio reuses this pipeline run and adds a revision only for Epics whose payload changed. "
        "Do not create a second pipeline run. Do not import to Xray from this prompt.\n"
        f"Workspace: {workspace_url}"
    )


def decide_status(current: str, assessment: str, detail: str | None) -> tuple[str, str | None]:
    """Map a file check onto a handoff status. Absence while waiting is not an error."""
    if assessment == "invalid":
        return "invalid_output", detail
    if assessment == "stale":
        if current == "imported":
            return "stale_output", detail
        return "invalid_output", detail
    if assessment == "missing":
        if current in {"imported", "stale_output"}:
            return "stale_output", detail or "Expected output is missing."
        return "awaiting_cursor", None
    if current == "imported":
        return "imported", None
    return "output_detected", None


def _prompt_sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def public_handoff(row: Any) -> dict[str, Any]:
    data = row_to_dict(row) or {}
    data["expected_paths"] = json_loads(data.pop("expected_paths_json", None)) or []
    data["expected_hashes"] = json_loads(data.pop("expected_hashes_json", None)) or {}
    return data


def list_handoffs(conn: Any, pipeline_run_id: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT * FROM cursor_handoff
        WHERE pipeline_run_id = ?
        ORDER BY stage, epic_key
        """,
        (pipeline_run_id,),
    ).fetchall()
    return [public_handoff(row) for row in rows]


def ensure_review_handoff(
    conn: Any,
    pipeline_run_id: str,
    manifest: dict[str, Any],
    manifest_path: str,
) -> dict[str, Any]:
    prompt = build_review_prompt(manifest, manifest_path, pipeline_run_id)
    paths = [manifest_path, *[epic["review_payload_path"] for epic in manifest["epics"]]]
    hashes = {
        manifest_path: file_sha256(resolve_repo_path(manifest_path)),
        **{epic["review_payload_path"]: epic["content_sha256"] for epic in manifest["epics"]},
    }
    now = utc_now()
    handoff_id = f"review:{pipeline_run_id}"
    existing = conn.execute(
        "SELECT * FROM cursor_handoff WHERE id = ?",
        (handoff_id,),
    ).fetchone()
    if existing:
        conn.execute(
            """
            UPDATE cursor_handoff
            SET prompt_version = ?, prompt_text = ?, prompt_sha256 = ?,
                status = 'imported', expected_paths_json = ?, expected_hashes_json = ?,
                imported_at = COALESCE(imported_at, ?), error = NULL, updated_at = ?
            WHERE id = ?
            """,
            (
                PROMPT_VERSION,
                prompt,
                _prompt_sha(prompt),
                json.dumps(paths),
                json.dumps(hashes),
                now,
                now,
                handoff_id,
            ),
        )
    else:
        conn.execute(
            """
            INSERT INTO cursor_handoff (
              id, pipeline_run_id, stage, epic_key, prompt_version, prompt_text, prompt_sha256,
              status, expected_paths_json, expected_hashes_json, detected_at, imported_at,
              retry_count, created_at, updated_at
            )
            VALUES (?, ?, 'review', '', ?, ?, ?, 'imported', ?, ?, ?, ?, 0, ?, ?)
            """,
            (
                handoff_id,
                pipeline_run_id,
                PROMPT_VERSION,
                prompt,
                _prompt_sha(prompt),
                json.dumps(paths),
                json.dumps(hashes),
                now,
                now,
                now,
                now,
            ),
        )
    row = conn.execute("SELECT * FROM cursor_handoff WHERE id = ?", (handoff_id,)).fetchone()
    return public_handoff(row)


def create_handoff(
    conn: Any,
    pipeline_run_id: str,
    *,
    stage: str,
    epic_key: str = "",
    prompt_text: str,
    expected_paths: list[str],
    expected_hashes: dict[str, str] | None = None,
    status: str = "awaiting_cursor",
    coverage_profile: str | None = None,
) -> dict[str, Any]:
    if stage not in {"review", "creator_draft"}:
        raise ValueError(f"Unknown handoff stage: {stage}")
    if status not in STATUSES:
        raise ValueError(f"Unknown handoff status: {status}")
    for path in expected_paths:
        resolve_repo_path(path)
    now = utc_now()
    handoff_id = f"{stage}:{pipeline_run_id}:{epic_key or 'portfolio'}"
    conn.execute(
        """
        INSERT INTO cursor_handoff (
          id, pipeline_run_id, stage, epic_key, prompt_version, prompt_text, prompt_sha256,
          coverage_profile, status, expected_paths_json, expected_hashes_json, retry_count,
          created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
        """,
        (
            handoff_id,
            pipeline_run_id,
            stage,
            epic_key,
            PROMPT_VERSION,
            prompt_text,
            _prompt_sha(prompt_text),
            coverage_profile,
            status,
            json.dumps(expected_paths),
            json.dumps(expected_hashes or {}),
            now,
            now,
        ),
    )
    row = conn.execute("SELECT * FROM cursor_handoff WHERE id = ?", (handoff_id,)).fetchone()
    return public_handoff(row)


def _assess(paths: list[str], hashes: dict[str, str]) -> tuple[str, str | None]:
    missing: list[str] = []
    invalid: list[str] = []
    stale: list[str] = []
    for path in paths:
        try:
            resolved = resolve_repo_path(path)
        except ValueError:
            invalid.append(path)
            continue
        if not resolved.is_file():
            missing.append(path)
            continue
        expected = hashes.get(path) or ""
        actual = file_sha256(resolved)
        if expected and actual != expected:
            stale.append(path)
            continue
        if not expected:
            try:
                json.loads(resolved.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                invalid.append(path)
    if invalid:
        return "invalid", "Output is not valid JSON: " + ", ".join(invalid)
    if stale:
        return "stale", "Output hash changed: " + ", ".join(stale)
    if missing:
        return "missing", "Expected output is missing: " + ", ".join(missing)
    return "present", None


def check_handoff(conn: Any, handoff_id: str) -> dict[str, Any]:
    row = conn.execute("SELECT * FROM cursor_handoff WHERE id = ?", (handoff_id,)).fetchone()
    if row is None:
        raise KeyError(handoff_id)
    current = public_handoff(row)
    assessment, detail = _assess(current["expected_paths"], current["expected_hashes"])
    status, error = decide_status(current["status"], assessment, detail)
    retry = current["retry_count"]
    if status in {"invalid_output", "stale_output"} and status != current["status"]:
        retry += 1
    now = utc_now()
    detected_at = current["detected_at"]
    if status == "output_detected" and not detected_at:
        detected_at = now
    conn.execute(
        """
        UPDATE cursor_handoff
        SET status = ?, error = ?, retry_count = ?, detected_at = ?, updated_at = ?
        WHERE id = ?
        """,
        (status, error, retry, detected_at, now, handoff_id),
    )
    updated = conn.execute("SELECT * FROM cursor_handoff WHERE id = ?", (handoff_id,)).fetchone()
    return public_handoff(updated)


SETTLE_SECONDS = 2.0


def suite_path_for(jira_key: str) -> str:
    return f"Trinity/creator/artifacts/{jira_key}/suite-payload.json"


def creator_handoff_id(pipeline_run_id: str, jira_key: str) -> str:
    return f"creator_draft:{pipeline_run_id}:{jira_key}"


def _creator_prompt_text(conn: Any, unit: Any) -> tuple[str, str]:
    from coverage_profile import resolve_for_unit
    from creator_handoff import build_creator_prompt, payload_readiness
    from review_unit_export import export_review_unit

    profile = resolve_for_unit(conn, unit)
    export = export_review_unit(conn, unit["id"])
    payload = export["payload"]
    pipeline_run_id = unit["pipeline_run_id"]
    jira_key = unit["jira_key"]
    workspace_url = f"{studio_base_url()}/workspace/{pipeline_run_id}"
    prompt = (
        build_creator_prompt(
            review_ref=export["review_ref"],
            jira_key=jira_key,
            creator_run_id=jira_key,
            gate_status=(payload.get("gate") or {}).get("status"),
            readiness_label=payload_readiness(payload),
            qa_planning_fit=unit["qa_planning_fit"],
            pipeline_run_id=pipeline_run_id,
            coverage=profile,
        )
        + "\n### Return to Studio\n\n"
        + f"Write the suite to `{suite_path_for(jira_key)}`. "
        + "Studio imports it automatically. Do not import it manually and do not import to Xray. "
        + f"Then return to {workspace_url}\n"
    )
    return prompt, profile["id"]


def _baseline_hashes(row: Any, relative: str) -> str:
    hashes = json_loads(row["expected_hashes_json"]) or {}
    if not hashes.get(relative):
        try:
            resolved = resolve_repo_path(relative)
        except ValueError:
            resolved = None
        if resolved is not None and resolved.is_file():
            hashes[relative] = file_sha256(resolved)
    return json.dumps(hashes)


def sync_creator_prompt(conn: Any, unit: Any) -> tuple[dict[str, Any] | None, bool]:
    """Rewrite an existing Creator prompt when its coverage depth no longer matches.

    Returns (handoff, changed). The handoff is None when this Epic has no prompt yet.
    """
    from coverage_profile import resolve_for_unit, stale_message

    pipeline_run_id = unit["pipeline_run_id"]
    jira_key = unit["jira_key"]
    handoff_id = creator_handoff_id(pipeline_run_id, jira_key)
    existing = conn.execute("SELECT * FROM cursor_handoff WHERE id = ?", (handoff_id,)).fetchone()
    if existing is None:
        return None, False
    profile = resolve_for_unit(conn, unit)
    if existing["coverage_profile"] == profile["id"]:
        return public_handoff(existing), False
    prompt, profile_id = _creator_prompt_text(conn, unit)
    relative = suite_path_for(jira_key)
    status = existing["status"]
    error = existing["error"]
    hashes = existing["expected_hashes_json"]
    if status in {"imported", "output_detected", "stale_output"}:
        status = "stale_output"
        error = stale_message(profile)
        hashes = _baseline_hashes(existing, relative)
    elif status == "invalid_output":
        status = "awaiting_cursor"
        error = None
    now = utc_now()
    conn.execute(
        """
        UPDATE cursor_handoff
        SET prompt_text = ?, prompt_sha256 = ?, coverage_profile = ?,
            status = ?, error = ?, copied_at = NULL, expected_hashes_json = ?, updated_at = ?
        WHERE id = ?
        """,
        (prompt, _prompt_sha(prompt), profile_id, status, error, hashes, now, handoff_id),
    )
    updated = conn.execute("SELECT * FROM cursor_handoff WHERE id = ?", (handoff_id,)).fetchone()
    return public_handoff(updated), True


def _refreshed_entry(jira_key: str, handoff: dict[str, Any]) -> dict[str, str]:
    return {"epic_key": jira_key, "status": handoff["status"], "id": handoff["id"]}


def _depth_message(profile: dict[str, Any], refreshed: list[dict[str, str]], *, epic_key: str | None = None) -> str:
    label = (
        f"{profile['label']} ({profile['test_count_min']}–{profile['test_count_max']} journeys)"
    )
    if epic_key:
        lead = f"{epic_key} coverage depth is now {label}."
    else:
        lead = f"Coverage depth is now {label}."
    if not refreshed:
        return lead
    keys = ", ".join(item["epic_key"] for item in refreshed)
    return f"{lead} Copy the Creator prompt again for {keys}."


def set_portfolio_coverage(conn: Any, run_id: str, profile_id: str) -> dict[str, Any]:
    from coverage_profile import profile_by_id

    profile = profile_by_id(profile_id)
    run = conn.execute("SELECT id FROM pipeline_run WHERE id = ?", (run_id,)).fetchone()
    if run is None:
        raise KeyError(run_id)
    now = utc_now()
    conn.execute(
        "UPDATE pipeline_run SET coverage_profile = ?, updated_at = ? WHERE id = ?",
        (profile["id"], now, run_id),
    )
    units = conn.execute(
        """
        SELECT * FROM review_unit
        WHERE pipeline_run_id = ? AND (coverage_profile IS NULL OR coverage_profile = '')
        ORDER BY jira_key
        """,
        (run_id,),
    ).fetchall()
    refreshed = []
    for unit in units:
        handoff, changed = sync_creator_prompt(conn, unit)
        if changed and handoff:
            refreshed.append(_refreshed_entry(unit["jira_key"], handoff))
    return {
        "coverage_profile": profile["id"],
        "refreshed": refreshed,
        "message": _depth_message(profile, refreshed),
    }


def set_epic_coverage(conn: Any, run_id: str, unit_id: str, profile_id: str | None) -> dict[str, Any]:
    from coverage_profile import profile_by_id, resolve_for_unit

    if profile_id:
        profile_by_id(profile_id)
    unit = conn.execute(
        "SELECT * FROM review_unit WHERE id = ? AND pipeline_run_id = ?",
        (unit_id, run_id),
    ).fetchone()
    if unit is None:
        raise KeyError(unit_id)
    now = utc_now()
    conn.execute(
        "UPDATE review_unit SET coverage_profile = ?, updated_at = ? WHERE id = ?",
        (profile_id or None, now, unit_id),
    )
    unit = conn.execute("SELECT * FROM review_unit WHERE id = ?", (unit_id,)).fetchone()
    handoff, changed = sync_creator_prompt(conn, unit)
    profile = resolve_for_unit(conn, unit)
    refreshed = [_refreshed_entry(unit["jira_key"], handoff)] if changed and handoff else []
    return {
        "coverage_profile": profile["id"],
        "override": unit["coverage_profile"],
        "refreshed": refreshed,
        "message": _depth_message(profile, refreshed, epic_key=unit["jira_key"]),
    }


def prepare_creator_handoff(conn: Any, unit_id: str) -> dict[str, Any]:
    """Export the approved review and record the Creator prompt. Idempotent per Epic."""
    unit = conn.execute("SELECT * FROM review_unit WHERE id = ?", (unit_id,)).fetchone()
    if unit is None:
        raise KeyError(unit_id)
    if not unit["approved_revision_id"]:
        raise ValueError("Approve this Epic's review before drafting tests.")
    if unit["qa_planning_fit"] == "not_fit":
        raise ValueError("This Epic is not testable yet. Resolve its blocker questions first.")
    pipeline_run_id = unit["pipeline_run_id"]
    jira_key = unit["jira_key"]
    handoff_id = creator_handoff_id(pipeline_run_id, jira_key)
    existing = conn.execute("SELECT * FROM cursor_handoff WHERE id = ?", (handoff_id,)).fetchone()
    if existing:
        handoff, _changed = sync_creator_prompt(conn, unit)
        if handoff is None:
            raise KeyError(handoff_id)
        return handoff
    prompt, profile_id = _creator_prompt_text(conn, unit)
    return create_handoff(
        conn,
        pipeline_run_id,
        stage="creator_draft",
        epic_key=jira_key,
        prompt_text=prompt,
        expected_paths=[suite_path_for(jira_key)],
        coverage_profile=profile_id,
    )


def _validate_suite(path: Any, *, coverage_profile: str | None = None) -> str | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return "Suite file is not valid JSON."
    if not isinstance(data, dict):
        return "Suite file must be a JSON object."
    tests = data.get("tests")
    if not isinstance(tests, list) or not tests:
        return "Suite file has no tests."
    for index, test in enumerate(tests, start=1):
        if not isinstance(test, dict) or not str(test.get("title") or "").strip():
            return f"Test {index} has no title."
    if coverage_profile:
        from coverage_profile import profile_by_id

        limit = profile_by_id(coverage_profile)["test_count_max"]
        if len(tests) > limit:
            return (
                f"This coverage depth allows at most {limit} journey tests; "
                f"the suite has {len(tests)}."
            )
        declared = data.get("coverage_profile")
        if isinstance(declared, dict) and declared.get("id") not in (None, "", coverage_profile):
            return (
                f"Suite coverage depth is {declared.get('id')}; "
                f"this prompt asked for {coverage_profile}."
            )
    return None


def _coverage_decision(current: dict[str, Any], path: Any, relative: str) -> str | tuple[str, str | None]:
    """Hold import while a coverage-depth change is waiting for a replacement suite.

    "continue" keeps the normal import rules. "accept" imports a replacement that
    declares the requested profile. A tuple is a status to save immediately.
    """
    import time

    from coverage_profile import is_coverage_stale

    requested = current.get("coverage_profile")
    error = current.get("error") or ""
    if not requested or not is_coverage_stale(error):
        return "continue"
    if not path.is_file():
        return "stale_output", error
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return "invalid_output", "Suite file is not valid JSON."
    declared = data.get("coverage_profile") if isinstance(data, dict) else None
    suite_id = declared.get("id") if isinstance(declared, dict) else None
    digest = file_sha256(path)
    known = (current.get("expected_hashes") or {}).get(relative) or ""
    replaced = bool(known) and digest != known
    if suite_id == requested and replaced:
        if time.time() - path.stat().st_mtime < SETTLE_SECONDS:
            return "stale_output", error
        return "accept"
    if replaced and suite_id and suite_id != requested:
        return (
            "invalid_output",
            f"Suite coverage depth is {suite_id}; this prompt asked for {requested}.",
        )
    if replaced and not suite_id:
        return (
            "invalid_output",
            f"The replacement suite must include coverage_profile.id {requested}.",
        )
    return "stale_output", error


def ingest_creator_output(
    conn: Any, handoff_id: str, *, accept_changes: bool = False
) -> dict[str, Any]:
    """Check the expected suite file and import it once it is complete and valid."""
    import time

    from import_review import import_test_case_batch

    row = conn.execute("SELECT * FROM cursor_handoff WHERE id = ?", (handoff_id,)).fetchone()
    if row is None:
        raise KeyError(handoff_id)
    current = public_handoff(row)
    relative = current["expected_paths"][0]
    path = resolve_repo_path(relative)
    now = utc_now()

    def save(status: str, error: str | None, **extra: Any) -> dict[str, Any]:
        retry = current["retry_count"]
        if status in {"invalid_output", "stale_output"} and status != current["status"]:
            retry += 1
        detected = current["detected_at"]
        if status in {"output_detected", "imported"} and not detected:
            detected = now
        conn.execute(
            """
            UPDATE cursor_handoff
            SET status = ?, error = ?, retry_count = ?, detected_at = ?,
                expected_hashes_json = COALESCE(?, expected_hashes_json),
                imported_at = COALESCE(?, imported_at), updated_at = ?
            WHERE id = ?
            """,
            (
                status,
                error,
                retry,
                detected,
                extra.get("hashes"),
                extra.get("imported_at"),
                now,
                handoff_id,
            ),
        )
        updated = conn.execute("SELECT * FROM cursor_handoff WHERE id = ?", (handoff_id,)).fetchone()
        return public_handoff(updated)

    decision = _coverage_decision(current, path, relative)
    if decision == "accept":
        accept_changes = True
    elif isinstance(decision, tuple):
        return save(decision[0], decision[1])

    if not path.is_file():
        status, error = decide_status(current["status"], "missing", f"Expected output is missing: {relative}")
        return save(status, error)
    digest = file_sha256(path)
    known = current["expected_hashes"].get(relative)
    if current["status"] in {"imported", "stale_output"} and known == digest:
        return save("imported", None)
    if current["status"] in {"imported", "stale_output"} and not accept_changes:
        return save("stale_output", "The suite changed on disk after import.")
    if time.time() - path.stat().st_mtime < SETTLE_SECONDS:
        return save("output_detected", None)
    problem = _validate_suite(path, coverage_profile=current.get("coverage_profile"))
    if problem:
        return save("invalid_output", problem)
    imported = import_test_case_batch(path, creator_run_id=current["epic_key"])
    unit_id = f"{current['pipeline_run_id']}:{current['epic_key']}"
    conn.execute(
        """
        UPDATE creator_run
        SET pipeline_run_id = ?, review_unit_id = ?, updated_at = ?
        WHERE id = ?
        """,
        (current["pipeline_run_id"], unit_id, now, imported["creator_run_id"]),
    )
    return save(
        "imported",
        None,
        hashes=json.dumps({relative: digest}),
        imported_at=now,
    )


def mark_copied(conn: Any, handoff_id: str) -> dict[str, Any]:
    row = conn.execute("SELECT id FROM cursor_handoff WHERE id = ?", (handoff_id,)).fetchone()
    if row is None:
        raise KeyError(handoff_id)
    now = utc_now()
    conn.execute(
        """
        UPDATE cursor_handoff
        SET copied_at = COALESCE(copied_at, ?), updated_at = ?
        WHERE id = ?
        """,
        (now, now, handoff_id),
    )
    updated = conn.execute("SELECT * FROM cursor_handoff WHERE id = ?", (handoff_id,)).fetchone()
    return public_handoff(updated)
