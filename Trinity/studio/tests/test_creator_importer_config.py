from creator_importer_config import importer_defaults_for_handoff, resolve_folder_template


def test_folder_template_substitution():
    assert resolve_folder_template("/TC Importer/{requirement_key}", "ONE-99") == "/TC Importer/ONE-99"


def test_importer_defaults_from_handoff():
    handoff = {
        "product_id": "bigpicture",
        "tests": [{"linked_requirement_keys": ["ONE-228469"]}],
    }
    defaults = importer_defaults_for_handoff(handoff)
    assert defaults["default_jira_project_key"] == "TC"
    assert "ONE-228469" in defaults["suggested_folder_path"]
    assert defaults["primary_requirement_key"] == "ONE-228469"
