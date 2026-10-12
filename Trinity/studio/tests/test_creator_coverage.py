import json
import uuid
from pathlib import Path

from db import db, utc_now
from creator_coverage import (
    build_coverage_summary,
    format_coverage_matrix_for_prompt,
    load_latest_batch,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
DEMO_BATCH = REPO_ROOT / "Trinity/creator/samples/demo-story.suite.json"


def test_format_coverage_matrix_for_prompt():
    text = format_coverage_matrix_for_prompt(
        {"matrix": [{"ac_id": "AC-01", "status": "Covered", "covered_by": ["TC-001"]}]}
    )
    assert "AC-01" in text
    assert "Covered" in text


def test_load_latest_batch_and_gaps():
    run_id = f"cov-demo-{uuid.uuid4().hex[:8]}"
    batch = json.loads(DEMO_BATCH.read_text(encoding="utf-8"))
    now = utc_now()
    with db() as conn:
        conn.execute(
            """
            INSERT INTO creator_run (id, label, status, created_at, updated_at)
            VALUES (?, ?, 'draft', ?, ?)
            """,
            (run_id, run_id, now, now),
        )
        conn.execute(
            """
            INSERT INTO test_case_batch_revision
              (creator_run_id, revision, batch_json, source, created_at, created_by)
            VALUES (?, 1, ?, 'import', ?, 'test')
            """,
            (run_id, json.dumps(batch), now),
        )
        row_id = f"{run_id}:TC-001"
        conn.execute(
            """
            INSERT INTO test_case_row (
              id, creator_run_id, draft_id, title, human_review_status,
              marked_for_xray_import, updated_at
            ) VALUES (?, ?, 'TC-001', 't1', 'pending', 0, ?)
            """,
            (row_id, run_id, now),
        )
        tc = batch["tests"][0]
        conn.execute(
            """
            INSERT INTO test_case_revision (test_case_row_id, revision, case_json, source, created_at, created_by)
            VALUES (?, 1, ?, 'import', ?, 'test')
            """,
            (row_id, json.dumps(tc), now),
        )
        tests = [dict(conn.execute("SELECT * FROM test_case_row WHERE creator_run_id = ?", (run_id,)).fetchone())]
        loaded, rev = load_latest_batch(conn, run_id)
        assert rev == 1
        assert loaded["run_id"] == batch["run_id"]
        summary = build_coverage_summary(conn, run_id, tests)
        assert summary["available"]
        assert summary["gap_count"] >= 1
        ac01 = next(r for r in summary["matrix"] if r["ac_id"] == "AC-01")
        assert ac01["review_gap"] is True
        assert ac01["gap_reason"] == "No approved test links this AC/goal id"
