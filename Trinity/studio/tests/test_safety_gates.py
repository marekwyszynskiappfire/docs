import json
import os
import sys
from pathlib import Path

TRINITY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TRINITY_ROOT / "importer" / "scripts"))


def test_unlinked_review_requires_acknowledgement():
    from importer_review_gate import assess_reviewer_gate

    gate = assess_reviewer_gate(None)
    assert gate["linked"] is False
    assert gate["requires_acknowledgement"] is True
    assert gate["messages"]


def test_production_credential_profile_does_not_stick(monkeypatch, tmp_path):
    monkeypatch.setenv("XRAY_CLIENT_ID", "sandbox-id")
    (tmp_path / ".env.production").write_text("XRAY_CLIENT_ID=prod-id\n", encoding="utf-8")
    monkeypatch.setattr("studio_env.STUDIO_ROOT", tmp_path)
    from studio_env import importer_credential_scope

    with importer_credential_scope("appfire-production"):
        assert os.environ["XRAY_CLIENT_ID"] == "prod-id"
    assert os.environ["XRAY_CLIENT_ID"] == "sandbox-id"

    with importer_credential_scope("appfire-sandbox"):
        assert os.environ["XRAY_CLIENT_ID"] == "sandbox-id"


def test_production_cli_requires_confirmation():
    import xray_graphql_import as cli

    assert cli.production_confirmation_error({"environment": "production"}, "")
    assert cli.production_confirmation_error({"environment": "production"}, "PRODUCTION") is None
    assert cli.production_confirmation_error({"environment": "sandbox"}, "") is None


def test_cli_execute_gates_match_studio():
    import xray_graphql_import as cli

    assert cli.existing_xray_key_error({"draft_id": "TC-1", "existing_xray_test_key": "TC-9"}, False)
    assert cli.existing_xray_key_error({"draft_id": "TC-1", "existing_xray_test_key": "TC-9"}, True) is None
    missing = cli.reviewer_gate_execute_error({}, False)
    assert missing and "acknowledge" in missing.lower()
    assert cli.reviewer_gate_execute_error({}, True) is None


def test_known_creator_run_ignores_stale_export_file(studio_db, tmp_path):
    from api_models import ImporterPlanBody
    from db import db, utc_now
    from routers.importer import _resolve_importer_handoff

    run_id = "DEMO-4500"
    now = utc_now()
    case = {
        "draft_id": "TC-NEW",
        "title": "Current approved test",
        "linked_requirement_keys": ["DEMO-99"],
        "steps": [{"step": "Open the board", "expected_result": "The board is visible"}],
    }
    stale = tmp_path / "importer-payload.json"
    stale.write_text(
        json.dumps(
            {
                "export_kind": "creator_importer_handoff",
                "creator_run_id": run_id,
                "tests": [{"draft_id": "TC-OLD", "title": "Stale export"}],
            }
        ),
        encoding="utf-8",
    )
    with db() as conn:
        conn.execute(
            """
            INSERT INTO creator_run (id, label, status, created_at, updated_at)
            VALUES (?, ?, 'draft', ?, ?)
            """,
            (run_id, run_id, now, now),
        )
        conn.execute(
            """
            INSERT INTO test_case_row (
              id, creator_run_id, draft_id, title, human_review_status,
              marked_for_xray_import, updated_at
            ) VALUES (?, ?, 'TC-NEW', 'Current approved test', 'approved', 1, ?)
            """,
            (f"{run_id}:TC-NEW", run_id, now),
        )
        conn.execute(
            """
            INSERT INTO test_case_revision (test_case_row_id, revision, case_json, source, created_at, created_by)
            VALUES (?, 1, ?, 'import', ?, 'test')
            """,
            (f"{run_id}:TC-NEW", json.dumps(case), now),
        )
    body = ImporterPlanBody(
        jira_instance_id="appfire-sandbox",
        folder_path="/Trinity",
        creator_run_id=run_id,
        payload_path=str(stale),
    )
    handoff, resolved = _resolve_importer_handoff(body)
    assert resolved == run_id
    assert [test["draft_id"] for test in handoff["tests"]] == ["TC-NEW"]
    assert handoff["epic_key"] == "DEMO-4500"
