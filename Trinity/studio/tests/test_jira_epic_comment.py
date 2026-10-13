"""Jira epic comment preview and CQ-adjacent helpers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURE = (
    Path(__file__).resolve().parents[1] / "fixtures/demo-reviewer-run/DEMO-4500/review-payload.json"
)


@pytest.fixture()
def demo_payload() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_epic_feedback_count_zero_by_default(demo_payload):
    from jira_epic_comment import epic_feedback_count

    assert epic_feedback_count(demo_payload) == 0


def test_epic_feedback_count_with_send_to_epic(demo_payload):
    from jira_epic_comment import epic_feedback_count

    demo_payload["studio_qa"] = {
        "decisions": {
            "Q1": {"validity": "valid", "send_to_epic": True, "comment": "Please confirm"},
        }
    }
    # demo may not have Q1 - add a question
    demo_payload.setdefault("questions", []).append(
        {"question_id": "Q1", "question": "Test?", "status": "open", "priority": "High"}
    )
    assert epic_feedback_count(demo_payload) >= 1


def test_recommend_studio_when_send_to_epic(studio_db, demo_payload):
    from db import db
    from jira_epic_comment import recommend_variant

    demo_payload["studio_qa"] = {"decisions": {"Q1": {"validity": "valid", "send_to_epic": True}}}
    demo_payload.setdefault("questions", []).append(
        {"question_id": "Q1", "question": "?", "status": "open"}
    )
    with db() as conn:
        rec = recommend_variant(conn, "unit-x", demo_payload)
    assert rec["variant"] == "studio"


def test_preview_studio_empty_blocker(studio_db, demo_payload):
    from db import db
    from jira_epic_comment import preview_comment

    with db() as conn:
        out = preview_comment(conn, "u1", demo_payload, "DEMO-4500", "studio")
    assert "studio_variant_empty" in out.get("blockers", [])


def test_cq02_catalog_warning():
    from creator_coverage import cq02_catalog_warnings

    cases = {
        "r1": {
            "draft_id": "DR-1",
            "coverage_catalog_id": "AC-1",
            "linked_ac_ids": ["AC-2"],
        }
    }
    w = cq02_catalog_warnings(cases)
    assert len(w) == 1
    assert "CQ-02" in w[0]


def test_jira_status_endpoint(client):
    r = client.get("/api/jira/status")
    assert r.status_code == 200
    assert "configured" in r.json()
