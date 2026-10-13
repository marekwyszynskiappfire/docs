# Trinity — operator setup (checkout → operational)

**Audience:** QA engineer bringing Trinity up on a fresh machine.  
**Confluence:** sectional copies live under [`confluence/`](confluence/) (see [`confluence/README.md`](confluence/README.md)).  
**Diagram:** [`confluence/assets/trinity-operator-pipeline.svg`](confluence/assets/trinity-operator-pipeline.svg)

| Mode | Goal | Stop after step |
|------|------|-----------------|
| **Demo only** | Prove Studio UI + fixtures | **Step 6** |
| **Full pipeline** | Reviewer → Studio → Creator → Importer | **Step 14** |
| **Jira write** | Epic comments or Xray execute | **Steps 4 + 12–14** (credentials) |

---

## Step 1 — Clone and open the repo

```bash
git clone <your-docs-repo-url> DOCS
cd DOCS
```

Repo root is the folder that contains `Trinity/`.

---

## Step 2 — Tool versions

| Tool | Minimum | Check |
|------|---------|--------|
| Python | 3.11 | `python3 --version` |
| Node.js | 18 | `node --version` |
| Cursor | Current desktop | Skills + MCP (step 7) |

---

## Step 3 — Preflight smoke (no Jira)

```bash
python3 Trinity/reviewer/scripts/render_report.py \
  Trinity/reviewer/samples/demo-epic.payload.json --strict
```

Expect exit code 0. Details: [`PREFLIGHT.md`](PREFLIGHT.md).

---

## Step 4 — Studio credentials (optional for demo; required for Jira/Xray writes)

```bash
cp Trinity/studio/.env.example Trinity/studio/.env
```

Edit `.env`:

- **Jira REST** — `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` (comments, scope resolve, Importer project list).
- **Xray** — `XRAY_CLIENT_ID`, `XRAY_CLIENT_SECRET` (Importer execute).

Use **sandbox** URLs and keys until you deliberately target production. Production Importer and production Jira host require typing **`PRODUCTION`** in Studio before execute/post.

---

## Step 5 — Start Trinity Studio

Terminal 1 (leave running):

```bash
./Trinity/studio/scripts/start.sh
```

Verify:

```bash
curl -sf http://127.0.0.1:8765/api/health | python3 -m json.tool
```

Open **http://127.0.0.1:5173**

Ports busy: `./Trinity/studio/scripts/stop.sh` or `STUDIO_FORCE=1 ./Trinity/studio/scripts/start.sh`

First start may take several minutes (pip + `npm ci`).

---

## Step 6 — Load demo data (10-minute path)

Terminal 2:

```bash
./Trinity/studio/scripts/seed-demo.sh
```

Dashboard → open the imported run → unit **`DEMO-4500`** (fictional demo epic; folder name matches payload `scope.value`).

Hands-on table: [`QUICKSTART.md`](QUICKSTART.md).

Optional Creator demo batch:

- **Creator** tab → import `Trinity/creator/samples/demo-story.suite.json`

You are **operational for Studio demo** after this step.

---

## Step 7 — Cursor skills and MCP (live Reviewer/Creator/Importer)

```bash
./Trinity/scripts/install-trinity-skills.sh
```

Atlassian MCP (often two sites): [`reviewer/config/DUAL-ATLASSIAN-MCP.md`](reviewer/config/DUAL-ATLASSIAN-MCP.md).

Skills installed: `trinity-reviewer`, `trinity-creator`, `trinity-importer` (names may appear under `.cursor/skills/`).

---

## Step 8 — Portfolio run config

1. Studio → **Reviewer configs** → open or duplicate [`reviewer/config/runs/example.demo-portfolio.json`](reviewer/config/runs/example.demo-portfolio.json).
2. Set **scope** to your epics (keys, JQL, or filter URL).
3. Set **persona** and **product_id**.
4. **Save** → file under `Trinity/reviewer/config/runs/{portfolio_id}.json`.

For **JQL/filter** scope: resolve epic keys in Cursor (or Studio **Resolve** / paste keys) before gather. Sample: [`confluence/samples/jql-resolve-prompt.md`](confluence/samples/jql-resolve-prompt.md).

---

## Step 9 — Run Reviewer in Cursor

1. Studio → **Reviewer configs** → **Copy Cursor prompt** for your portfolio.
2. New Cursor chat → paste → run gather per skill.
3. Outputs: `Trinity/reviewer/runs/<run-folder>/<EPIC-KEY>/review-payload.json`.

**Rule:** folder name **must equal** the epic Jira key in the payload (`scope.value`). Import fails on mismatch.

Sample start prompt: [`confluence/samples/reviewer-portfolio-start.md`](confluence/samples/reviewer-portfolio-start.md).

Deep dive: [`reviewer/MANUAL.md`](reviewer/MANUAL.md).

---

## Step 10 — Import Reviewer run into Studio

```bash
./Trinity/studio/scripts/import-run.sh Trinity/reviewer/runs/<your-run-folder>
```

Or Dashboard → **Import Reviewer run** → path to that folder.

---

## Step 11 — Review unit (human QA)

1. Dashboard → run → epic unit.
2. Triage questions/findings (`studio_qa`: validity, **Include in epic feedback**).
3. **Save draft** (Jira comment preview uses saved payload only).
4. **Approve & export for Creator** when ready.

Run-level Creator handoff: run page → **In Creator** toggles, JQL, handoff JSON.

---

## Step 12 — Jira epic comments (optional)

On the unit page → panel **Jira epic comment**:

1. Check credentials chip (`GET /api/jira/status`).
2. **Refresh preview** (smart / studio / full / short).
3. Confirm issue key; on production host type `PRODUCTION`.
4. **Post to Jira** (always creates a **new** comment).

Do **not** post demo key `DEMO-4500` to real Jira. Use a sandbox **Epic** key for end-to-end tests.

Spec: [`studio/JIRA-EPIC-COMMENTS-OUTLINE.md`](studio/JIRA-EPIC-COMMENTS-OUTLINE.md).

---

## Step 13 — Creator

1. Unit page → **Send to Creator** (requires approve; blocked for `not_fit`).
2. Paste prompt into Cursor → run **trinity-creator**.
3. Studio → **Creator** → import `suite-payload.json` path from prompt.
4. Approve/reject tests; mark **Fit for Xray import**.
5. **Export for Importer** on the creator run.

Sample prompt shape: [`confluence/samples/creator-handoff-prompt.md`](confluence/samples/creator-handoff-prompt.md).

---

## Step 14 — Importer (Xray)

1. Studio → **Importer** (or `?creator_run_id=...`).
2. Choose instance (sandbox vs production).
3. Mapping + project key + folder path → **Preview import plan**.
4. Acknowledge Reviewer gate if shown.
5. **Copy Cursor prompt** or **Execute** (sandbox first).
6. **Persist Xray keys** from `xray-import-report.json`.

Full detail: [`GUIDE.md` §6](GUIDE.md#6-importer-studio--xray) · [`MANUAL.md`](MANUAL.md) § Importer.

---

## Step 15 — Validation checklist

Run through [`TESTING.md`](TESTING.md) before pilot sign-off.

---

## Related docs

| Doc | Use |
|-----|-----|
| [`PIPELINE.md`](PIPELINE.md) | End-to-end map |
| [`MANUAL.md`](MANUAL.md) | Personas, configs, handoffs |
| [`GUIDE.md`](GUIDE.md) | Credentials, golden, Importer selector |
| [`FAQ.md`](FAQ.md) | Capabilities & evidence |
| [`confluence/`](confluence/) | Pages for wiki publish |

**Last reviewed:** 2026-10-13
