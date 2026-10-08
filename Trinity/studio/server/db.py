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
