"""Rename and delete Studio runs (stable IDs for analytics)."""

from __future__ import annotations

from typing import Any

from db import utc_now
from telemetry import record_event


def resolve_creator_run_id(conn: Any, token: str) -> str:
    """Resolve Studio creator run from stable id or display label (after rename)."""
    trimmed = token.strip()
    if not trimmed:
        raise ValueError("Creator run id or label is required")
    by_id = conn.execute("SELECT id FROM creator_run WHERE id = ?", (trimmed,)).fetchone()
    if by_id:
        return by_id["id"]
    rows = conn.execute(
        """
        SELECT id FROM creator_run
        WHERE label = ? COLLATE NOCASE
        ORDER BY updated_at DESC
        """,
        (trimmed,),
    ).fetchall()
    if len(rows) == 1:
        return rows[0]["id"]
    if len(rows) > 1:
        raise ValueError(
            f"Multiple creator runs named '{trimmed}'; pick a unique label or use the run id"
        )
    raise KeyError(f"Creator run not found: {trimmed}")


def rename_pipeline_run(conn: Any, run_id: str, label: str) -> dict[str, Any]:
    row = conn.execute("SELECT id, label FROM pipeline_run WHERE id = ?", (run_id,)).fetchone()
    if not row:
        raise KeyError("Run not found")
    trimmed = label.strip()
    if not trimmed:
        raise ValueError("Label is required")
    now = utc_now()
    conn.execute(
        "UPDATE pipeline_run SET label = ?, updated_at = ? WHERE id = ?",
        (trimmed, now, run_id),
    )
    record_event(
        conn,
        "pipeline_run_renamed",
        "pipeline_run",
        run_id,
        run_id,
        {"old_label": row["label"], "new_label": trimmed},
    )
    return {"id": run_id, "label": trimmed, "updated_at": now}


def delete_pipeline_run(conn: Any, run_id: str) -> dict[str, Any]:
    row = conn.execute("SELECT id, label FROM pipeline_run WHERE id = ?", (run_id,)).fetchone()
    if not row:
        raise KeyError("Run not found")
    record_event(
        conn,
        "pipeline_run_deleted",
        "pipeline_run",
        run_id,
        run_id,
        {"label": row["label"]},
    )
    conn.execute("DELETE FROM pipeline_run WHERE id = ?", (run_id,))
    return {"deleted": True, "id": run_id}


def rename_creator_run(conn: Any, run_id: str, label: str) -> dict[str, Any]:
    row = conn.execute("SELECT id, label, pipeline_run_id FROM creator_run WHERE id = ?", (run_id,)).fetchone()
    if not row:
        raise KeyError("Run not found")
    trimmed = label.strip()
    if not trimmed:
        raise ValueError("Label is required")
    now = utc_now()
    conn.execute(
        "UPDATE creator_run SET label = ?, updated_at = ? WHERE id = ?",
        (trimmed, now, run_id),
    )
    record_event(
        conn,
        "creator_run_renamed",
        "creator_run",
        run_id,
        row["pipeline_run_id"],
        {"old_label": row["label"], "new_label": trimmed},
    )
    return {"id": run_id, "label": trimmed, "updated_at": now}


def delete_creator_run(conn: Any, run_id: str) -> dict[str, Any]:
    row = conn.execute(
        "SELECT id, label, pipeline_run_id FROM creator_run WHERE id = ?", (run_id,)
    ).fetchone()
    if not row:
        raise KeyError("Run not found")
    record_event(
        conn,
        "creator_run_deleted",
        "creator_run",
        run_id,
        row["pipeline_run_id"],
        {"label": row["label"]},
    )
    conn.execute("DELETE FROM creator_run WHERE id = ?", (run_id,))
    return {"deleted": True, "id": run_id}
