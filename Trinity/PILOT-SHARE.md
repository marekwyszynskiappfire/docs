# Trinity — pilot share pack (wider audience)

**Pilot wave:** 2026-10-15 → **feedback by 2026-10-29** (2 weeks)  
**Owner:** QA CoE / program lead (P2)  
**Status:** Internal pilot — not org-wide GA ([PATH-TO-1.0.md](PATH-TO-1.0.md))

---

## One link to send

**[Trinity — Start here (Confluence)](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754590489/Trinity+Start+here)**

Hub: [Trinity — AI-assisted QA pipeline](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3750559869/Trinity+AI-assisted+QA+pipeline+operator+guide)

Git repo (clone): `https://github.com/marekwyszynskiappfire/docs.git`

---

## Copy-paste announcement (Slack / email)

```text
Trinity pilot — AI-assisted QA (Reviewer → Studio → Creator → Xray Importer)

We’re opening a 2-week feedback window (through 29 Oct 2026).

Start here (wiki): https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754590489/Trinity+Start+here

Suggested first hour (no production Jira required):
1. Clone docs repo, run ./Trinity/studio/scripts/start.sh
2. ./Trinity/studio/scripts/seed-demo.sh — click through DEMO-4500
3. Follow “First run playbook” on the wiki for MCP + one sandbox Epic when ready

This is a pilot: use sandbox first; production Epics need QA lead portfolio + Importer mapping.

Feedback: GitHub issue “Trinity pilot feedback” on marekwyszynskiappfire/docs (label trinity-support)
or reply in this thread with epic key + what blocked you.

Thanks — your friction logs directly shape GA readiness.
```

---

## What we want from participants (pick any)

| Depth | Ask | Artifact |
|-------|-----|----------|
| **Light** | Phase 0–1 demo only (~20 min) | Thread reply or issue: “stuck at step X” |
| **Standard** | Full [FIRST-RUN.md](FIRST-RUN.md) on **sandbox** | [Pilot feedback issue](https://github.com/marekwyszynskiappfire/docs/issues/new?template=trinity-pilot-feedback.yml) |
| **Structured** | 90 min with QA lead | [UAT-SESSION.md](UAT-SESSION.md) + [OPERATOR-VALIDATION.md](OPERATOR-VALIDATION.md) |

---

## What to set expectations on

| Say | Avoid implying |
|-----|----------------|
| Pilot on **onboarded product lines** with QA-provided config | “Works on any Jira project day one” |
| **Studio copies prompts** — do not hand-write portfolio scans | “Just ask ChatGPT to review Jira” |
| **Sandbox first**; `PRODUCTION` gate on Importer | Silent production Xray writes |
| **DEMO-4500** is fictional | Posting demo data to prod |
| Feedback welcome through **29 Oct 2026** | Open-ended beta with no owner |

---

## Lead checklist (before / during wave)

- [ ] Confluence **Start here** synced (`sync_confluence_from_git.py`)
- [ ] At least one **sandbox** Epic + portfolio id ready for volunteers who finish Phase 1
- [ ] **Mapping file** + project key documented for sandbox imports ([GUIDE.md](GUIDE.md))
- [ ] Monitor `trinity-support` issues; triage weekly
- [ ] Optional: schedule 1–2 [UAT sessions](UAT-SESSION.md) with named operators
- [ ] **29 Oct:** rollup issues → update [NEWBIE-PERSONA-REVIEW.md](NEWBIE-PERSONA-REVIEW.md) scores + PATH-TO-1.0 gates

---

## Feedback triage (P2)

| Severity | SLA (pilot) | Action |
|----------|-------------|--------|
| **blocker** | 2 business days | Fix or doc workaround; reply on issue |
| **major** | End of wave | Backlog issue; FAQ if recurring |
| **minor / doc-only** | Batch weekly | FAQ or FIRST-RUN tweak |

---

## Version pin for reproducibility

Ask reporters to include:

```bash
cat Trinity/VERSION
./Trinity/scripts/pilot-preflight.sh
```
