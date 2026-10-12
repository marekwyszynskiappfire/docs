from validate_for_xray import (
    deferrable_export_warnings,
    enrich_test_for_xray_import,
    export_preflight_warnings,
    validate_test_legacy,
)


def _minimal_test(**overrides):
    base = {
        "title": "Sample",
        "linked_requirement_keys": ["ONE-1"],
        "steps": [{"step": "Do", "expected_result": "See"}],
        "coverage_catalog_id": "AC-1",
        "execution_tier": "P1",
        "test_pattern": "journey",
        "role": "Admin",
        "customer_impact": "High",
        "test_data_required": False,
        "test_data_prerequisites": "None",
    }
    base.update(overrides)
    return base


def test_enrich_adds_coverage_catalog_id():
    t = enrich_test_for_xray_import({"linked_ac_ids": ["42"]})
    assert t["coverage_catalog_id"] == "42"


def test_test_type_xray_coercion_note():
    from validate_for_xray import test_type_xray_coercion

    assert test_type_xray_coercion({"test_type": "Generic"}) == "Generic → Manual (Xray import)"
    assert test_type_xray_coercion({"test_type": "Manual"}) is None


def test_enrich_coerces_generic_to_manual():
    t = enrich_test_for_xray_import({"test_type": "Generic"})
    assert t["test_type"] == "Manual"


def test_legacy_validate_passes_minimal():
    assert validate_test_legacy(_minimal_test()) == []


def test_deferrable_warning():
    t = _minimal_test(deferrable=True, draft_id="TC-001")
    warnings = deferrable_export_warnings([t])
    assert any("TC-001" in w for w in warnings)


def test_export_preflight_includes_deferrable():
    t = _minimal_test(deferrable=True, draft_id="TC-002")
    payload = {"tests": [t]}
    warnings = export_preflight_warnings(payload)
    assert len(warnings) >= 1
