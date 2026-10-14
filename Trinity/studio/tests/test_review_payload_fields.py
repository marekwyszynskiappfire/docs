from review_payload_fields import (
    apply_payload_fields_to_unit,
    gate_status_from_payload,
    qa_planning_fit_from_payload,
)


def test_qa_planning_fit_prefers_report():
    payload = {
        "report": {"qa_planning_fit": "provisional"},
        "requirements": [{"qa_planning_fit": "fit"}],
    }
    assert qa_planning_fit_from_payload(payload) == "provisional"


def test_qa_planning_fit_falls_back_to_requirements():
    payload = {"requirements": [{"qa_planning_fit": "not_fit"}]}
    assert qa_planning_fit_from_payload(payload) == "not_fit"


def test_gate_status_from_gate_object():
    assert gate_status_from_payload({"gate": {"status": "PASS_WITH_WARNINGS"}}) == "PASS_WITH_WARNINGS"


def test_apply_payload_fields_to_unit():
    unit = {"qa_planning_fit": None, "gate_status": None}
    apply_payload_fields_to_unit(
        unit,
        {"report": {"qa_planning_fit": "provisional"}, "gate": {"status": "PASS"}},
    )
    assert unit["qa_planning_fit"] == "provisional"
    assert unit["gate_status"] == "PASS"
