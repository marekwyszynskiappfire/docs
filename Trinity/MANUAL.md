# Trinity — operator manual

*Draft for Confluence publishing. Written for the **QA engineer** running Reviewer → Studio → Creator → Importer day to day, with callouts for QA leads, PMs, and platform admins. This manual explains **how to operate the pipeline**; contracts and schemas live in [`CONTRACTS.md`](CONTRACTS.md), [`reviewer/SKILL.md`](reviewer/SKILL.md), and [`creator/SKILL.md`](creator/SKILL.md).*

**First time using Trinity?** Follow [`FIRST-RUN.md`](FIRST-RUN.md) phase by phase (demo → three Cursor prompts → one epic).  
**Companion docs:** [`OPERATOR-SETUP.md`](OPERATOR-SETUP.md) · [`TESTING.md`](TESTING.md) · [`GUIDE.md`](GUIDE.md) · [`reviewer/MANUAL.md`](reviewer/MANUAL.md) · [`PIPELINE.md`](PIPELINE.md).

**Last reviewed:** 2026-10-13

---

## 1. What Trinity is

Trinity is an **AI-assisted QA pipeline** for Jira-backed products. It does not replace human judgment; it **front-loads** requirement quality, drafts journey-level tests, and gives you a **local workbench** (Trinity Studio) where every handoff to Jira/Xray is explicit and auditable.

| Piece | Where it runs | What it produces |
|-------|----------------|------------------|
| **Reviewer** | Cursor (`trinity-reviewer`) | `review-payload.json`, HTML report, optional Jira comment text files |
| **Trinity Studio** | Your machine (browser + API) | SQLite revisions, `studio_qa` triage, exports, metrics, Importer plan/execute |
| **Creator** | Cursor (`trinity-creator`) | `suite-payload.json` — 3–5 E2E journey tests per Epic |
| **Importer** | Studio + Cursor (`trinity-importer`) | Xray tests in Jira, import reports, persisted keys in Studio |

**Design rule:** Cursor agents **gather and generate**; Studio is the **control plane** for approve/export/post/execute in v1. Studio does not run Reviewer gathers (no MCP from the API).

---

## 2. Quick start — “I want to…”

| You want to… | Do this | You need |
|--------------|---------|----------|
| **First run — don’t think, just follow** | [`FIRST-RUN.md`](FIRST-RUN.md) Phases 0–3 | Python, Node; Phase 3 needs MCP |
| Prove Studio works in 10 minutes | [`FIRST-RUN.md`](FIRST-RUN.md) Phase 0–1 | No Jira |
| Run a full pipeline on real epics | Setup steps 1–14 in [`OPERATOR-SETUP.md`](OPERATOR-SETUP.md) | MCP, `.env`, Xray keys for execute |
| Understand a Reviewer HTML report | [`reviewer/MANUAL.md`](reviewer/MANUAL.md) §3–7 | Sample: `reviewer/sample-report.html` |
| Configure a portfolio / pass type | Studio → **Reviewer configs** (§5 below) | Saved JSON under `reviewer/config/runs/` |
| Triage findings and send feedback to Jira | Unit page → `studio_qa` → **Jira epic comment** (§8) | `JIRA_*` in `studio/.env` |
| Hand off to test design | **Approve & export** → **Send to Creator** (§9) | Approved unit; not `not_fit` |
| Import tests to Xray | **Importer** tab (§10) | Mapping, project key, folder; production gate |
| Fix “import failed: folder ≠ epic key” | Rename run folder to match `scope.value` in payload | §6 |
| Track engineering backlog | GitHub Issues ([`docs/agents/issue-tracker.md`](../docs/agents/issue-tracker.md)) | — |

---

## 3. Architecture — one picture, three boundaries

**Diagram (attach in Confluence):** [`confluence/assets/trinity-operator-pipeline.svg`](confluence/assets/trinity-operator-pipeline.svg)

**Data flow for one Epic**

1. Reviewer writes `Trinity/reviewer/runs/<run>/<EPIC-KEY>/review-payload.json` (and optional `review-report.html`).
2. You import the run folder into Studio → payload stored as revisions + `studio_qa` overlay.
3. You approve → export lands under `Trinity/studio/data/exports/`.
4. Creator writes `suite-payload.json` → you import in Studio → approve tests.
5. Importer creates Xray tests → you persist keys back into Studio for metrics.

**Boundaries (do not blur these)**

| Action | Tool |
|--------|------|
| Jira/Confluence gather, portfolio HTML build | Cursor — Reviewer skill |
| Edit personas, run configs, triage, approve, Jira post, Importer plan | Studio |
| Test case generation from `review_ref` | Cursor — Creator skill |
| Xray `createTest` / `createFolder` | Studio execute **or** Importer skill / CLI |

**Ports:** API **8765**, Vite UI **5173** (or built React on 8765 after `npm run build`). Health: `GET /api/health`.

---

## 4. First-time setup (summary)

Full numbered steps: [`OPERATOR-SETUP.md`](OPERATOR-SETUP.md). This section is the **narrative** version.

### 4.1 Machine and repo

- Clone the docs repo; all paths assume repo root contains `Trinity/`.
- **Python 3.11+**, **Node 18+**, **Cursor** with skills installed:

```bash
./Trinity/scripts/install-trinity-skills.sh
```

- Offline smoke (no Jira):

```bash
python3 Trinity/reviewer/scripts/render_report.py \
  Trinity/reviewer/samples/demo-epic.payload.json --strict
```

Details: [`PREFLIGHT.md`](PREFLIGHT.md).

### 4.2 Studio credentials

Copy `Trinity/studio/.env.example` → `.env`. Never commit `.env`.

| Variable group | Used for |
|----------------|----------|
| `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` | Epic comments, JQL resolve (optional), Importer project list, scope resolve |
| `XRAY_CLIENT_ID`, `XRAY_CLIENT_SECRET` | Importer **execute** (batch create in Xray) |

Production Xray often lives in `Trinity/studio/.env.production` (gitignored). **Production writes** in Studio require typing **`PRODUCTION`** in the UI (Importer execute and Jira post on production host).

Use **sandbox** until you deliberately target production. Demo epic **`DEMO-4500`** is fictional — do not post it to real Jira.

### 4.3 Start Studio and load demo

```bash
./Trinity/studio/scripts/start.sh          # terminal 1
./Trinity/studio/scripts/seed-demo.sh      # terminal 2
```

Open http://127.0.0.1:5173 → Dashboard → run from seed → unit **DEMO-4500**.

Ports busy: `./Trinity/studio/scripts/stop.sh` or `STUDIO_FORCE=1 ./Trinity/studio/scripts/start.sh`.

### 4.4 Atlassian MCP (live Reviewer/Creator)

Many Appfire programs use **two** hosts (e.g. `appfire.atlassian.net` + `appfireteam.atlassian.net`). Configure **one MCP connection per host** or Confluence pages show *Unavailable* in Reviewer **Data sources**.

Checklist: [`reviewer/config/DUAL-ATLASSIAN-MCP.md`](reviewer/config/DUAL-ATLASSIAN-MCP.md).

---

## 5. Trinity Studio — navigation and roles

Studio is a **single-operator workbench**. You will use these areas in order during a program.

### 5.1 Dashboard

- Lists **pipeline runs** (imported Reviewer folders).
- **Import Reviewer run** — path to `Trinity/reviewer/runs/<folder>` or use `import-run.sh`.
- Each run shows epic units; open the run for portfolio-level Creator handoff.

### 5.2 Personas

- Edits markdown under `Trinity/personas/` (Reviewer tone, Creator personas).
- Changes affect **future** Cursor prompts, not already-imported payloads until you re-gather.
- Audience matrix: [`personas/P1-P10.md`](personas/P1-P10.md).

### 5.3 Reviewer configs

- Create/edit portfolio JSON validated against `run-config.schema.json`.
- Saved to `Trinity/reviewer/config/runs/{portfolio_id}.json` (or `*-local.json` for private configs — gitignored).
- **Copy Cursor prompt** — primary way to start a gather in Cursor (Studio does not invoke MCP).
- **List new epics** — works when scope is `epic_keys` / `epic_url` and keys are resolved.
- **JQL / filter scope:** resolve epic keys in Cursor (or paste into **Resolved epic keys**) before gather. Use **Copy JQL resolve prompt** when REST resolve is not configured.

**Portfolio interview (first run in Cursor):** portfolio id, scope, pass type (`full_sweep`, `rescan_delta`, `new_epics_only`), persona, outputs, Jira comment policy. Return visits reuse config unless you change scope. Say **skip config** only when you explicitly want to bypass the interview.

Committed example: [`reviewer/config/runs/example.demo-portfolio.json`](reviewer/config/runs/example.demo-portfolio.json).

### 5.4 Pipeline run page

After import, open a run to:

- Toggle **In Creator** per epic (or bulk **Include all** / **Exclude not_fit**).
- Copy **Creator JQL**, **handoff JSON**, or download JSON for planning.
- See **portfolio report path** when `portfolio/index.html` exists (Profile B rollup).

### 5.5 Review unit page

The **center of human QA** on requirements (§7).

### 5.6 Creator

- Import `suite-payload.json` from a Creator run folder or path.
- Open a **creator run** to triage tests, bulk approve, filter **Ready for Xray import**, **Export for Importer**.

### 5.7 Importer

- Plan dry-run, acknowledge gates, copy Cursor prompt or **Execute import batch**, persist Xray keys (§10).

### 5.8 Telemetry and Cursor cost (optional)

- Local `metric_event` rows in SQLite; optional BigQuery when configured — [`METRICS.md`](METRICS.md).
- Cursor usage backfill when `CURSOR_ADMIN_API_KEY` is set — [`CURSOR-COST.md`](CURSOR-COST.md).

---

## 6. Reviewer outputs — import rules and portfolio

### 6.1 Folder name = epic key

Each epic lives in:

```
Trinity/reviewer/runs/<portfolio-run-id>/<EPIC-KEY>/review-payload.json
```

**`<EPIC-KEY>` must equal `scope.value`** in that JSON. Studio import **rejects** mismatches to prevent wrong epic attribution.

### 6.2 Import command

```bash
./Trinity/studio/scripts/import-run.sh Trinity/reviewer/runs/<your-run-folder>
```

Or Dashboard → import path. Re-import creates new revisions; triage in `studio_qa` is per unit in SQLite.

### 6.3 HTML reports

- Per-epic: `review-report.html` (Profile A) — link from unit page when present.
- Portfolio: `portfolio/index.html` (Profile B) — themes, readiness, Creator handoff checkboxes.

Rendering rules: [`shared/html-report-guidelines.md`](shared/html-report-guidelines.md). Reading reports: [`reviewer/MANUAL.md`](reviewer/MANUAL.md).

### 6.4 Jira comment files from Reviewer

By default Reviewer writes `jira-comment-full.txt` and `jira-comment-short.txt` for **manual paste**. Auto-post is off unless product config sets `policy.jira_comment` to `auto-post` (§9 in Reviewer manual).

Studio **Jira epic comment** panel is the preferred path **after triage** — it respects `studio_qa` and production gates.

---

## 7. Review unit workflow — triage, approve, export

Open Dashboard → run → **epic unit**.

### 7.1 What you are looking at

- **Payload** — findings (F#), questions (Q#), gate, readiness, `qa_planning_fit`, context-loaded alerts.
- **studio_qa overlay** — your decisions; stored separately from the raw Reviewer JSON.

### 7.2 Triage each question and finding

For each item you typically set:

| Field | Meaning |
|-------|---------|
| **Validity** | `valid` / `discuss` / `invalid` — `invalid` = do not ask PO (never posted to Jira) |
| **Include in epic feedback** (`send_to_epic`) | When checked, item can appear in Studio/Jira epic comment |
| **Comment** | Operator note; appended as `_QA note:_` in wiki output when posting |

**Discuss** items post to Jira **only** if **Include in epic feedback** is checked.

### 7.3 Save draft

**Save draft** writes a new **payload revision** in SQLite. The **Jira comment preview** uses the **saved** payload only — triage changes are invisible to preview until you save.

### 7.4 Planning fit and Creator block

Reviewer sets `qa_planning_fit`: `fit`, `provisional`, or `not_fit` (empty/hollow epics).

- **`not_fit`** — **Send to Creator** is disabled; exclude from run-level Creator handoff unless you override at portfolio level deliberately.
- **`provisional`** — Creator may run; expect thin tests until scope improves.

### 7.5 Approve and export

1. **Approve & export for Creator** — writes `review-payload.json` (with `studio_qa`) under `Trinity/studio/data/exports/`.
2. **Send to Creator** — copies a markdown prompt with `review_ref` path and Epic key.
3. Paste into Cursor → run **trinity-creator** (one run **per Epic**, CR-EPIC-01).

Optional: **Download epic feedback** JSON for ad-hoc tooling; prefer Jira panel for PO-facing text.

### 7.6 Context-loaded alerts

When Reviewer flags thin gather (missing Confluence, etc.), Studio surfaces **context loaded** warnings on the dashboard. Treat as “re-gather or accept provisional scope,” not as a Studio bug.

---

## 8. Jira epic comments (Studio)

Prerequisites: `JIRA_*` in `.env`; credentials chip on panel should be green.

| Step | Action |
|------|--------|
| 1 | Complete triage → **Save draft** |
| 2 | Open **Jira epic comment** panel on unit page |
| 3 | Choose **Smart** (recommended) or short / full / studio variant |
| 4 | **Refresh preview** — read warnings (redaction **blocks** post) |
| 5 | Optional **Unlock wording** for minor edits (telemetry records `preview_edited`) |
| 6 | Checkbox + type epic **issue key** to confirm target |
| 7 | On production host, type **`PRODUCTION`** |
| 8 | **Post to Jira** — always a **new** comment; duplicate-post warning within 24h unless you acknowledge |

**Variants (summary)**

- **Studio** — items with `send_to_epic` after triage.
- **Full / short** — Reviewer template shapes; smart picker chooses based on history and open questions.

**Never post** `invalid` items. **Do not** use `DEMO-4500` against production.

Jira panel behaviour is documented in §8 above; telemetry in [`METRICS.md`](METRICS.md).

---

## 9. Creator — from approved review to Studio tests

### 9.1 In Cursor

Prompt includes:

- `review_ref` — exported JSON path from Studio
- Epic key and `suite_mode` (release-slice E2E journeys)
- Product / golden config from `Trinity/creator/config/`

Output: `suite-payload.json` under `Trinity/creator/artifacts/` or path shown in chat.

Golden corpora affect **style and depth**, not Importer project — [`GUIDE.md`](GUIDE.md) §5–6.

### 9.2 In Studio

1. **Creator** tab → import batch (path from Creator run).
2. Per test: edit steps, set `automation_fit`, blockers, `human_review_status`.
3. **Approve** or **reject**; check **Fit for Xray import** on approved rows.
4. **Export for Importer** → `studio/data/exports/creator/{run}/importer-payload.json`.
5. **Open in Importer** link or copy `creator_run_id` into Importer URL.

Creator reference: [`creator/reference.md`](creator/reference.md).

---

## 10. Importer — plan, gates, execute, persist

### 10.1 Before you open Importer

- Creator run has approved tests marked **Fit for Xray import**.
- You know **Jira instance** (sandbox vs production), **mapping file**, **project key**, and **Xray folder path**.

Quick reference for project key vs mapping: [`GUIDE.md`](GUIDE.md) Importer sections.

### 10.2 Preview import plan

Studio → **Importer**:

| Control | Purpose |
|---------|---------|
| **Jira instance** | Site + risk tier; production requires `PRODUCTION` confirm |
| **Mapping** | Custom fields, labels, default project (often `TC`) |
| **Project key** | Where **Test** issues are created (`project_key_override`) |
| **Folder path** | Xray Test Repository path |
| **Create folder** | Uses `project.id` from mapping — must match target project |
| **Skip requirement link** | When Jira link step not needed |

**Preview** returns validation per test, credentials summary, and **Reviewer gate** if linked review findings need acknowledgement.

### 10.3 Execute gates (production safety)

| Gate | Behaviour |
|------|-----------|
| **Reviewer gate** | Checkbox + re-preview when plan shows `requires_acknowledgement` |
| **Xray idempotency** | When Studio already has `xray_test_key` for a draft, execute blocked until you **acknowledge** duplicate-key warning |
| **Export preflight redaction** | Email/sensitive URL patterns in tests **block execute** unless `STUDIO_IMPORTER_ALLOW_REDACTION_EXECUTE=1` (emergency only) |
| **Credentials** | `execute_ready` false until Xray + Jira env vars present and validation clean |

### 10.4 Execute paths

1. **Studio → Execute import batch** when `execute_ready` (sandbox first).
2. **Copy Cursor prompt** → run **trinity-importer** or CLI from prompt.
3. **Persist Xray keys** — point to `xray-import-report.json` or report folder + **Creator run id** so Studio metrics and idempotency stay accurate.

Telemetry: [`METRICS.md`](METRICS.md). ADR: [`docs/adr/0002-trinity-importer-telemetry-decisions.md`](../docs/adr/0002-trinity-importer-telemetry-decisions.md).

---

## 11. Who does what (personas P1–P10)

Trinity serves design-time audiences **P1–P10** plus editable runtime prompts. Full matrix: [`personas/P1-P10.md`](personas/P1-P10.md).

| If you are… | Start here |
|-------------|------------|
| **QA engineer (P1)** | This manual §7–10; Reviewer manual for report reading |
| **QA lead (P2)** | Portfolio `index.html`, [`METRICS.md`](METRICS.md) |
| **PM / BA (P3)** | Reviewer readiness + questions; Importer **PM-safe summary** on plan |
| **Automation engineer (P4)** | Creator `automation_fit`, blockers; approved rows for Importer |
| **Skill maintainer (P5)** | Personas, run configs, schemas, [`CONTRACTS.md`](CONTRACTS.md) |
| **Test-data steward (P6)** | Creator prerequisites in batch JSON — not Reviewer |
| **Release manager (P8)** | Epic portfolio bundle; Studio Creator handoff JQL |
| **Security (P9)** | Redaction before share; Importer preflight warnings |
| **Platform / MCP admin (P10)** | Reviewer **Data sources**; dual MCP setup |

Reviewer-only persona table: [`reviewer/MANUAL.md`](reviewer/MANUAL.md) §11.

---

## 12. Files and contracts (operator map)

| Path | Role |
|------|------|
| `reviewer/runs/` | Reviewer outputs (gitignored run folders) |
| `reviewer/config/runs/` | Portfolio configs |
| `studio/data/qa-studio.db` | SQLite — revisions, `studio_qa`, telemetry, Xray keys |
| `studio/data/exports/` | Approved review + creator handoffs |
| `creator/artifacts/` | Creator suite payloads |
| `importer/config/mappings/` | Per-site/project Xray field maps |
| `personas/` | Runtime prompt markdown |

Payload schemas and handoff fields: [`CONTRACTS.md`](CONTRACTS.md).

---

## 13. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Import run fails on epic folder | Folder name ≠ `scope.value` | Rename folder or fix payload key |
| Jira preview empty / stale | Did not **Save draft** after triage | Save, then refresh preview |
| Importer not execute-ready | Missing env, validation errors, gate, idempotency, redaction | Read plan `execute_blockers`; fix tests or acknowledge |
| Reviewer report thin | MCP missing second site, or PDF-only links | [`reviewer/MANUAL.md`](reviewer/MANUAL.md) §12–13; dual MCP doc |
| `createFolder` fails | Mapping `project.id` wrong for selected project key | New mapping file per project — [`GUIDE.md`](GUIDE.md) |
| Studio UI old shell | Legacy static fallback | `cd studio/web && npm run build`; or use :5173 |
| Duplicate Jira comment posted | Double-click post | 24h duplicate warning; acknowledge override if intentional |

More: [`FAQ.md`](FAQ.md) · [`FIRST-RUN.md`](FIRST-RUN.md) troubleshooting table.

---

## 14. Glossary

| Term | Meaning |
|------|---------|
| **Pipeline run** | One imported Reviewer folder (portfolio run id) |
| **Review unit** | One epic inside a pipeline run |
| **studio_qa** | Operator overlay on `review-payload.json` (validity, send_to_epic, comments) |
| **review_ref** | Path to exported review JSON for Creator |
| **Pass type** | `full_sweep`, `rescan_delta`, or `new_epics_only` on portfolio config |
| **execute_ready** | Importer plan flag — all gates and credentials satisfied |
| **Golden** | Style reference corpus for Creator — not Importer project selector |

---

## 15. Validation and sign-off

Before calling a pilot “done,” walk [`TESTING.md`](TESTING.md) end-to-end on sandbox, then one controlled production path (Importer + optional Jira comment) with real keys.

Pilot evidence: capture metrics export from Studio and attach to your program’s GitHub Issue or Confluence page.

---

## 16. Version and publishing

This manual describes Trinity Studio **0.2.x** operator flows (Jira epic comments MVP, Importer execute guards, React UI). When behaviour changes, update this file and [`OPERATOR-SETUP.md`](OPERATOR-SETUP.md), then re-publish [Operator manual (full)](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3750658179/Trinity+Operator+manual+full) under the [QA CoE Trinity tree](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3750559869/Trinity+AI-assisted+QA+pipeline+operator+guide).

Short sectional pages remain in [`confluence/`](confluence/) for wiki navigation; **this document is the canonical long-form manual.**
