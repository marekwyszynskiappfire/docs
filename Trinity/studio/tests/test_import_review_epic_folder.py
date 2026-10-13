"""Reviewer import: epic folder name must match payload epic key."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from import_review import epic_key_from_payload, import_reviewer_run


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
