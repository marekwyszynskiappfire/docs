"""Write approved/latest review payload to Studio export directory."""

from __future__ import annotations

import json
from typing import Any

from creator_handoff import review_ref_relative
from db import utc_now
from studio_paths import EXPORT_ROOT


def export_review_unit(conn: Any, unit_id: str) -> dict[str, Any]:
    """Persist review-payload.json under EXPORT_ROOT; requires open DB connection."""
    unit = conn.execute("SELECT * FROM review_unit WHERE id = ?", (unit_id,)).fetchone()
    if not unit:
        raise KeyError("Unit not found")
    rev = None
    if unit["approved_revision_id"]:
        rev = conn.execute(
            "SELECT * FROM review_payload_revision WHERE id = ?",
            (unit["approved_revision_id"],),
        ).fetchone()
    if not rev:
        rev = conn.execute(
            """
            SELECT * FROM review_payload_revision
            WHERE review_unit_id = ? ORDER BY revision DESC LIMIT 1
            """,
            (unit_id,),
        ).fetchone()
    if not rev:
        raise ValueError("No payload")
    payload = json.loads(rev["payload_json"])
    meta = {
        "studio_run_id": unit["pipeline_run_id"],
        "studio_unit_id": unit_id,
        "approved_revision": rev["revision"],
        "exported_at": utc_now(),
    }
    payload["studio_export"] = meta

    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
    out_dir = EXPORT_ROOT / unit["pipeline_run_id"] / unit["jira_key"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "review-payload.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")

    rel = review_ref_relative(str(out_path))
    return {
        "path": str(out_path),
        "review_ref": rel,
        "jira_key": unit["jira_key"],
        "payload": payload,
        "approved_revision_row_id": rev["id"],
    }
