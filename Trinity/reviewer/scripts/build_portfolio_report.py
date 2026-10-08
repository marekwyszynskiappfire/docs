#!/usr/bin/env python3
"""Build Reviewer portfolio bundle (Profile B) for a multi-Epic run folder.

Reads per-epic review-payload.json under {run_dir}/{KEY}/, copies shareable epic
reports into {run_dir}/portfolio/epics/{KEY}/, and generates data/report-data.js.

Usage:
    python3 build_portfolio_report.py --run-dir PATH/TO/portfolio_run \\
        [--title "Portfolio title"] [--jql "..."] [--subtitle "..."]

Static shell is copied from ../portfolio-report-template/. Only report-data.js is
generated data; do not hand-edit rendered output.

Exit 0 on success, 1 if fewer than 2 epics or missing payloads.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = SCRIPT_DIR.parent / "portfolio-report-template"
JIRA_BROWSE = "https://appfire.atlassian.net/browse/"
JIRA_ISSUES = "https://appfire.atlassian.net/issues/?jql="

COPY_NAMES = (
    "review-report.html",
    "review-report.md",
    "review-payload.json",
    "jira-comment-full.txt",
    "jira-comment-short.txt",
)

THEME_LABELS = {
    "behavioral_gap": "Ambiguous or undefined behavior",
    "epic_lifecycle": "Epic / child backlog gaps",
    "acceptance_criteria": "Missing or weak acceptance criteria",
    "open_questions": "Unresolved open questions",
    "data_sensitivity": "Security, privacy, or data-handling gaps",
    "traceability": "Weak traceability (PRD, design, links)",
    "scope": "Unclear scope boundaries",
    "testability": "Testability blockers",
    "template_compliance": "Template or process compliance gaps",
}

THEME_EXPLANATIONS = {
    "behavioral_gap": (
        "Requirements do not pin down concrete behavior: outcomes, errors, limits, and edge cases "
        "are missing or contradictory — QA cannot define expected results yet."
    ),
    "epic_lifecycle": (
        "Backlog or delivery picture is incomplete: title-only children, missing stories for the "
        "epic journey, or lifecycle fields still open."
    ),
    "acceptance_criteria": (
        "No testable epic-level or rolled-up acceptance criteria — success is narrative rather "
        "than verifiable (checklist A3)."
    ),
    "open_questions": (
        "Explicit clarification questions remain that block decisions on rollout, scope, or "
        "dependencies."
    ),
    "data_sensitivity": (
        "Security, privacy, or compliance handling is mentioned but not specified enough for "
        "safe test design."
    ),
    "traceability": (
        "Jira, Confluence, Figma, or child links are missing, broken, or inconsistent — no "
        "single authoritative spec."
    ),
    "scope": (
        "In/out of release or Q4 slice is unclear, or parallel work blurs what QA should sign off on."
    ),
    "testability": (
        "Intent may be clear but verification is not: missing observability, data setup, or "
        "repeatable pass/fail signals."
    ),
    "template_compliance": (
        "Requirement shape or mandatory fields do not match the expected template — hygiene gaps "
        "that hide missing content."
    ),
}

THEME_COLORS = {
    "behavioral_gap": "#f43f5e",
    "epic_lifecycle": "#f59e0b",
    "acceptance_criteria": "#8b5cf6",
    "open_questions": "#3b82f6",
    "data_sensitivity": "#ec4899",
    "traceability": "#06b6d4",
    "scope": "#10b981",
    "testability": "#64748b",
    "template_compliance": "#a855f7",
}

READINESS_SORT = {
    "Ready to build tests": 0,
    "Needs clarification before test design": 1,
    "Needs clarification before scope can be tested": 2,
}


def epic_numeric_key(key: str) -> int:
    m = re.search(r"-(\d+)$", key)
    return int(m.group(1)) if m else 0


def discover_epic_keys(run_dir: Path) -> list[str]:
    keys = []
    for child in run_dir.iterdir():
        if not child.is_dir():
            continue
        name = child.name
        if name.startswith("_") or name in ("portfolio", "scripts"):
            continue
        if not re.match(r"^[A-Z][A-Z0-9]+-\d+$", name):
            continue
        payload = child / "review-payload.json"
        if payload.is_file():
            keys.append(name)
    keys.sort(key=epic_numeric_key)
    return keys


GAP_FLAG_DEFS = (
    ("missing_ac", "Missing / weak AC", {"acceptance_criteria"}, {"A3"}),
    ("backlog_gaps", "Child / backlog gaps", {"epic_lifecycle"}, {"B12", "C1", "C2"}),
    ("open_questions", "Open questions in text", {"open_questions"}, {"A6", "A8"}),
    ("traceability", "PRD / link traceability", {"traceability"}, {"A5", "A8"}),
    ("scope_unclear", "Scope unclear", {"scope"}, {"A2", "A4"}),
)


def compute_gap_flags(findings: list, data: dict) -> list[dict]:
    cats = {x.get("category") for x in findings if x.get("category")}
    refs = {x.get("checklist_ref") for x in findings if x.get("checklist_ref")}
    flags = []
    for fid, label, cat_set, ref_set in GAP_FLAG_DEFS:
        if cats & cat_set or refs & ref_set:
            flags.append({"id": fid, "label": label})
    inv = (data.get("rollup") or {}).get("epic_child_inventory") or []
    if inv:
        title_only = sum(1 for c in inv if c.get("content_source") == "title_only")
        if title_only == len(inv):
            flags.append({"id": "all_title_only", "label": "All children title-only"})
        elif title_only > 0:
            flags.append({"id": "some_title_only", "label": f"{title_only} title-only children"})
    if not inv and is_epic_payload(data):
        flags.append({"id": "no_children", "label": "No child issues"})
    # dedupe by id
    seen = set()
    out = []
    for f in flags:
        if f["id"] in seen:
            continue
        seen.add(f["id"])
        out.append(f)
    return out


def is_epic_payload(data: dict) -> bool:
    return (data.get("scope") or {}).get("type") == "epic"


def creator_jql_for_keys(keys: list[str]) -> str:
    if not keys:
        return "key = IMPOSSIBLE-0"
    return "key in (" + ", ".join(keys) + ") ORDER BY key ASC"


def default_creator_include(fit: str) -> bool:
    return fit != "not_fit"


def load_row(run_dir: Path, key: str) -> dict:
    with (run_dir / key / "review-payload.json").open(encoding="utf-8") as f:
        data = json.load(f)
    req = (data.get("requirements") or [{}])[0]
    rep = data.get("report") or {}
    cls = data.get("classifications") or {}
    readiness = cls.get("readiness") or {}
    findings = data.get("findings") or []
    questions = data.get("questions") or []
    high = sum(1 for x in findings if x.get("severity") == "HIGH")
    med = sum(1 for x in findings if x.get("severity") == "MEDIUM")
    low = sum(1 for x in findings if x.get("severity") == "LOW")
    cats = sorted({x["category"] for x in findings if x.get("category")})
    refs = sorted({x["checklist_ref"] for x in findings if x.get("checklist_ref")})
    label = readiness.get("human_label") or "Needs clarification before test design"
    fit = rep.get("qa_planning_fit") or "fit"
    target = req.get("planning_target_date")
    gap_flags = compute_gap_flags(findings, data)
    return {
        "key": key,
        "keyNum": epic_numeric_key(key),
        "summary": req.get("summary") or key,
        "url": req.get("url") or f"{JIRA_BROWSE}{key}",
        "reportPath": f"epics/{key}/review-report.html",
        "planningTargetDate": target,
        "noPlanningDate": not target,
        "qaPlanningFit": fit,
        "creatorIncludeDefault": default_creator_include(fit),
        "readinessLabel": label,
        "readinessSort": READINESS_SORT.get(label, 9),
        "readinessValue": readiness.get("value"),
        "gate": (data.get("gate") or {}).get("status", "PASS_WITH_WARNINGS"),
        "highCount": high,
        "mediumCount": med,
        "lowCount": low,
        "findingCount": len(findings),
        "questionCount": len(questions),
        "categories": cats,
        "checklistRefs": refs,
        "gapFlags": gap_flags,
        "gapFlagCount": len(gap_flags),
        "multiGap": len(gap_flags) >= 2,
        "findings": findings,
    }


def copy_epic_reports(run_dir: Path, portfolio: Path, keys: list[str]) -> None:
    epics_dir = portfolio / "epics"
    epics_dir.mkdir(parents=True, exist_ok=True)
    for key in keys:
        src = run_dir / key
        dst = epics_dir / key
        dst.mkdir(parents=True, exist_ok=True)
        for name in COPY_NAMES:
            sp = src / name
            if sp.is_file():
                shutil.copy2(sp, dst / name)


def copy_template(portfolio: Path) -> None:
    if not TEMPLATE_DIR.is_dir():
        raise SystemExit(f"Missing template dir: {TEMPLATE_DIR}")
    portfolio.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TEMPLATE_DIR / "index.html", portfolio / "index.html")
    assets = portfolio / "assets"
    assets.mkdir(exist_ok=True)
    shutil.copy2(TEMPLATE_DIR / "assets" / "styles.css", assets / "styles.css")
    shutil.copy2(TEMPLATE_DIR / "assets" / "app.js", assets / "app.js")
    readme_src = TEMPLATE_DIR / "README.md"
    if readme_src.is_file():
        shutil.copy2(readme_src, portfolio / "README.md")


def js_embed(obj: dict) -> str:
    raw = json.dumps(obj, ensure_ascii=True, indent=2)
    raw = raw.replace("</", "<\\/")
    return f"window.REPORT_DATA = {raw};\n"


def build_filters(rows: list[dict], cat_counts: dict[str, int]) -> list[dict]:
    filters = [
        {"id": "planning-not-fit", "label": "Not suitable for test design", "predicate": "field", "field": "qaPlanningFit", "value": "not_fit"},
        {"id": "planning-provisional", "label": "Provisional test design fit", "predicate": "field", "field": "qaPlanningFit", "value": "provisional"},
        {"id": "no-planning-date", "label": "No planning date in Jira", "predicate": "flag", "field": "noPlanningDate"},
        {"id": "readiness-ready", "label": "Ready to build tests", "predicate": "field", "field": "readinessLabel", "value": "Ready to build tests"},
        {"id": "readiness-scope", "label": "Clarify before scope", "predicate": "field", "field": "readinessLabel", "value": "Needs clarification before scope can be tested"},
        {"id": "has-high", "label": "Has HIGH findings", "predicate": "minHigh", "min": 1},
        {"id": "multi-gap", "label": "Multiple gap types", "predicate": "flag", "field": "multiGap"},
        {"id": "creator-default", "label": "Default: include for Creator", "predicate": "flag", "field": "creatorIncludeDefault"},
    ]
    for cat in sorted(cat_counts.keys(), key=lambda c: -cat_counts[c]):
        filters.append({
            "id": f"cat-{cat}",
            "label": THEME_LABELS.get(cat, cat.replace("_", " ")),
            "predicate": "category",
            "category": cat,
        })
    return filters


def synthesis_text(rows: list[dict], cat_counts: dict[str, int], readiness_counts: dict[str, int]) -> str:
    total_f = sum(cat_counts.values())
    top = sorted(cat_counts.items(), key=lambda x: -x[1])[:3]
    top_names = [THEME_LABELS.get(c, c) for c, _ in top]
    ready = readiness_counts.get("Ready to build tests", 0)
    not_fit = sum(1 for r in rows if r["qaPlanningFit"] == "not_fit")
    parts = [
        f"{len(rows)} epics synthesised with {total_f} findings across the portfolio.",
    ]
    if top_names:
        parts.append(f"Dominant gap themes: {', '.join(top_names)}.")
    parts.append(
        f"{ready} epic(s) labelled ready to build tests; {not_fit} not suitable for test design until scope is written."
    )
    parts.append("Epic mode gates are PASS_WITH_WARNINGS at most — use readiness and test design suitability for scheduling.")
    return " ".join(parts)


def write_creator_handoff(
    portfolio: Path,
    run_id: str,
    source_jql: str,
    rows: list[dict],
) -> None:
    included = [r["key"] for r in rows if r.get("creatorIncludeDefault")]
    excluded = [r["key"] for r in rows if not r.get("creatorIncludeDefault")]
    jql = creator_jql_for_keys(included)
    url = JIRA_ISSUES + quote(jql)
    payload = {
        "schema_version": "1.0",
        "run_id": run_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_jql": source_jql,
        "creator_jql": jql,
        "creator_jql_url": url,
        "included_epics": included,
        "excluded_by_default": excluded,
        "note": (
            "Defaults exclude qa_planning_fit=not_fit. Toggle epics in portfolio/index.html; "
            "use Export creator handoff to refresh this file after changes."
        ),
    }
    data_dir = portfolio / "data"
    data_dir.mkdir(exist_ok=True)
    (data_dir / "creator-handoff.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    md = f"""# Creator handoff — {run_id}

Generated from the Reviewer portfolio (default selection). Open `index.html` to toggle epics, then **Export creator handoff**.

## JQL for The Creator

```
{jql}
```

**Jira search URL:** {url}

## Included by default ({len(included)})

{", ".join(included) if included else "—"}

## Excluded by default — not suitable for test design ({len(excluded)})

{", ".join(excluded) if excluded else "—"}

## Source portfolio JQL

```
{source_jql or "(not recorded)"}
```
"""
    (portfolio / "creator-handoff.md").write_text(md, encoding="utf-8")


def write_portfolio_readme(portfolio: Path, run_dir: Path, run_id: str) -> None:
    text = f"""# Reviewer portfolio report

Open **`index.html`** in a browser (double-click). Zip this entire `portfolio/` folder to share.

**Run folder:** `{run_dir.name}`  
**Regenerate:**

```bash
python3 "{SCRIPT_DIR / "build_portfolio_report.py"}" --run-dir "{run_dir}"
```

**Guidelines:** [`../../../shared/html-report-guidelines.md`](../../../shared/html-report-guidelines.md) (Profile B).

Per-epic HTML copies: `epics/{{KEY}}/review-report.html`

**Creator handoff:** `creator-handoff.md` and `data/creator-handoff.json` (toggle epics in the UI, then export).
"""
    (portfolio / "README.md").write_text(text, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Build Reviewer portfolio Profile B bundle")
    ap.add_argument("--run-dir", type=Path, required=True, help="Portfolio run root (contains ONE-* folders)")
    ap.add_argument("--title", default="", help="Page title")
    ap.add_argument("--subtitle", default="", help="Meta subtitle line")
    ap.add_argument("--jql", default="", help="Source JQL (for meta only)")
    args = ap.parse_args()

    run_dir = args.run_dir.resolve()
    if not run_dir.is_dir():
        raise SystemExit(f"Not a directory: {run_dir}")

    keys = discover_epic_keys(run_dir)
    if len(keys) < 2:
        raise SystemExit(f"Need at least 2 epic payloads under {run_dir}; found {len(keys)}")

    rows = [load_row(run_dir, k) for k in keys]
    cat_counts: dict[str, int] = defaultdict(int)
    cats_epic: dict[str, set[str]] = defaultdict(set)
    readiness_counts: dict[str, int] = defaultdict(int)
    for row in rows:
        readiness_counts[row["readinessLabel"]] += 1
        for fn in row["findings"]:
            c = fn.get("category")
            if not c:
                continue
            cat_counts[c] += 1
            cats_epic[c].add(row["key"])

    themes = []
    for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
        themes.append({
            "id": cat,
            "label": THEME_LABELS.get(cat, cat),
            "explanation": THEME_EXPLANATIONS.get(cat, ""),
            "color": THEME_COLORS.get(cat, "#94a3b8"),
            "findingCount": count,
            "epicKeys": sorted(cats_epic[cat], key=epic_numeric_key),
        })

    run_id = run_dir.name
    title = args.title or f"Reviewer portfolio — {run_id}"
    subtitle = args.subtitle or (
        f"{len(keys)} epics · run {run_id} · "
        f"{sum(cat_counts.values())} findings · generated "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
    )

    portfolio = run_dir / "portfolio"
    copy_template(portfolio)
    copy_epic_reports(run_dir, portfolio, keys)

    report = {
        "meta": {
            "title": title,
            "subtitle": subtitle,
            "runId": run_id,
            "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "jql": args.jql,
            "jiraBase": JIRA_BROWSE,
            "jiraIssuesJqlBase": JIRA_ISSUES,
            "epicCount": len(keys),
            "synthesis": synthesis_text(rows, dict(cat_counts), dict(readiness_counts)),
            "note": (
                "Combined view for a multi-Epic Reviewer run. Each epic has its own Profile A "
                "review-report.html under epics/{KEY}/. Filters and themes are derived from "
                "review-payload.json only — not hand-authored."
            ),
        },
        "themes": themes,
        "filters": build_filters(rows, dict(cat_counts)),
        "rows": [{k: v for k, v in r.items() if k != "findings"} for r in rows],
    }

    data_dir = portfolio / "data"
    data_dir.mkdir(exist_ok=True)
    (data_dir / "report-data.js").write_text(js_embed(report), encoding="utf-8")
    write_creator_handoff(portfolio, run_id, args.jql, rows)
    (portfolio / "portfolio-meta.json").write_text(
        json.dumps(
            {
                "epic_count": len(keys),
                "total_findings": sum(cat_counts.values()),
                "category_counts": dict(sorted(cat_counts.items(), key=lambda x: -x[1])),
                "readiness": dict(readiness_counts),
                "qa_planning_fit": {
                    "fit": sum(1 for r in rows if r["qaPlanningFit"] == "fit"),
                    "provisional": sum(1 for r in rows if r["qaPlanningFit"] == "provisional"),
                    "not_fit": sum(1 for r in rows if r["qaPlanningFit"] == "not_fit"),
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    write_portfolio_readme(portfolio, run_dir, run_id)

    print(f"Portfolio bundle: {portfolio / 'index.html'}")
    print(f"Epics copied: {len(keys)} → {portfolio / 'epics'}")


if __name__ == "__main__":
    main()
