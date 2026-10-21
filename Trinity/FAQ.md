# Trinity — FAQ (new operators)

**Wiki:** [Trinity — FAQ](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754164473/Trinity+FAQ) · **Start:** [Start here](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754590489/Trinity+Start+here)

Answers are short on purpose. Follow links for procedures.

---

## Getting started

### Pilot feedback (Oct 2026 wave)

**Through 29 Oct 2026** we’re collecting feedback from a wider internal pilot. Start at [START-HERE.md](START-HERE.md) or the [wiki Start here](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754590489/Trinity+Start+here). File issues: [Trinity pilot feedback](https://github.com/marekwyszynskiappfire/docs/issues/new?template=trinity-pilot-feedback.yml). Leads: [PILOT-SHARE.md](PILOT-SHARE.md).

### What is Trinity?

An **AI-assisted QA pipeline**: **Reviewer** (requirement quality) → **Studio** (human triage) → **Creator** (journey tests) → **Importer** (Xray on Jira). Cursor runs the skills; Studio is the local workbench on your laptop.

### Do I need the git repo?

**Yes.** Clone the docs repo, open **repo root** in Cursor, run Studio from `Trinity/studio/scripts/start.sh`. There is no hosted Trinity SaaS.

### What should I read first?

1. [START-HERE.md](START-HERE.md) (or the wiki **Start here** page).  
2. [FIRST-RUN.md](FIRST-RUN.md) Phases 0 → 3 (canonical tutorial order).  
3. [OPERATOR-ONBOARDING.md](OPERATOR-ONBOARDING.md) for the same steps as sign-off gates.  
4. This FAQ when you hit a question.

QA leads reviewing docs as a newcomer: [NEWBIE-PERSONA-REVIEW.md](NEWBIE-PERSONA-REVIEW.md) and persona [operator-first-time.md](personas/operator-first-time.md).

### Is this only a pilot?

**No for daily work** on an **onboarded product line** — you can run real Epics and import to Xray. **Yes for org-wide “any product, zero setup”** — that is [PATH-TO-1.0.md](PATH-TO-1.0.md) (internal GA). See [Production use vs GA](START-HERE.md#production-use-vs-ga).

### How long does the first Epic take?

~90 minutes first time (MCP + first Reviewer scan). Later Epics ~30–45 minutes if portfolio config already exists.

### Can I use Trinity without Jira?

**Partially.** `seed-demo.sh` + **DEMO-4500** teaches Studio and Creator without live Jira. Reviewer gather and Importer execute need Jira/Xray (or sandbox).

---

## Access and accounts

### What access do I need?

Jira read on Epics; Confluence read if Epics link docs; Xray permission to **create Tests** for import; Jira **API token**; Xray **API keys** for execute. Checklist: [OPERATOR-ONBOARDING.md §0](OPERATOR-ONBOARDING.md#0-before-you-start-access-checklist).

### Sandbox or production first?

**Always sandbox** for first import execute. Use production only after sandbox validation and your QA lead’s policy. Type **PRODUCTION** in Studio only when you mean production Xray.

### Who configures my product line?

**QA lead (P2):** portfolio JQL, `reviewer/config`, Creator golden, Importer **mapping** JSON. You should not invent mapping files without them.

---

## Cursor and skills

### What is Cursor’s role?

**Agent mode** runs long tasks: Jira/Confluence gather, writing `review-payload.json`, generating tests, calling Xray APIs. Studio **copies the prompts** — you paste into chat.

### Do I write my own prompts?

**No.** On the workspace list, open **New portfolio** and use **Run Reviewer in Cursor**. After a workspace exists, use the same action under **Reviewer prompt**, then follow **Next step**. Creator and Importer also have **Run in Cursor** after their gates are satisfied. **Copy prompt** is recovery only. Hand-written prompts cause wrong paths and skipped checks. See [PROMPTS-AND-INPUTS.md](PROMPTS-AND-INPUTS.md).

### How do I install skills?

```bash
./Trinity/scripts/install-trinity-skills.sh
```

Creates symlinks in `~/.cursor/skills/` to `trinity-reviewer`, `trinity-creator`, `trinity-importer`.

### trinity-importer missing after install?

Re-run the install script. If a broken symlink exists, remove it first. Importer requires `Trinity/importer/SKILL.md` in the repo.

### Agent vs Chat?

Use **Agent** for Reviewer portfolio scans, Creator, and Importer execute. Simple questions can use Chat, but pipeline work is Agent.

---

## MCP (Atlassian)

### What is MCP?

Cursor’s connection to **Atlassian Cloud** so the agent can read Jira issues and Confluence pages. Setup: [CURSOR-MCP-SETUP.md](CURSOR-MCP-SETUP.md).

### One MCP or two?

**One** if all your sources are on a single site (e.g. sandbox only). **Two** if Jira is on `appfire.atlassian.net` and Confluence docs are on `appfireteam.atlassian.net` — [DUAL-ATLASSIAN-MCP.md](reviewer/config/DUAL-ATLASSIAN-MCP.md).

### Confluence shows “Unavailable” / cross-site in the report

Dual MCP is incomplete or sites are swapped on consent. Fix: [CURSOR-MCP-SETUP.md § Troubleshooting](CURSOR-MCP-SETUP.md#6-troubleshooting).

### Do I need MCP for Creator or Importer?

**Creator:** no (reads approved files). **Importer:** no for plan preview; execute uses Xray API via `.env` and the skill. **Reviewer gather:** yes (unless you manually paste requirements — not supported for portfolio scale).

### mcp-remote hangs on install

Corporate TLS: `npm_config_strict_ssl=false npm install -g mcp-remote` and use full path from `which mcp-remote` in `~/.cursor/mcp.json`.

---

## Trinity Studio

### URLs?

- UI: **http://127.0.0.1:5173**  
- API: **http://127.0.0.1:8765/api/health**

### Studio won’t start

Check Python 3.11+ and Node 18+. Run `./Trinity/studio/scripts/start.sh` from repo root. Read terminal errors; often missing `npm install` in `Trinity/studio/web`.

### Where is data stored?

Local SQLite under `Trinity/studio/data/` (gitignored). The workspace keeps the approved review export and the Xray plan. **Creator runs** writes `importer-payload.json`. **Record Xray keys** stores keys from `xray-import-report.json`.

### What is DEMO-4500?

A **fake** demo Epic. Never post to production Jira or Xray.

### Save draft before Jira comment?

**Yes.** In **Findings and Jira comment**, **Save draft** before **Jira comment preview** or you see stale text.

### What do readiness buckets mean?

From latest `review-payload.json` → `report.qa_planning_fit`: **ready** (fit), **ready with reservations** (provisional / warnings), **not ready** (not_fit). [METRICS.md](METRICS.md).

### Statistics page — compare runs?

Pick a run, then up to four more in dropdowns (Run 1 = baseline). [MANUAL.md](MANUAL.md) §5.9.

---

## Reviewer

### Epic folder name rule?

**Folder name must equal the Jira Epic key**, e.g. `ONE-228469/review-payload.json`.

### Where do Reviewer outputs go?

`Trinity/reviewer/runs/.../<EPIC-KEY>/` — gitignored; import into Studio after scan. Pass the folder that **directly contains** `<EPIC-KEY>/` (may be `runs/<portfolio_id>` or a dated subfolder).

### How do I import a run?

A finished Reviewer prints a workspace URL and imports the payloads. Open that URL.

If it did not:

```bash
./Trinity/studio/scripts/import-run.sh Trinity/reviewer/runs/<folder-that-directly-contains-EPIC-KEY>
```

Then expand **Import a review folder** on the workspace list. **Import and open** opens that workspace.

### Reviewer stopped halfway

Re-run **Prompt 1** from Studio; skill resumes using existing folders. Do not rename epic folders mid-run.

### Resolve from scope greyed out?

Add `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_BASE_URL` to `Trinity/studio/.env`, or use **Copy JQL resolve prompt**.

---

## Creator

### How many tests per Epic?

Default **3–5 E2E journey** tests (not exhaustive regression). Edit/reject in Studio; use rejection reasons for metrics.

### Creator writes to Xray?

**No.** Only **Importer** creates Xray Tests after you approve and export.

### Where is the Creator batch file?

Under `Trinity/creator/artifacts/<batch>/suite-payload.json` — path is in the prompt. The workspace imports that file when it appears. On the Epic, **Import a suite file** is the fallback.

---

## Importer and Xray

### Why does the UI default project **TC**?

Shipped mappings target the QA Test project used for golden exports. Override **project key** in Importer; if fields differ, you need another **mapping file** — [GUIDE.md](GUIDE.md).

### I changed project key but import failed on custom fields

**Mapping JSON** defines required fields, not the project key alone. Ask QA lead for the correct mapping for your project.

### Project key vs Xray folder?

**Project key** = Jira project for new Test issues. **Folder path** = Xray Test Repository location (not the same thing).

### Preview vs execute?

Always **Preview import plan** first. Execute only in sandbox until validated; production requires typing **PRODUCTION**.

### Where do Xray credentials go?

`Trinity/studio/.env` — `XRAY_CLIENT_ID` and `XRAY_CLIENT_SECRET` for the **same Jira site** as Importer instance.

---

## Prompts (cheat sheet)

| # | Click in Studio | Output |
|---|-----------------|--------|
| 1 | Workspace → Reviewer prompt → Run Reviewer in Cursor | `review-payload.json` |
| 1b | Copy JQL resolve prompt (optional) | Epic key list |
| 2 | Workspace → Run Creator in Cursor | `suite-payload.json` |
| 3 | Workspace → Plan Xray import → Run Importer in Cursor | Xray Tests |

Detail: [PROMPTS-AND-INPUTS.md](PROMPTS-AND-INPUTS.md).

---

## Quality, safety, and metrics

### Does approving an epic update the JSON in the Reviewer run folder?

**No.** **Approve** is stored in Studio SQLite (`approved_revision_id`). The files under `Trinity/reviewer/runs/.../ONE-*/review-payload.json` stay as imported until you re-run Reviewer or re-import.

Preparing the Creator handoff on the workspace writes an approved snapshot to `Trinity/studio/data/exports/{run_id}/{EPIC_KEY}/review-payload.json` — that path is the **`review_ref`** in the Creator prompt. **Approve & export** on the unit page writes the same snapshot.

**In Creator** on the run page is separate: it only drives run-level handoff JQL (`include_in_creator`), not approval. See [MANUAL.md §7.5.1](MANUAL.md#751-what-changes-on-disk-vs-in-studio-approval-handoff).

### Can AI import without my approval?

**No.** You approve Epics and tests in Studio. Importer execute is a deliberate step (with production guard).

### How is quality measured?

Studio approve/reject, telemetry summary (`/api/telemetry/summary`), pipeline Statistics, scorecard exports — [METRICS.md](METRICS.md).

### Where are decisions documented?

Importer/telemetry: ADR 0002 in repo `docs/adr/`. Backlog: GitHub Issues on docs repo.

---

## Troubleshooting

| Problem | Try |
|---------|-----|
| Grey MCP tools | Re-auth; [CURSOR-MCP-SETUP.md](CURSOR-MCP-SETUP.md) |
| Health check fails | Restart `start.sh`; port 8765 free |
| Import run empty | Epic folder names vs keys in scope |
| All units “not ready” | Re-import after payload update; check `qa_planning_fit` |
| Strict render errors | `python3 Trinity/reviewer/scripts/render_report.py <payload> --strict` |
| Preflight FAIL | `./Trinity/scripts/pilot-preflight.sh` output lines |

Full recovery table: [OPERATOR-ONBOARDING.md §6](OPERATOR-ONBOARDING.md#6-failure-recovery).

---

## Confluence and documentation

### Where is documentation for my team?

**QACoE Confluence** under [Trinity hub](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3750559869/Trinity+AI-assisted+QA+pipeline+operator+guide). **Entry point:** [Start here](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754590489/Trinity+Start+here).

### Git vs wiki?

**Git is source of truth.** Maintainers run `python3 Trinity/scripts/sync_confluence_from_git.py` after edits. Page list: [confluence/README.md](confluence/README.md).

### Wiki looks like a code block?

Markdown conversion failed once; re-run sync with valid API token. Git markdown is always readable.

---

## Who to contact

| Topic | Contact |
|-------|---------|
| Product mapping / portfolio scope | QA lead (P2) |
| MCP / machine policy | Platform admin (P10) |
| Bug or doc gap | GitHub Issue `trinity-support` |
| “Is my product onboarded?” | QA lead — see [PATH-TO-1.0.md](PATH-TO-1.0.md) |

When asking for help, include: **portfolio id**, **Epic key**, **sandbox vs prod**, screenshot of Studio error, and whether MCP verify passed.

---

## Legacy capability tables

### End-to-end capabilities

| Capability | How | Doc |
|------------|-----|-----|
| Tests from requirements | Reviewer → Creator | [creator/SKILL.md](creator/SKILL.md) |
| Xray persist | Importer | [importer/SKILL.md](importer/SKILL.md) |
| Human control | Studio | [MANUAL.md](MANUAL.md) |

### Quality controls

| Area | Mechanism |
|------|-----------|
| Granularity | Golden v2 + Studio reject reasons |
| Requirements quality | Reviewer findings + approve gate |
| Production safety | PRODUCTION confirmation, preview plan |
