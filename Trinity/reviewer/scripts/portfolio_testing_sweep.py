#!/usr/bin/env python3
"""Jira REST portfolio sweep → lightweight payloads + testing PDF (NOT full Reviewer).

**Do not use when the operator asked for a review** — run `trinity-reviewer` + MCP gather instead
(see `.cursor/rules/trinity-reviewer-mandatory.mdc`).

Uses Trinity/studio/.env (JIRA_*). No Confluence body, child remotelinks, comments, or Figma.

  python3 Trinity/reviewer/scripts/portfolio_testing_sweep.py \\
    --config Trinity/reviewer/config/runs/q4-backlog.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

REPO = Path(__file__).resolve().parents[3]
REVIEWER = REPO / "Trinity" / "reviewer"
RUN_ID = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M")


def load_env() -> None:
    env_path = REPO / "Trinity" / "studio" / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


def jira_client() -> tuple[str, httpx.BasicAuth]:
    base = os.environ["JIRA_BASE_URL"].rstrip("/")
    auth = httpx.BasicAuth(os.environ["JIRA_EMAIL"], os.environ["JIRA_API_TOKEN"])
    return base, auth


def adf_to_text(node: Any) -> str:
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "".join(adf_to_text(n) for n in node)
    if not isinstance(node, dict):
        return ""
    t = node.get("type")
    if t == "text":
        return node.get("text", "")
    if t == "hardBreak":
        return "\n"
    return adf_to_text(node.get("content"))


def plain_description(fields: dict) -> str:
    desc = fields.get("description")
    if desc is None:
        return ""
    if isinstance(desc, str):
        return desc.strip()
    return adf_to_text(desc).strip()


def fetch_issue(client: httpx.Client, base: str, auth: httpx.BasicAuth, key: str) -> dict:
    r = client.get(
        f"{base}/rest/api/3/issue/{key}",
        auth=auth,
        params={"fields": "summary,status,description,duedate,comment,issuelinks,issuetype"},
    )
    r.raise_for_status()
    return r.json()


def fetch_children(client: httpx.Client, base: str, auth: httpx.BasicAuth, epic_key: str) -> list[dict]:
    jql = f'project = ONE AND (parent = {epic_key} OR "Epic Link" = {epic_key}) ORDER BY rank'
    keys: list[dict] = []
    start = 0
    while True:
        r = client.get(
            f"{base}/rest/api/3/search/jql",
            auth=auth,
            params={
                "jql": jql,
                "startAt": start,
                "maxResults": 50,
                "fields": "summary,status,description,issuetype",
            },
        )
        if r.status_code == 410:
            r = client.get(
                f"{base}/rest/api/3/search",
                auth=auth,
                params={
                    "jql": jql,
                    "startAt": start,
                    "maxResults": 50,
                    "fields": "summary,status,description,issuetype",
                },
            )
        r.raise_for_status()
        data = r.json()
        for issue in data.get("issues", []):
            f = issue.get("fields", {})
            keys.append(
                {
                    "key": issue["key"],
                    "type": (f.get("issuetype") or {}).get("name", "?"),
                    "status": (f.get("status") or {}).get("name", "?"),
                    "summary": f.get("summary", ""),
                    "description_len": len(plain_description(f)),
                }
            )
        if data.get("isLast", True) or not data.get("issues"):
            break
        start += len(data["issues"])
    return keys


def fetch_remote_links(client: httpx.Client, base: str, auth: httpx.BasicAuth, key: str) -> list[str]:
    r = client.get(f"{base}/rest/api/3/issue/{key}/remotelink", auth=auth)
    if r.status_code >= 400:
        return []
    urls = []
    for item in r.json() or []:
        obj = item.get("object") or {}
        url = obj.get("url") or ""
        if url:
            urls.append(url)
    return urls


def fingerprint(epic_key: str, updated: str) -> str:
    h = hashlib.sha256(f"{epic_key}:{updated}".encode()).hexdigest()
    return h[:16]


def build_payload(
    epic_key: str,
    issue: dict,
    children: list[dict],
    remote_urls: list[str],
    run_id: str,
) -> dict[str, Any]:
    fields = issue.get("fields", {})
    summary = fields.get("summary", "")
    status = (fields.get("status") or {}).get("name", "")
    desc = plain_description(fields)
    base_url = os.environ["JIRA_BASE_URL"].rstrip("/")

    findings: list[dict] = []
    questions: list[dict] = []
    not_stated: list[str] = []
    fi = 1
    qi = 1

    def add_finding(sev: str, cat: str, cref: str, summ: str, impact: str) -> str:
        nonlocal fi
        fid = f"RR-{epic_key}-{fi:02d}"
        fi += 1
        findings.append(
            {
                "finding_id": fid,
                "jira_key": epic_key,
                "severity": sev,
                "category": cat,
                "checklist_ref": cref,
                "finding_summary": summ,
                "testing_impact": impact,
                "owner_hint": "PM",
                "source": "jira_description",
                "blocks_test_generation": False,
                "status": "open",
            }
        )
        return fid

    if len(desc) < 80:
        add_finding(
            "HIGH",
            "scope",
            "A2",
            "Epic description is missing or too thin to define test boundaries.",
            "QA cannot scope regression or name pass/fail criteria at epic level.",
        )
        not_stated.append("Clear in-scope / out-of-scope and definition of done for QA.")

    if not children:
        add_finding(
            "HIGH",
            "epic_lifecycle",
            "C1",
            "No child issues linked under this Epic (parent or Epic Link).",
            "No stories to execute tests against; Creator batch has nothing to anchor.",
        )
    else:
        title_only = sum(1 for c in children if c["description_len"] < 40)
        if title_only > len(children) // 2:
            add_finding(
                "HIGH",
                "behavioral_gap",
                "B2",
                f"{title_only}/{len(children)} children lack substantive descriptions.",
                "Cannot derive steps or expected results from titles alone.",
            )
        open_children = sum(1 for c in children if c["status"] not in ("Done", "Closed", "Resolved"))
        if open_children == len(children) and len(children) > 0:
            not_stated.append("Which children are in scope for Q4 QA vs later phases.")

    conf = [u for u in remote_urls if "atlassian.net/wiki" in u or "confluence" in u.lower()]
    if not conf and len(desc) < 200:
        add_finding(
            "MEDIUM",
            "testability",
            "A8",
            "No Confluence remote link on Epic and description is brief.",
            "PRD-level behaviour may be undocumented for testers.",
        )
        not_stated.append("Authoritative PRD or spec link for acceptance criteria.")

    pdf_links = [u for u in remote_urls if ".pdf" in u.lower()]
    if pdf_links:
        not_stated.append("Linked PDF(s) were not fetched in this sweep (Reviewer v1 policy).")

    if findings and any(f["severity"] == "HIGH" for f in findings):
        qa_fit = "provisional"
        fit_line = "Epic can be scheduled for Q4 QA only after gaps below are closed or stories are enriched."
    elif findings:
        qa_fit = "provisional"
        fit_line = "Medium gaps remain; confirm test data and environments before execution."
    else:
        qa_fit = "fit"
        fit_line = "Epic and children are sufficiently described to start test design on linked stories."

    if qa_fit != "fit" and not questions:
        qtext = (
            f"Which child issues under {epic_key} are in scope for Q4 Backlog QA, "
            f"and where is the authoritative acceptance criteria (Confluence or AC field)?"
        )
        questions.append(
            {
                "question_id": f"Q{qi}",
                "topic": "Definition of done",
                "question": qtext,
                "context": (
                    f"Automated sweep of {len(children)} children and Epic text found gaps that block "
                    "confident test design without PO confirmation on scope and documentation."
                ),
                "source": f"{epic_key} gather",
                "priority": "High",
                "status": "open",
                "owner_hint": "PM",
            }
        )

    high_count = sum(1 for f in findings if f["severity"] == "HIGH")
    gate = "PASS_WITH_WARNINGS" if high_count else "PASS"
    if qa_fit == "not_fit":
        gate = "PASS_WITH_WARNINGS"

    # Epic mode: no CRITICAL
    for f in findings:
        if f["severity"] == "CRITICAL":
            f["severity"] = "HIGH"

    child_inventory = [
        {
            "key": c["key"],
            "type": c["type"],
            "status": c["status"],
            "summary": c["summary"][:120],
            "content_source": "description" if c["description_len"] >= 40 else "title_only",
            "recommended_for_batch": c["status"] not in ("Done", "Closed", "Resolved"),
        }
        for c in children[:40]
    ]

    if qa_fit == "fit":
        readiness = {
            "value": "ready_with_clarifications",
            "human_label": "Ready to build tests",
            "blocking_refs": [],
        }
    elif qa_fit == "not_fit":
        readiness = {
            "value": "not_ready",
            "human_label": "Needs clarification before scope can be tested",
            "blocking_refs": [f["finding_id"] for f in findings[:3]],
        }
    else:
        readiness = {
            "value": "needs_clarification_before_scope_lock",
            "human_label": "Needs clarification before test design",
            "blocking_refs": [f["finding_id"] for f in findings if f["severity"] == "HIGH"][:5],
        }

    return {
        "payload_version": "1.1",
        "schema_version": "1.1",
        "run_id": run_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scan_label": "REST sweep",
        "gather_mode": "rest_sweep",
        "host": "cursor",
        "product": {"id": "default", "name": "BigPicture"},
        "scope": {
            "type": "epic",
            "value": epic_key,
            "issue_type": "Epic",
            "is_epic_batch": True,
        },
        "requirement_keys": [epic_key],
        "requirement_fingerprint": fingerprint(epic_key, issue.get("fields", {}).get("updated", run_id)),
        "context_loaded": [
            {
                "source": epic_key,
                "type": "jira_issue",
                "status": "analyzed",
                "detail": f"Summary, status, description ({len(desc)} chars)",
            },
            {
                "source": "Child issues",
                "type": "jira_epic_child",
                "status": "analyzed",
                "detail": f"{len(children)} children via JQL parent/Epic Link",
            },
            {
                "source": "Remote links",
                "type": "jira_link",
                "status": "analyzed" if remote_urls else "not_applicable",
                "detail": f"{len(remote_urls)} link(s)" if remote_urls else "None",
            },
            {
                "source": "Confluence (first hop)",
                "type": "confluence_page",
                "status": "unavailable" if not conf else "analyzed",
                "detail": conf[0] if conf else "No wiki URL on Epic remote links",
                **(
                    {"reason": "Full body not fetched in REST sweep — run full Reviewer for PRD text"}
                    if conf
                    else {}
                ),
            },
        ],
        "requirements": [
            {
                "jira_key": epic_key,
                "summary": summary,
                "issue_type": "Epic",
                "status": status,
                "url": f"{base_url}/browse/{epic_key}",
                "description_excerpt": desc[:500] if desc else "(empty)",
            }
        ],
        "findings": findings,
        "questions": questions,
        "classifications": {
            "testability": "Medium" if findings else "High",
            "test_scope_confidence": "Low" if not children else ("Medium" if findings else "High"),
            "risk": {"level": "Medium", "rationale_tags": ["regression surface"]},
            "automation_candidate": {
                "value": "TBD",
                "rationale": "Decided per child after scope lock.",
                "suggested_level": "TBD",
            },
            "readiness": readiness,
        },
        "rollup": {
            "epic_child_inventory": child_inventory,
            "epic_status_mix": {},
            "recommended_batch_keys": [c["key"] for c in children if c["status"] not in ("Done", "Closed")][:10],
        },
        "gate": {
            "status": gate,
            "critical_unresolved_count": 0,
            "high_unresolved_count": high_count,
            "blocks_test_generation": False,
        },
        "report": {
            "readiness_line": fit_line,
            "facts": [
                {"text": f"Epic status: {status}.", "source": epic_key},
                {"text": f"{len(children)} child issues under Epic.", "source": "Jira search"},
            ],
            "not_stated": not_stated or ["No major documentation gaps detected by REST sweep."],
            "risks": [],
            "testing_focus": [
                {
                    "text": "Prioritize children with descriptions; defer title-only stories until AC is added.",
                    "blocks": [f["finding_id"] for f in findings[:3]],
                }
            ],
            "next_action": "Close HIGH findings or run full Reviewer gather (MCP) if Confluence/Figma required.",
            "qa_planning_fit": qa_fit,
            "qa_planning_fit_line": fit_line,
            "batch_rationale": "Open / in-progress children recommended for Creator batch.",
        },
    }


def write_onepager_pdf(html_path: Path, pdf_path: Path) -> None:
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if not Path(chrome).exists():
        return
    subprocess.run(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            f"--print-to-pdf={pdf_path}",
            "--no-pdf-header-footer",
            html_path.as_uri(),
        ],
        check=False,
        capture_output=True,
    )


def onepager_html(epic_key: str, payload: dict) -> str:
    r = payload["report"]
    gaps = r.get("not_stated") or []
    findings = payload.get("findings") or []
    fit = r.get("qa_planning_fit", "?")
    summary = payload["requirements"][0]["summary"]
    lines = []
    for f in findings[:6]:
        lines.append(f"<li><strong>{f['severity']}</strong> {f['finding_summary']} — <em>{f.get('testing_impact','')}</em></li>")
    gap_li = "".join(f"<li>{g}</li>" for g in gaps[:8])
    find_ul = "".join(lines) or "<li>No HIGH findings from REST sweep.</li>"
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>{epic_key}</title>
<style>
@page {{ size: A4; margin: 12mm; }}
body {{ font: 11pt/1.35 system-ui, sans-serif; color: #111; max-width: 100%; }}
h1 {{ font-size: 14pt; margin: 0 0 4px; }}
.meta {{ color: #444; font-size: 9pt; margin-bottom: 10px; }}
.pill {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 9pt;
  background: {'#e8f5e9' if fit=='fit' else '#fff3e0'}; }}
h2 {{ font-size: 11pt; margin: 10px 0 4px; }}
ul {{ margin: 4px 0; padding-left: 18px; }}
</style></head><body>
<h1>{epic_key} — {summary[:90]}</h1>
<p class="meta">Q4 Backlog QA readiness (filter 41907) · QA planning fit: <span class="pill">{fit}</span></p>
<h2>What is missing for testing</h2>
<ul>{gap_li}</ul>
<h2>Findings (sweep)</h2>
<ul>{find_ul}</ul>
<p class="meta">Next: {r.get('next_action','')}</p>
</body></html>"""


def merge_pdfs(parts: list[Path], out: Path) -> None:
    try:
        from pypdf import PdfWriter
    except ImportError:
        return
    w = PdfWriter()
    for p in parts:
        if p.is_file():
            w.append(str(p))
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "wb") as f:
        w.write(f)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--skip-render", action="store_true")
    args = parser.parse_args()
    load_env()
    if not os.environ.get("JIRA_API_TOKEN"):
        sys.exit("Set JIRA_* in Trinity/studio/.env")

    cfg_path = Path(args.config)
    if not cfg_path.is_absolute():
        cfg_path = REPO / cfg_path
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    portfolio_id = cfg["portfolio_id"]
    run_dir = REPO / "Trinity" / "reviewer" / "runs" / portfolio_id
    run_dir.mkdir(parents=True, exist_ok=True)
    keys = cfg.get("resolved_epic_keys") or []
    base, auth = jira_client()
    pdf_parts: list[Path] = []

    with httpx.Client(timeout=90.0) as client:
        for key in keys:
            epic_dir = run_dir / key
            epic_dir.mkdir(parents=True, exist_ok=True)
            try:
                issue = fetch_issue(client, base, auth, key)
                children = fetch_children(client, base, auth, key)
                remotes = fetch_remote_links(client, base, auth, key)
            except Exception as e:
                (epic_dir / "error.txt").write_text(str(e), encoding="utf-8")
                print(f"FAIL {key}: {e}", file=sys.stderr)
                continue
            payload = build_payload(key, issue, children, remotes, RUN_ID)
            sweep_dir = epic_dir / "rest-sweep"
            sweep_dir.mkdir(parents=True, exist_ok=True)
            payload_path = sweep_dir / "review-payload.json"
            canonical = epic_dir / "review-payload.json"
            if canonical.is_file():
                print(f"KEEP {key} canonical review-payload.json")
            payload_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            if not args.skip_render:
                subprocess.run(
                    [sys.executable, str(REVIEWER / "scripts" / "render_report.py"), str(payload_path), "--strict"],
                    cwd=REPO,
                    check=False,
                )
            html = onepager_html(key, payload)
            one_html = epic_dir / "testing-gap-onepager.html"
            one_html.write_text(html, encoding="utf-8")
            one_pdf = epic_dir / "testing-gap-onepager.pdf"
            write_onepager_pdf(one_html, one_pdf)
            if one_pdf.is_file():
                pdf_parts.append(one_pdf)
            print(f"OK {key} children={len(children)} fit={payload['report']['qa_planning_fit']}")

    portfolio = run_dir / "portfolio"
    portfolio.mkdir(exist_ok=True)
    merged = portfolio / "Q4-Backlog-QA-readiness-all-epics.pdf"
    merge_pdfs(pdf_parts, merged)
    if merged.is_file():
        print(f"Merged PDF: {merged}")
    else:
        print("Install pypdf for merged PDF: pip install pypdf", file=sys.stderr)

    subprocess.run(
        [sys.executable, str(REVIEWER / "scripts" / "build_portfolio_report.py"), "--run-dir", str(run_dir)],
        cwd=REPO,
        check=False,
    )
    print(f"Studio import path: Trinity/reviewer/runs/{portfolio_id}")
    print(f"Or: ./Trinity/studio/scripts/import-run.sh Trinity/reviewer/runs/{portfolio_id}")


if __name__ == "__main__":
    main()
