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
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _migrate_schema(conn: sqlite3.Connection) -> None:
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
