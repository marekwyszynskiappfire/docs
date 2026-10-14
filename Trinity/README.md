# Trinity

**Trinity** combines three Cursor Agent skills — **Reviewer**, **Creator**, and **Importer** — with **Trinity Studio**, the local workbench for human QA review, approvals, and handoff.

## Share with your team (Confluence)

**[Trinity — Start here](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754590489/Trinity+Start+here)** · **[FAQ](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754164473/Trinity+FAQ)** · [Full wiki tree](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3750559869/Trinity+AI-assisted+QA+pipeline+operator+guide)

Git mirrors under `Trinity/`; republish with `python3 Trinity/scripts/sync_confluence_from_git.py` ([`confluence/README.md`](confluence/README.md)).

---

## Production use vs internal GA

| | |
|--|--|
| **You can use Trinity for real Epics and Xray today** | On a **product line** that has portfolio config, Creator golden, and Importer mapping (QA lead owns onboarding). |
| **Not yet “any team, any product”** | See [`PATH-TO-1.0.md`](PATH-TO-1.0.md) for org-wide GA gates (multiple operators, scorecards, hardening). |
| **New operator path** | [`START-HERE.md`](START-HERE.md) → [`OPERATOR-ONBOARDING.md`](OPERATOR-ONBOARDING.md) → [`FAQ.md`](FAQ.md) |

---

## Start here (git)

| Doc | Purpose |
|-----|---------|
| **[`START-HERE.md`](START-HERE.md)** | **New operators** — paths, wiki links, five commands |
| **[`FAQ.md`](FAQ.md)** | **Questions before you ask in chat** |
| **[`OPERATOR-ONBOARDING.md`](OPERATOR-ONBOARDING.md)** | Setup gates, MCP, demo, real Epic, recovery |
| [`FIRST-RUN.md`](FIRST-RUN.md) | Phased first run (0–3) |
| [`CURSOR-MCP-SETUP.md`](CURSOR-MCP-SETUP.md) · [`PROMPTS-AND-INPUTS.md`](PROMPTS-AND-INPUTS.md) | MCP · Studio prompts |
| [`MANUAL.md`](MANUAL.md) | Full operator reference |
| [`OPERATOR-SETUP.md`](OPERATOR-SETUP.md) | Linear checklist |

**Release:** [`VERSION`](VERSION) · [`VERSIONING.md`](VERSIONING.md) · Mateusz POC: [`MATEUSZ-CRITERIA.md`](MATEUSZ-CRITERIA.md)

---

## Quick start

```bash
./Trinity/studio/scripts/start.sh          # UI http://127.0.0.1:5173
./Trinity/studio/scripts/seed-demo.sh      # demo data
./Trinity/scripts/install-trinity-skills.sh
./Trinity/scripts/pilot-preflight.sh       # after skills installed
```

---

## Layout

| Path | Role |
|------|------|
| [`reviewer/`](reviewer/) | Requirement quality review |
| [`creator/`](creator/) | Test suite generation |
| [`importer/`](importer/) | Approved suites → Xray |
| [`studio/`](studio/) | Trinity Studio — FastAPI + React |
| [`confluence/`](confluence/) | Wiki page map + publish |
| [`scripts/`](scripts/) | Skills install, preflight, Confluence sync |

---

## Prerequisites

- Cursor + Atlassian MCP ([`CURSOR-MCP-SETUP.md`](CURSOR-MCP-SETUP.md))
- Python 3.11+ · Node 18+
- Jira/Xray access per [`OPERATOR-ONBOARDING.md`](OPERATOR-ONBOARDING.md)
