"""Aggregated Studio statistics helpers."""

from __future__ import annotations

import json
from typing import Any

# Cap JSON walks for dashboard stats on large portfolios.
OPEN_QF_UNIT_CAP = 500


def count_open_questions_and_findings(conn: Any, unit_cap: int = OPEN_QF_UNIT_CAP) -> dict[str, Any]:
    total_units = conn.execute("SELECT COUNT(*) FROM review_unit").fetchone()[0]
    capped = total_units > unit_cap
    rows = conn.execute(
        """
        SELECT r.payload_json FROM review_payload_revision r
        INNER JOIN (
          SELECT review_unit_id, MAX(revision) AS mr FROM review_payload_revision GROUP BY review_unit_id
        ) latest ON latest.review_unit_id = r.review_unit_id AND latest.mr = r.revision
        INNER JOIN review_unit u ON u.id = r.review_unit_id
        ORDER BY u.updated_at DESC
        LIMIT ?
        """,
        (unit_cap,),
    )
    findings_open = 0
    questions_open = 0
    for row in rows:
        p = json.loads(row["payload_json"])
        for f in p.get("findings") or []:
            if f.get("status", "open") == "open":
                findings_open += 1
        for q in p.get("questions") or []:
            if q.get("status", "open") == "open":
                questions_open += 1
    return {
        "open_findings_latest": findings_open,
        "open_questions_latest": questions_open,
        "open_qf_counts_capped": capped,
        "open_qf_unit_cap": unit_cap if capped else None,
    }
