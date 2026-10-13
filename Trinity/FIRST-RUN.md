# Trinity — first run playbook

**Audience:** Someone using Trinity for the **first time**. Follow the phases **in order**. You do not need to read the whole repo — only this page until Phase 2.

| Phase | Time (after deps) | Needs Jira/MCP? | Outcome |
|-------|-------------------|-----------------|---------|
| **0** Checkout | 5–15 min first `start.sh` | No | Studio running |
| **1** Demo Studio | ~10 min | No | You know where every button lives |
| **2** Wire Cursor | ~20 min once | MCP + optional `.env` | Ready for a real epic |
| **3** One epic E2E | 1–3 hours | Yes | Review → tests → Xray plan (or execute) |

Deep reference later: [`MANUAL.md`](MANUAL.md) · Checklist: [`OPERATOR-SETUP.md`](OPERATOR-SETUP.md) · Validation: [`TESTING.md`](TESTING.md).

---

## Golden rules (read once)

1. **Prompts come from Studio** — use **Copy Cursor prompt**, **Send to Creator**, or Importer **Copy Cursor prompt**. Do not invent prompts by hand unless Studio is down.
2. **Epic folder name = Jira epic key** — e.g. `ONE-228469/review-payload.json`, not a random folder name.
3. **Save draft** on the unit page before **Jira comment preview** or you will see stale text.
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
    studio1[Import + triage]
    p2[Prompt 2 Creator]
    studio2[Approve tests]
    p3[Prompt 3 Importer]
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
git clone <your-docs-repo-url> DOCS
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

**Goal:** Click through the product once so Phase 3 is muscle memory.

### 1.1 Load demo data

Second terminal, repo root:

```bash
./Trinity/studio/scripts/seed-demo.sh
```

Refresh Studio **Dashboard** — you should see a pipeline run.

### 1.2 Dashboard → open the run

1. Click the imported **pipeline run** row.
2. You see epic unit **`DEMO-4500`** (fictional).

### 1.3 Unit page (review UI)

1. Click **`DEMO-4500`**.
2. Skim findings and questions (read-only practice).
3. You do **not** need to triage for the demo; notice **Save draft**, **Approve & export for Creator**, **Send to Creator**, **Jira epic comment** panel.

### 1.4 Creator tab

1. Top nav → **Creator**.
2. **Import** batch path: `Trinity/creator/samples/demo-story.suite.json`
3. Open the new **creator run** → approve/reject a test → toggle **Fit for Xray import** (practice only).

### 1.5 Importer tab

1. Top nav → **Importer**.
2. Choose any **Jira instance** in the dropdown (UI works without `.env`).
3. Click **Preview import plan** if you have a creator run linked — or skip if the form is empty.
4. You are **not** executing Xray in Phase 1.

**Phase 1 done.** You know: Dashboard, run page, unit page, Creator, Importer.

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

Reviewer needs Jira/Confluence read access. If your org uses two sites (common at Appfire), configure **both**:

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

1. Studio → **Reviewer configs**.
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

1. Still on **Reviewer configs** → click **Copy Cursor prompt**.
2. Open **new Cursor chat** (fresh context).
3. Paste the prompt → send.

The prompt tells the agent to run **trinity-reviewer** with your `portfolio_id`, scope, and persona. **You do not need to type `scan YOUR-EPIC-KEY`** if the pasted prompt is complete — follow what the agent asks; confirm scope if it interviews you.

**Wait until the agent finishes.** You should get files like:

```text
Trinity/reviewer/runs/my-first-portfolio/<run-subfolder>/YOUR-EPIC-KEY/review-payload.json
Trinity/reviewer/runs/.../YOUR-EPIC-KEY/review-report.html   (optional)
```

The prompt ends with an **import command** — keep that path.

### 3.3 Import into Studio

In terminal (use the path from the agent or from the prompt footer):

```bash
./Trinity/studio/scripts/import-run.sh Trinity/reviewer/runs/my-first-portfolio/<run-subfolder>
```

Or Dashboard → **Import Reviewer run** → paste that folder path.

Refresh **Dashboard** → open the run → open unit **`YOUR-EPIC-KEY`**.

### 3.4 Studio — triage and approve (no Cursor)

On the **unit page**, in order:

| Step | Action |
|------|--------|
| 1 | Skim gate, readiness, findings, questions |
| 2 | For each item: set **valid** / **discuss** / **invalid**; check **Include in epic feedback** only where PO should see it |
| 3 | **Save draft** |
| 4 | Optional: open **review-report.html** link if shown |
| 5 | Optional: **Jira epic comment** → Refresh preview → fix redaction warnings → post to **sandbox** epic (not `DEMO-4500`) |
| 6 | **Approve & export for Creator** |
| 7 | **Send to Creator** — copies **Prompt #2** to clipboard |

If **Send to Creator** is disabled: epic is **`not_fit`** — fix scope in Jira and re-run Reviewer, or pick another epic.

### 3.5 Prompt #2 — Creator (second Cursor prompt)

1. **New Cursor chat** (recommended).
2. Paste **Prompt #2** from **Send to Creator**.
3. Run **trinity-creator** per the prompt (`review_ref`, epic key, `suite_mode: release_slice_e2e`).

**Wait until done.** Output path is usually:

```text
Trinity/creator/artifacts/YOUR-EPIC-KEY/suite-payload.json
```

(path is also in the Studio prompt).

### 3.6 Studio — Creator triage

| Step | Where | Action |
|------|--------|--------|
| 1 | **Creator** tab | Import `suite-payload.json` (path from agent) |
| 2 | Open **creator run** | Read 3–5 journey tests |
| 3 | Per test | Edit if needed → **Approve** or **Reject** |
| 4 | Approved rows | Check **Fit for Xray import** |
| 5 | Creator run page | **Export for Importer** |

Optional: **Open in Importer** link on the creator run.

### 3.7 Studio — Importer plan (third prompt or execute)

1. **Importer** tab (or URL with `?creator_run_id=...`).
2. **Jira instance** — sandbox first.
3. **Mapping file** — default production/sandbox mapping for your site.
4. **Project key** — where Test issues are created (often `TC`; see [`GUIDE.md`](GUIDE.md)).
5. **Folder path** — Xray Test Repository folder, e.g. `/Trinity imports/YOUR-EPIC-KEY`.
6. **Preview import plan** — read validation; fix any errors in tests back on Creator run.
7. If **Reviewer gate** or **idempotency** panels appear → check acknowledgement → **Preview** again.
8. Choose one path:
   - **Sandbox learning:** **Copy Cursor prompt** → **Prompt #3** in new Cursor chat → run importer skill/CLI → paste report path → **Persist Xray keys** in Studio.
   - **Studio execute:** when `execute_ready` and sandbox creds OK → **Execute import batch** → then persist keys if needed.

**Production:** type `PRODUCTION` in the Importer form before preview/execute; use production `.env` / mapping policy per [`GUIDE.md`](GUIDE.md).

### 3.8 Prompt #3 — Importer (when not using Studio execute)

1. After **Preview import plan** → **Copy Cursor prompt**.
2. New Cursor chat → paste → run **trinity-importer** (or commands inside the prompt).
3. Back in Studio → **Persist Xray keys** with path to `xray-import-report.json` and your **creator run id**.

**Phase 3 done** for one epic.

---

## What to do on the second epic

1. **Reviewer configs** → same `portfolio_id`, update scope or use `new_epics_only` / `rescan_delta`.
2. **Copy Cursor prompt** again (Prompt #1) — return visit should skip full interview.
3. Repeat Phase 3.3–3.8.

Run-level shortcuts: Dashboard → **run page** → bulk **In Creator**, **Copy JQL**, handoff JSON for multi-epic planning.

---

## Prompt cheat sheet

| # | When | Where to get it | Cursor skill |
|---|------|-----------------|--------------|
| **1** | Before any review exists in Studio | **Reviewer configs** → **Copy Cursor prompt** | trinity-reviewer |
| **1b** | JQL/filter scope only | **Copy JQL resolve prompt** | MCP in Cursor (not a skill) |
| **2** | After approve on unit page | **Send to Creator** | trinity-creator |
| **3** | After Importer preview | **Copy Cursor prompt** on Importer | trinity-importer |

---

## Studio map (one sentence per area)

| Nav | Use it for |
|-----|------------|
| **Dashboard** | Import runs; open pipeline runs |
| **Personas** | Edit Reviewer/Creator tone (maintainers) |
| **Reviewer configs** | Portfolio JSON; **Prompt #1** |
| **Run page** | Which epics go to Creator; JQL/handoff export |
| **Unit page** | Triage; approve; **Prompt #2**; Jira comments |
| **Creator** | Import suites; approve tests; export for Importer |
| **Importer** | Plan; **Prompt #3** or execute; persist Xray keys |

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

**Last reviewed:** 2026-10-13
