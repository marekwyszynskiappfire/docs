# Trinity — first run playbook

**Audience:** Someone using Trinity for the **first time**. Follow the phases **in order**. You do not need to read the whole repo — only this page until Phase 2.

**New operators (wiki):** [Start here](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754590489/Trinity+Start+here) · [FAQ](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754164473/Trinity+FAQ)

**Setup without a buddy:** [`OPERATOR-ONBOARDING.md`](OPERATOR-ONBOARDING.md) — gates, MCP, prompts, [`OPERATOR-VALIDATION.md`](OPERATOR-VALIDATION.md) sign-off.

| Phase | Time (after deps) | Needs Jira/MCP? | Outcome |
|-------|-------------------|-----------------|---------|
| **0** Checkout | 5–15 min first `start.sh` | No | Studio running |
| **1** Demo Studio | ~10 min | No | You know where every button lives |
| **2** Wire Cursor | ~20 min once | MCP + optional `.env` | Ready for a real epic |
| **3** One epic E2E | 1–3 hours | Yes | Review → tests → Xray plan (or execute) |

Deep reference later: [`MANUAL.md`](MANUAL.md) · Architecture: [`ARCHITECTURE.md`](ARCHITECTURE.md) · Checklist: [`OPERATOR-SETUP.md`](OPERATOR-SETUP.md) · Validation: [`TESTING.md`](TESTING.md) · Prompt I/O: [`PROMPTS-AND-INPUTS.md`](PROMPTS-AND-INPUTS.md).

**Confluence (QACoE):** [Start here](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754590489/Trinity+Start+here) · [FAQ](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754164473/Trinity+FAQ) · [First run](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3750592672/Trinity+First+run+playbook) · [Onboarding](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3755311111/Trinity+Operator+onboarding) · [Manual](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3750658179/Trinity+Operator+manual)

---

## Golden rules (read once)

1. **Follow Next step on the workspace.** Expand **Portfolio** to change scope, persona, and pass type, then **Reviewer prompt** to copy the Cursor prompt. Create the first portfolio from **New portfolio** on the workspace list. Do not invent prompts by hand unless Studio is down.
2. **Epic folder name = Jira epic key** — e.g. `ONE-228469/review-payload.json`, not a random folder name.
3. **Jira comments stay on the open Epic.** Expand **Findings and Jira comment**, then **Save draft** before **Jira comment preview**.
4. **Demo epic `DEMO-4500` is fake** — never post it to production Jira or Xray.
5. **Sandbox first** — type `PRODUCTION` in Studio only when you mean production Jira/Xray.

```mermaid
flowchart LR
  subgraph phase0 [Phase 0]
    clone[Clone repo]
    start[Start Studio]
  end
  subgraph phase1 [Phase 1 no Jira]
    seed[seed-demo.sh]
    click[Click through UI]
  end
  subgraph phase2 [Phase 2 once]
    skills[install-trinity-skills]
    mcp[Atlassian MCP]
    env[optional .env]
  end
  subgraph phase3 [Phase 3 per epic]
    p1[Prompt 1 Reviewer]
    studio1[Open workspace]
    p2[Copy Creator prompt]
    studio2[Review tests]
    p3[Plan Xray import]
  end
  clone --> start --> seed --> click
  click --> skills --> mcp --> env
  env --> p1 --> studio1 --> p2 --> studio2 --> p3
```

---

## Phase 0 — Checkout and start Studio

All commands from **repo root** (folder that contains `Trinity/`).

### 0.1 Clone

```bash
git clone https://github.com/marekwyszynskiappfire/docs.git DOCS
cd DOCS
```

### 0.2 Check tools

```bash
python3 --version   # need 3.11+
node --version      # need 18+
```

### 0.3 Optional smoke (30 seconds, no Jira)

```bash
python3 Trinity/reviewer/scripts/render_report.py \
  Trinity/reviewer/samples/demo-epic.payload.json --strict
```

Exit code `0` = Python side OK.

### 0.4 Start Studio (leave terminal open)

```bash
./Trinity/studio/scripts/start.sh
```

First run installs dependencies (**often 3–8 minutes**). When ready:

```bash
curl -sf http://127.0.0.1:8765/api/health
```

Open in browser: **http://127.0.0.1:5173**

| URL | What |
|-----|------|
| http://127.0.0.1:5173 | Studio UI (primary) |
| http://127.0.0.1:8765 | API only |

Ports busy: `./Trinity/studio/scripts/stop.sh` then `STUDIO_FORCE=1 ./Trinity/studio/scripts/start.sh`

**Stop here if the health check fails** — see [Troubleshooting](#troubleshooting) at the bottom.

---

## Phase 1 — Learn Studio (no Cursor, no Jira)

**Goal:** Open the workspace once so Phase 3 is muscle memory.

### 1.1 Load demo data

Second terminal, repo root:

```bash
./Trinity/studio/scripts/seed-demo.sh
```

Refresh **http://127.0.0.1:5173**. The home page lists the demo run.

### 1.2 Open the workspace

1. On the demo run row, click **Open workspace**.
2. You see epic **`DEMO-4500`** (fictional), a four-stage stepper, and one **Next step** card.
3. Open the Epic and skim the verdict. You do **not** need to approve it for the demo.
4. **Process help** explains the four stages: assess testability, draft tests, review tests, import to Xray.

### 1.3 The rest of the top bar

| Control | Use it for |
|---------|------------|
| **Workspace** | The page you just opened. This is the normal path. |
| **Personas** | Role prompts. The list shows the heading inside each file; the filename stays above the editor. |
| **Statistics** | Single-run report, or compare 2–5 runs. |
| **More** | Dashboard, Creator, Importer, and Reviewer configs. Use these when the workspace does not cover the step. |

**Phase 1 done** when you can find **Next step**, the Epic, and **More**.

---

## Phase 2 — Wire Cursor (once per machine)

Do this before a **real** epic. Skip if you only demo Studio for now.

### 2.1 Install Trinity skills

```bash
./Trinity/scripts/install-trinity-skills.sh
```

In Cursor you should be able to invoke:

- **trinity-reviewer**
- **trinity-creator**
- **trinity-importer**

### 2.2 Atlassian MCP

Reviewer needs Jira/Confluence read access. Start with **[`CURSOR-MCP-SETUP.md`](CURSOR-MCP-SETUP.md)** (sandbox single-site vs production dual-site). If your org uses two Cloud sites (common at Appfire), configure **both**:

[`reviewer/config/DUAL-ATLASSIAN-MCP.md`](reviewer/config/DUAL-ATLASSIAN-MCP.md)

**Quick check:** after a small Reviewer gather, open the HTML report → **Data sources** should show *Analyzed*, not *Unavailable* for links you expect.

### 2.3 Studio `.env` (for Jira list, comments, Xray execute)

```bash
cp Trinity/studio/.env.example Trinity/studio/.env
```

Edit at minimum for **live** work:

| Variable | When you need it |
|----------|------------------|
| `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` | Jira epic comments, project list on Importer, optional JQL resolve |
| `XRAY_CLIENT_ID`, `XRAY_CLIENT_SECRET` | Importer **Execute import batch** |

Restart Studio after editing `.env`:

```bash
./Trinity/studio/scripts/stop.sh
./Trinity/studio/scripts/start.sh
```

Production Xray: also `Trinity/studio/.env.production` (see [`GUIDE.md`](GUIDE.md)).

---

## Phase 3 — One real epic, end to end

Replace **`YOUR-EPIC-KEY`** with one sandbox **Epic** key (e.g. `ONE-12345`). One epic per first run — do not multi-task.

### 3.1 Create portfolio config in Studio

1. On the workspace list, open **New portfolio**.
2. Duplicate or edit [`example.demo-portfolio`](reviewer/config/runs/example.demo-portfolio.json):
   - **portfolio_id** — pick a stable name, e.g. `my-first-portfolio`.
   - **scope kind** — start with **`epic_keys`**.
   - **scope value** — `YOUR-EPIC-KEY` (one key only for first run).
   - **pass_type** — `full_sweep`.
3. **Save** (writes `Trinity/reviewer/config/runs/my-first-portfolio.json`).

**If scope is JQL or a filter URL instead of keys:**

1. Click **Copy JQL resolve prompt** → paste in **new Cursor chat** → run MCP search.
2. Paste returned epic keys into **Resolved epic keys** → **Save pasted keys**.
3. Then continue with **Copy Cursor prompt** below.

### 3.2 Prompt #1 — Reviewer (first Cursor prompt)

1. After the review is imported, open the workspace and expand **Reviewer prompt** → **Copy Cursor prompt**. Before that folder exists, use **Copy Reviewer prompt** on **New portfolio**.
2. Open **new Cursor chat** (fresh context).
3. Paste the prompt → send.

The prompt tells the agent to run **trinity-reviewer** with your `portfolio_id`, scope, and persona. **You do not need to type `scan YOUR-EPIC-KEY`** if the pasted prompt is complete — follow what the agent asks; confirm scope if it interviews you.

**Wait until the agent finishes.** You should get files like:

```text
Trinity/reviewer/runs/.../YOUR-EPIC-KEY/review-payload.json
Trinity/reviewer/runs/.../YOUR-EPIC-KEY/review-report.html   (optional)
```

The agent may write under `runs/<portfolio_id>/` or `runs/<portfolio_id>/<dated-portfolio_run_id>/` — both are valid.

The agent finishes by printing a **workspace URL**. Open that URL. Importing the same payloads again does not add another review revision.

If no URL was printed, expand **Import a review folder** on the workspace list. The folder must directly contain `YOUR-EPIC-KEY/`. **Import and open** opens that workspace.

```bash
./Trinity/studio/scripts/import-run.sh Trinity/reviewer/runs/<folder-that-contains-YOUR-EPIC-KEY>
```

### 3.3 Workspace — verdict and Creator prompt

Stay on the workspace.

| Step | Action |
|------|--------|
| 1 | Read the testability verdict and the blocker questions on the Epic |
| 2 | **Next step → Approve** when the verdict is right |
| 3 | **Next step → Prepare Creator prompt**, then **Copy Creator prompt** |
| 4 | Paste that prompt into a **new Cursor chat** |

Finding-by-finding triage and the Jira epic comment are on the open Epic: expand **Findings and Jira comment**. **Save draft** there before a comment preview. Post only to the **sandbox** epic, never `DEMO-4500`.

If the Epic is not testable yet, fix the scope in Jira and re-run Reviewer, or pick another Epic.

### 3.4 Prompt #2 — Creator (second Cursor prompt)

1. **New Cursor chat** (recommended).
2. Paste the prompt you copied from the workspace.
3. Run **trinity-creator** per the prompt (`review_ref`, epic key, `suite_mode: release_slice_e2e`).

**Wait until done.** Output path is usually:

```text
Trinity/creator/artifacts/YOUR-EPIC-KEY/suite-payload.json
```

For a **multi-epic** Reviewer portfolio (e.g. `q4-backlog`):

```text
Trinity/creator/artifacts/q4-backlog/ONE-{number}/suite-payload.json
```

One file per Epic. The workspace imports the file for the Epic you are on. See [`creator/artifacts/README.md`](creator/artifacts/README.md). Portfolio programs: [`creator/config/portfolios/`](creator/config/portfolios/).

(path is also in the Studio prompt).

### 3.5 Workspace — review the tests

Stay on the same workspace. When `suite-payload.json` appears, Studio imports it. If the card is still waiting, click **Check for the file now**.

| Step | Action |
|------|--------|
| 1 | Open the Epic and read the journey tests |
| 2 | **Approve** or **Reject** each test. A rejection needs a reason |
| 3 | Mark the approved tests for Xray import |
| 4 | **Next step → Plan Xray import** |

On the Epic, expand **Import a suite file** when the suite was written to a different path. One file per Epic.

### 3.6 Workspace — Xray plan

The import panel is on the same page.

1. **Jira instance** — sandbox first.
2. **Mapping file** — the mapping your QA lead gave you.
3. **Project key** — where Test issues are created (often `TC`; see [`GUIDE.md`](GUIDE.md)).
4. **Folder path** — Xray Test Repository folder, e.g. `/Trinity imports/YOUR-EPIC-KEY`.
5. **Preview import plan** — read validation. Fix test errors in the Epic above, then preview again.
6. If the plan asks for a Reviewer-gate or idempotency confirmation, check it and preview again.
7. **Write to Xray** when the plan says it is ready.

**Production:** type `PRODUCTION` before preview or write. Use the production `.env` and mapping policy in [`GUIDE.md`](GUIDE.md).

### 3.7 Prompt #3 — Importer in Cursor (when you do not write from the workspace)

1. On the workspace, preview the plan, then expand **Importer Cursor prompt**.
2. New Cursor chat → paste → run **trinity-importer**.
3. Back on the workspace, expand **Record Xray keys** and point it at `xray-import-report.json`.

**Phase 3 done** for one epic.

---

## What to do on the second epic

1. **More → Reviewer configs** → same `portfolio_id`, update scope or use `new_epics_only` / `rescan_delta`.
2. Open the workspace and expand **Reviewer prompt** → **Copy Cursor prompt** again. A return visit should skip the full interview.
3. Open the workspace URL the agent prints, and repeat from §3.3.

The run page under **More → Dashboard** still has bulk **In Creator**, **Copy JQL**, and the handoff JSON for multi-epic planning.

---

## Prompt cheat sheet

| # | When | Where to get it | Cursor skill |
|---|------|-----------------|--------------|
| **1** | This portfolio already has a workspace | Workspace → **Reviewer prompt** → **Copy Cursor prompt** | trinity-reviewer |
| **1a** | Before any review exists in Studio | Workspace list → **New portfolio** → **Copy Reviewer prompt** | trinity-reviewer |
| **1b** | JQL/filter scope only | **Copy JQL resolve prompt** | MCP in Cursor (not a skill) |
| **2** | After you approve the review | Workspace **Next step → Copy Creator prompt** | trinity-creator |
| **3** | You are writing through Cursor instead of the workspace | Workspace → preview the plan → **Importer Cursor prompt** | trinity-importer |

---

## Studio map (one sentence per area)

| Nav | Use it for |
|-----|------------|
| **Workspace** | One portfolio: verdict, Creator prompt, test review, Creator runs, Xray plan |
| **Personas** | Edit role prompts. The list shows the heading in the file |
| **Statistics** | Single-run E2E report; compare 2–5 runs (baseline = Run 1 dropdown) |
| **Workspace list** | **New portfolio**, then import a review folder and open that workspace |
| **More → Reviewer configs** | Every portfolio; JQL resolve and new-epics list |
| **More → Creator** | Every Creator run, and a suite path the workspace Epic does not show |
| **More → Importer** | Payload-path import and the page execute |
| **Run page / unit page** | Bulk handoff, finding triage, Jira epic comments |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Empty Dashboard after import | Wrong folder — must contain `YOUR-EPIC-KEY/review-payload.json` |
| Import error folder ≠ epic | Rename folder to match `scope.value` in JSON |
| Reviewer thin / missing Confluence | Fix MCP — [`DUAL-ATLASSIAN-MCP.md`](reviewer/config/DUAL-ATLASSIAN-MCP.md) |
| Jira preview wrong | **Save draft** after triage |
| Importer not execute-ready | Open plan message — credentials, validation, gates, idempotency |
| `start.sh` slow | Normal first time; wait for `npm ci` / pip |

Reset demo only: `rm Trinity/studio/data/qa-studio.db` → restart → `seed-demo.sh`.

---

## After your first epic

- Read [`MANUAL.md`](MANUAL.md) for edge cases and roles.
- Walk [`TESTING.md`](TESTING.md) before pilot sign-off.
- Portfolio HTML and multi-epic: [`reviewer/MANUAL.md`](reviewer/MANUAL.md).
- **Mateusz POC evidence:** update [`SCORECARD.md`](SCORECARD.md) pilot log; run `./Trinity/scripts/export-telemetry.sh` while Studio is up.

**Last reviewed:** 2026-10-20
