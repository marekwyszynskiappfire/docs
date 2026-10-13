# Trinity

**Trinity** combines three Cursor Agent skills — **Reviewer**, **Creator**, and **Importer** — with **Trinity Studio**, the local workbench for human QA review, approvals, and handoff.

## Start here

| Doc | Purpose |
|-----|---------|
| **[`FIRST-RUN.md`](FIRST-RUN.md)** | **First time** — checkout → demo → three Cursor prompts → one epic |
| [`MANUAL.md`](MANUAL.md) | Full operator reference |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Components, diagrams, repo layout |
| [`OPERATOR-SETUP.md`](OPERATOR-SETUP.md) | Linear setup checklist |
| [`GUIDE.md`](GUIDE.md) | Credentials, golden corpus, Importer project key |
| [`PREFLIGHT.md`](PREFLIGHT.md) · [`TESTING.md`](TESTING.md) | Smoke checks and validation |

**Release:** `Trinity/VERSION` (see [`VERSIONING.md`](VERSIONING.md)) · **Mateusz POC closure:** [`MATEUSZ-CRITERIA.md`](MATEUSZ-CRITERIA.md) · [`Mateusz.MD`](Mateusz.MD) (requirements PL).

Planning artifacts (grill sessions, filled scorecards, Slides drafts) stay **local or Confluence** — engineering backlog in GitHub Issues ([`docs/agents/issue-tracker.md`](../docs/agents/issue-tracker.md)).

## Getting started

```bash
./Trinity/studio/scripts/start.sh          # terminal 1 — UI http://127.0.0.1:5173
./Trinity/studio/scripts/seed-demo.sh      # terminal 2 — demo Reviewer import
./Trinity/scripts/install-trinity-skills.sh   # Cursor skills (live Jira path)
```

Open **http://127.0.0.1:5173** · API **http://127.0.0.1:8765/api/health**

Import a Reviewer run:

```bash
./Trinity/studio/scripts/import-run.sh Trinity/reviewer/runs/<your-run-folder>
```

## Layout

| Path | Role |
|------|------|
| [`reviewer/`](reviewer/) | Requirement quality review (SKILL, schemas, portfolio HTML) |
| [`creator/`](creator/) | Test suite generation |
| [`importer/`](importer/) | Approved suites → Xray |
| [`studio/`](studio/) | Trinity Studio — FastAPI + React |
| [`shared/`](shared/) | HTML report guidelines |
| [`personas/`](personas/) | Runtime prompts |
| [`scripts/`](scripts/) | `install-trinity-skills.sh`, `export-telemetry.sh` (pilot evidence) |
| [`confluence/`](confluence/) | Wiki publish map + pipeline SVG |

## More docs

| Doc | Purpose |
|-----|---------|
| [`PIPELINE.md`](PIPELINE.md) | End-to-end flow map |
| [`CONTRACTS.md`](CONTRACTS.md) | Payload and handoff JSON |
| [`FAQ.md`](FAQ.md) | Capabilities and policies |
| [`METRICS.md`](METRICS.md) · [`CURSOR-COST.md`](CURSOR-COST.md) | Telemetry and Cursor usage |
| [`VERSIONING.md`](VERSIONING.md) | Release semver vs JSON schema versions |
| [`MATEUSZ-CRITERIA.md`](MATEUSZ-CRITERIA.md) | POC traceability and scorecard template |
| [`reviewer/MANUAL.md`](reviewer/MANUAL.md) | Reading Reviewer HTML reports |
| [`confluence/README.md`](confluence/README.md) | Confluence (QACoE) three-page tree |

## Prerequisites

- Cursor with Atlassian MCP ([`reviewer/config/DUAL-ATLASSIAN-MCP.md`](reviewer/config/DUAL-ATLASSIAN-MCP.md))
- Python 3.11+ · Node 18+
