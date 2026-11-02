"""Google Sheets API for Trinity Usage Scorecard (service account)."""

from __future__ import annotations

import os
import re
from typing import Any

from scorecard_config import SCORECARD_SPREADSHEET_ID, SCORECARD_SPREADSHEET_URL

_RUN_ID_RE = re.compile(r"^([A-Z]+-)(\d+)$", re.I)


def credentials_path() -> str | None:
    for key in ("TRINITY_SCORECARD_CREDENTIALS", "GOOGLE_APPLICATION_CREDENTIALS"):
        path = os.environ.get(key, "").strip()
        if path and os.path.isfile(path):
            return path
    return None


def is_configured() -> bool:
    if not credentials_path():
        return False
    try:
        import google.oauth2.service_account  # noqa: F401
        import googleapiclient.discovery  # noqa: F401
    except ImportError:
        return False
    return True


def _sheets_service():
    path = credentials_path()
    if not path:
        raise RuntimeError(
            "Scorecard credentials missing. Set TRINITY_SCORECARD_CREDENTIALS or "
            "GOOGLE_APPLICATION_CREDENTIALS to a service-account JSON file with "
            "access to the Trinity Usage Scorecard spreadsheet."
        )
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = service_account.Credentials.from_service_account_file(path, scopes=scopes)
    return build("sheets", "v4", credentials=creds, cache_discovery=False)


def _quote_tab(tab: str) -> str:
    escaped = tab.replace("'", "''")
    return f"'{escaped}'"


def read_column_a(tab: str) -> list[str]:
    service = _sheets_service()
    range_name = f"{_quote_tab(tab)}!A2:A"
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=SCORECARD_SPREADSHEET_ID, range=range_name)
        .execute()
    )
    rows = result.get("values") or []
    return [str(row[0]).strip() for row in rows if row and str(row[0]).strip()]


def next_run_id(tab: str, prefix: str) -> str:
    existing = read_column_a(tab)
    max_num = 100
    for cell in existing:
        if not cell.upper().startswith(prefix.upper()):
            continue
        m = _RUN_ID_RE.match(cell.strip())
        if not m:
            continue
        if m.group(1).upper() != prefix.upper():
            continue
        max_num = max(max_num, int(m.group(2)))
    return f"{prefix}{max_num + 1}"


def find_row_for_run_id(tab: str, run_id: str) -> int | None:
    """1-based sheet row number, or None."""
    service = _sheets_service()
    range_name = f"{_quote_tab(tab)}!A2:A"
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=SCORECARD_SPREADSHEET_ID, range=range_name)
        .execute()
    )
    rows = result.get("values") or []
    target = run_id.strip().upper()
    for idx, row in enumerate(rows, start=2):
        if row and str(row[0]).strip().upper() == target:
            return idx
    return None


def append_row(tab: str, values: list[Any]) -> int:
    service = _sheets_service()
    body = {"values": [values]}
    result = (
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=SCORECARD_SPREADSHEET_ID,
            range=f"{_quote_tab(tab)}!A:O",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body,
        )
        .execute()
    )
    updated = result.get("updates") or {}
    range_updated = updated.get("updatedRange") or ""
    m = re.search(r"!A(\d+):", range_updated)
    if m:
        return int(m.group(1))
    return len(read_column_a(tab)) + 1


def update_row(tab: str, row_number: int, values: list[Any]) -> None:
    service = _sheets_service()
    range_name = f"{_quote_tab(tab)}!A{row_number}:O{row_number}"
    (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=SCORECARD_SPREADSHEET_ID,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body={"values": [values]},
        )
        .execute()
    )


def push_row(tab: str, values: list[Any], *, existing_run_id: str | None) -> dict[str, Any]:
    if existing_run_id:
        row_num = find_row_for_run_id(tab, existing_run_id)
        if row_num:
            update_row(tab, row_num, values)
            return {
                "action": "updated",
                "row_number": row_num,
                "external_run_id": existing_run_id,
            }
    row_num = append_row(tab, values)
    return {
        "action": "appended",
        "row_number": row_num,
        "external_run_id": values[0] if values else existing_run_id,
    }


def public_config() -> dict[str, Any]:
    return {
        "spreadsheet_id": SCORECARD_SPREADSHEET_ID,
        "spreadsheet_url": SCORECARD_SPREADSHEET_URL,
        "configured": is_configured(),
        "credentials_env": ["TRINITY_SCORECARD_CREDENTIALS", "GOOGLE_APPLICATION_CREDENTIALS"],
    }
