# Trinity

**Trinity** combines three Cursor Agent skills — **Reviewer**, **Creator**, and **Importer** — with **Trinity Studio**, the local workbench for human QA review, approvals, and handoff.

Start here for install, preflight, and the full operator manual.

## Quick start

```bash
# 1. Install skills into Cursor (from repo root)
./Trinity/scripts/install-trinity-skills.sh

# 2. Start Trinity Studio
./Trinity/studio/scripts/start.sh
```

Open **http://127.0.0.1:5173** (UI) · API **http://127.0.0.1:8765**

**Hands-on test path:** [`TESTING.md`](TESTING.md) (Reviewer → Studio → Creator).

Import a Reviewer run (example):

```bash
./Trinity/studio/scripts/import-run.sh Trinity/reviewer/runs/<your-run-folder>
```

## Layout

| Path | Role |
|------|------|
| [`reviewer/`](reviewer/) | Requirement quality review (SKILL, schemas, `runs/`, portfolio builder) |
| [`creator/`](creator/) | Test suite generation ([`SKILL.md`](creator/SKILL.md); demo batch in `samples/`) |
| [`importer/`](importer/) | Approved suites → Xray (roadmap; CR-IMPORTER-01) |
| [`studio/`](studio/) | Trinity Studio — FastAPI + React, SQLite revisions |
| [`shared/`](shared/) | HTML report guidelines (Profile A/B) |
| [`personas/`](personas/) | Editable Reviewer/Creator/Importer role prompts |
| [`scripts/`](scripts/) | `install-trinity-skills.sh` |

## Documentation

| Doc | Purpose |
|-----|---------|
| [PREFLIGHT.md](PREFLIGHT.md) | MCP, skills, health checks |
| [MANUAL.md](MANUAL.md) | Operator guide (Reviewer interview, Studio personas/configs) |
| [PIPELINE.md](PIPELINE.md) | End-to-end Reviewer → Studio → Creator |
| [CONTRACTS.md](CONTRACTS.md) | Payload and handoff contracts |
| [parity-matrix.md](parity-matrix.md) | Studio vs Reviewer HTML (Phase 0 stub) |

## Prerequisites

- Cursor with Atlassian MCP ([`reviewer/config/DUAL-ATLASSIAN-MCP.md`](reviewer/config/DUAL-ATLASSIAN-MCP.md))
- Python 3.11+ for Studio and `render_report.py`
- Node 18+ for Trinity Studio UI (`Trinity/studio/web`)
