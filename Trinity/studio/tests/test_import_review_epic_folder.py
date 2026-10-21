"""Reviewer import: epic folder name must match payload epic key."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from db import db
from import_review import (
    epic_key_from_payload,
    import_reviewer_run,
    import_test_case_batch,
    repair_creator_pipeline_links,
)


def test_epic_key_from_payload_demo_fixture():
    fixture = (
        Path(__file__).resolve().parents[1]
        / "fixtures/demo-reviewer-run/DEMO-4500/review-payload.json"
    )
    payload = json.loads(fixture.read_text(encoding="utf-8"))
    assert epic_key_from_payload(payload) == "DEMO-4500"


def test_import_rejects_folder_epic_mismatch(tmp_path: Path):
    run = tmp_path / "run"
    wrong = run / "ONE-90001"
    wrong.mkdir(parents=True)
    fixture = (
        Path(__file__).resolve().parents[1]
        / "fixtures/demo-reviewer-run/DEMO-4500/review-payload.json"
    )
    (wrong / "review-payload.json").write_text(fixture.read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(ValueError, match="does not match payload epic key"):
        import_reviewer_run(run)


def test_creator_batch_links_to_reviewer_pipeline_and_product(
    studio_db, tmp_path: Path, monkeypatch
):
    monkeypatch.setenv("TRINITY_OPERATOR_ID", "operator@appfire.com")
    monkeypatch.setenv("TRINITY_OPERATOR_NAME", "QA Operator")
    run = tmp_path / "bigpicture-run"
    epic = run / "ONE-90001"
    epic.mkdir(parents=True)
    review = epic / "review-payload.json"
    review.write_text(
        json.dumps(
            {
                "scope": {"type": "epic", "value": "ONE-90001"},
                "requirements": [
                    {"jira_key": "ONE-90001", "summary": "Linked epic"}
                ],
            }
        ),
        encoding="utf-8",
    )
    imported = import_reviewer_run(run)
    suite = tmp_path / "suite.json"
    suite.write_text(
        json.dumps(
            {
                "run_id": "creator-linked",
                "product_id": "bigpicture",
                "review_ref": str(review),
                "tests": [{"draft_id": "TC-1", "title": "Journey"}],
            }
        ),
        encoding="utf-8",
    )
    import_test_case_batch(suite)

    with db() as conn:
        pipeline = conn.execute(
            """
            SELECT product_id, operator_id, operator_name
            FROM pipeline_run WHERE id = ?
            """,
            (imported["pipeline_run_id"],),
        ).fetchone()
        creator = conn.execute(
            """
            SELECT pipeline_run_id, review_unit_id
            FROM creator_run WHERE id = 'creator-linked'
            """
        ).fetchone()
    assert dict(pipeline) == {
        "product_id": "bigpicture",
        "operator_id": "operator@appfire.com",
        "operator_name": "QA Operator",
    }
    assert creator["pipeline_run_id"] == imported["pipeline_run_id"]
    assert creator["review_unit_id"].endswith(":ONE-90001")

    with db() as conn:
        conn.execute(
            """
            UPDATE creator_run
            SET pipeline_run_id = NULL, review_unit_id = NULL
            WHERE id = 'creator-linked'
            """
        )
        assert repair_creator_pipeline_links(conn) == 1
        repaired = conn.execute(
            """
            SELECT pipeline_run_id, review_unit_id
            FROM creator_run WHERE id = 'creator-linked'
            """
        ).fetchone()
    assert repaired["pipeline_run_id"] == imported["pipeline_run_id"]
    assert repaired["review_unit_id"].endswith(":ONE-90001")
