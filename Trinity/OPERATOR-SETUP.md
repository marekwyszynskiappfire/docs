# Trinity — operator setup (checkout → operational)

**Audience:** QA engineer bringing Trinity up on a fresh machine.  
**Wiki:** [Setup checklist](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754459462/Trinity+Setup+checklist) · **Onboarding:** [`OPERATOR-ONBOARDING.md`](OPERATOR-ONBOARDING.md) · **FAQ:** [`FAQ.md`](FAQ.md)  
**First run (recommended):** [`FIRST-RUN.md`](FIRST-RUN.md) — checkout → demo → Prompts #1–#3 → one epic.  
**Reference manual:** [`MANUAL.md`](MANUAL.md). This file is the **same flow as numbered steps** without narrative.  
**Confluence:** publish [`MANUAL.md`](MANUAL.md) as the primary wiki page; short sections under [`confluence/`](confluence/).  
**Diagram:** [`confluence/assets/trinity-operator-pipeline.svg`](confluence/assets/trinity-operator-pipeline.svg)

| Mode | Goal | Stop after step |
|------|------|-----------------|
| **Demo only** | Prove Studio UI + fixtures | **Step 6** |
| **Full pipeline** | Reviewer → Studio → Creator → Importer | **Step 14** |
| **Telemetry** | Same run visible in BigQuery and Looker Studio | **Step 17** |
| **Jira write** | Epic comments or Xray execute | **Steps 4 + 12–14** (credentials) |

---

## Step 1 — Clone and open the repo

```bash
git clone https://github.com/marekwyszynskiappfire/docs.git DOCS
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
- **Human analytics identity** — `TRINITY_OPERATOR_ID` and
  `TRINITY_OPERATOR_NAME`. Use your own values; these identify the human in
  BigQuery, not the GCP service account.
- **BigQuery target** — `BQ_PROJECT`, `BQ_DATASET`, and later an absolute
  `GOOGLE_APPLICATION_CREDENTIALS` path when local ingest is enabled.

Example (placeholders only):

```bash
TRINITY_OPERATOR_ID=you@appfire.com
TRINITY_OPERATOR_NAME="Your Name"
BQ_PROJECT=qa-coe
BQ_DATASET=trinity
# GOOGLE_APPLICATION_CREDENTIALS=/Users/<mac-login>/.config/trinity/key.json
```

`.env` and `.env.production` are gitignored. Never put personal values, API
tokens, or JSON key contents in `.env.example`; that tracked file is a template
only. Store the service-account JSON outside the repository. The repository's
full BigQuery and Looker Studio reference is `Trinity/BIGQUERY.md`.

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

1. On the workspace list, open **New portfolio**. The sample shape is [`reviewer/config/runs/example.demo-portfolio.json`](reviewer/config/runs/example.demo-portfolio.json).
2. Set **scope** to your epics (keys, JQL, or filter URL).
3. Set **persona** and **product_id**.
4. **Save** → file under `Trinity/reviewer/config/runs/{portfolio_id}.json`.

For **JQL/filter** scope: resolve epic keys in Cursor (or Studio **Copy JQL resolve prompt** / paste keys) before gather. See [`FIRST-RUN.md`](FIRST-RUN.md) §3.1.

---

## Step 9 — Run Reviewer in Cursor

1. On the workspace list, open **New portfolio**, save it, and **Copy Reviewer prompt**. On an existing workspace, expand **Portfolio**, then **Reviewer prompt** → **Copy Cursor prompt**.
2. New Cursor chat → paste → run gather per skill.
3. Outputs: `Trinity/reviewer/runs/.../<EPIC-KEY>/review-payload.json` (under `portfolio_id` and optionally a dated `portfolio_run_id` subfolder).

**Rule:** folder name **must equal** the epic Jira key in the payload (`scope.value`). Import fails on mismatch.

Use **Reviewer prompt** on the workspace (see [`FIRST-RUN.md`](FIRST-RUN.md) §3.2). Create the portfolio from **New portfolio** on the workspace list. **More → Reviewer configs** lists every portfolio.

Deep dive: [`reviewer/MANUAL.md`](reviewer/MANUAL.md).

---

## Step 10 — Open the workspace

The Reviewer prints a workspace URL. Open it. Importing the same payloads again does not add another review revision.

If no URL was printed:

```bash
./Trinity/studio/scripts/import-run.sh Trinity/reviewer/runs/<folder-that-directly-contains-EPIC-KEY>
```

Then expand **Import a review folder** on the workspace list. **Import and open** opens that workspace.

---

## Step 11 — Verdict on the workspace

1. Read the testability verdict and the blocker questions.
2. **Next step → Approve** when the verdict is right.
3. **Next step → Copy Creator prompt**. Several approved Epics: **Prepare Creator prompts**, then **Copy Creator prompts**.

Finding-by-finding triage is on the open Epic: expand **Findings and Jira comment**. **Save draft** there before a Jira comment preview. Run-level handoff (**In Creator**, JQL, handoff JSON) stays on the run page.

---

## Step 12 — Jira epic comments (optional)

On the open Epic, expand **Findings and Jira comment** → panel **Jira epic comment**:

1. Check credentials chip (`GET /api/jira/status`).
2. **Refresh preview** (smart / studio / full / short).
3. Confirm issue key; on production host type `PRODUCTION`.
4. **Post to Jira** (always creates a **new** comment).

Do **not** post demo key `DEMO-4500` to real Jira. Use a sandbox **Epic** key for end-to-end tests.

Detail: [`MANUAL.md`](MANUAL.md) §8.

---

## Step 13 — Creator

1. Paste the workspace Creator prompt into Cursor → run **trinity-creator**. An Epic that is not testable yet cannot be drafted.
2. Stay on the workspace. Studio imports `suite-payload.json` when the file appears. **Check for the file now** if the card is still waiting.
3. Approve or reject each test. A rejection needs a reason. Tick **Send to Xray**, or **Approve selected** for the tests you ticked.
4. On the Epic, expand **Import a suite file** when the suite was written to a different path. Expand **Creator runs** for this workspace’s list and **Export for Importer**. **More → Creator** still lists every Creator run.

Detail: [`FIRST-RUN.md`](FIRST-RUN.md) §3.4–3.5.

---

## Step 14 — Importer (Xray)

On the workspace, **Next step → Plan Xray import**:

1. Choose instance (sandbox vs production).
2. Mapping + project key + folder path → **Preview import plan**.
3. Acknowledge the Reviewer gate or idempotency confirmation if the plan asks.
4. **Write to Xray** when the plan is ready. Production requires typing PRODUCTION. Several Epics can be previewed together; the write stays one Epic.

**Write to Xray** stores keys when Studio writes them. After a Cursor write, expand **Record Xray keys** and point it at `xray-import-report.json`. **More → Importer** remains the payload-path page.

Full detail: [`GUIDE.md` §6](GUIDE.md#6-importer-studio--xray) · [`MANUAL.md`](MANUAL.md) § Importer.

---

## Step 15 — Validation checklist

Run through [`TESTING.md`](TESTING.md) before pilot sign-off.

---

## Step 16 — Pipeline statistics (pilot evidence)

1. Studio → **Statistics** → **Single run** — confirm TC readiness buckets match Reviewer (`fit` / `provisional` / `not_fit` on latest payloads).
2. With two+ imported runs → **Compare runs** — set **Run 1 (baseline)** and **Run 2** from dropdowns; optional runs 3–5.
3. **Download export JSON** on a run for `pipeline_run_report` archive / scorecard attachment.

Details: [`MANUAL.md`](MANUAL.md) §5.9 · [`METRICS.md`](METRICS.md).

---

## Step 17 — BigQuery

After the workspace has the review, the tests, and the Xray keys, the same run can be read in BigQuery. A failed upload does not stop the pipeline.

1. Put the service-account JSON at `~/.config/trinity/qa-coe-bigquery.json` (`chmod 600`). It is not in the repo.
2. In `Trinity/studio/.env`, set `TRINITY_OPERATOR_ID`, `TRINITY_OPERATOR_NAME`, `BQ_PROJECT=qa-coe`, `BQ_DATASET=trinity`, and an absolute `GOOGLE_APPLICATION_CREDENTIALS` path. Leave `TRINITY_TELEMETRY_URL` unset so `start.sh` uses local ingest.
3. Restart `./Trinity/studio/scripts/start.sh`.
4. Confirm with `curl -s -X POST http://127.0.0.1:8765/api/telemetry/sync`. Expect `failed: 0` and `pending: 0`.

Sample values and the Looker views are in [`MANUAL.md`](MANUAL.md) (New operator, §5) and [`BIGQUERY.md`](BIGQUERY.md) · [BigQuery and Looker](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3779068614/Trinity+BigQuery+and+Looker).

---

## Related docs

| Doc | Use |
|-----|-----|
| [`PIPELINE.md`](PIPELINE.md) | End-to-end map |
| [`MANUAL.md`](MANUAL.md) | Personas, configs, handoffs |
| [`GUIDE.md`](GUIDE.md) | Credentials, golden, Importer selector |
| [`FAQ.md`](FAQ.md) | Capabilities & evidence |
| [`confluence/`](confluence/) | Pages for wiki publish |

**Last reviewed:** 2026-10-21
