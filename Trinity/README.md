# Trinity

**Trinity** combines three Cursor Agent skills — **Reviewer**, **Creator**, and **Importer** — with **Trinity Studio**, the local workbench for human QA review, approvals, and handoff.

Start here for install. **Full operator guide:** [`GUIDE.md`](GUIDE.md) (architecture, checkout steps, golden exports, Importer project choice).

## Getting Started

**New operators:** read **[`GUIDE.md` → Getting Started](GUIDE.md#getting-started)** (15‑min demo, credentials, Importer **project selector**, golden exports).

```bash
./Trinity/scripts/install-trinity-skills.sh
./Trinity/studio/scripts/start.sh
```

Open **http://127.0.0.1:5173** · API **http://127.0.0.1:8765/api/health**

Validate: [`TESTING.md`](TESTING.md) · Preflight: [`PREFLIGHT.md`](PREFLIGHT.md)

Import a Reviewer run (example):

```bash
./Trinity/studio/scripts/import-run.sh Trinity/reviewer/runs/<your-run-folder>
```

## Layout

| Path | Role |
|------|------|
| [`reviewer/`](reviewer/) | Requirement quality review (SKILL, schemas, `runs/`, portfolio builder) |
| [`creator/`](creator/) | Test suite generation ([`SKILL.md`](creator/SKILL.md); demo batch in `samples/`) |
| [`importer/`](importer/) | Approved suites → Xray (instance + folder targeting; dry-run in Studio) |
| [`studio/`](studio/) | Trinity Studio — FastAPI + React, SQLite revisions |
| [`shared/`](shared/) | HTML report guidelines (Profile A/B) |
| [`personas/`](personas/) | Runtime prompts + [`personas/P1-P10.md`](personas/P1-P10.md) operator matrix |
| [`scripts/`](scripts/) | `install-trinity-skills.sh` |

## Documentation

| Doc | Purpose |
|-----|---------|
| **[GUIDE.md](GUIDE.md)** | **Getting Started, prerequisites, golden, Importer project selector** |
| [FAQ.md](FAQ.md) | Capabilities, metrics, multi-product validation, sign-off evidence |
| [CURSOR-COST.md](CURSOR-COST.md) | Per-stage Cursor usage and USD cost (hooks + Admin API) |
| [REVIEW-PRODUCT-AND-DOCS.md](REVIEW-PRODUCT-AND-DOCS.md) | Multi-persona product/doc review + open questions |
| [FAQ.md](FAQ.md) | Engineering FAQ (capabilities, metrics, sign-off evidence) |
| [NEXT-STEPS.md](NEXT-STEPS.md) | Post-P2: grill, doc cleanup, UI, pilot sign-off |
| [PREFLIGHT.md](PREFLIGHT.md) | MCP, skills, health checks |
| [TESTING.md](TESTING.md) | Hands-on validation checklist |
| [MANUAL.md](MANUAL.md) | Reviewer interview, Studio personas/configs |
| [PIPELINE.md](PIPELINE.md) | End-to-end Reviewer → Studio → Creator → Importer |
| [CONTRACTS.md](CONTRACTS.md) | Payload and handoff contracts |
| [parity-matrix.md](parity-matrix.md) | Studio vs Reviewer HTML (Phase 0 stub) |

## Prerequisites

- Cursor with Atlassian MCP ([`reviewer/config/DUAL-ATLASSIAN-MCP.md`](reviewer/config/DUAL-ATLASSIAN-MCP.md))
- Python 3.11+ for Studio and `render_report.py`
- Node 18+ for Trinity Studio UI (`Trinity/studio/web`)
