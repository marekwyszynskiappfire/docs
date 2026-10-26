"""Cursor handoff status, Creator ingestion, and workspace guidance."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cursor_handoff import create_handoff, decide_status


def _use_repo(monkeypatch, root: Path) -> None:
    import cursor_handoff
    import review_unit_export
    import studio_paths

    monkeypatch.setattr(studio_paths, "DOCS_REPO_ROOT", root)
    monkeypatch.setattr(review_unit_export, "EXPORT_ROOT", root / "exports")
    monkeypatch.setattr(cursor_handoff, "SETTLE_SECONDS", 0)


def _write_epic(run_dir: Path, key: str, questions: list | None = None) -> None:
    epic = run_dir / key
    epic.mkdir(parents=True)
    (epic / "review-payload.json").write_text(
        json.dumps(
            {
                "scope": {"type": "epic", "value": key},
                "requirements": [{"summary": key, "jira_key": key}],
                "questions": questions or [],
            }
        ),
        encoding="utf-8",
    )


def _publish(tmp_path: Path, questions: list | None = None):
    from pipeline_manifest import build_manifest, import_pipeline_manifest, write_manifest

    run_dir = tmp_path / "runs" / "demo-portfolio"
    _write_epic(run_dir, "DEMO-4500", questions)
    path = write_manifest(
        run_dir,
        build_manifest(
            run_dir,
            "demo-portfolio",
            product_id="demo",
            persona_id="reviewer-expert-qa-automation.md",
            scope_kind="epic_keys",
            scope_value="DEMO-4500",
        ),
    )
    return path, import_pipeline_manifest(path)


def _write_suite(root: Path, key: str, tests: list[dict], coverage_profile: dict | None = None) -> Path:
    path = root / "Trinity" / "creator" / "artifacts" / key / "suite-payload.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict = {"run_id": key, "tests": tests}
    if coverage_profile:
        payload["coverage_profile"] = coverage_profile
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_decide_status_absence_is_not_failure():
    assert decide_status("awaiting_cursor", "missing", "gone") == ("awaiting_cursor", None)
    assert decide_status("imported", "missing", "gone")[0] == "stale_output"
    assert decide_status("awaiting_cursor", "invalid", "bad")[0] == "invalid_output"
    assert decide_status("imported", "present", None) == ("imported", None)
    assert decide_status("awaiting_cursor", "present", None) == ("output_detected", None)


def test_import_records_one_review_handoff(studio_db, monkeypatch, tmp_path):
    _use_repo(monkeypatch, tmp_path)
    path, imported = _publish(tmp_path)
    run_id = imported["pipeline_run_id"]

    from pipeline_manifest import import_pipeline_manifest

    second = import_pipeline_manifest(path)
    assert second["pipeline_run_id"] == run_id
    assert second["unchanged"] is True

    from db import connect

    with connect() as conn:
        rows = conn.execute("SELECT id, status, prompt_text FROM cursor_handoff").fetchall()
    assert [(row["id"], row["status"]) for row in rows] == [(f"review:{run_id}", "imported")]
    assert "rescan" in rows[0]["prompt_text"]
    assert "Do not import to Xray" in rows[0]["prompt_text"]


def test_guidance_walks_one_epic_end_to_end(client, monkeypatch, tmp_path):
    _use_repo(monkeypatch, tmp_path)
    _path, imported = _publish(tmp_path)
    run_id = imported["pipeline_run_id"]

    def summary():
        response = client.get(f"/api/workspace/{run_id}")
        assert response.status_code == 200
        return response.json()

    body = summary()
    assert body["next_action"]["current_stage"] == "review"
    assert body["next_action"]["primary"]["kind"] == "approve_review"
    assert body["portfolio_actions"] == []
    assert [stage["status"] for stage in body["stages"]] == [
        "current",
        "upcoming",
        "upcoming",
        "upcoming",
    ]
    unit_id = body["epics"][0]["unit_id"]
    assert body["epics"][0]["verdict"] == "testable_now"

    assert client.post(f"/api/units/{unit_id}/approve").status_code == 200
    body = summary()
    assert body["next_action"]["primary"]["kind"] == "prepare_creator"
    assert body["stages"][0]["status"] == "complete"

    prepared = client.post(f"/api/workspace/{run_id}/units/{unit_id}/prepare-creator")
    assert prepared.status_code == 200
    handoff_id = prepared.json()["id"]
    again = client.post(f"/api/workspace/{run_id}/units/{unit_id}/prepare-creator")
    assert again.json()["id"] == handoff_id

    body = summary()
    assert body["next_action"]["primary"]["kind"] == "copy_prompt"
    assert "suite-payload.json" in body["next_action"]["cursor_prompt"]["text"]
    assert body["watch_handoff_ids"] == [handoff_id]

    waiting = client.post(f"/api/workspace/{run_id}/handoffs/{handoff_id}/check")
    assert waiting.json()["status"] == "awaiting_cursor"
    assert waiting.json()["error"] is None

    _write_suite(tmp_path, "DEMO-4500", [{"draft_id": "TC-001", "title": "Export CSV"}])
    done = client.post(f"/api/workspace/{run_id}/handoffs/{handoff_id}/check")
    assert done.json()["status"] == "imported"

    body = summary()
    epic = body["epics"][0]
    assert epic["tests"]["total"] == 1
    assert body["next_action"]["current_stage"] == "test_review"
    assert body["watch_handoff_ids"] == []

    test_id = f"{epic['creator_run_id']}:TC-001"
    patched = client.patch(f"/api/tests/{test_id}", json={"human_review_status": "approved"})
    assert patched.status_code == 200
    body = summary()
    assert body["next_action"]["current_stage"] == "import"
    assert body["next_action"]["primary"]["kind"] == "review_tests"

    client.patch(f"/api/tests/{test_id}", json={"marked_for_xray_import": True})
    body = summary()
    assert body["next_action"]["primary"]["kind"] == "open_importer"
    assert body["next_action"]["primary"]["label"] == "Plan Xray import"
    assert "path" not in body["next_action"]["primary"]


def test_invalid_suite_then_fixed_is_imported(client, monkeypatch, tmp_path):
    _use_repo(monkeypatch, tmp_path)
    _path, imported = _publish(tmp_path)
    run_id = imported["pipeline_run_id"]
    unit_id = f"{run_id}:DEMO-4500"
    client.post(f"/api/units/{unit_id}/approve")
    handoff_id = client.post(
        f"/api/workspace/{run_id}/units/{unit_id}/prepare-creator"
    ).json()["id"]

    _write_suite(tmp_path, "DEMO-4500", [])
    bad = client.post(f"/api/workspace/{run_id}/handoffs/{handoff_id}/check").json()
    assert bad["status"] == "invalid_output"
    assert bad["error"] == "Suite file has no tests."
    body = client.get(f"/api/workspace/{run_id}").json()
    assert body["next_action"]["title"] == "Fix the suite file for DEMO-4500"
    assert handoff_id in body["watch_handoff_ids"]

    _write_suite(tmp_path, "DEMO-4500", [{"title": "Export CSV"}])
    good = client.post(f"/api/workspace/{run_id}/handoffs/{handoff_id}/check").json()
    assert good["status"] == "imported"


def test_existing_suite_waits_for_a_new_file(client, monkeypatch, tmp_path):
    _use_repo(monkeypatch, tmp_path)
    _path, imported = _publish(tmp_path)
    run_id = imported["pipeline_run_id"]
    unit_id = f"{run_id}:DEMO-4500"
    client.post(f"/api/units/{unit_id}/approve")
    _write_suite(tmp_path, "DEMO-4500", [{"draft_id": "TC-OLD", "title": "Already on disk"}])

    prepared = client.post(f"/api/workspace/{run_id}/units/{unit_id}/prepare-creator")
    assert prepared.status_code == 200
    handoff_id = prepared.json()["id"]
    held = client.post(f"/api/workspace/{run_id}/handoffs/{handoff_id}/check").json()
    assert held["status"] == "awaiting_cursor"

    _write_suite(tmp_path, "DEMO-4500", [{"draft_id": "TC-NEW", "title": "Replacement"}])
    done = client.post(f"/api/workspace/{run_id}/handoffs/{handoff_id}/check").json()
    assert done["status"] == "imported"
    body = client.get(f"/api/workspace/{run_id}").json()
    assert body["epics"][0]["tests"]["total"] == 1
    assert body["epics"][0]["creator_run_id"]


def test_changed_suite_after_import_needs_confirmation(client, monkeypatch, tmp_path):
    _use_repo(monkeypatch, tmp_path)
    _path, imported = _publish(tmp_path)
    run_id = imported["pipeline_run_id"]
    unit_id = f"{run_id}:DEMO-4500"
    client.post(f"/api/units/{unit_id}/approve")
    handoff_id = client.post(
        f"/api/workspace/{run_id}/units/{unit_id}/prepare-creator"
    ).json()["id"]
    _write_suite(tmp_path, "DEMO-4500", [{"draft_id": "TC-001", "title": "One"}])
    client.post(f"/api/workspace/{run_id}/handoffs/{handoff_id}/check")

    _write_suite(
        tmp_path,
        "DEMO-4500",
        [{"draft_id": "TC-001", "title": "One"}, {"draft_id": "TC-002", "title": "Two"}],
    )
    stale = client.post(f"/api/workspace/{run_id}/handoffs/{handoff_id}/check").json()
    assert stale["status"] == "stale_output"
    body = client.get(f"/api/workspace/{run_id}").json()
    assert body["next_action"]["primary"]["kind"] == "accept_changes"
    assert body["epics"][0]["tests"]["total"] == 1

    accepted = client.post(
        f"/api/workspace/{run_id}/handoffs/{handoff_id}/check",
        json={"accept_changes": True},
    ).json()
    assert accepted["status"] == "imported"
    body = client.get(f"/api/workspace/{run_id}").json()
    assert body["epics"][0]["tests"]["total"] == 2


def test_not_fit_epic_is_blocked_and_cannot_draft(client, monkeypatch, tmp_path):
    _use_repo(monkeypatch, tmp_path)
    _path, imported = _publish(tmp_path)
    run_id = imported["pipeline_run_id"]
    unit_id = f"{run_id}:DEMO-4500"
    client.patch(f"/api/units/{unit_id}", json={"qa_planning_fit": "not_fit"})
    body = client.get(f"/api/workspace/{run_id}").json()
    assert body["epics"][0]["verdict"] == "not_testable_yet"
    assert body["next_action"]["title"] == "No Epic is testable yet"
    client.post(f"/api/units/{unit_id}/approve")
    refused = client.post(f"/api/workspace/{run_id}/units/{unit_id}/prepare-creator")
    assert refused.status_code == 400


def test_authored_verdict_wins_over_the_guess():
    from review_payload_fields import testability_verdict

    payload = {
        "report": {
            "testability_verdict": "testable_now",
            "testability_reasons": ["The success result is observable in the Epic description."],
        },
        "questions": [{"priority": "High", "status": "open"}],
        "findings": [{"blocks_test_generation": True}],
    }
    assert testability_verdict(payload, "not_fit") == "testable_now"


def test_open_high_question_means_clarifications(client, monkeypatch, tmp_path):
    _use_repo(monkeypatch, tmp_path)
    _path, imported = _publish(
        tmp_path,
        questions=[{"question_id": "Q1", "question": "Which roles?", "priority": "High"}],
    )
    body = client.get(f"/api/workspace/{imported['pipeline_run_id']}").json()
    epic = body["epics"][0]
    assert epic["verdict"] == "testable_with_clarifications"
    assert epic["blocker_questions"][0]["question_id"] == "Q1"


def test_missing_creator_output_stays_awaiting(studio_db, monkeypatch, tmp_path):
    _use_repo(monkeypatch, tmp_path)
    _path, imported = _publish(tmp_path)
    from cursor_handoff import ingest_creator_output
    from db import connect

    with connect() as conn:
        created = create_handoff(
            conn,
            imported["pipeline_run_id"],
            stage="creator_draft",
            epic_key="DEMO-4500",
            prompt_text="Draft the suite, then return to the workspace.",
            expected_paths=["Trinity/creator/artifacts/DEMO-4500/suite-payload.json"],
        )
        checked = ingest_creator_output(conn, created["id"])
    assert checked["status"] == "awaiting_cursor"
    assert checked["error"] is None
    assert checked["retry_count"] == 0


def test_create_handoff_rejects_path_outside_repo(studio_db, monkeypatch, tmp_path):
    _use_repo(monkeypatch, tmp_path)
    _path, imported = _publish(tmp_path)
    from db import connect

    with connect() as conn, pytest.raises(ValueError):
        create_handoff(
            conn,
            imported["pipeline_run_id"],
            stage="creator_draft",
            epic_key="DEMO-4500",
            prompt_text="x",
            expected_paths=["../outside.json"],
        )


def test_portfolio_actions_cover_two_epics(client, monkeypatch, tmp_path):
    from pipeline_manifest import build_manifest, import_pipeline_manifest, write_manifest

    _use_repo(monkeypatch, tmp_path)
    run_dir = tmp_path / "runs" / "demo-portfolio"
    _write_epic(run_dir, "DEMO-4500")
    _write_epic(run_dir, "DEMO-4501")
    path = write_manifest(
        run_dir,
        build_manifest(
            run_dir,
            "demo-portfolio",
            product_id="demo",
            persona_id="reviewer-expert-qa-automation.md",
            scope_kind="epic_keys",
            scope_value="DEMO-4500,DEMO-4501",
        ),
    )
    run_id = import_pipeline_manifest(path)["pipeline_run_id"]

    def summary():
        response = client.get(f"/api/workspace/{run_id}")
        assert response.status_code == 200
        return response.json()

    for key in ("DEMO-4500", "DEMO-4501"):
        assert client.post(f"/api/units/{run_id}:{key}/approve").status_code == 200

    body = summary()
    batch = next(item for item in body["portfolio_actions"] if item["kind"] == "prepare_creator_batch")
    assert batch["epic_keys"] == ["DEMO-4500", "DEMO-4501"]
    assert body["next_action"]["epic_key"] == "DEMO-4500"

    prepared = client.post(f"/api/workspace/{run_id}/prepare-creator-batch")
    assert prepared.status_code == 200
    assert [item["epic_key"] for item in prepared.json()["prepared"]] == ["DEMO-4500", "DEMO-4501"]
    again = client.post(f"/api/workspace/{run_id}/prepare-creator-batch")
    assert again.json()["prepared"] == []

    body = summary()
    copied = next(item for item in body["portfolio_actions"] if item["kind"] == "copy_creator_prompts")
    assert copied["epic_keys"] == ["DEMO-4500", "DEMO-4501"]

    for key in ("DEMO-4500", "DEMO-4501"):
        _write_suite(tmp_path, key, [{"draft_id": "TC-001", "title": key}])
        handoff_id = f"creator_draft:{run_id}:{key}"
        assert client.post(f"/api/workspace/{run_id}/handoffs/{handoff_id}/check").json()["status"] == "imported"

    body = summary()
    review = next(item for item in body["portfolio_actions"] if item["kind"] == "review_selected_tests")
    assert review["epic_keys"] == ["DEMO-4500", "DEMO-4501"]

    for epic in body["epics"]:
        client.patch(
            f"/api/tests/{epic['creator_run_id']}:TC-001",
            json={"human_review_status": "approved", "marked_for_xray_import": True},
        )
    body = summary()
    plans = next(item for item in body["portfolio_actions"] if item["kind"] == "preview_import_plans")
    assert plans["epic_keys"] == ["DEMO-4500", "DEMO-4501"]


def test_coverage_depth_rewrites_the_creator_prompt(client, monkeypatch, tmp_path):
    from pipeline_manifest import build_manifest, import_pipeline_manifest, write_manifest

    _use_repo(monkeypatch, tmp_path)
    run_dir = tmp_path / "runs" / "demo-portfolio"
    _write_epic(run_dir, "DEMO-4500")
    _write_epic(run_dir, "DEMO-4501")
    path = write_manifest(
        run_dir,
        build_manifest(
            run_dir,
            "demo-portfolio",
            product_id="demo",
            persona_id="reviewer-expert-qa-automation.md",
            scope_kind="epic_keys",
            scope_value="DEMO-4500,DEMO-4501",
        ),
    )
    run_id = import_pipeline_manifest(path)["pipeline_run_id"]

    def summary():
        response = client.get(f"/api/workspace/{run_id}")
        assert response.status_code == 200
        return response.json()

    body = summary()
    assert body["coverage_profile"] == "balanced"
    assert [item["id"] for item in body["coverage_profiles"]] == [
        "smoke",
        "core",
        "balanced",
        "thorough",
        "edge",
    ]
    for key in ("DEMO-4500", "DEMO-4501"):
        assert client.post(f"/api/units/{run_id}:{key}/approve").status_code == 200
        prepared = client.post(f"/api/workspace/{run_id}/units/{run_id}:{key}/prepare-creator")
        assert prepared.status_code == 200
        assert "profile `balanced`" in prepared.json()["prompt_text"]
        assert "5–8" in prepared.json()["prompt_text"]

    unknown = client.put(
        f"/api/workspace/{run_id}/coverage-profile",
        json={"profile": "hot"},
    )
    assert unknown.status_code == 400

    override = client.put(
        f"/api/workspace/{run_id}/units/{run_id}:DEMO-4501/coverage-profile",
        json={"profile": "edge"},
    )
    assert override.status_code == 200
    assert "12–20" in client.get(f"/api/workspace/{run_id}").json()["epics"][1]["creator_handoff"]["prompt"]

    moved = client.put(
        f"/api/workspace/{run_id}/coverage-profile",
        json={"profile": "smoke"},
    )
    assert moved.status_code == 200
    body = summary()
    prompts = {epic["jira_key"]: epic["creator_handoff"]["prompt"] for epic in body["epics"]}
    assert "profile `smoke`" in prompts["DEMO-4500"]
    assert "1–2" in prompts["DEMO-4500"]
    assert "profile `edge`" in prompts["DEMO-4501"]
    assert body["epics"][0]["creator_handoff"]["status"] == "awaiting_cursor"

    handoff_id = body["epics"][0]["creator_handoff"]["id"]
    too_many = [{"draft_id": f"TC-{index}", "title": f"Case {index}"} for index in range(3)]
    _write_suite(tmp_path, "DEMO-4500", too_many)
    rejected = client.post(f"/api/workspace/{run_id}/handoffs/{handoff_id}/check").json()
    assert rejected["status"] == "invalid_output"
    assert "at most 2" in rejected["error"]

    _write_suite(tmp_path, "DEMO-4500", [{"draft_id": "TC-001", "title": "Happy path"}])
    imported = client.post(f"/api/workspace/{run_id}/handoffs/{handoff_id}/check").json()
    assert imported["status"] == "imported"

    deepened = client.put(
        f"/api/workspace/{run_id}/coverage-profile",
        json={"profile": "thorough"},
    )
    assert deepened.status_code == 200
    assert "Copy the Creator prompt again" in deepened.json()["message"]
    body = summary()
    epic = next(item for item in body["epics"] if item["jira_key"] == "DEMO-4500")
    assert epic["creator_handoff"]["status"] == "stale_output"
    assert epic["creator_handoff"]["error"].startswith("Coverage depth changed")
    assert "profile `thorough`" in epic["creator_handoff"]["prompt"]
    assert body["next_action"]["primary"]["kind"] == "copy_prompt"
    held = client.post(f"/api/workspace/{run_id}/handoffs/{handoff_id}/check").json()
    assert held["status"] == "stale_output"
    assert held["error"].startswith("Coverage depth changed")

    other = next(item for item in body["epics"] if item["jira_key"] == "DEMO-4501")
    assert "profile `edge`" in other["creator_handoff"]["prompt"]

    _write_suite(
        tmp_path,
        "DEMO-4500",
        [{"draft_id": "TC-001", "title": "Happy path"}],
        coverage_profile={"id": "thorough", "test_count_min": 8, "test_count_max": 12, "actual_count": 1},
    )
    replaced = client.post(f"/api/workspace/{run_id}/handoffs/{handoff_id}/check").json()
    assert replaced["status"] == "imported"
