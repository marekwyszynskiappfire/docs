# Trinity — operator onboarding

**Wiki:** [Trinity — Operator onboarding](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3755311111/Trinity+Operator+onboarding) · **Hub:** [Start here](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754590489/Trinity+Start+here)

**Goal:** A new operator with **Jira + Xray access** can complete **demo → real Epics → Xray import** without a buddy, using this doc, the [FAQ](FAQ.md), and **Studio-generated prompts only**.

**Time budget:** ~90 minutes first time (MCP auth and first portfolio scan dominate). Repeat runs: ~30–45 minutes per Epic batch.

**Learning order (first day):** Follow [FIRST-RUN.md](FIRST-RUN.md) Phases **0 → 1 → 2 → 3** (Studio demo before MCP). Sections below use **gate numbers** for [OPERATOR-VALIDATION.md](OPERATOR-VALIDATION.md) sign-off — same steps, grouped for checklist use.

| Companion | Use when |
|-----------|----------|
| [FAQ](FAQ.md) | Quick answers — read before asking in chat |
| [PROMPTS-AND-INPUTS.md](PROMPTS-AND-INPUTS.md) | Every Studio **Copy prompt** |
| [CURSOR-MCP-SETUP.md](CURSOR-MCP-SETUP.md) | MCP decision tree + `mcp.json` |
| [PREFLIGHT.md](PREFLIGHT.md) | Short smoke list |
| [MANUAL.md](MANUAL.md) | Deep reference in Studio |
| [OPERATOR-VALIDATION.md](OPERATOR-VALIDATION.md) | QA lead sign-off after sandbox |

---

## 0. Before you start (access checklist)

Complete every row **before** MCP setup. Missing access → stop and contact QA lead (P2) or platform admin (P10).

| # | Requirement | How to verify |
|---|-------------|----------------|
| 1 | **Git** clone of the docs repo | `git status` at repo root |
| 2 | **Cursor** desktop (Agent mode) | Open repo root as workspace |
| 3 | **Python 3.11+** | `python3 --version` |
| 4 | **Node 18+** | `node --version` |
| 5 | **Jira** read on target Epics | Open an Epic in browser |
| 6 | **Confluence** read if Epics link cross-site docs | Dual MCP — [CURSOR-MCP-SETUP.md](CURSOR-MCP-SETUP.md) |
| 7 | **Xray** create Tests (import path) | Test Repository visible in Jira |
| 8 | **Jira API token** | [Atlassian API tokens](https://id.atlassian.com/manage-profile/security/api-tokens) |
| 9 | **Xray API keys** | Jira → Apps → Xray → Settings → API Keys |

**Sandbox vs production**

| Profile | Jira site | When to use |
|---------|-----------|-------------|
| **Learning** | `appfire-sandbox-774.atlassian.net` | First runs; no production Test pollution |
| **Production** | `appfire.atlassian.net` | After sandbox validation |

Match Studio Importer and `Trinity/studio/.env` to your profile ([`studio/.env.example`](studio/.env.example)).

---

## 1. Machine setup (no Jira yet)

### 1.1 Clone and open Cursor

```bash
git clone https://github.com/marekwyszynskiappfire/docs.git DOCS
cd DOCS
```

**File → Open Folder** → `DOCS` (repo root).

### 1.2 Start Studio

```bash
./Trinity/studio/scripts/start.sh
```

Verify: `curl -sf http://127.0.0.1:8765/api/health` · UI **http://127.0.0.1:5173**

**Gate 1 (partial):** Health `ok` · Dashboard loads.

---

## 2. Demo path (~15 min, no MCP gather)

Do this **before** MCP so you know where buttons live ([FIRST-RUN.md](FIRST-RUN.md) Phase 1).

```bash
./Trinity/studio/scripts/seed-demo.sh
```

Dashboard → **DEMO-4500** → Creator → import `Trinity/creator/samples/demo-story.suite.json` → Importer preview.

**Gate 4:** Skim unit · import Creator batch · read Importer plan (execute not required).

Nav: `Dashboard → Run → Unit → Creator → Importer → Statistics`

---

## 3. Wire Cursor (once per machine)

### 3.1 Install Trinity skills

```bash
./Trinity/scripts/install-trinity-skills.sh
```

Symlinks: `~/.cursor/skills/trinity-reviewer`, `trinity-creator`, `trinity-importer`.

| Skill | How to run |
|-------|------------|
| Reviewer | Workspace list → **New portfolio** → **Copy Reviewer prompt**. After a workspace exists, **Reviewer prompt** → **Copy Cursor prompt** (do not hand-write) |
| Creator | Workspace **Next step → Copy Creator prompt** |
| Importer | Workspace **Plan Xray import**, then **Importer Cursor prompt** after a preview. **More → Importer** for the full page |

**Gate 1 (complete):** Skills linked · `./Trinity/scripts/pilot-preflight.sh` passes.

### 3.2 Cursor MCP (Atlassian)

Follow **[CURSOR-MCP-SETUP.md](CURSOR-MCP-SETUP.md)** end to end.

| Epics use… | MCP profile |
|------------|-------------|
| Sandbox only | **Single-site** |
| Prod Jira + `appfireteam` Confluence | **Dual-site** — [DUAL-ATLASSIAN-MCP.md](reviewer/config/DUAL-ATLASSIAN-MCP.md) |

Verify in Agent chat: `getAccessibleAtlassianResources` → expected site URL(s).

**Gate 2:** MCP authorised · no grey tools in Cursor Settings → MCP.

### 3.3 Studio `.env` (live Jira)

```bash
cp Trinity/studio/.env.example Trinity/studio/.env
```

Restart Studio after edits. Without `.env`, use **Copy JQL resolve prompt** ([PROMPTS-AND-INPUTS.md](PROMPTS-AND-INPUTS.md) §1b).

**Gate 3:** `.env` matches the target Jira site. The workspace import panel lists that instance.

---

## 4. Real Epic — end to end

1. Workspace list → **New portfolio** — portfolio JSON under `Trinity/reviewer/config/runs/`.
2. **Prompt 1** — Copy Cursor prompt → Agent → `reviewer/runs/.../<EPIC>/review-payload.json`. Open the workspace URL the agent prints.
3. **Fallback import** — only when that URL was not printed. Pass the folder that **directly contains** `<EPIC>/`:

   `./Trinity/studio/scripts/import-run.sh Trinity/reviewer/runs/<folder-with-epic-keys>`
4. **Verdict** — read it on the workspace and approve when it is right ([MANUAL.md](MANUAL.md) §2).
5. **Prompt 2** — Copy Creator prompt. The workspace imports `suite-payload.json`. Approve the tests and mark Send to Xray.
6. **Xray** — Plan Xray import on the workspace. Preview, then sandbox write. **More → Importer** when you need the Cursor prompt ([GUIDE.md](GUIDE.md)).

**Gate 5–6:** Verdict on the workspace · Tests in Xray (sandbox) with the correct project and folder.

Details: [PROMPTS-AND-INPUTS.md](PROMPTS-AND-INPUTS.md) · [FIRST-RUN.md](FIRST-RUN.md) Phase 3.

---

## 6. Failure recovery

| Symptom | First action |
|---------|--------------|
| MCP auth errors | [CURSOR-MCP-SETUP.md](CURSOR-MCP-SETUP.md) |
| Confluence *Unavailable* cross-site | Complete dual MCP |
| Missing epics after import | Folder name = Epic Jira key |
| Wrong readiness counts | Re-import; see [METRICS.md](METRICS.md) |
| Wrong Xray project/fields | Mapping file + project key — [FAQ](FAQ.md) |

More: [FAQ — Troubleshooting](FAQ.md#troubleshooting).

Issues: GitHub `marekwyszynskiappfire/docs`, label `trinity-support`.

---

## 7. Preflight script

```bash
./Trinity/scripts/pilot-preflight.sh
```

---

## 8. Sign-off

Sandbox Gates 1–6 → [OPERATOR-VALIDATION.md](OPERATOR-VALIDATION.md) for QA lead.

**Republish wiki after doc edits:** `python3 Trinity/scripts/sync_confluence_from_git.py` (needs Confluence write token).

---

## Three prompts (quick reference)

| # | Studio source | Output |
|---|---------------|--------|
| 1 | Workspace list → New portfolio | `review-payload.json` and a workspace URL |
| 2 | Workspace → Copy Creator prompt | `suite-payload.json` |
| 3 | Workspace → Plan Xray import | Xray Tests |
