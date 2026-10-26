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
