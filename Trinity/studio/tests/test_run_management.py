from db import db, utc_now
from run_management import delete_creator_run, delete_pipeline_run, rename_creator_run, rename_pipeline_run


def test_rename_and_delete_pipeline_run(studio_db):
    run_id = "pr-test-001"
    now = utc_now()
    with db() as conn:
        conn.execute(
            """
            INSERT INTO pipeline_run (id, label, trigger_type, trigger_value, created_at, updated_at)
            VALUES (?, ?, 'reviewer_folder', 'x', ?, ?)
            """,
            (run_id, "Old name", now, now),
        )
        out = rename_pipeline_run(conn, run_id, "Q4 planning")
        assert out["label"] == "Q4 planning"
        delete_pipeline_run(conn, run_id)
        assert conn.execute("SELECT id FROM pipeline_run WHERE id = ?", (run_id,)).fetchone() is None


def test_rename_and_delete_creator_run(studio_db):
    run_id = "cr-test-001"
    now = utc_now()
    with db() as conn:
        conn.execute(
            """
            INSERT INTO creator_run (id, label, status, created_at, updated_at)
            VALUES (?, ?, 'draft', ?, ?)
            """,
            (run_id, "Suite A", now, now),
        )
        rename_creator_run(conn, run_id, "Suite B")
        delete_creator_run(conn, run_id)
        assert conn.execute("SELECT id FROM creator_run WHERE id = ?", (run_id,)).fetchone() is None
