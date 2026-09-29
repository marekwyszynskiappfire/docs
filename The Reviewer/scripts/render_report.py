#!/usr/bin/env python3
"""Render a ReviewPayload into review-report.md and review-report.html.

The model writes only review-payload.json; every report is produced by this
script so that section set, order, tiering, ids, and wording rules are identical
across runs (PRF-21). Standard library only; `jsonschema` is used for validation
when installed.

Usage:
    python3 render_report.py PATH/TO/review-payload.json [--out-dir DIR] [--strict]

Writes review-report.md, review-report.html, jira-comment-full.txt and
jira-comment-short.txt (the Jira files go beside the Markdown report).

Exit codes: 0 rendered, 1 payload invalid or wrong version, 2 `--strict` and lint found problems (no report files written).
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

SUPPORTED_VERSION = "1.1"
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "review-payload.schema.json"

SEVERITY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
SEVERITY_LABEL = {"CRITICAL": "Critical", "HIGH": "High", "MEDIUM": "Medium", "LOW": "Low"}
STORY_TOPICS = ["Behavior", "Scope", "Edge cases", "Integrations", "Permissions", "Data"]
EPIC_TOPICS = ["Definition of done", "PRD authority", "Design authority", "Rollout"]
PRIORITY_ORDER = ["High", "Medium", "Optional"]
STRIP_CLASS = {
    "ready_with_clarifications": ("ok", "✓"),
    "needs_clarification_before_scope_lock": ("warn", "⚠"),
    "cannot_plan_scope_yet": ("blocked", "⚠"),
}
LEVEL_DOT = {"High": "emerald", "Medium": "amber", "Low": "rose"}
RISK_DOT = {"High": "rose", "Medium": "amber", "Low": "emerald"}
AUTOMATION_DOT = {"Yes": "emerald", "TBD": "amber", "No": "slate"}
SOURCE_STATUS_LABEL = {
    "analyzed": "Analyzed", "unavailable": "Unavailable",
    "failed": "Could not read", "not_applicable": "Not applicable",
}
SOURCE_STATUS_CLASS = {"analyzed": "analyzed", "unavailable": "unavailable", "failed": "failed", "not_applicable": "na"}
CONTENT_SOURCE_LABEL = {"description": "Description", "title_only": "Title only", "unavailable": "Unavailable"}

# Wording lint — mirrors SKILL.md §7 "Blocked phrases" and D12 (no percentages in prose).
BLOCKED_PATTERNS = [
    r"\bstory failed\b", r"\bnot ready\b", r"\bblocked by qa\b", r"\bpm did not provide ac\b",
    r"\bgate\b", r"\bblockers?\b", r"\bstory is invalid\b",
]
PERCENT_PATTERN = r"\d+(?:\.\d+)?\s?%"

# Allowed category → checklist rows (reference.md "Finding categories", PRF-19).
CATEGORY_ROWS = {
    "acceptance_criteria": {"A3"},
    "scope": {"A2", "A4"},
    "testability": {"A8", "B9", "B10"},
    "traceability": {"A5"},
    "open_questions": {"A6", "A8"},
    "template_compliance": {"A1", "A2", "A8"},
    "data_sensitivity": {"A7"},
    "behavioral_gap": {f"B{i}" for i in range(1, 13)},
    "epic_lifecycle": {"C1", "C2", "C3"},
}
HIGH_QUESTION_CAP = 5


# --------------------------------------------------------------------------- helpers

def esc(text) -> str:
    return html.escape("" if text is None else str(text), quote=True)


def inline(text) -> str:
    """Escape, then render `code` spans. The only inline markup the payload may use."""
    return re.sub(r"`([^`]+)`", r'<span class="mono">\1</span>', esc(text))


def md_inline(text) -> str:
    return "" if text is None else str(text).replace("\n", " ").replace("|", "\\|")


def status_class(status: str) -> str:
    s = (status or "").strip().lower()
    if s in {"done", "closed", "resolved"}:
        return "done"
    if s in {"canceled", "cancelled", "won't do", "wont do"}:
        return "canceled"
    if s.startswith("waiting for") or s in {"ready for release", "ready to deploy"}:
        return "wfr"
    if s in {"in progress", "in review", "code review", "in qa", "testing", "in development"}:
        return "inprogress"
    return "open"


def issue_type(p: dict) -> str:
    scope = p.get("scope", {})
    if scope.get("issue_type"):
        return scope["issue_type"]
    reqs = p.get("requirements") or []
    if reqs and reqs[0].get("issue_type"):
        return reqs[0]["issue_type"]
    return scope.get("type", "story").capitalize()


def is_epic(p: dict) -> bool:
    return p.get("scope", {}).get("type") == "epic"


def is_post_delivery(p: dict) -> bool:
    return is_epic(p) and p.get("scope", {}).get("lifecycle") == "post_delivery"


def readiness_heading(p: dict) -> str:
    return "Readiness for regression and sign-off" if is_post_delivery(p) else "Readiness for test planning"


def scan_label(p: dict) -> str:
    label = p.get("scan_label", "Initial scan")
    if is_post_delivery(p):
        return "Post-delivery rescan" if label == "Rescan" else "Post-delivery review"
    return label


def lead_sentence(p: dict) -> str:
    if not is_post_delivery(p):
        return ""
    status = ((p.get("requirements") or [{}])[0].get("status") or "").strip()
    if not status:
        status = "delivered"
    return (f"This epic is already {status}: the findings below are gaps to close for regression "
            "coverage and sign-off, not reasons to hold back the build.")


def topic_order(p: dict) -> list:
    return EPIC_TOPICS + STORY_TOPICS if is_epic(p) else STORY_TOPICS + EPIC_TOPICS


def plural(n: int, word: str) -> str:
    if n == 1:
        return f"{n} {word}"
    return f"{n} " + ("children" if word == "child" else word + "s")


def epic_has_scannable_children(p: dict) -> bool:
    return any(status_class(c.get("status", "")) != "canceled" for c in children(p))


def gate_line(p: dict) -> str:
    gate = p["gate"]
    crit = gate.get("critical_unresolved_count", 0)
    if is_epic(p) and not epic_has_scannable_children(p):
        if gate["status"] == "PASS":
            return ("No child issues are linked yet; epic-level review is clear enough to break work down "
                    "when children exist.")
        return ("No child issues are linked yet; address the findings below before individual child scans.")
    subject = "Child scans" if is_epic(p) else "Test case drafting"
    tail = "them" if is_epic(p) else "it"
    if gate["status"] == "PASS":
        return f"{subject} can start."
    if gate["status"] == "BLOCKED":
        return f"{subject} waits on {plural(crit, 'critical finding')}."
    if gate.get("force_override"):
        who = gate.get("force_override_by", "unknown")
        when = (gate.get("force_override_at") or "")[:10]
        return (f"{subject} was started by explicit override ({who}, {when}); "
                f"{plural(crit, 'critical finding')} remain open.")
    return f"{subject} can start; the findings below should travel with {tail}."


def sorted_findings(p: dict) -> list:
    return sorted(p.get("findings", []), key=lambda f: (SEVERITY_ORDER.index(f["severity"]), f["finding_id"]))


def grouped_questions(p: dict) -> list:
    def qnum(q):
        m = re.search(r"\d+", q["question_id"])
        return int(m.group()) if m else 0
    groups = {}
    for q in p.get("questions", []):
        groups.setdefault(q["topic"], []).append(q)
    fixed = topic_order(p)
    order = [t for t in fixed if t in groups] + [t for t in groups if t not in fixed]
    return [(t, sorted(groups[t], key=qnum)) for t in order]


def has_decision(item: dict) -> bool:
    """Decision-layer inclusion rule (reference.md, PRF-05)."""
    if "severity" in item:
        return item["severity"] in ("CRITICAL", "HIGH")
    return item.get("priority") == "High"


def open_items(p: dict) -> list:
    ids = [f["finding_id"] for f in sorted_findings(p) if has_decision(f) and f.get("status", "open") == "open"]
    ids += [q["question_id"] for _, qs in grouped_questions(p) for q in qs
            if has_decision(q) and q.get("status", "open") == "open"]
    return ids


def counts_line(p: dict) -> tuple[str, str]:
    fs = p.get("findings", [])
    sev = {s: sum(1 for f in fs if f["severity"] == s) for s in SEVERITY_ORDER}
    qs = [q for q in p.get("questions", []) if q.get("status", "open") == "open"]
    pri = {s: sum(1 for q in qs if q["priority"] == s) for s in PRIORITY_ORDER}
    f_part = ", ".join(f"{sev[s]} {SEVERITY_LABEL[s]}" for s in SEVERITY_ORDER)
    q_part = ", ".join(f"{pri[s]} {s}" for s in PRIORITY_ORDER if pri[s])
    head_f = plural(len(fs), "finding")
    head_q = plural(len(qs), "open question")
    return f"{head_f} — {f_part}", f"{head_q}" + (f" — {q_part}" if q_part else "")


def not_stated_heading(p: dict) -> str:
    return f"Not stated in {issue_type(p).lower()}"


def children(p: dict) -> list:
    return (p.get("rollup") or {}).get("epic_child_inventory") or []


def status_mix(p: dict) -> dict:
    mix = (p.get("rollup") or {}).get("epic_status_mix")
    if mix:
        return mix
    out = {}
    for c in children(p):
        out[c.get("status", "Unknown")] = out.get(c.get("status", "Unknown"), 0) + 1
    return out


def mention_count(p: dict, key: str) -> int:
    """Batch rank: at most one count per open finding (HIGH+) and per open question (PRF-16)."""
    pat = re.compile(rf"\b{re.escape(key)}\b")
    n = 0
    for f in p.get("findings", []):
        if f.get("status", "open") != "open":
            continue
        if f["severity"] not in ("CRITICAL", "HIGH", "MEDIUM"):
            continue
        blob = " ".join(t for t in (f.get("finding_summary"), f.get("testing_impact")) if t)
        if blob and pat.search(blob):
            n += 1
    for q in p.get("questions", []):
        if q.get("status", "open") != "open":
            continue
        blob = " ".join(t for t in (q.get("question"), q.get("context"), " ".join(q.get("unblocks") or [])) if t)
        if blob and pat.search(blob):
            n += 1
    return n


def ranked_batch(p: dict) -> list:
    """Every non-Canceled child, ranked (PRF-16): most-named first, then status, then key."""
    status_rank = {"wfr": 0, "inprogress": 0, "open": 1, "done": 2}

    def key_num(k):
        m = re.search(r"(\d+)$", k)
        return (k.rsplit("-", 1)[0], int(m.group(1)) if m else 0)

    kids = [c for c in children(p) if status_class(c.get("status", "")) != "canceled"]
    return [c["key"] for c in sorted(kids, key=lambda c: (
        -mention_count(p, c["key"]), status_rank.get(status_class(c.get("status", "")), 1), key_num(c["key"])))]


def lint(p: dict) -> list:
    """Wording lint over every human-facing prose field the payload carries."""
    texts = []
    for f in p.get("findings", []):
        texts += [(f["finding_id"], f.get("finding_summary")), (f["finding_id"], f.get("testing_impact"))]
    for q in p.get("questions", []):
        texts += [(q["question_id"], q.get("question")), (q["question_id"], q.get("context"))]
    r = p.get("report", {})
    texts.append(("report.readiness_line", r.get("readiness_line")))
    texts.append(("report.next_action", r.get("next_action")))
    texts.append(("report.handoff_note", r.get("handoff_note")))
    texts.append(("report.batch_rationale", r.get("batch_rationale")))
    for key in ("facts", "risks", "design_observations", "epic_context"):
        for i, item in enumerate(r.get(key, [])):
            texts.append((f"report.{key}[{i}]", item.get("text")))
    for i, t in enumerate(r.get("not_stated", [])):
        texts.append((f"report.not_stated[{i}]", t))
    for i, t in enumerate(r.get("testing_focus", [])):
        texts.append((f"report.testing_focus[{i}]", t.get("text")))
    problems = []
    for where, text in texts:
        if not text:
            continue
        # Verbatim quotes of source text are exempt (PRF-11).
        prose = re.sub(r'"[^"]*"|“[^”]*"|\'[^\']*\'', " ", text)
        for pat in BLOCKED_PATTERNS:
            m = re.search(pat, prose, re.IGNORECASE)
            if m:
                problems.append(f"{where}: blocked phrase \"{m.group()}\"")
        m = re.search(PERCENT_PATTERN, prose)
        if m:
            problems.append(f"{where}: percentage \"{m.group()}\" in prose (use the raw count)")

    shown = [q["question_id"] for _, qs in grouped_questions(p) for q in qs]
    expected = [f"Q{i}" for i in range(1, len(shown) + 1)]
    if shown != expected:
        problems.append(f"questions: ids read {', '.join(shown)} in display order; renumber to {', '.join(expected)} (PRF-17)")

    kids = {c["key"]: c for c in children(p)}
    batch = (p.get("rollup") or {}).get("recommended_batch_keys") or []
    for k in batch:
        if status_class(kids.get(k, {}).get("status", "")) == "canceled":
            problems.append(f"rollup.recommended_batch_keys: {k} is Canceled; name it in a finding or question instead (PRF-16)")
    if is_epic(p) and kids:
        expected = ranked_batch(p)
        if set(batch) != set(expected):
            missing = [k for k in expected if k not in batch]
            extra = [k for k in batch if k not in expected]
            problems.append("rollup.recommended_batch_keys must list every non-Canceled child (PRF-16)"
                            + (f"; missing {', '.join(missing)}" if missing else "")
                            + (f"; not a non-Canceled child: {', '.join(extra)}" if extra else ""))
        elif batch != expected:
            problems.append(f"rollup.recommended_batch_keys out of ranked order; expected {', '.join(expected)} (PRF-16)")

    fs = p.get("findings", [])
    for f in fs:
        ref, cat = f["checklist_ref"], f["category"]
        if ref not in CATEGORY_ROWS.get(cat, set()):
            problems.append(f"{f['finding_id']}: category {cat} does not fit checklist row {ref} (PRF-19)")
        if ref.startswith("C") and not is_epic(p):
            problems.append(f"{f['finding_id']}: Group C row {ref} is Epic scope only (PRF-19)")
        if ref == "C3" and f["severity"] not in ("LOW",):
            problems.append(f"{f['finding_id']}: C3 is LOW at most (PRF-19)")

    open_sev = [f["severity"] for f in fs if f.get("status", "open") == "open"]
    gate = p["gate"]
    if "CRITICAL" in open_sev:
        expected = "PASS_WITH_WARNINGS" if gate.get("force_override") else "BLOCKED"
    elif "HIGH" in open_sev or "MEDIUM" in open_sev:
        expected = "PASS_WITH_WARNINGS"
    else:
        expected = "PASS"
    if gate["status"] != expected:
        problems.append(f"gate.status is {gate['status']} but open finding severities give {expected} (PRF-14)")

    by_id = {f["finding_id"]: f for f in fs}
    open_qs = [q for q in p.get("questions", []) if q.get("status", "open") == "open"]
    for q in open_qs:
        clears = [u for u in q.get("unblocks") or []
                  if by_id.get(u, {}).get("severity") in ("CRITICAL", "HIGH")]
        if clears and q["priority"] != "High":
            problems.append(f"{q['question_id']}: clears {', '.join(clears)} (HIGH+) so it must be High priority, not {q['priority']} (PRF-13)")
    n_high = sum(1 for q in open_qs if q["priority"] == "High")
    if n_high > HIGH_QUESTION_CAP and not p.get("report", {}).get("question_cap_reason"):
        problems.append(f"questions: {n_high} High priority exceeds {HIGH_QUESTION_CAP}; merge related questions "
                        "or state report.question_cap_reason (PRF-13)")
    return problems


# --------------------------------------------------------------------------- HTML

CSS = """
  :root {
    --emerald: #10b981; --emerald-bg: #ecfdf5; --emerald-text: #047857;
    --amber: #f59e0b; --amber-bg: #fffbeb; --amber-text: #92400e;
    --rose: #f43f5e; --rose-bg: #fff1f2; --rose-text: #be123c;
    --blue: #3b82f6; --blue-bg: #eff6ff; --blue-text: #1e40af;
    --slate: #64748b; --slate-bg: #f8fafc; --slate-text: #334155;
    --ink: #0f172a; --line: #e2e8f0; --paper: #ffffff; --muted: #64748b;
  }
  * { box-sizing: border-box; }
  body { margin: 0; padding: 0; background: #f1f5f9; color: var(--ink);
    font: 15px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
  .wrap { max-width: 960px; margin: 0 auto; padding: 28px 20px 80px; }
  code, .mono { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 0.92em; }
  .header-card { background: var(--paper); border: 1px solid var(--line); border-radius: 14px; padding: 20px 24px; margin-bottom: 14px; }
  .header-top h1 { font-size: 20px; margin: 0; }
  .badge { display: inline-block; font-size: 11px; padding: 2px 8px; border-radius: 999px; background: var(--slate-bg); color: var(--slate-text); margin-left: 8px; font-weight: 600; letter-spacing: .02em; vertical-align: middle; }
  .header-meta { color: var(--muted); font-size: 13px; margin-top: 6px; }
  .header-meta a { color: #0369a1; text-decoration: none; }
  .summary-line { font-size: 14px; margin-top: 12px; }
  .readiness-strip { border-radius: 12px; padding: 16px 20px; margin: 14px 0; border: 1px solid; }
  .readiness-strip.ok { background: var(--emerald-bg); border-color: #a7f3d0; color: var(--emerald-text); }
  .readiness-strip.warn { background: var(--amber-bg); border-color: #fde68a; color: var(--amber-text); }
  .readiness-strip.blocked { background: var(--rose-bg); border-color: #fecdd3; color: var(--rose-text); }
  .readiness-strip .r-kicker { font-size: 11px; text-transform: uppercase; letter-spacing: .05em; font-weight: 700; opacity: .75; margin-bottom: 2px; }
  .readiness-strip .r-label { font-size: 17px; font-weight: 800; }
  .readiness-strip .r-sub { font-size: 13px; margin-top: 4px; opacity: .9; }
  .gate-line { font-size: 13px; margin: -6px 0 14px 4px; color: var(--slate-text); }
  .kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 14px 0 22px; }
  .kpi { background: var(--paper); border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; }
  .kpi-label { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }
  .kpi-value { font-size: 16px; font-weight: 700; margin-top: 4px; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
  .kpi-note { font-size: 11px; color: #94a3b8; font-weight: 400; }
  .dot { width: 9px; height: 9px; border-radius: 50%; display: inline-block; }
  .dot.emerald { background: var(--emerald); } .dot.amber { background: var(--amber); } .dot.rose { background: var(--rose); } .dot.slate { background: var(--slate); }
  details { background: var(--paper); border: 1px solid var(--line); border-radius: 12px; margin-bottom: 10px; }
  details > summary { cursor: pointer; padding: 13px 18px; font-weight: 600; list-style: none; display: flex; justify-content: space-between; align-items: center; }
  details > summary::-webkit-details-marker { display: none; }
  details > summary .count { color: var(--muted); font-weight: 400; font-size: 13px; margin-left: 6px; }
  details > summary .chev { font-size: 12px; color: #94a3b8; }
  .section-body { padding: 4px 18px 18px; }
  .tier-label { font-size: 11px; text-transform: uppercase; letter-spacing: .06em; color: #94a3b8; margin: 22px 2px 6px; font-weight: 700; }
  table { width: 100%; border-collapse: collapse; font-size: 13.5px; margin-top: 6px; }
  th { text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: .03em; color: var(--muted); border-bottom: 1px solid var(--line); padding: 6px 8px; }
  td { border-bottom: 1px solid #f1f5f9; padding: 8px 8px; vertical-align: top; }
  tr:last-child td { border-bottom: none; }
  .sev { font-weight: 700; white-space: nowrap; }
  .sev.CRITICAL { color: #fff; background: var(--rose); padding: 1px 7px; border-radius: 5px; }
  .sev.HIGH { color: var(--rose-text); } .sev.MEDIUM { color: var(--amber-text); } .sev.LOW { color: var(--slate-text); }
  .ref { font-family: monospace; font-size: 12px; background: var(--slate-bg); padding: 1px 6px; border-radius: 6px; }
  .fid { font-family: monospace; font-size: 12px; white-space: nowrap; }
  .owner { display: inline-block; font-size: 10.5px; padding: 1px 8px; border-radius: 999px; font-weight: 700; white-space: nowrap; }
  .owner.PM { background: #e0e7ff; color: #3730a3; } .owner.UX { background: #fae8ff; color: #86198f; }
  .owner.EM { background: #dbeafe; color: #1e40af; } .owner.Security { background: var(--rose-bg); color: var(--rose-text); }
  .owner.PO { background: #ccfbf1; color: #0f766e; } .owner.QA { background: var(--slate-bg); color: var(--slate-text); }
  .status-pill { display: inline-block; font-size: 10.5px; padding: 1px 8px; border-radius: 999px; font-weight: 700; white-space: nowrap; }
  .status-pill.analyzed, .status-pill.done { background: var(--emerald-bg); color: var(--emerald-text); }
  .status-pill.na, .status-pill.open, .status-pill.canceled { background: var(--slate-bg); color: var(--slate-text); }
  .status-pill.unavailable, .status-pill.wfr { background: var(--amber-bg); color: var(--amber-text); }
  .status-pill.failed { background: var(--rose-bg); color: var(--rose-text); }
  .status-pill.inprogress { background: var(--blue-bg); color: var(--blue-text); }
  .fact { margin: 0 0 8px; padding-left: 16px; position: relative; font-size: 13.5px; }
  .fact::before { content: "•"; position: absolute; left: 0; color: #cbd5e1; }
  .src { color: var(--muted); font-size: 12px; font-style: italic; }
  .empty-state { color: #94a3b8; font-style: italic; font-size: 13px; padding: 8px 0; margin: 0; }
  .q-topic { font-weight: 700; font-size: 12px; text-transform: uppercase; letter-spacing: .03em; color: #0369a1; margin: 16px 0 6px; }
  .q-card { border: 1px solid var(--line); border-radius: 10px; padding: 12px 14px; margin-bottom: 8px; background: #fafbfc; }
  .q-title { font-weight: 700; font-size: 14px; }
  .q-meta { font-size: 12.5px; color: var(--muted); margin-top: 6px; display: grid; grid-template-columns: 1fr 1fr; gap: 3px 14px; }
  .prio { display: inline-block; font-size: 10.5px; padding: 1px 7px; border-radius: 999px; font-weight: 700; }
  .prio.High { background: var(--rose-bg); color: var(--rose-text); }
  .prio.Medium { background: var(--amber-bg); color: var(--amber-text); }
  .prio.Optional { background: var(--slate-bg); color: var(--slate-text); }
  .decision-row { display: flex; gap: 6px; margin-top: 8px; flex-wrap: wrap; align-items: center; }
  .decision-row .fid { margin-right: 4px; color: var(--muted); }
  .decision-row button { font-size: 12px; padding: 5px 11px; border-radius: 7px; border: 1px solid var(--line); background: #fff; cursor: pointer; color: var(--ink); }
  .decision-row button.active-accept { background: var(--emerald-bg); border-color: var(--emerald); color: var(--emerald-text); }
  .decision-row button.active-reject { background: var(--rose-bg); border-color: var(--rose); color: var(--rose-text); }
  .decision-row button.active-discuss { background: var(--amber-bg); border-color: var(--amber); color: var(--amber-text); }
  .decision-row input[type=text] { flex: 1; min-width: 140px; font-size: 12px; padding: 5px 8px; border: 1px solid var(--line); border-radius: 7px; }
  .mix-bar { display: flex; height: 14px; border-radius: 7px; overflow: hidden; margin: 10px 0 8px; border: 1px solid var(--line); }
  .mix-seg.done { background: var(--emerald); } .mix-seg.inprogress { background: var(--blue); }
  .mix-seg.open { background: #cbd5e1; } .mix-seg.wfr { background: var(--amber); } .mix-seg.canceled { background: #94a3b8; }
  .mix-legend { display: flex; gap: 16px; font-size: 12.5px; color: var(--muted); flex-wrap: wrap; }
  .mix-legend .lg { display: flex; align-items: center; gap: 5px; }
  .mix-legend .sw { width: 9px; height: 9px; border-radius: 2px; display: inline-block; }
  .sw.done { background: var(--emerald); } .sw.inprogress { background: var(--blue); } .sw.open { background: #cbd5e1; }
  .sw.wfr { background: var(--amber); } .sw.canceled { background: #94a3b8; }
  .batch-block { border: 1px solid #bae6fd; border-radius: 14px; padding: 18px 20px; background: #f0f9ff; margin: 18px 0; }
  .batch-block h3, .tc-handoff h3 { margin: 0 0 6px; font-size: 15px; }
  .batch-block p { font-size: 13px; margin: 6px 0; color: #0c4a6e; }
  .batch-keys { display: flex; gap: 6px; flex-wrap: wrap; margin: 10px 0; }
  .batch-keys .k { font-family: monospace; font-size: 12px; background: #fff; border: 1px solid #bae6fd; border-radius: 6px; padding: 3px 9px; }
  .batch-cmds { font-family: monospace; font-size: 12px; background: #fff; border: 1px solid #bae6fd; border-radius: 8px; padding: 10px 12px; margin-top: 8px; }
  .batch-cmds div { margin-bottom: 3px; }
  .tc-handoff { border: 1px solid #99f6e4; border-radius: 14px; padding: 18px 20px; background: #f0fdfa; margin-top: 18px; }
  .tc-handoff p { font-size: 13px; margin: 6px 0; color: #134e4a; }
  .tc-options { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
  .tc-opt { border-radius: 10px; padding: 10px 12px; font-size: 12px; }
  .tc-opt.a { background: var(--amber-bg); border: 1px solid #fde68a; }
  .tc-opt.b { background: var(--emerald-bg); border: 1px solid #a7f3d0; }
  .tc-opt .lbl { font-weight: 700; margin-bottom: 3px; }
  .export-bar { position: sticky; bottom: 0; background: rgba(241,245,249,.92); backdrop-filter: blur(6px); padding: 14px 0 4px; margin-top: 10px; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--line); }
  .export-bar .status { font-size: 12.5px; color: var(--muted); }
  .export-bar button { background: var(--ink); color: #fff; border: none; padding: 9px 16px; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; }
  .footer-note { text-align: center; color: #94a3b8; font-size: 11.5px; margin-top: 22px; }
  @media print { .export-bar, .decision-row { display: none !important; } details { break-inside: avoid; } }
"""

SCRIPT = """
  const decisions = {};
  const TOTAL_ITEMS = %(total)d;
  function setDecision(id, action, btn) {
    decisions[id] = decisions[id] || {};
    decisions[id].action = action;
    btn.closest('.decision-row').querySelectorAll('button').forEach(b => b.classList.remove('active-accept', 'active-reject', 'active-discuss'));
    btn.classList.add('active-' + action);
    updateStatus();
  }
  function setComment(id, value) { decisions[id] = decisions[id] || {}; decisions[id].comment = value; }
  function updateStatus() {
    const decided = Object.keys(decisions).filter(k => decisions[k].action).length;
    document.getElementById('decision-status').textContent = decided + ' of ' + TOTAL_ITEMS + ' items decided';
  }
  function exportDecisions() {
    const payload = { run_id: %(run_id)s, jira_key: %(key)s, schema_version: %(version)s, exported_at: new Date().toISOString(), decisions: decisions };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = %(filename)s;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
"""


def decision_row(item_id: str) -> str:
    i = esc(item_id)
    js = json.dumps(item_id)
    return (f'<div class="decision-row" data-id="{i}"><span class="fid">{i}</span>'
            f'<button onclick=\'setDecision({js},"accept",this)\'>Accept</button>'
            f'<button onclick=\'setDecision({js},"reject",this)\'>Reject</button>'
            f'<button onclick=\'setDecision({js},"discuss",this)\'>Needs discussion</button>'
            f'<input type="text" placeholder="Optional comment on {i}…" oninput=\'setComment({js}, this.value)\'></div>')


def section(sec_id: str, title: str, count: str, body: str, open_: bool) -> str:
    chev = "▾" if open_ else "▸"
    attr = " open" if open_ else ""
    c = f' <span class="count">({esc(count)})</span>' if count != "" else ""
    return (f'<details{attr} id="{sec_id}"><summary><span>{esc(title)}{c}</span><span class="chev">{chev}</span></summary>'
            f'<div class="section-body">{body}</div></details>')


def empty(text: str) -> str:
    return f'<p class="empty-state">{esc(text)}</p>'


def sourced(items: list) -> str:
    out = []
    for it in items:
        src = f' <span class="src">(Source: {inline(it["source"])})</span>' if it.get("source") else ""
        out.append(f'<p class="fact">{inline(it["text"])}{src}</p>')
    return "".join(out)


def html_findings(p: dict) -> str:
    fs = sorted_findings(p)
    if not fs:
        return empty("No findings.")
    rows = []
    for f in fs:
        owner = f'<span class="owner {esc(f.get("owner_hint", ""))}">{esc(f.get("owner_hint", "—"))}</span>' if f.get("owner_hint") else "—"
        rows.append(
            f'<tr><td class="fid">{esc(f["finding_id"])}</td><td class="sev {f["severity"]}">{SEVERITY_LABEL[f["severity"]]}</td>'
            f'<td><span class="ref">{esc(f["checklist_ref"])}</span></td><td>{inline(f["finding_summary"])}</td>'
            f'<td>{inline(f.get("testing_impact", "")) or "—"}</td><td>{owner}</td></tr>')
    table = ('<table><thead><tr><th>ID</th><th>Sev</th><th>Ref</th><th>Finding</th><th>Testing impact</th><th>Owner</th></tr></thead>'
             f'<tbody>{"".join(rows)}</tbody></table>')
    decisions = "".join(decision_row(f["finding_id"]) for f in fs if has_decision(f))
    return table + decisions


def html_questions(p: dict) -> str:
    groups = grouped_questions(p)
    if not groups:
        return empty("No clarification questions.")
    out = []
    for topic, qs in groups:
        out.append(f'<div class="q-topic">{esc(topic)}</div>')
        for q in qs:
            owner = f'<span class="owner {esc(q["owner_hint"])}">{esc(q["owner_hint"])}</span>' if q.get("owner_hint") else "—"
            unblocks = ", ".join(q.get("unblocks") or []) or "—"
            out.append(
                f'<div class="q-card"><div class="q-title">{esc(q["question_id"])}. {inline(q["question"])}</div><div class="q-meta">'
                f'<div><strong>Context:</strong> {inline(q.get("context", "—"))}</div>'
                f'<div><strong>Priority:</strong> <span class="prio {esc(q["priority"])}">{esc(q["priority"])}</span></div>'
                f'<div><strong>Source:</strong> {inline(q.get("source", "—"))}</div>'
                f'<div><strong>Unblocks:</strong> {esc(unblocks)}</div>'
                f'<div><strong>Owner:</strong> {owner}</div></div>'
                + (decision_row(q["question_id"]) if has_decision(q) else "") + '</div>')
    return "".join(out)


def html_risks(p: dict) -> str:
    r = p["report"]
    out = ['<div class="tier-label" style="margin-top:0;">Known or suspected risks</div>']
    out.append(sourced(r["risks"]) if r["risks"] else empty("No risks identified."))
    out.append('<div class="tier-label">Suggested testing focus</div>')
    if r["testing_focus"]:
        for t in r["testing_focus"]:
            blocks = f' <em>(waits on: {esc(", ".join(t["blocks"]))})</em>' if t.get("blocks") else ""
            out.append(f'<p class="fact">{inline(t["text"])}{blocks}</p>')
    else:
        out.append(empty("No testing focus suggested."))
    return "".join(out)


def html_children(p: dict) -> str:
    kids = children(p)
    if not kids:
        return empty("This epic has no child work items yet.")
    mix = status_mix(p)
    total = sum(mix.values()) or 1
    segs = "".join(f'<div class="mix-seg {status_class(s)}" style="width:{n * 100 / total:.1f}%"></div>' for s, n in mix.items())
    legend = "".join(f'<span class="lg"><span class="sw {status_class(s)}"></span>{esc(s)} — {n}</span>' for s, n in mix.items())
    cs = {}
    for c in kids:
        cs[c.get("content_source", "unavailable")] = cs.get(c.get("content_source", "unavailable"), 0) + 1
    rows = []
    for c in kids:
        src = c.get("content_source", "unavailable")
        pill = "analyzed" if src == "description" else "unavailable"
        rows.append(f'<tr><td class="fid">{esc(c["key"])}</td><td>{esc(c.get("type", ""))}</td><td>{inline(c.get("summary", ""))}</td>'
                    f'<td><span class="status-pill {status_class(c.get("status", ""))}">{esc(c.get("status", ""))}</span></td>'
                    f'<td><span class="status-pill {pill}">{CONTENT_SOURCE_LABEL.get(src, src)}</span></td></tr>')
    cs_line = " · ".join(f"{n} read via {CONTENT_SOURCE_LABEL.get(k, k).lower()}" for k, n in cs.items())
    return (f'<div class="mix-bar">{segs}</div><div class="mix-legend">{legend}</div>'
            f'<p class="fact" style="margin-top:12px;">Full inventory — {plural(len(kids), "child")}, paginated to <span class="mono">isLast</span>, never a sample. {esc(cs_line)}.</p>'
            '<table style="margin-top:10px;"><thead><tr><th>Key</th><th>Type</th><th>Summary</th><th>Status</th><th>Content</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table>'
            '<p class="src" style="margin-top:10px;">"Title only" means the child\'s description was empty at scan time. Its summary is a lower-confidence signal and never marks checklist B12 covered by itself.</p>')


def html_batch(p: dict) -> str:
    keys = (p.get("rollup") or {}).get("recommended_batch_keys") or []
    rationale = p["report"].get("batch_rationale", "")
    if not keys:
        empty = ("The epic has no linked child issues yet — there is nothing to batch-scan. "
                 "Break work down in Jira first, or address the epic-level findings above.")
        return ('<div class="batch-block"><h3>Epic batch handoff</h3>'
                f'<p>{inline(rationale) or empty}</p></div>')
    chips = "".join(f'<span class="k">{esc(k)}</span>' for k in keys)
    cmds = [f'<div>confirm batch — scan all {plural(len(keys), "child")} in the order shown, 8 at a time</div>']
    cmds.append(f'<div>--batch keys {esc(",".join(keys[:2]))} — scan a specific subset</div>')
    return ('<div class="batch-block"><h3>Epic batch handoff</h3>'
            + (f'<p>{inline(rationale)}</p>' if rationale else "")
            + f'<div class="batch-keys">{chips}</div><div class="batch-cmds">{"".join(cmds)}</div>'
            '<p style="font-size:11.5px;color:#0369a1;margin-top:10px;">The batch does not run automatically — one of the commands above, or an explicit "yes," is required.</p></div>')


def html_datasources(p: dict) -> str:
    rows, problems = [], 0
    for s in p.get("context_loaded", []):
        st = s["status"]
        if st in ("unavailable", "failed"):
            problems += 1
        detail = s.get("reason") if st in ("unavailable", "failed") else s.get("detail", "")
        rows.append(f'<tr><td>{inline(s["source"])}</td><td><span class="status-pill {SOURCE_STATUS_CLASS[st]}">{SOURCE_STATUS_LABEL[st]}</span></td>'
                    f'<td>{inline(detail or "")}</td></tr>')
    table = ('<table><thead><tr><th>Source</th><th>Status</th><th>Detail</th></tr></thead>'
             f'<tbody>{"".join(rows)}</tbody></table>')
    note = "" if problems else '<p class="fact" style="margin-top:10px;">No sources were unavailable or failed in this run.</p>'
    return table + note


def html_checklist(p: dict) -> str:
    rows = "".join(
        f'<tr><td>{esc(c.get("index", i + 1))}</td><td>{inline(c.get("check", ""))}</td><td>{inline(c.get("source", ""))}</td>'
        f'<td>{esc(c.get("owner", ""))}</td><td>{"☑" if c.get("done") else "☐"}</td></tr>'
        for i, c in enumerate(p.get("qa_readiness_checklist") or []))
    return ('<table><thead><tr><th>#</th><th>Check</th><th>Source</th><th>Owner</th><th>Done</th></tr></thead>'
            f'<tbody>{rows}</tbody></table>')


def html_handoff(p: dict) -> str:
    label = p["classifications"]["readiness"]["human_label"]
    items = open_items(p)
    items_html = f' <strong>Open items:</strong> {esc(", ".join(items))}.' if items else ""
    note = p["report"].get("handoff_note")
    parts = ['<div class="tc-handoff"><h3>Next step — draft test cases</h3>',
             '<p>Handoff to <strong>The Creator</strong> (this report does not contain test cases).'
             + (" At epic scope, run The Creator per child after that child's own Reviewer scan — not against this report." if is_epic(p) else "")
             + '</p>',
             f'<p><strong>Readiness:</strong> {esc(label)}.{items_html}</p>',
             f'<p>{esc(gate_line(p))}</p>']
    if note:
        parts.append(f'<p>{inline(note)}</p>')
    if not is_epic(p) and p["gate"]["status"] == "PASS_WITH_WARNINGS":
        parts.append('<div class="tc-options">'
                     '<div class="tc-opt a"><div class="lbl">Option A — now</div>Run The Creator today → preliminary draft; open items above travel with it as assumptions to confirm before Xray import.</div>'
                     '<div class="tc-opt b"><div class="lbl">Option B — after rescan</div>Resolve the High questions first, rescan, then run The Creator → fewer assumptions.</div></div>')
    parts.append('</div>')
    return "".join(parts)


def render_html(p: dict) -> str:
    key = p["scope"]["value"]
    req = (p.get("requirements") or [{}])[0]
    itype = issue_type(p)
    date = p["generated_at"][:10]
    cls = p["classifications"]
    readiness = cls["readiness"]
    strip_cls, icon = STRIP_CLASS[readiness["value"]]
    link = f' · <a href="{esc(req["url"])}">View in Jira ↗</a>' if req.get("url") else ""
    status = f' · {esc(req["status"])}' if req.get("status") else ""
    f_line, q_line = counts_line(p)
    kids_line = f' · <strong>{plural(len(children(p)), "child")}</strong> (full inventory, not a sample)' if is_epic(p) else ""
    risk = cls["risk"]
    tags = ", ".join(risk.get("rationale_tags") or [])
    auto = cls["automation_candidate"]
    auto_val = auto["value"] if isinstance(auto, dict) else auto

    def kpi(label, value, dot, note=""):
        n = f' <span class="kpi-note">— {esc(note)}</span>' if note else ""
        return f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value"><span class="dot {dot}"></span>{esc(value)}{n}</div></div>'

    r = p["report"]
    tier2 = [
        section("sec-findings", f"{'Epic-scope' if is_epic(p) else 'Testability'} findings", str(len(p.get("findings", []))), html_findings(p), True),
        section("sec-questions", "Clarification questions", str(len(p.get("questions", []))), html_questions(p), True),
        section("sec-risks", "Known risks & suggested testing focus", f'{len(r["risks"])} + {len(r["testing_focus"])}', html_risks(p), True),
    ]
    if is_epic(p):
        tier2.append(section("sec-children", "Child inventory & status mix", f"{len(children(p))} — full set", html_children(p), True))

    tier3 = [
        section("sec-datasources", "Data sources",
                f'{sum(1 for s in p["context_loaded"] if s["status"] == "analyzed")} analyzed · '
                f'{sum(1 for s in p["context_loaded"] if s["status"] in ("unavailable", "failed"))} unavailable or failed',
                html_datasources(p), False),
        section("sec-facts", "Information identified", str(len(r["facts"])),
                sourced(r["facts"]) if r["facts"] else empty("No facts recorded."), False),
    ]
    if r.get("design_observations"):
        tier3.append(section("sec-figma", "Design observations (Figma)", str(len(r["design_observations"])),
                             '<p class="src">Design reference only — not verified on build.</p>' + sourced(r["design_observations"]), False))
    tier3.append(section("sec-notstated", not_stated_heading(p), str(len(r["not_stated"])),
                         "".join(f'<p class="fact">{inline(t)}</p>' for t in r["not_stated"]) or empty("Nothing material was left unstated."), False))
    if not is_epic(p):
        tier3.append(section("sec-epic", "Epic context", str(len(r.get("epic_context") or [])),
                             sourced(r.get("epic_context") or []) or empty("No parent Epic, or nothing relevant found in it."), False))
    if p.get("qa_readiness_checklist"):
        tier3.append(section("sec-checklist", "QA readiness checklist (preliminary)", str(len(p["qa_readiness_checklist"])), html_checklist(p), False))

    total = sum(1 for f in p.get("findings", []) if has_decision(f)) + sum(1 for q in p.get("questions", []) if has_decision(q))
    script = SCRIPT % {"total": total, "run_id": json.dumps(p["run_id"]), "key": json.dumps(key),
                       "version": json.dumps(p["schema_version"]), "filename": json.dumps(f"{key}-review-decisions.json")}

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Requirement Review — {esc(key)} ({esc(itype)})</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<div class="header-card">
  <div class="header-top"><h1><span class="mono">{esc(key)}</span> — {inline(req.get("summary", ""))} <span class="badge">{esc(itype)}</span></h1></div>
  <div class="header-meta">{esc(scan_label(p))} — {esc(date)}{status}{link} · schema {esc(p["schema_version"])} · run_id {esc(p["run_id"])}</div>
  <div class="summary-line"><strong>{esc(f_line.split(" — ")[0])}</strong> — {esc(f_line.split(" — ")[1])} · <strong>{esc(q_line.split(" — ")[0])}</strong>{(" — " + esc(q_line.split(" — ")[1])) if " — " in q_line else ""}{kids_line}</div>
</div>
<div class="readiness-strip {strip_cls}">
  <div class="r-kicker">{esc(readiness_heading(p))}</div>
  <div class="r-label">{icon} {esc(readiness["human_label"])}</div>
  <div class="r-sub">{esc(lead_sentence(p) + " " if lead_sentence(p) else "")}{inline(r["readiness_line"])} This supports shift-left preparation — it does not approve or reject the {esc(itype.lower())}.</div>
</div>
<div class="gate-line">{esc(gate_line(p))}</div>
<div class="kpis">
  {kpi("Testability", cls["testability"], LEVEL_DOT[cls["testability"]])}
  {kpi("Test scope confidence", cls["test_scope_confidence"], LEVEL_DOT[cls["test_scope_confidence"]])}
  {kpi("Risk", risk["level"], RISK_DOT[risk["level"]], tags)}
  {kpi("Automation candidate", auto_val, AUTOMATION_DOT.get(auto_val, "slate"))}
</div>
<div class="tier-label">Why — findings, questions, risk{", children" if is_epic(p) else ""}</div>
{"".join(tier2)}
{html_batch(p) if is_epic(p) else ""}
<div class="tier-label">Reference &amp; audit detail</div>
{"".join(tier3)}
<div class="tier-label">Recommended next action</div>
<p class="fact">{inline(r["next_action"])}</p>
{html_handoff(p)}
<div class="export-bar"><div class="status" id="decision-status">0 of {total} items decided</div>
<button onclick="exportDecisions()">Export decisions (.json)</button></div>
<p class="footer-note">Generated by The Reviewer · read-only on Jira · this report supports shift-left preparation — it does not approve or reject the requirement · run_id {esc(p["run_id"])}</p>
</div>
<script>{script}</script>
</body>
</html>
"""


# --------------------------------------------------------------------------- Markdown

def render_md(p: dict) -> str:
    key = p["scope"]["value"]
    req = (p.get("requirements") or [{}])[0]
    itype = issue_type(p)
    cls = p["classifications"]
    r = p["report"]
    risk = cls["risk"]
    auto = cls["automation_candidate"]
    auto_val = auto["value"] if isinstance(auto, dict) else auto
    analyzed = [s["source"] for s in p["context_loaded"] if s["status"] == "analyzed"]
    missing = [f'{s["source"]} ({s.get("reason", "no reason recorded")})' for s in p["context_loaded"] if s["status"] in ("unavailable", "failed")]
    title = f' — [{key}]({req["url"]})' if req.get("url") else f" — {key}"
    L = [
        f"# Requirement Review — {p['run_id']}", "",
        f"**Scanned:** {scan_label(p)} — {p['generated_at'][:10]}  ",
        f"**Scope:** {itype}{title} — \"{md_inline(req.get('summary', ''))}\"" + (f" · Status: {req['status']}" if req.get("status") else "") + "  ",
        f"**Product:** {p['product'].get('name', p['product']['id'])} · schema {p['schema_version']}  ",
        f"**Data sources analyzed:** {' · '.join(analyzed) or 'none'}  ",
        f"**Data sources unavailable or failed:** {'; '.join(missing) or 'none'}", "",
        f"**{readiness_heading(p)}:** {cls['readiness']['human_label']}  ",
        f"_{md_inline((lead_sentence(p) + ' ') if lead_sentence(p) else '')}{md_inline(r['readiness_line'])}_  ",
        gate_line(p), "",
        f"**Testability:** {cls['testability']} · **Test scope confidence:** {cls['test_scope_confidence']} · "
        f"**Risk:** {risk['level']}" + (f" ({', '.join(risk.get('rationale_tags') or [])})" if risk.get("rationale_tags") else "")
        + f" · **Automation candidate:** {auto_val}", "",
        "## Findings", "",
    ]
    fs = sorted_findings(p)
    if fs:
        L += ["| ID | Severity | Checklist ref | Finding | Testing impact | Owner |", "|----|----------|---------------|---------|----------------|-------|"]
        L += [f"| {f['finding_id']} | {f['severity']} | {f['checklist_ref']} | {md_inline(f['finding_summary'])} | "
              f"{md_inline(f.get('testing_impact', '')) or '—'} | {f.get('owner_hint', '—')} |" for f in fs]
    else:
        L.append("_No findings._")
    L += ["", "## Clarification questions", ""]
    groups = grouped_questions(p)
    if not groups:
        L.append("_No clarification questions._")
    for topic, qs in groups:
        L += [f"### {topic}", ""]
        for q in qs:
            L += [f"#### {q['question_id']}. {md_inline(q['question'])}",
                  f"- Context: {md_inline(q.get('context', '—'))} · Source: {md_inline(q.get('source', '—'))} · Priority: {q['priority']} · "
                  f"Unblocks: {', '.join(q.get('unblocks') or []) or '—'} · Owner: {q.get('owner_hint', '—')}", ""]
    L += [f"## {not_stated_heading(p)}", ""]
    L += [f"- {md_inline(t)}" for t in r["not_stated"]] or ["_Nothing material was left unstated._"]
    L += ["", "## Known or suspected risks", ""]
    L += [f"- {md_inline(x['text'])}" + (f" *(Source: {md_inline(x['source'])})*" if x.get("source") else "") for x in r["risks"]] or ["_No risks identified._"]
    L += ["", "## Suggested testing focus", ""]
    L += [f"- {md_inline(t['text'])}" + (f" *(waits on: {', '.join(t['blocks'])})*" if t.get("blocks") else "") for t in r["testing_focus"]] or ["_No testing focus suggested._"]
    L += ["", "## Information identified", ""]
    L += [f"- {md_inline(x['text'])}" + (f" *(Source: {md_inline(x['source'])})*" if x.get("source") else "") for x in r["facts"]] or ["_No facts recorded._"]
    if r.get("design_observations"):
        L += ["", "## Design observations (Figma)", "", "_Design reference only — not verified on build._", ""]
        L += [f"- {md_inline(x['text'])}" + (f" *(Source: {md_inline(x['source'])})*" if x.get("source") else "") for x in r["design_observations"]]
    if not is_epic(p):
        L += ["", "## Epic context", ""]
        L += [f"- {md_inline(x['text'])}" + (f" *(Source: {md_inline(x['source'])})*" if x.get("source") else "") for x in r.get("epic_context") or []] \
            or ["_No parent Epic, or nothing relevant found in it._"]
    if p.get("qa_readiness_checklist"):
        L += ["", "## QA readiness checklist (preliminary)", "", "| # | Check | Source | Owner | Done |", "|---|-------|--------|-------|------|"]
        L += [f"| {c.get('index', i + 1)} | {md_inline(c.get('check', ''))} | {md_inline(c.get('source', ''))} | {c.get('owner', '')} | {'☑' if c.get('done') else '☐'} |"
              for i, c in enumerate(p["qa_readiness_checklist"])]
    if is_epic(p):
        kids = children(p)
        mix = status_mix(p)
        L += ["", "## Child inventory & status mix", "",
              f"**Full inventory — {plural(len(kids), 'child')}, paginated to `isLast`, never a sample.**  ",
              "**Status mix:** " + (" · ".join(f"{s} — {n}" for s, n in mix.items()) or "no children yet"), ""]
        if kids:
            L += ["| Key | Type | Status | Summary | Content |", "|-----|------|--------|---------|---------|"]
            L += [f"| {c['key']} | {c.get('type', '')} | {c.get('status', '')} | {md_inline(c.get('summary', ''))} | {c.get('content_source', '')} |" for c in kids]
        keys = (p.get("rollup") or {}).get("recommended_batch_keys") or []
        L += ["", "## Epic batch handoff", ""]
        if r.get("batch_rationale"):
            L += [md_inline(r["batch_rationale"]), ""]
        if keys:
            L += ["**Batch (every non-Canceled child, in scan order):** " + " · ".join(f"`{k}`" for k in keys), "",
                  f"- `confirm batch` — scan all {plural(len(keys), 'child')} in the order shown, 8 at a time",
                  "- `--batch keys <comma-separated>` — scan a specific subset", "",
                  "The batch does not run automatically."]
        else:
            L.append("The epic has no linked child issues yet — there is nothing to batch-scan.")
    L += ["", "## Recommended next action", "", md_inline(r["next_action"]), "",
          "---", "_This review supports shift-left preparation. It does not approve or reject the requirement._", ""]
    return "\n".join(L)


# --------------------------------------------------------------------------- Jira comments (PRF-22)

def wiki(text) -> str:
    """Single-line wiki text; braces and pipes would be read as macros/tables."""
    return re.sub(r"\s+", " ", str(text or "")).replace("{", "(").replace("}", ")").replace("|", "/").strip()


def jira_questions(p: dict, high_only: bool) -> list:
    L, n = [], 0
    for topic, qs in grouped_questions(p):
        qs = [q for q in qs if q.get("status", "open") == "open" and (q["priority"] == "High" or not high_only)]
        if high_only:
            qs = qs[: max(0, 5 - n)]
        if not qs:
            continue
        n += len(qs)
        L.append(f"*{topic}*")
        L += [f"# {wiki(q['question'])} _— for {q.get('owner_hint', 'PM')}_" for q in qs]
    return L


def render_jira_full(p: dict) -> str:
    cls, r = p["classifications"], p["report"]
    risk = cls["risk"]
    auto = cls["automation_candidate"]
    auto_val = auto["value"] if isinstance(auto, dict) else auto
    rationale = ", ".join(risk.get("rationale_tags") or []) or "no rationale recorded"
    analyzed = [s["source"] for s in p["context_loaded"] if s["status"] == "analyzed"]
    top = [f for f in sorted_findings(p) if f.get("status", "open") == "open"][:5]
    L = [f"h3. Requirement Review — {p['scope']['value']}", "",
         "_Based on the current content, here is a collaborative review to support early alignment._", "",
         "----",
         f"*Testability:* {cls['testability']}    *Test scope confidence:* {cls['test_scope_confidence']}",
         f"*Risk level:* {risk['level']} — {wiki(rationale)}    *{readiness_heading(p)}:* {cls['readiness']['human_label']}",
         f"*Automation candidate:* {auto_val}", "",
         f"*Data reviewed:* {wiki(', '.join(analyzed) or 'none')}", "",
         "h4. Top findings (testing impact)"]
    L += [f"* {SEVERITY_LABEL[f['severity']]} — {wiki(f['finding_summary']).rstrip('.')}: {wiki(f.get('testing_impact') or 'not recorded')}"
          for f in top] or ["* No open findings."]
    L += ["", "h4. Clarification questions"]
    L += jira_questions(p, high_only=False) or ["_No open clarification questions._"]
    L += ["----", "_This review supports shift-left preparation — it does not approve or reject the requirement._", ""]
    return "\n".join(L)


def render_jira_short(p: dict) -> str:
    L = [f"h3. Requirement Review (summary) — {p['scope']['value']}", "",
         f"*{readiness_heading(p)}:* {p['classifications']['readiness']['human_label']}", "",
         "h4. Priority clarification needed"]
    L += jira_questions(p, high_only=True) or ["_No High priority questions are open._"]
    L += ["----", ""]
    return "\n".join(L)


# --------------------------------------------------------------------------- main

def validate(p: dict) -> list:
    if p.get("schema_version") != SUPPORTED_VERSION or p.get("payload_version") != SUPPORTED_VERSION:
        return [f"payload is schema {p.get('schema_version')!r}; this renderer only renders {SUPPORTED_VERSION!r}. "
                f"Re-run the scan to produce a {SUPPORTED_VERSION} payload (PRF-20)."]
    try:
        import jsonschema
    except ImportError:
        print("warning: jsonschema not installed — schema validation skipped", file=sys.stderr)
        return []
    schema = json.loads(SCHEMA_PATH.read_text())
    validator = jsonschema.validators.validator_for(schema)(schema)
    return [f"{'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message}" for e in validator.iter_errors(p)]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("payload", type=Path)
    ap.add_argument("--out-dir", type=Path, help="defaults to the payload's directory")
    ap.add_argument("--md", type=Path, help="explicit Markdown output path (overrides --out-dir)")
    ap.add_argument("--html", type=Path, help="explicit HTML output path (overrides --out-dir)")
    ap.add_argument("--strict", action="store_true", help="exit 2 if the wording lint finds problems")
    args = ap.parse_args()

    p = json.loads(args.payload.read_text())
    errors = validate(p)
    if errors:
        print("payload invalid — nothing rendered:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    problems = lint(p)
    if problems:
        for msg in problems:
            print(f"lint: {msg}", file=sys.stderr)
        if args.strict:
            print("strict: reports not written — fix the payload and re-run.", file=sys.stderr)
            return 2

    out = args.out_dir or args.payload.parent
    md_path = args.md or out / "review-report.md"
    jira_prefix = "" if md_path.name == "review-report.md" else md_path.name.split(".")[0] + "."
    targets = [(md_path, render_md), (args.html or out / "review-report.html", render_html),
               (md_path.parent / f"{jira_prefix}jira-comment-full.txt", render_jira_full),
               (md_path.parent / f"{jira_prefix}jira-comment-short.txt", render_jira_short)]
    for path, render in targets:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(p))
        print(f"wrote {path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
