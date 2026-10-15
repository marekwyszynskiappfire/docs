# Studio prompts — inputs and outputs

**Wiki:** [Trinity — Prompts and inputs](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3755442183/Trinity+Prompts+and+inputs)

Every **Copy prompt** / **Send to Creator** action in Trinity Studio is listed here so an operator knows what to have ready **before** starting Agent mode.

**Contracts:** [`CONTRACTS.md`](CONTRACTS.md) · **Walkthrough:** [`OPERATOR-ONBOARDING.md`](OPERATOR-ONBOARDING.md) §5.

---

## Overview

| ID | Studio source | Cursor skill | You must provide | Primary outputs |
|----|---------------|--------------|------------------|-----------------|
| **1** | Reviewer configs → **Copy Cursor prompt** | `trinity-reviewer` | Portfolio id, scope (JQL/keys), product config path, MCP access; may include **portfolio interview** | `reviewer/runs/.../<EPIC>/review-payload.json` (+ HTML) |
| **1b** | Reviewer configs → **Copy JQL resolve prompt** | Agent (no skill) | JQL string; optional `JIRA_*` in Studio `.env` | Epic key list → paste into scope / run config |
| **2** | Unit detail → **Send to Creator** | `trinity-creator` | Approved unit; `review_ref` path in prompt | `creator/artifacts/.../suite-payload.json` |
| **3** | Importer → **Copy Cursor prompt** | `trinity-importer` | Exported `importer-payload.json`; mapping; instance; dry-run plan reviewed | Xray Tests, folders, Jira links |

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
| `suite-payload.json` | Journey tests; import via Studio **Creator** tab |
| Draft markdown/json | Under `creator/artifacts/<batch-id>/` |

### Operator checks

- Import batch in Studio; triage each test (approve/reject/edit).
- **Export for Importer** produces handoff JSON ([`CONTRACTS.md`](CONTRACTS.md)).

---

## Prompt 3 — Importer

### When to run

- Handoff exported from Studio Creator path.
- **Preview import plan** in UI reviewed (counts, project key, folder, field mapping).

### Inputs (in prompt + disk)

| Input | Source |
|-------|--------|
| `importer-payload.json` | Studio export (`export_kind`: `creator_importer_handoff`) |
| Operator config | Importer tab (instance, mapping path, project override, folder) |
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
Reviewer configs     → Prompt 1, 1b
Dashboard → Run      → Import folder; open units
Unit detail            → Approve; Send to Creator (Prompt 2)
Creator                → Import suite; Export for Importer
Importer               → Plan preview; Prompt 3
Statistics             → Post-run metrics (no prompt)
Personas               → Edit role text (affects Prompt 1/2 tone)
```

Screenshots: [`docs/screenshots/README.md`](docs/screenshots/README.md).
