"""Preview and post Jira epic comments from Reviewer payload + studio_qa."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from jira_client import post_issue_comment, scan_redaction_warnings
from jira_comment_render import render_jira_full, render_jira_short

Variant = str  # full | short | studio | auto


def _studio_decisions(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    studio = payload.get("studio_qa") or {}
    if not isinstance(studio, dict):
        return {}
    return dict(studio.get("decisions") or {})


def epic_feedback_count(payload: dict[str, Any]) -> int:
    return len(_collect_epic_feedback_items(payload))


def _collect_epic_feedback_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    decisions = _studio_decisions(payload)
    items: list[dict[str, Any]] = []

    def include(item_id: str) -> bool:
        d = decisions.get(item_id) or {}
        if d.get("validity") == "invalid":
            return False
        return bool(d.get("send_to_epic"))

    for q in payload.get("questions") or []:
        if not isinstance(q, dict):
            continue
        qid = q.get("question_id")
        if qid and include(str(qid)):
            items.append({"type": "question", "id": qid, "body": q.get("question"), "why": q.get("context")})

    studio = payload.get("studio_qa") or {}
    for q in (studio.get("added_questions") or []) if isinstance(studio, dict) else []:
        if isinstance(q, dict) and q.get("question_id") and include(str(q["question_id"])):
            items.append(
                {
                    "type": "question",
                    "id": q["question_id"],
                    "body": q.get("question"),
                    "why": q.get("context"),
                    "origin": "qa_studio",
                }
            )

    for f in payload.get("findings") or []:
        if not isinstance(f, dict):
            continue
        fid = f.get("finding_id")
        if fid and include(str(fid)):
            items.append(
                {
                    "type": "finding",
                    "id": fid,
                    "body": f.get("finding_summary"),
                    "why": f.get("testing_impact"),
                }
            )
    return items


def _qa_note(payload: dict[str, Any], item_id: str) -> str:
    d = _studio_decisions(payload).get(item_id) or {}
    return (d.get("comment") or "").strip()


def _wiki(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "")).replace("{", "(").replace("}", ")").replace("|", "/").strip()


def render_jira_studio(payload: dict[str, Any], jira_key: str) -> str:
    items = _collect_epic_feedback_items(payload)
    lines = [
        f"h3. QA feedback — {jira_key}",
        "",
        "_Items marked for epic feedback from Trinity Studio._",
        "",
    ]
    for item in items:
        prefix = "Q" if item["type"] == "question" else "F"
        lines.append(f"* {prefix} {item['id']}: {_wiki(item.get('body'))}")
        if item.get("why"):
            lines.append(f"_Context:_ {_wiki(item['why'])}")
        note = _qa_note(payload, str(item["id"]))
        if note:
            lines.append(f"_QA note:_ {_wiki(note)}")
        lines.append("")
    if not items:
        lines.append("_No items selected for epic feedback._")
    lines.append("----")
    return "\n".join(lines)


def _filter_payload_for_studio_render(payload: dict[str, Any]) -> dict[str, Any]:
    """Subset payload to send_to_epic items for full/short studio mode."""
    items = _collect_epic_feedback_items(payload)
    want_q = {i["id"] for i in items if i["type"] == "question"}
    want_f = {i["id"] for i in items if i["type"] == "finding"}
    out = json.loads(json.dumps(payload))
    out["questions"] = [q for q in (out.get("questions") or []) if q.get("question_id") in want_q]
    out["findings"] = [
        f
        for f in (out.get("findings") or [])
        if f.get("finding_id") in want_f and (f.get("status") or "open") == "open"
    ]
    return out


def _open_high_priority_questions(payload: dict[str, Any]) -> int:
    n = 0
    for q in payload.get("questions") or []:
        if (q.get("status") or "open") != "open":
            continue
        if (q.get("priority") or "").lower() == "high":
            n += 1
    return n


def recommend_variant(conn: Any, unit_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    if epic_feedback_count(payload) > 0:
        reasons.append(f"{epic_feedback_count(payload)} item(s) marked send_to_epic")
        return {"variant": "studio", "reasons": reasons}
    row = conn.execute(
        "SELECT id FROM jira_comment_post WHERE review_unit_id = ? LIMIT 1",
        (unit_id,),
    ).fetchone()
    if not row:
        reasons.append("First Jira post for this epic in Studio")
        return {"variant": "full", "reasons": reasons}
    hp = _open_high_priority_questions(payload)
    if hp <= 3:
        reasons.append(f"{hp} open High-priority question(s)")
        return {"variant": "short", "reasons": reasons}
    reasons.append("Multiple open questions — full comment for traceability")
    return {"variant": "full", "reasons": reasons}


def resolve_variant(variant: str, recommendation: dict[str, Any]) -> str:
    v = (variant or "auto").strip().lower()
    if v == "auto":
        return str(recommendation.get("variant") or "full")
    if v in ("full", "short", "studio"):
        return v
    return "full"


def render_body(payload: dict[str, Any], jira_key: str, variant: str) -> str:
    v = variant
    if v == "studio":
        body = render_jira_studio(payload, jira_key)
    elif v == "short":
        body = render_jira_short(payload)
    else:
        body = render_jira_full(payload)
    # Appendix QA notes on full/short for included items
    if v in ("full", "short"):
        extras: list[str] = []
        for item in _collect_epic_feedback_items(payload):
            note = _qa_note(payload, str(item["id"]))
            if note:
                extras.append(f"_QA note ({item['id']}):_ {_wiki(note)}")
        if extras:
            body = body.rstrip() + "\n\nh4. QA notes\n" + "\n".join(extras) + "\n"
    return body


def preview_comment(
    conn: Any,
    unit_id: str,
    payload: dict[str, Any],
    jira_key: str,
    variant: str = "auto",
) -> dict[str, Any]:
    recommendation = recommend_variant(conn, unit_id, payload)
    resolved = resolve_variant(variant, recommendation)
    if resolved == "studio" and epic_feedback_count(payload) == 0:
        return {
            "variant": resolved,
            "recommendation": recommendation,
            "body": "",
            "warnings": ["No items marked for epic feedback — triage questions/findings first."],
            "blockers": ["studio_variant_empty"],
            "epic_feedback_count": 0,
        }
    work_payload = payload
    if resolved == "studio":
        work_payload = payload
    body = render_body(work_payload, jira_key, resolved)
    warnings = scan_redaction_warnings(body)
    blockers = list(warnings) if warnings else []
    return {
        "variant": resolved,
        "recommendation": recommendation,
        "body": body,
        "warnings": warnings,
        "blockers": blockers,
        "epic_feedback_count": epic_feedback_count(payload),
    }


def request_hash(variant: str, body: str, revision_id: int | None) -> str:
    raw = f"{variant}\n{revision_id or 0}\n{body}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def post_comment(
    conn: Any,
    *,
    unit_id: str,
    jira_key: str,
    payload: dict[str, Any],
    variant: str,
    body_override: str | None,
    preview_edited: bool,
    payload_revision_id: int | None,
) -> dict[str, Any]:
    preview = preview_comment(conn, unit_id, payload, jira_key, variant)
    body = (body_override or preview["body"] or "").strip()
    if not body:
        raise ValueError("Comment body is empty")
    if preview.get("blockers"):
        raise ValueError("Cannot post: redaction or validation blockers present")
    result = post_issue_comment(jira_key, body)
    req_hash = request_hash(preview["variant"], body, payload_revision_id)
    from db import utc_now

    now = utc_now()
    conn.execute(
        """
        INSERT INTO jira_comment_post (
          review_unit_id, jira_issue_key, variant, jira_comment_id, jira_comment_url,
          payload_revision_id, preview_edited, request_hash, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            unit_id,
            jira_key,
            preview["variant"],
            result.get("id"),
            result.get("self"),
            payload_revision_id,
            1 if preview_edited else 0,
            req_hash,
            now,
        ),
    )
    return {
        "posted_at": now,
        "variant": preview["variant"],
        "jira_comment_id": result.get("id"),
        "jira_comment_url": result.get("self"),
        "preview_edited": preview_edited,
    }


def comment_history(conn: Any, unit_id: str, limit: int = 10) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT * FROM jira_comment_post
        WHERE review_unit_id = ?
        ORDER BY id DESC LIMIT ?
        """,
        (unit_id, min(max(limit, 1), 50)),
    ).fetchall()
    return [dict(r) for r in rows]
