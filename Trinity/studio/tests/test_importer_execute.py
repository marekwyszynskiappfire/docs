from unittest.mock import MagicMock, patch

from importer_execute import config_from_plan, run_batch_execute


def test_config_from_plan_merges_project_id():
    plan = {"project_key": "TC", "project_resolution": {"project_id": "99999"}}
    with (
        patch("importer_execute.load_config") as load,
        patch("importer_execute.resolve_mapping_path", return_value=MagicMock()),
    ):
        load.return_value = {"project": {"key": "TC", "id": "1"}, "defaults": {}}
        cfg = config_from_plan(plan, "Trinity/importer/config/mappings/appfire-production.json")
    assert cfg["project"]["id"] == "99999"
    assert cfg["project"]["key"] == "TC"


@patch("importer_execute.authenticate", return_value="token")
@patch("importer_execute.execute_single_test_import")
def test_run_batch_execute(mock_single, _auth, tmp_path):
    mock_single.return_value = {"action": "created", "xray_key": "TC-1", "errors": []}
    plan = {
        "project_key": "TC",
        "target": {"folder_path": "/F", "create_folder_if_missing": False},
        "tests": [{"draft_id": "TC-001", "validation_errors": []}],
        "mapping": {"path": "Trinity/importer/config/mappings/appfire-production.json"},
        "project_resolution": {},
    }
    handoff = {
        "creator_run_id": "run-1",
        "tests": [{"draft_id": "TC-001", "title": "t", "linked_requirement_keys": ["ONE-1"], "steps": []}],
    }
    batch_path = tmp_path / "importer-payload.json"
    with patch("importer_execute.load_config") as load:
        load.return_value = {
            "project": {"key": "TC", "id": "1"},
            "defaults": {"folder_path": "/x"},
            "jira": {},
            "xray": {},
        }
        summary = run_batch_execute(
            plan=plan,
            handoff=handoff,
            batch_path=batch_path,
            mapping_path="Trinity/importer/config/mappings/appfire-production.json",
            skip_requirement_link=True,
        )
    assert summary["created"] == 1
    assert summary["failed"] == 0
    mock_single.assert_called_once()
