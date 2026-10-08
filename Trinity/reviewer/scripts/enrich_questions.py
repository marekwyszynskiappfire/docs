#!/usr/bin/env python3
"""Normalize and expand clarification questions in ReviewPayload files (in-place).

Uses only text already in the payload (findings, child inventory, report facts) —
no invented requirements. Produces detailed `question` + `context` prose for PMs.

Usage:
    python3 enrich_questions.py --run-dir PATH/TO/portfolio_run
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

MIN_CONTEXT = 80
MIN_QUESTION = 45
PO_TOPICS = frozenset({"PRD authority"})

# Same quote stripping as render_report.lint (PRF-11): replacements apply only outside quotes.
_QUOTE_RE = re.compile(r'"[^"]*"|“[^”]*"|\'[^\']*\'')
_LINT_UNQUOTED_REPLACEMENTS = (
    (re.compile(r"\bgating\b", re.I), "restricting"),
    (re.compile(r"\bgate\b", re.I), "restrict"),
    (re.compile(r"\bblockers?\b", re.I), "open items"),
)


def lint_safe_prose(text: str) -> str:
    """Paraphrase blocked Reviewer voice words in unquoted prose; leave quoted source text verbatim."""
    if not text:
        return text

    def scrub(chunk: str) -> str:
        for pat, repl in _LINT_UNQUOTED_REPLACEMENTS:
            chunk = pat.sub(repl, chunk)
        return chunk

    out: list[str] = []
    last = 0
    for m in _QUOTE_RE.finditer(text):
        if m.start() > last:
            out.append(scrub(text[last : m.start()]))
        out.append(m.group())
        last = m.end()
    if last < len(text):
        out.append(scrub(text[last:]))
    return "".join(out)

TOPIC_ORDER_STORY = [
    "Behavior", "Scope", "Edge cases", "Integrations", "Permissions", "Data",
    "Definition of done", "PRD authority", "Design authority", "Rollout",
]
TOPIC_ORDER_EPIC = [
    "Definition of done", "PRD authority", "Design authority", "Rollout",
    "Behavior", "Scope", "Edge cases", "Integrations", "Permissions", "Data",
]

CATEGORY_TOPIC = {
    "acceptance_criteria": "Definition of done",
    "scope": "Scope",
    "behavioral_gap": "Behavior",
    "traceability": "PRD authority",
    "open_questions": "Scope",
    "testability": "Behavior",
    "template_compliance": "Definition of done",
    "data_sensitivity": "Data",
    "epic_lifecycle": "Rollout",
}


def epic_key_from_payload(p: dict) -> str:
    keys = p.get("requirement_keys") or []
    if keys:
        return keys[0]
    return p.get("scope", {}).get("value", "UNKNOWN")


def is_epic(p: dict) -> bool:
    return p.get("scope", {}).get("type") == "epic"


def topic_order(p: dict) -> list[str]:
    return TOPIC_ORDER_EPIC if is_epic(p) else TOPIC_ORDER_STORY


def finding_map(p: dict) -> dict[str, dict]:
    return {f["finding_id"]: f for f in p.get("findings", []) if f.get("finding_id")}


def truncate(s: str, n: int) -> str:
    s = re.sub(r"\s+", " ", (s or "").strip())
    if len(s) <= n:
        return s
    return s[: n - 1].rsplit(" ", 1)[0] + "…"


def child_citations(p: dict, limit: int = 3) -> list[str]:
    inv = (p.get("rollup") or {}).get("epic_child_inventory") or []
    out = []
    for c in inv:
        if c.get("content_source") == "title_only":
            out.append(f"{c['key']} (title only): \"{truncate(c.get('summary', ''), 100)}\"")
        elif c.get("description_excerpt"):
            out.append(
                f"{c['key']} ({truncate(c.get('summary', ''), 60)}): "
                f"\"{truncate(c['description_excerpt'], 140)}\""
            )
        if len(out) >= limit:
            break
    return out


def normalize_source_string(src: str, f: dict | None, epic_key: str) -> str:
    s = (src or "").strip()
    if len(s) >= 8:
        return s
    if f:
        return source_from_finding(f, epic_key)
    low = s.lower()
    if low in ("epic", "jira_description", "jira description"):
        return f"Epic {epic_key} — Jira description and epic-level narrative"
    if low in ("sibling", "jira_epic_child", "child"):
        return f"Epic {epic_key} — child story descriptions in epic inventory"
    if low.startswith("finding"):
        return s if len(s) >= 8 else f"Epic {epic_key} — {s}"
    return f"Epic {epic_key} — Reviewer gather ({s or 'requirement text'})"


def source_from_finding(f: dict, epic_key: str) -> str:
    raw = (f.get("source") or "").strip()
    ref = f.get("checklist_ref") or "?"
    if len(raw) >= 8 and raw.lower() not in ("jira_description", "epic"):
        return f"{epic_key} — {raw}"
    return f"{epic_key} Jira ({ref})"


def build_rich_context(
    q: dict,
    by_id: dict[str, dict],
    epic_key: str,
    p: dict,
) -> str:
    """Multi-sentence why-we're-asking from linked findings and gather."""
    unblocks = [u for u in (q.get("unblocks") or []) if u in by_id]
    if not unblocks:
        # Try to match finding_id pattern in question text
        for fid in by_id:
            if fid in (q.get("question") or ""):
                unblocks.append(fid)
    sentences: list[str] = []

    for fid in unblocks[:2]:
        f = by_id[fid]
        summary = (f.get("finding_summary") or "").strip()
        impact = (f.get("testing_impact") or "").strip()
        if summary:
            sentences.append(summary)
        if impact:
            imp = impact.strip()
            if imp.lower().startswith("without"):
                sentences.append(imp)
            else:
                lead = imp[0].lower() + imp[1:] if imp else imp
                sentences.append(f"Without an answer, {lead}")

    if len(sentences) < 2 and is_epic(p):
        kids = child_citations(p, 1)
        if kids:
            sentences.append(f"Related child text: {kids[0]}")

    if len(sentences) < 2:
        req = (p.get("requirements") or [{}])[0]
        ex = truncate(req.get("description_excerpt") or "", 120)
        if ex:
            sentences.append(f'Epic text says: "{ex}"')

    if not sentences:
        topic = (q.get("topic") or "").strip()
        if topic == "PRD authority":
            sentences.append(
                f"{epic_key} and linked docs may disagree; QA needs one authoritative source for expected results."
            )
        else:
            sentences.append(
                f"{epic_key} does not spell out this decision; QA cannot lock pass/fail checks yet."
            )

    text = ". ".join(s.strip().rstrip(".") for s in sentences if s.strip())
    if text and not text.endswith("."):
        text += "."
    return lint_safe_prose(text[:700])


def expand_question_text(q: dict, by_id: dict[str, dict], epic_key: str) -> None:
    text = (q.get("question") or "").strip()
    unblocks = [u for u in (q.get("unblocks") or []) if u in by_id]
    if len(text) >= MIN_QUESTION:
        return
    parts = [text.rstrip("?.") + "?"] if text else []
    for fid in unblocks[:2]:
        f = by_id[fid]
        summary = (f.get("finding_summary") or "").strip()
        if summary and summary.lower() not in text.lower():
            parts.append(f"Concretely: {summary}")
    if len(" ".join(parts)) < MIN_QUESTION and unblocks:
        f = by_id[unblocks[0]]
        qfm = (f.get("question_for_PM") or "").strip()
        if qfm:
            parts.append(qfm)
    topic = q.get("topic") or ""
    if len(" ".join(parts)) < MIN_QUESTION and topic == "PRD authority":
        src = (q.get("source") or "linked product documentation").strip()
        parts.append(
            f"Name the binding artefact (for example a PRD section title or Confluence page) when it "
            f"conflicts with epic or child text on {epic_key}; we saw the gap while reading {src}."
        )
    if len(" ".join(parts)) < MIN_QUESTION:
        parts.append(
            f"Please reply in Jira on {epic_key} so QA can lock scope and expected results for this epic slice."
        )
    q["question"] = lint_safe_prose(" ".join(p for p in parts if p).strip()[:900])


def normalize_owner(q: dict) -> None:
    topic = q.get("topic") or ""
    owner = q.get("owner_hint") or "PM"
    if owner == "PO" and topic not in PO_TOPICS:
        q["owner_hint"] = "PM"
    elif owner not in ("PM", "UX", "EM", "Security", "PO"):
        q["owner_hint"] = "PM"
    elif not q.get("owner_hint"):
        q["owner_hint"] = "PM"
    if q.get("topic") == "PRD authority" and q.get("owner_hint") == "PM":
        q["owner_hint"] = "PO"


def question_owner_for_finding(f: dict) -> str:
    cat = f.get("category") or ""
    if cat == "data_sensitivity":
        return "Security"
    hint = f.get("owner_hint") or "PM"
    if hint in ("UX", "EM", "Security", "PO"):
        return hint if hint != "PO" else "PM"
    return "PM"


def synthesize_question_from_finding(f: dict, epic_key: str, p: dict) -> dict:
    cat = f.get("category") or "behavioral_gap"
    topic = CATEGORY_TOPIC.get(cat, "Behavior")
    sev = f.get("severity") or "MEDIUM"
    priority = "High" if sev in ("CRITICAL", "HIGH") else "Medium"
    if sev == "LOW":
        priority = "Optional"
    summary = (f.get("finding_summary") or "Gap in requirement text").strip()
    qfm = (f.get("question_for_PM") or "").strip()
    if qfm:
        question = qfm if qfm.endswith("?") else qfm + "?"
    else:
        question = summary if summary.endswith("?") else f"What is the decision on: {summary}?"
    q = {
        "question_id": "Q0",
        "topic": topic,
        "question": question,
        "context": "",
        "source": source_from_finding(f, epic_key),
        "priority": priority,
        "unblocks": [f["finding_id"]],
        "owner_hint": question_owner_for_finding(f),
        "status": "open",
    }
    expand_question_text(q, {f["finding_id"]: f}, epic_key)
    q["context"] = build_rich_context(q, {f["finding_id"]: f}, epic_key, p)
    normalize_owner(q)
    return q


def findings_missing_questions(p: dict) -> list[dict]:
    by_id = finding_map(p)
    covered = set()
    for q in p.get("questions", []):
        for u in q.get("unblocks") or []:
            covered.add(u)
    out = []
    for f in p.get("findings", []):
        if f.get("status", "open") != "open":
            continue
        if f.get("severity") not in ("CRITICAL", "HIGH", "MEDIUM"):
            continue
        fid = f.get("finding_id")
        if fid and fid not in covered:
            out.append(f)
    return out


def renumber_questions(p: dict) -> None:
    order = topic_order(p)
    groups: dict[str, list] = {}
    for q in p.get("questions", []):
        groups.setdefault(q["topic"], []).append(q)
    n = 1
    for topic in order:
        for q in sorted(groups.get(topic, []), key=lambda x: x.get("question_id", "")):
            q["question_id"] = f"Q{n}"
            n += 1
    for topic in groups:
        if topic not in order:
            for q in sorted(groups[topic], key=lambda x: x.get("question_id", "")):
                q["question_id"] = f"Q{n}"
                n += 1


def enrich_question(q: dict, by_id: dict[str, dict], epic_key: str, p: dict, *, force: bool) -> None:
    normalize_owner(q)
    expand_question_text(q, by_id, epic_key)
    ctx = (q.get("context") or "").strip()
    if force or len(ctx) < MIN_CONTEXT or len([s for s in re.split(r"[.!?]", ctx) if s.strip()]) < 2:
        q["context"] = build_rich_context(q, by_id, epic_key, p)
    else:
        q["context"] = lint_safe_prose(ctx)
    q["question"] = lint_safe_prose((q.get("question") or "").strip())
    src = (q.get("source") or "").strip()
    unblocks = [u for u in (q.get("unblocks") or []) if u in by_id]
    f0 = by_id[unblocks[0]] if unblocks else None
    q["source"] = normalize_source_string(src, f0, epic_key)


def enrich_payload(p: dict, *, force: bool = False) -> tuple[int, int]:
    epic_key = epic_key_from_payload(p)
    by_id = finding_map(p)
    added = 0
    for f in findings_missing_questions(p):
        p.setdefault("questions", []).append(synthesize_question_from_finding(f, epic_key, p))
        by_id[f["finding_id"]] = f
        added += 1
    changed = 0
    for q in p.get("questions", []):
        before = json.dumps(q, sort_keys=True)
        enrich_question(q, by_id, epic_key, p, force=force)
        if json.dumps(q, sort_keys=True) != before:
            changed += 1
    renumber_questions(p)
    note = "Questions normalized — plain wording from findings (2026-10-07)."
    rep = p.setdefault("report", {})
    handoff = (rep.get("handoff_note") or "").strip()
    if note not in handoff:
        rep["handoff_note"] = f"{handoff} {note}".strip() if handoff else note
    return changed, added


def process_file(path: Path, dry_run: bool, *, force: bool) -> tuple[bool, str]:
    with path.open(encoding="utf-8") as f:
        p = json.load(f)
    changed, added = enrich_payload(p, force=force)
    if dry_run:
        return True, f"{path}: would update {changed}, add {added} question(s)"
    with path.open("w", encoding="utf-8") as f:
        json.dump(p, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return True, f"{path}: updated {changed}, added {added} question(s)"


def discover_payloads(run_dir: Path) -> list[Path]:
    out = []
    for child in run_dir.iterdir():
        if not child.is_dir():
            continue
        if child.name.startswith("_") or child.name == "portfolio":
            continue
        if not re.match(r"^[A-Z][A-Z0-9]+-\d+$", child.name):
            continue
        p = child / "review-payload.json"
        if p.is_file():
            out.append(p)
    return sorted(out, key=lambda p: p.parent.name)


def main() -> None:
    ap = argparse.ArgumentParser(description="Expand Reviewer clarification questions in payloads")
    ap.add_argument("paths", nargs="*", type=Path)
    ap.add_argument("--run-dir", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--force",
        action="store_true",
        help="Rebuild every question context from findings/child excerpts (still no invented requirements)",
    )
    args = ap.parse_args()
    paths: list[Path] = list(args.paths)
    if args.run_dir:
        paths.extend(discover_payloads(args.run_dir.resolve()))
    if not paths:
        raise SystemExit("Provide --run-dir or payload path(s)")
    ok = 0
    for path in paths:
        path = path.resolve()
        if not path.is_file():
            continue
        _, msg = process_file(path, args.dry_run, force=args.force)
        ok += 1
        print(msg)
    print(f"Done: {ok}/{len(paths)} payload(s)")


if __name__ == "__main__":
    main()
