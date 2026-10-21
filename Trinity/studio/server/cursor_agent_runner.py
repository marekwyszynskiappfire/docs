"""Run persisted local Cursor SDK agents without blocking the Studio API."""

from __future__ import annotations

import os
import threading
import uuid
from typing import Any

from db import db, row_to_dict, utc_now
from personas import docs_repo_root

ACTIVE_RUNS: dict[str, Any] = {}
ACTIVE_LOCK = threading.Lock()


def sdk_status() -> dict[str, Any]:
    try:
        import cursor_sdk  # noqa: F401

        installed = True
    except ImportError:
        installed = False
    return {
        "installed": installed,
        "configured": bool(os.environ.get("CURSOR_API_KEY", "").strip()),
        "model": os.environ.get("CURSOR_MODEL", "auto").strip() or "auto",
    }


def _public(row: Any) -> dict[str, Any]:
    return row_to_dict(row) or {}


def get_agent_run(run_id: str) -> dict[str, Any]:
    with db() as conn:
        row = conn.execute("SELECT * FROM cursor_agent_run WHERE id = ?", (run_id,)).fetchone()
    if row is None:
        raise KeyError(run_id)
    return _public(row)


def list_agent_runs(pipeline_run_id: str | None = None, limit: int = 30) -> list[dict[str, Any]]:
    with db() as conn:
        if pipeline_run_id:
            rows = conn.execute(
                """
                SELECT * FROM cursor_agent_run
                WHERE pipeline_run_id = ?
                ORDER BY created_at DESC LIMIT ?
                """,
                (pipeline_run_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM cursor_agent_run ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
    return [_public(row) for row in rows]


def launch_agent(
    *,
    stage: str,
    prompt_text: str,
    pipeline_run_id: str | None = None,
    creator_run_id: str | None = None,
    handoff_id: str | None = None,
    epic_key: str | None = None,
    portfolio_id: str | None = None,
) -> dict[str, Any]:
    status = sdk_status()
    if not status["installed"]:
        raise RuntimeError("Cursor SDK is not installed. Restart Studio to sync requirements.")
    if not status["configured"]:
        raise RuntimeError("CURSOR_API_KEY is not configured in Trinity/studio/.env.")
    if stage not in {"reviewer", "creator", "importer"}:
        raise ValueError(f"Unsupported Cursor stage: {stage}")
    run_id = f"car-{uuid.uuid4()}"
    now = utc_now()
    with db() as conn:
        conn.execute(
            """
            INSERT INTO cursor_agent_run (
              id, stage, status, prompt_text, pipeline_run_id, creator_run_id,
              handoff_id, epic_key, portfolio_id, model, created_at, updated_at
            ) VALUES (?, ?, 'queued', ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                stage,
                prompt_text,
                pipeline_run_id,
                creator_run_id,
                handoff_id,
                epic_key,
                portfolio_id,
                status["model"],
                now,
                now,
            ),
        )
    threading.Thread(target=_worker, args=(run_id,), daemon=True).start()
    return get_agent_run(run_id)


def _worker(run_id: str) -> None:
    from cursor_sdk import Agent, CursorAgentError, LocalAgentOptions

    current = get_agent_run(run_id)
    model = current["model"]
    now = utc_now()
    with db() as conn:
        conn.execute(
            """
            UPDATE cursor_agent_run
            SET status = 'running', started_at = ?, updated_at = ?
            WHERE id = ? AND status = 'queued'
            """,
            (now, now, run_id),
        )
    try:
        with Agent.create(
            api_key=os.environ["CURSOR_API_KEY"].strip(),
            model=model,
            local=LocalAgentOptions(cwd=docs_repo_root(), setting_sources=["all"]),
            name=f"Trinity {current['stage']}",
        ) as agent:
            sdk_run = agent.send(current["prompt_text"])
            with ACTIVE_LOCK:
                ACTIVE_RUNS[run_id] = sdk_run
            with db() as conn:
                conn.execute(
                    """
                    UPDATE cursor_agent_run
                    SET agent_id = ?, sdk_run_id = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (agent.agent_id, sdk_run.run_id, utc_now(), run_id),
                )
            result = sdk_run.wait()
            status_value = getattr(result.status, "value", str(result.status)).lower()
            final_status = "finished" if status_value in {"finished", "success", "completed"} else "error"
            error = None if final_status == "finished" else (
                result.error_message or f"Cursor run ended with status {status_value}."
            )
            with db() as conn:
                conn.execute(
                    """
                    UPDATE cursor_agent_run
                    SET status = ?, final_text = ?, error = ?, finished_at = ?, updated_at = ?
                    WHERE id = ? AND status != 'cancelled'
                    """,
                    (final_status, result.result or "", error, utc_now(), utc_now(), run_id),
                )
    except CursorAgentError as exc:
        _save_error(run_id, f"{exc} (retryable: {getattr(exc, 'is_retryable', False)})")
    except Exception as exc:  # SDK failures must remain visible without killing Studio.
        _save_error(run_id, str(exc))
    finally:
        with ACTIVE_LOCK:
            ACTIVE_RUNS.pop(run_id, None)


def _save_error(run_id: str, message: str) -> None:
    with db() as conn:
        conn.execute(
            """
            UPDATE cursor_agent_run
            SET status = CASE WHEN status = 'cancelled' THEN status ELSE 'error' END,
                error = CASE WHEN status = 'cancelled' THEN error ELSE ? END,
                finished_at = COALESCE(finished_at, ?),
                updated_at = ?
            WHERE id = ?
            """,
            (message, utc_now(), utc_now(), run_id),
        )


def cancel_agent_run(run_id: str) -> dict[str, Any]:
    current = get_agent_run(run_id)
    if current["status"] not in {"queued", "running"}:
        return current
    with ACTIVE_LOCK:
        sdk_run = ACTIVE_RUNS.get(run_id)
    if sdk_run is not None and sdk_run.supports("cancel"):
        sdk_run.cancel()
    now = utc_now()
    with db() as conn:
        conn.execute(
            """
            UPDATE cursor_agent_run
            SET status = 'cancelled', error = 'Cancelled by operator.',
                finished_at = ?, updated_at = ?
            WHERE id = ?
            """,
            (now, now, run_id),
        )
    return get_agent_run(run_id)
