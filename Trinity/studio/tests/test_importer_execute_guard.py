import pytest

from importer_execute_guard import (
    assert_execute_allowed,
    finalize_import_plan_execute_readiness,
    redaction_preflight_warnings,
)


def test_redaction_preflight_filters_email_and_sensitive_url():
    warnings = [
        "Possible email in step 2",
        "Unrelated warning",
        "Sensitive URL in expected result",
    ]
    hits = redaction_preflight_warnings(warnings)
    assert len(hits) == 2
    assert "email" in hits[0].lower()


def test_idempotency_blocks_execute_until_acknowledged():
    plan = {
        "credentials": {"execute_ready": True},
        "idempotency_warnings": ["TC-001 already has Xray key TC-9999"],
        "export_preflight_warnings": [],
    }
    finalize_import_plan_execute_readiness(plan, idempotency_acknowledged=False)
    assert plan["credentials"]["execute_ready"] is False
    assert "xray_idempotency" in plan["execute_blockers"]
    assert plan["idempotency"]["requires_acknowledgement"] is True

    plan["credentials"]["execute_ready"] = True
    finalize_import_plan_execute_readiness(plan, idempotency_acknowledged=True)
    assert plan["credentials"]["execute_ready"] is True
    assert "xray_idempotency" not in plan.get("execute_blockers", [])


def test_assert_execute_allowed_raises_on_idempotency():
    plan = {
        "credentials": {"execute_ready": True},
        "idempotency_warnings": ["duplicate key"],
        "export_preflight_warnings": [],
    }
    with pytest.raises(ValueError, match="acknowledge idempotency"):
        assert_execute_allowed(plan, idempotency_acknowledged=False)


def test_redaction_blocks_execute_by_default(monkeypatch):
    monkeypatch.delenv("STUDIO_IMPORTER_ALLOW_REDACTION_EXECUTE", raising=False)
    plan = {
        "credentials": {"execute_ready": True},
        "export_preflight_warnings": ["Possible email in title"],
        "idempotency_warnings": [],
    }
    finalize_import_plan_execute_readiness(plan, idempotency_acknowledged=True)
    assert plan["credentials"]["execute_ready"] is False
    assert "export_preflight_redaction" in plan["execute_blockers"]

    with pytest.raises(ValueError, match="redaction"):
        assert_execute_allowed(plan, idempotency_acknowledged=True)


def test_redaction_override_env_allows_execute(monkeypatch):
    monkeypatch.setenv("STUDIO_IMPORTER_ALLOW_REDACTION_EXECUTE", "1")
    plan = {
        "credentials": {"execute_ready": True},
        "export_preflight_warnings": ["Possible email in title"],
        "idempotency_warnings": [],
    }
    finalize_import_plan_execute_readiness(plan, idempotency_acknowledged=True)
    assert plan["credentials"]["execute_ready"] is True
    assert_execute_allowed(plan, idempotency_acknowledged=True)
