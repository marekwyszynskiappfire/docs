"""SQLite access for QA Studio."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"
DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "qa-studio.db"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_db_path() -> Path:
    import os

    return Path(os.environ.get("QA_STUDIO_DB", str(DEFAULT_DB)))


def connect() -> sqlite3.Connection:
    path = get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def _migrate_schema(conn: sqlite3.Connection) -> None:
    pipeline_cols = {
        row[1] for row in conn.execute("PRAGMA table_info(pipeline_run)")
    }
    if pipeline_cols and "operator_id" not in pipeline_cols:
        conn.execute("ALTER TABLE pipeline_run ADD COLUMN operator_id TEXT")
    if pipeline_cols and "operator_name" not in pipeline_cols:
        conn.execute("ALTER TABLE pipeline_run ADD COLUMN operator_name TEXT")
    if pipeline_cols and "coverage_profile" not in pipeline_cols:
        conn.execute(
            "ALTER TABLE pipeline_run ADD COLUMN coverage_profile TEXT NOT NULL DEFAULT 'balanced'"
        )
    unit_cols = {row[1] for row in conn.execute("PRAGMA table_info(review_unit)")}
    if unit_cols and "coverage_profile" not in unit_cols:
        conn.execute("ALTER TABLE review_unit ADD COLUMN coverage_profile TEXT")

    cols = {row[1] for row in conn.execute("PRAGMA table_info(test_case_row)")}
    if cols and "marked_for_xray_import" not in cols:
        conn.execute(
            "ALTER TABLE test_case_row ADD COLUMN marked_for_xray_import INTEGER NOT NULL DEFAULT 0"
        )
    if cols and "automation_fit" not in cols:
        conn.execute("ALTER TABLE test_case_row ADD COLUMN automation_fit TEXT")
    if cols and "rejection_reason" not in cols:
        conn.execute("ALTER TABLE test_case_row ADD COLUMN rejection_reason TEXT")
    outbox = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='telemetry_outbox'"
    ).fetchone()
    if not outbox:
        conn.execute(
            """
            CREATE TABLE telemetry_outbox (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              event_json TEXT NOT NULL,
              created_at TEXT NOT NULL,
              sent_at TEXT,
              last_error TEXT
            )
            """
        )
    cursor_usage = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='cursor_usage_event'"
    ).fetchone()
    if not cursor_usage:
        conn.executescript(
            """
            CREATE TABLE cursor_usage_event (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              pipeline_run_id TEXT,
              creator_run_id TEXT,
              stage TEXT NOT NULL,
              conversation_id TEXT,
              generation_id TEXT,
              model TEXT,
              model_id TEXT,
              duration_ms INTEGER,
              status TEXT,
              input_tokens INTEGER,
              output_tokens INTEGER,
              cache_read_tokens INTEGER,
              cache_write_tokens INTEGER,
              cost_cents INTEGER,
              cost_currency TEXT NOT NULL DEFAULT 'USD',
              source TEXT NOT NULL,
              notes TEXT,
              created_at TEXT NOT NULL,
              billed_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_cursor_usage_pipeline ON cursor_usage_event(pipeline_run_id);
            CREATE INDEX IF NOT EXISTS idx_cursor_usage_conversation ON cursor_usage_event(conversation_id);
            """
        )
    run_report = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='pipeline_run_report'"
    ).fetchone()
    if not run_report:
        conn.execute(
            """
            CREATE TABLE pipeline_run_report (
              pipeline_run_id TEXT PRIMARY KEY REFERENCES pipeline_run(id) ON DELETE CASCADE,
              schema_version INTEGER NOT NULL,
              report_json TEXT NOT NULL,
              computed_at TEXT NOT NULL
            )
            """
        )
    jira_post = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='jira_comment_post'"
    ).fetchone()
    if not jira_post:
        conn.executescript(
            """
            CREATE TABLE jira_comment_post (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              review_unit_id TEXT NOT NULL,
              jira_issue_key TEXT NOT NULL,
              variant TEXT NOT NULL,
              jira_comment_id TEXT,
              jira_comment_url TEXT,
              payload_revision_id INTEGER,
              preview_edited INTEGER NOT NULL DEFAULT 0,
              request_hash TEXT,
              created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_jira_comment_unit ON jira_comment_post(review_unit_id);
            """
        )
    manifest = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='pipeline_manifest'"
    ).fetchone()
    if not manifest:
        conn.execute(
            """
            CREATE TABLE pipeline_manifest (
              pipeline_run_id TEXT PRIMARY KEY REFERENCES pipeline_run(id) ON DELETE CASCADE,
              manifest_path TEXT NOT NULL,
              manifest_json TEXT NOT NULL,
              payload_set_hash TEXT NOT NULL,
              imported_at TEXT NOT NULL
            )
            """
        )
    handoff = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='cursor_handoff'"
    ).fetchone()
    if not handoff:
        conn.executescript(
            """
            CREATE TABLE cursor_handoff (
              id TEXT PRIMARY KEY,
              pipeline_run_id TEXT NOT NULL REFERENCES pipeline_run(id) ON DELETE CASCADE,
              stage TEXT NOT NULL CHECK (stage IN ('review', 'creator_draft')),
              epic_key TEXT NOT NULL DEFAULT '',
              prompt_version TEXT NOT NULL,
              prompt_text TEXT NOT NULL,
              prompt_sha256 TEXT NOT NULL,
              coverage_profile TEXT,
              status TEXT NOT NULL CHECK (status IN (
                'awaiting_cursor', 'output_detected', 'invalid_output', 'imported', 'stale_output'
              )),
              expected_paths_json TEXT NOT NULL,
              expected_hashes_json TEXT NOT NULL,
              copied_at TEXT,
              detected_at TEXT,
              imported_at TEXT,
              retry_count INTEGER NOT NULL DEFAULT 0,
              error TEXT,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              UNIQUE (pipeline_run_id, stage, epic_key)
            );
            CREATE INDEX IF NOT EXISTS idx_cursor_handoff_pipeline ON cursor_handoff(pipeline_run_id);
            """
        )
    handoff_cols = {row[1] for row in conn.execute("PRAGMA table_info(cursor_handoff)")}
    if handoff_cols and "coverage_profile" not in handoff_cols:
        conn.execute("ALTER TABLE cursor_handoff ADD COLUMN coverage_profile TEXT")
    agent_runs = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='cursor_agent_run'"
    ).fetchone()
    if not agent_runs:
        conn.executescript(
            """
            CREATE TABLE cursor_agent_run (
              id TEXT PRIMARY KEY,
              stage TEXT NOT NULL CHECK (stage IN ('reviewer', 'creator', 'importer')),
              status TEXT NOT NULL CHECK (status IN (
                'queued', 'running', 'finished', 'error', 'cancelled', 'interrupted'
              )),
              prompt_text TEXT NOT NULL,
              pipeline_run_id TEXT REFERENCES pipeline_run(id) ON DELETE SET NULL,
              creator_run_id TEXT,
              handoff_id TEXT,
              epic_key TEXT,
              portfolio_id TEXT,
              agent_id TEXT,
              sdk_run_id TEXT,
              model TEXT,
              final_text TEXT,
              error TEXT,
              started_at TEXT,
              finished_at TEXT,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE INDEX idx_cursor_agent_run_pipeline
              ON cursor_agent_run(pipeline_run_id, created_at DESC);
            """
        )
    persona_revision = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='persona_revision'"
    ).fetchone()
    if not persona_revision:
        conn.executescript(
            """
            CREATE TABLE persona_revision (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              filename TEXT NOT NULL,
              content TEXT NOT NULL,
              content_sha256 TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_persona_revision_file ON persona_revision(filename, id DESC);
            """
        )


def recover_orphan_agent_runs() -> None:
    """Mark queued or running agents interrupted. Call once at process start.

    The SDK bridge lives in this process. Import paths also call init_db and
    must not interrupt an agent that is still running.
    """
    now = utc_now()
    with db() as conn:
        conn.execute(
            """
            UPDATE cursor_agent_run
            SET status = 'interrupted',
                error = COALESCE(error, 'Studio restarted while this Cursor agent was running.'),
                finished_at = COALESCE(finished_at, ?),
                updated_at = ?
            WHERE status IN ('queued', 'running')
            """,
            (now, now),
        )


def init_db() -> None:
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with connect() as conn:
        conn.executescript(sql)
        _migrate_schema(conn)
        conn.commit()


@contextmanager
def db() -> Iterator[sqlite3.Connection]:
    conn = connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row)


def log_event(
    conn: sqlite3.Connection,
    event_type: str,
    entity_type: str,
    entity_id: str | None = None,
    pipeline_run_id: str | None = None,
    payload: dict[str, Any] | None = None,
) -> None:
    conn.execute(
        """
        INSERT INTO metric_event (pipeline_run_id, entity_type, entity_id, event_type, payload_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            pipeline_run_id,
            entity_type,
            entity_id,
            event_type,
            json.dumps(payload) if payload else None,
            utc_now(),
        ),
    )


def json_loads(text: str | None) -> Any:
    if not text:
        return None
    return json.loads(text)
