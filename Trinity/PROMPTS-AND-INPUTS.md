# Studio prompts — inputs and outputs

**Wiki:** [Trinity — Prompts and inputs](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3755442183/Trinity+Prompts+and+inputs)

Every prompt Studio copies is listed here so an operator knows what to have ready **before** starting Agent mode. The normal path is the workspace. **More** still has Reviewer configs, Creator, and Importer when that page does not cover the step.

**Contracts:** [`CONTRACTS.md`](CONTRACTS.md) · **Walkthrough:** [`OPERATOR-ONBOARDING.md`](OPERATOR-ONBOARDING.md) §5.

---

## Overview

| ID | Studio source | Cursor skill | You must provide | Primary outputs |
|----|---------------|--------------|------------------|-----------------|
| **1** | Workspace list → **New portfolio** → **Copy Reviewer prompt**. After a workspace exists: **Reviewer prompt** → **Copy Cursor prompt** | `trinity-reviewer` | Portfolio id, scope (JQL/keys), product config path, MCP access; may include **portfolio interview** | `reviewer/runs/.../<EPIC>/review-payload.json` (+ HTML). The agent prints a workspace URL |
| **1b** | Reviewer configs → **Copy JQL resolve prompt** | Agent (no skill) | JQL string; optional `JIRA_*` in Studio `.env` | Epic key list → paste into scope / run config |
| **2** | Workspace **Next step → Copy Creator prompt**. Several approved Epics: **Prepare Creator prompts**, then **Copy Creator prompts** | `trinity-creator` | Approved review; `review_ref` path in prompt | `creator/artifacts/.../suite-payload.json`. The workspace imports the file when it appears |
| **3** | Workspace **Plan Xray import**, or **More → Importer → Copy Cursor prompt** when writing through Cursor | `trinity-importer` | Mapping, instance, folder; dry-run plan reviewed | Xray Tests, folders, Jira links |

---

## Prompt 1 — Reviewer portfolio scan

### When to run

- New portfolio or refreshed Epic set under `Trinity/reviewer/config/runs/<portfolio_id>.json`.
- After scope/JQL change.
- After major persona or checklist change.

### Inputs (embedded in Studio prompt)

| Input | Source | Notes |
|-------|--------|-------|
| Portfolio / run config | `Trinity/reviewer/config/runs/{id}.json` | Scope, product, personas |
| Product policies | `Trinity/reviewer/config/{product}.json` | Field maps, gates |
| Personas | `Trinity/personas/*.md` | Linked from run config |
| Jira + Confluence | MCP | [`CURSOR-MCP-SETUP.md`](CURSOR-MCP-SETUP.md) |
| Output root | `Trinity/reviewer/runs/{portfolio_run_id}/` | Gitignored; one folder per Epic **key**. Import path = directory that **directly contains** `{EPIC}/` (may be `runs/{portfolio_id}` or `runs/{portfolio_id}/{dated-run}`). |

### Outputs per Epic

| File | Schema |
|------|--------|
| `review-payload.json` | [`reviewer/schemas/review-payload.schema.json`](reviewer/schemas/review-payload.schema.json) |
| `review-report.html` | [`shared/html-report-guidelines.md`](shared/html-report-guidelines.md) Profile A/B |
| Gather logs / sidecars | Under epic folder per skill run |

### Operator checks before import

- Folder name **equals** Epic Jira key (e.g. `ONE-228469`).
- `scope.value` in payload matches that key.
- `report.qa_planning_fit` present for Statistics readiness ([`METRICS.md`](METRICS.md)).

### Portfolio interview (before gather)

Studio **Copy Cursor prompt** starts **trinity-reviewer**, which runs the **interactive run configuration** interview when `config/runs/{portfolio_id}.json` is missing or scope changed. The agent will ask (in order): portfolio id, scope (JQL/keys/filter), pass type, product id, persona, child-scan mode, outputs, Creator handoff defaults, Jira comment policy.

**Operator:** answer in chat; confirm saved path under `Trinity/reviewer/config/runs/`. Do not skip unless you already have a committed run config from QA lead. Full wizard: [`reviewer/SKILL.md` § Interactive run configuration](reviewer/SKILL.md#interactive-run-configuration-mandatory).

**Return visit:** agent asks “Any changes to run configuration?” — say **no** to reuse scope.

### Next step

```bash
./Trinity/studio/scripts/import-run.sh Trinity/reviewer/runs/<folder-that-directly-contains-EPIC-KEY>
```

---

## Prompt 1b — JQL resolve (optional)

### When to run

- Studio **Resolve from scope** disabled or failing (no `.env`).
- You have a filter/JQL and need epic keys for run config.

### Inputs

| Input | Where |
|-------|--------|
| JQL | Reviewer config scope field |
| Jira REST | `Trinity/studio/.env` → `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` |

### Output

- List of Epic issue keys → update `run-config` scope or confirm folder list before Prompt 1.

---

## Prompt 2 — Creator

### When to run

- Epic unit **approved** in Studio for test design.
- `review_ref` points at approved `review-payload.json` (path in generated prompt).

### Inputs

| Input | Source |
|-------|--------|
| `review_ref` | Studio export / prompt body |
| Golden style (optional) | `Trinity/creator/golden/v2/` |
| Personas | Creator `SKILL.md` + run context |

### Outputs

| File | Notes |
|------|-------|
| `suite-payload.json` | Journey tests. The workspace imports this file. **More → Creator** is the fallback |
| Draft markdown/json | Under `creator/artifacts/<batch-id>/` |

### Operator checks

- On the workspace, approve or reject each test. A rejection needs a reason. Tick **Send to Xray** on the approved tests you want imported, or use **Approve selected** for the ones you ticked.
- Expand **Creator runs** → **Export for Importer** to write the handoff JSON. **More → Creator** still lists every Creator run ([`CONTRACTS.md`](CONTRACTS.md)).

---

## Prompt 3 — Importer

### When to run

- Handoff exported from Studio Creator path.
- **Preview import plan** in UI reviewed (counts, project key, folder, field mapping).

### Inputs (in prompt + disk)

| Input | Source |
|-------|--------|
| `importer-payload.json` | Studio export (`export_kind`: `creator_importer_handoff`) |
| Operator config | Workspace import panel, or the Importer page (instance, mapping path, project override, folder) |
| Mapping JSON | `Trinity/importer/config/mappings/*.json` |
| Xray credentials | `studio/.env` `XRAY_CLIENT_ID` / `XRAY_CLIENT_SECRET` |
| Jira token | Same `.env` for requirement links |

### Outputs

| Output | Where |
|--------|--------|
| Xray Test issues | Target Jira project (UI **project key**) |
| Test Repository folder | Xray folder path from UI |
| Import report | Skill / CLI stdout; optional JSON under `importer/` |

### Operator checks

- Sandbox dry-run first ([`OPERATOR-ONBOARDING.md`](OPERATOR-ONBOARDING.md) Gate 6).
- Mapping `jira.site_url` matches selected instance ([`GUIDE.md`](GUIDE.md)).

---

## Prompt hygiene

1. **One portfolio scan per Agent thread** — long runs; avoid mixing Epics from different portfolios in one paste.
2. **Do not edit** generated prompt headers (paths and portfolio id are consistency checks for the skill).
3. **Re-copy** after changing Reviewer config, scope, or Importer mapping — stale prompts cause wrong folders or project keys.
4. **Secrets** stay in `.env` and MCP OAuth — never in prompt text.

---

## Studio UI map (where to click)

```text
Workspace            → Verdict, Prompt 2, test review, Xray plan, import a review folder
                     → New portfolio and Prompt 1 before a workspace exists
                     → Portfolio: prepare/copy Creator prompts, approve selected tests, preview plans
                     → Creator runs for this portfolio; Export for Importer
                     → Record Xray keys after a Cursor write
More → Reviewer configs → Every portfolio; Prompt 1b
Workspace list       → Import a review folder and open that workspace
More → Creator       → Every Creator run; paste a suite path the Epic does not show
More → Importer      → Payload-path import and the page execute
Unit page            → Finding triage; Jira epic comment
Statistics           → Post-run metrics (no prompt)
Personas             → Edit role text (affects Prompt 1/2 tone)
```

Screenshots: [`docs/screenshots/README.md`](docs/screenshots/README.md).
