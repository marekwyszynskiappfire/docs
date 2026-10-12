"""Cursor IDE usage and cost attribution for Trinity pipeline stages."""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from db import utc_now

CURSOR_STAGES: tuple[str, ...] = (
    "reviewer_analyze",
    "reviewer_mcp",
    "creator",
    "importer",
    "unscoped",
)

STAGE_LABELS: dict[str, str] = {
    "reviewer_analyze": "Reviewer — gather & analyze epic",
    "reviewer_mcp": "Reviewer — MCP / Jira questions",
    "creator": "Creator — generate test cases",
    "importer": "Importer — plan & execute (agent)",
    "unscoped": "Unscoped Cursor session",
}


def normalize_stage(stage: str | None) -> str:
    if not stage:
        return "unscoped"
    s = stage.strip().lower()
    if s in CURSOR_STAGES:
        return s
    aliases = {
        "reviewer": "reviewer_analyze",
        "review": "reviewer_analyze",
        "mcp": "reviewer_mcp",
        "creator_generate": "creator",
        "import": "importer",
    }
    return aliases.get(s, "unscoped")


def record_cursor_usage(
    conn: Any,
    *,
    stage: str,
    conversation_id: str | None = None,
    pipeline_run_id: str | None = None,
    creator_run_id: str | None = None,
    model: str | None = None,
    model_id: str | None = None,
    generation_id: str | None = None,
    duration_ms: int | None = None,
    status: str | None = None,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    cache_read_tokens: int | None = None,
    cache_write_tokens: int | None = None,
    cost_cents: int | None = None,
    cost_currency: str = "USD",
    source: str = "cursor_hook",
    notes: str | None = None,
    billed_at: str | None = None,
) -> dict[str, Any]:
    stage_norm = normalize_stage(stage)
    if not conversation_id and source == "cursor_hook":
        raise ValueError("conversation_id is required for Cursor hook events")
    now = utc_now()
    conn.execute(
        """
        INSERT INTO cursor_usage_event (
          pipeline_run_id, creator_run_id, stage, conversation_id, generation_id,
          model, model_id, duration_ms, status,
          input_tokens, output_tokens, cache_read_tokens, cache_write_tokens,
          cost_cents, cost_currency, source, notes, created_at, billed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            pipeline_run_id,
            creator_run_id,
            stage_norm,
            conversation_id,
            generation_id,
            model,
            model_id,
            duration_ms,
            status,
            input_tokens,
            output_tokens,
            cache_read_tokens,
            cache_write_tokens,
            cost_cents,
            cost_currency,
            source,
            notes,
            now,
            billed_at or (now if cost_cents is not None else None),
        ),
    )
    row_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    return {"id": row_id, "stage": stage_norm, "created_at": now}


def _pipeline_scope_sql(param_name: str = "run_id") -> str:
    return f"""
        pipeline_run_id = :{param_name}
        OR creator_run_id IN (
          SELECT id FROM creator_run WHERE pipeline_run_id = :{param_name}
        )
    """


def usage_summary_for_pipeline(conn: Any, pipeline_run_id: str) -> dict[str, Any]:
    scope = _pipeline_scope_sql("pid")
    rows = conn.execute(
        f"""
        SELECT * FROM cursor_usage_event
        WHERE {scope}
        ORDER BY created_at ASC
        """,
        {"pid": pipeline_run_id},
    ).fetchall()

    return _aggregate_summary(rows, pipeline_run_id=pipeline_run_id)


def usage_summary_for_creator(conn: Any, creator_run_id: str) -> dict[str, Any]:
    row = conn.execute(
        "SELECT pipeline_run_id FROM creator_run WHERE id = ?", (creator_run_id,)
    ).fetchone()
    pipeline_run_id = row["pipeline_run_id"] if row else None
    rows = conn.execute(
        """
        SELECT * FROM cursor_usage_event
        WHERE creator_run_id = ?
        ORDER BY created_at ASC
        """,
        (creator_run_id,),
    ).fetchall()
    return _aggregate_summary(rows, pipeline_run_id=pipeline_run_id, creator_run_id=creator_run_id)


def _aggregate_summary(
    rows: list[Any],
    *,
    pipeline_run_id: str | None = None,
    creator_run_id: str | None = None,
) -> dict[str, Any]:
    by_stage: dict[str, dict[str, Any]] = {}
    models: dict[str, int] = {}
    total_cost_cents = 0
    total_input = 0
    total_output = 0
    pending_cost = 0

    for row in rows:
        stage = row["stage"]
        bucket = by_stage.setdefault(
            stage,
            {
                "stage": stage,
                "label": STAGE_LABELS.get(stage, stage),
                "sessions": 0,
                "cost_cents": 0,
                "cost_pending_sessions": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "models": [],
            },
        )
        bucket["sessions"] += 1
        if row["input_tokens"]:
            bucket["input_tokens"] += int(row["input_tokens"])
            total_input += int(row["input_tokens"])
        if row["output_tokens"]:
            bucket["output_tokens"] += int(row["output_tokens"])
            total_output += int(row["output_tokens"])
        m = row["model_id"] or row["model"]
        if m:
            models[m] = models.get(m, 0) + 1
            if m not in bucket["models"]:
                bucket["models"].append(m)
        if row["cost_cents"] is not None:
            c = int(row["cost_cents"])
            bucket["cost_cents"] += c
            total_cost_cents += c
        else:
            bucket["cost_pending_sessions"] += 1
            pending_cost += 1

    stages = [by_stage[k] for k in CURSOR_STAGES if k in by_stage]
    for k in by_stage:
        if k not in CURSOR_STAGES:
            stages.append(by_stage[k])

    return {
        "pipeline_run_id": pipeline_run_id,
        "creator_run_id": creator_run_id,
        "currency": "USD",
        "total_cost_cents": total_cost_cents,
        "total_cost_display": _format_usd(total_cost_cents),
        "total_input_tokens": total_input or None,
        "total_output_tokens": total_output or None,
        "sessions_pending_cost": pending_cost,
        "models_used": [{"model": m, "sessions": n} for m, n in sorted(models.items())],
        "by_stage": stages,
        "events": [dict(r) for r in rows],
        "admin_api_configured": bool(os.environ.get("CURSOR_ADMIN_API_KEY", "").strip()),
    }


def _format_usd(cents: int) -> str:
    return f"${cents / 100:.2f}"


def write_cursor_session_file(
    data_dir: Path | str,
    *,
    pipeline_run_id: str | None,
    creator_run_id: str | None,
    stage: str,
) -> Path:
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    path = data_dir / ".cursor-session.json"
    payload = {
        "pipeline_run_id": pipeline_run_id,
        "creator_run_id": creator_run_id,
        "stage": normalize_stage(stage),
        "updated_at": utc_now(),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def read_cursor_session_file(data_dir: Path | str) -> dict[str, Any] | None:
    path = Path(data_dir) / ".cursor-session.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def backfill_costs_from_admin_api(
    conn: Any,
    *,
    conversation_ids: list[str] | None = None,
    hours_back: int = 48,
) -> dict[str, Any]:
    """Sum chargedCents from Cursor Team Admin API for known conversation_ids."""
    api_key = os.environ.get("CURSOR_ADMIN_API_KEY", "").strip()
    if not api_key:
        return {"updated": 0, "skipped": "no CURSOR_ADMIN_API_KEY"}

    if conversation_ids is None:
        rows = conn.execute(
            """
            SELECT DISTINCT conversation_id FROM cursor_usage_event
            WHERE conversation_id IS NOT NULL AND cost_cents IS NULL
            """
        ).fetchall()
        conversation_ids = [r["conversation_id"] for r in rows if r["conversation_id"]]
    if not conversation_ids:
        return {"updated": 0, "skipped": "no pending conversations"}

    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=hours_back)
    body = json.dumps(
        {
            "startTime": int(start.timestamp() * 1000),
            "endTime": int(end.timestamp() * 1000),
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://api.cursor.com/teams/filtered-usage-events",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    req.add_header(
        "Authorization",
        f"Basic {base64.b64encode(f'{api_key}:'.encode()).decode()}",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        return {"updated": 0, "error": f"Admin API HTTP {exc.code}: {detail}"}
    except urllib.error.URLError as exc:
        return {"updated": 0, "error": str(exc)}

    events = payload.get("usageEvents") or payload.get("events") or payload.get("data") or []
    if isinstance(events, dict):
        events = events.get("usageEvents") or []

    want = set(conversation_ids)
    totals: dict[str, dict[str, Any]] = {}
    for ev in events:
        if not isinstance(ev, dict):
            continue
        cid = ev.get("conversationId") or ev.get("conversation_id")
        if cid not in want:
            continue
        cents = ev.get("chargedCents") or ev.get("charged_cents") or 0
        tu = ev.get("tokenUsage") or ev.get("token_usage") or {}
        bucket = totals.setdefault(
            cid,
            {"cost_cents": 0, "input_tokens": 0, "output_tokens": 0, "model": ev.get("model")},
        )
        bucket["cost_cents"] += int(cents)
        if isinstance(tu, dict):
            bucket["input_tokens"] += int(tu.get("inputTokens") or tu.get("input_tokens") or 0)
            bucket["output_tokens"] += int(tu.get("outputTokens") or tu.get("output_tokens") or 0)
        if ev.get("model"):
            bucket["model"] = ev.get("model")

    updated = 0
    now = utc_now()
    for cid, agg in totals.items():
        cur = conn.execute(
            """
            UPDATE cursor_usage_event
            SET cost_cents = ?, input_tokens = COALESCE(input_tokens, ?),
                output_tokens = COALESCE(output_tokens, ?),
                model = COALESCE(model, ?),
                billed_at = ?, source = CASE WHEN source = 'cursor_hook' THEN 'admin_api' ELSE source END
            WHERE conversation_id = ? AND cost_cents IS NULL
            """,
            (
                agg["cost_cents"],
                agg["input_tokens"] or None,
                agg["output_tokens"] or None,
                agg.get("model"),
                now,
                cid,
            ),
        )
        updated += cur.rowcount

    return {
        "updated": updated,
        "conversations_matched": len(totals),
        "api_events_scanned": len(events),
    }
