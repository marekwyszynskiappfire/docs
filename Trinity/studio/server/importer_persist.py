"""Persist Xray import results into Studio SQLite (IQ-05)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from db import utc_now
from telemetry import record_event


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def resolve_report_path(path_str: str) -> Path:
    path = Path(path_str)
    if not path.is_absolute():
        path = (_repo_root() / path).resolve()
    if not path.exists():
        raise FileNotFoundError(path_str)
    return path


def load_reports_from_path(path: Path) -> list[dict[str, Any]]:
    if path.is_file():
        return [json.loads(path.read_text(encoding="utf-8"))]
    reports: list[dict[str, Any]] = []
    for json_path in sorted(path.rglob("xray-import-report.json")):
        try:
            reports.append(json.loads(json_path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    return reports


def apply_xray_reports(
    conn: Any,
    creator_run_id: str,
    reports: list[dict[str, Any]],
) -> dict[str, Any]:
    updated = 0
    skipped = 0
    details: list[dict[str, Any]] = []
    now = utc_now()

    for report in reports:
        draft_id = report.get("draft_id")
        xray_key = report.get("xray_key")
        if not draft_id:
            skipped += 1
            continue
        row = conn.execute(
            """
            SELECT id FROM test_case_row
            WHERE creator_run_id = ? AND draft_id = ?
            """,
            (creator_run_id, draft_id),
        ).fetchone()
        if not row:
            skipped += 1
            details.append({"draft_id": draft_id, "status": "no_matching_row"})
            continue
        if not xray_key:
            status = "failed" if report.get("errors") else "no_key"
            conn.execute(
                """
                UPDATE test_case_row SET import_status = ?, updated_at = ?
                WHERE id = ?
                """,
                (status, now, row["id"]),
            )
            skipped += 1
            details.append({"draft_id": draft_id, "status": status})
            continue
        conn.execute(
            """
            UPDATE test_case_row SET xray_test_key = ?, import_status = 'imported', updated_at = ?
            WHERE id = ?
            """,
            (xray_key, now, row["id"]),
        )
        updated += 1
        details.append({"draft_id": draft_id, "xray_test_key": xray_key, "status": "imported"})

    if updated:
        conn.execute(
            """
            UPDATE creator_run SET status = 'imported', updated_at = ?
            WHERE id = ?
            """,
            (now, creator_run_id),
        )

    record_event(
        conn,
        "xray_import_persisted",
        "creator_run",
        creator_run_id,
        None,
        {"updated": updated, "skipped": skipped, "report_count": len(reports)},
    )
    return {"updated": updated, "skipped": skipped, "details": details}
