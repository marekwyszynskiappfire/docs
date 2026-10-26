import json
from pathlib import Path

from db import db
from import_review import import_test_case_batch


def _write_suite(path: Path, tests: list[dict]) -> None:
    path.write_text(
        json.dumps({"run_id": "cr-reimport", "tests": tests}),
        encoding="utf-8",
    )


def test_reimport_resets_approval_when_case_changes(studio_db, tmp_path: Path):
    suite = tmp_path / "suite-payload.json"
    _write_suite(suite, [{"draft_id": "TC-001", "title": "Old"}])
    import_test_case_batch(suite)
    with db() as conn:
        conn.execute(
            """
            UPDATE test_case_row
            SET human_review_status = 'approved', marked_for_xray_import = 1
            WHERE draft_id = 'TC-001'
            """
        )
    _write_suite(suite, [{"draft_id": "TC-001", "title": "New"}])
    import_test_case_batch(suite)
    with db() as conn:
        row = conn.execute(
            "SELECT human_review_status, marked_for_xray_import FROM test_case_row WHERE draft_id = 'TC-001'"
        ).fetchone()
        revisions = conn.execute("SELECT COUNT(*) FROM test_case_revision").fetchone()[0]
    assert row["human_review_status"] == "pending"
    assert row["marked_for_xray_import"] == 0
    assert revisions == 2


def test_reimport_keeps_approval_when_case_is_unchanged(studio_db, tmp_path: Path):
    suite = tmp_path / "suite-payload.json"
    _write_suite(suite, [{"draft_id": "TC-001", "title": "Same"}])
    import_test_case_batch(suite)
    with db() as conn:
        conn.execute(
            """
            UPDATE test_case_row
            SET human_review_status = 'approved', marked_for_xray_import = 1
            WHERE draft_id = 'TC-001'
            """
        )
    import_test_case_batch(suite)
    with db() as conn:
        row = conn.execute(
            "SELECT human_review_status, marked_for_xray_import FROM test_case_row WHERE draft_id = 'TC-001'"
        ).fetchone()
        revisions = conn.execute("SELECT COUNT(*) FROM test_case_revision").fetchone()[0]
    assert row["human_review_status"] == "approved"
    assert row["marked_for_xray_import"] == 1
    assert revisions == 1


def test_reimport_marks_dropped_draft_removed(studio_db, tmp_path: Path):
    suite = tmp_path / "suite-payload.json"
    _write_suite(
        suite,
        [
            {"draft_id": "TC-001", "title": "Keep"},
            {"draft_id": "TC-002", "title": "Drop"},
        ],
    )
    import_test_case_batch(suite)
    with db() as conn:
        conn.execute(
            """
            UPDATE test_case_row
            SET human_review_status = 'approved', marked_for_xray_import = 1
            """
        )
    _write_suite(suite, [{"draft_id": "TC-001", "title": "Keep"}])
    import_test_case_batch(suite)
    with db() as conn:
        dropped = conn.execute(
            "SELECT human_review_status, marked_for_xray_import, import_status FROM test_case_row WHERE draft_id = 'TC-002'"
        ).fetchone()
        kept = conn.execute(
            "SELECT human_review_status, marked_for_xray_import FROM test_case_row WHERE draft_id = 'TC-001'"
        ).fetchone()
    assert dropped["import_status"] == "removed"
    assert dropped["marked_for_xray_import"] == 0
    assert dropped["human_review_status"] == "pending"
    assert kept["human_review_status"] == "approved"
    assert kept["marked_for_xray_import"] == 1
