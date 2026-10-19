from pathlib import Path

from priority_score import (
    apply_priority_fields,
    build_execution_plan,
    compute_total,
    tier_from_total,
    validate_priority_policy,
)
def test_tier_bands():
    assert tier_from_total(15) == "P0"
    assert tier_from_total(13) == "P0"
    assert tier_from_total(12) == "P1"
    assert tier_from_total(10) == "P1"
    assert tier_from_total(9) == "P2"
    assert tier_from_total(7) == "P2"
    assert tier_from_total(6) == "P3"
    assert compute_total(4, 3, 4) == 11


def test_apply_fills_canonical_p1():
    t = apply_priority_fields(
        {
            "draft_id": "TC-001",
            "execution_tier": "P1",
            "customer_impact": "Admins cannot complete the primary setup.",
        }
    )
    assert t["priority"] == "High"
    assert t["priority_score"]["total"] == 11
    assert t["priority_score"]["derived_tier"] == "P1"
    assert t["deferrable"] is False
    assert validate_priority_policy(t) == []


def test_p3_requires_deferrable():
    t = apply_priority_fields({"draft_id": "TC-003", "execution_tier": "P3"})
    assert t["priority"] == "Low"
    assert t["deferrable"] is True
    assert t["deferrable_rationale"]
    assert validate_priority_policy(t) == []


def test_mismatch_priority_is_error():
    t = apply_priority_fields({"draft_id": "TC-002", "execution_tier": "P1"})
    t["priority"] = "Low"
    errors = validate_priority_policy(t)
    assert any("does not match P1" in e for e in errors)


def test_demo_suite_priority_policy():
    import json

    path = Path(__file__).resolve().parents[3] / "Trinity/creator/samples/demo-story.suite.json"
    batch = json.loads(path.read_text(encoding="utf-8"))
    for test in batch["tests"]:
        assert validate_priority_policy(test) == []
    plan = batch["execution_plan"]
    assert plan["p1_mandatory"]["count"] == 2
    assert build_execution_plan(batch["tests"])["p1_mandatory"]["count"] == 2
