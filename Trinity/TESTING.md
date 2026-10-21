# Trinity — hands-on testing guide

One path from zero to Reviewer → Studio → Creator → Importer handoff file.  
**Wiki:** [Start here](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754590489/Trinity+Start+here) · Hub: [`START-HERE.md`](START-HERE.md) · Preflight: [`PREFLIGHT.md`](PREFLIGHT.md) · Pipeline: [`PIPELINE.md`](PIPELINE.md)

---

## 0. One-time setup (repo root)

```bash
cd /path/to/DOCS   # this repo

# Cursor skills (Reviewer + Creator)
./Trinity/scripts/install-trinity-skills.sh

# Studio: start.sh creates/syncs .venv (if API fails with missing httpx, delete Trinity/studio/.venv and re-run start.sh)

# Studio UI deps
cd Trinity/studio/web && npm install && cd ../../..
```

**Optional:** Atlassian MCP in Cursor for live Jira (Reviewer gather, JQL resolve).  
**Optional:** `Trinity/studio/.env` from `.env.example` for Studio **Resolve from scope** via REST (otherwise use **Copy JQL resolve prompt**).

**Skills in Cursor:** invoke `@trinity-reviewer` or open `Trinity/reviewer/SKILL.md`; Creator: `@trinity-creator` / `Trinity/creator/SKILL.md`.

---

## 1. Reviewer (no Studio required)

### 1a. Renderer smoke (offline)

```bash
python3 Trinity/reviewer/scripts/render_report.py \
  Trinity/reviewer/samples/demo-epic.payload.json
```

Opens HTML beside the sample or prints output path. Confirms Python + template work.

### 1b. Portfolio config (Studio or file)

**Option A — Studio:** start Studio (section 2), **Reviewer configs** → edit `example.demo-portfolio` → save.

**Option B — file:** edit [`reviewer/config/runs/example.demo-portfolio.json`](reviewer/config/runs/example.demo-portfolio.json).

### 1c. Live Reviewer run (Cursor)

1. Studio → **Reviewer configs** to save the portfolio, then on the workspace expand **Reviewer prompt** → **Copy Cursor prompt** (or follow the interview in `reviewer/SKILL.md`).
2. In Cursor, run **trinity-reviewer** with your portfolio scope.
3. Outputs land under **`Trinity/reviewer/runs/{portfolio_run_id}/`** (gitignored), e.g.  
   `{run}/ONE-12345/review-payload.json` + `review-report.html`.

**Quick demo without Jira:** copy sample into a fake run folder:

```bash
RUN=Trinity/reviewer/runs/demo-local-test
mkdir -p "$RUN/DEMO-4500"
cp Trinity/reviewer/samples/demo-epic.payload.json "$RUN/DEMO-4500/review-payload.json"
cp Trinity/reviewer/samples/demo-epic.report.md "$RUN/DEMO-4500/review-report.md" 2>/dev/null || true
```

Use that folder in Studio import below.

---

## 2. Trinity Studio (web UI)

### Start

```bash
./Trinity/studio/scripts/start.sh
```

| URL | Role |
|-----|------|
| http://127.0.0.1:5173 | React UI |
| http://127.0.0.1:8765/api/health | API health |

Keep the terminal open (Ctrl+C stops API + Vite).

### 2a. Workspace

- Run `./Trinity/studio/scripts/seed-demo.sh`, or import `Trinity/studio/fixtures/demo-reviewer-run` from **More → Dashboard**.
- On the run row, click **Open workspace**. Confirm the stepper, **Next step**, and the demo Epic.

### 2b. Review workflow

1. On the workspace, read the verdict. **Next step → Approve**, then **Copy Creator prompt** (the prompt includes `review_ref`). An Epic that is not testable yet cannot be drafted.
2. **Personas** — the list shows the heading in each file. The filename stays above the editor. A save writes `Trinity/personas/`.
3. Open the Epic and expand **Findings and Jira comment**. **Save draft** and **Approve & export** work there. The Epic’s own page shows the same panel.

### 2c. Creator workflow (UI only, no Cursor)

1. **More → Creator** → import path:  
   `Trinity/creator/samples/demo-story.suite.json`
2. Open the run → table of tests.
3. **Edit** a test → change steps, **automation fit**, blockers → **Save & approve** → check **Fit for Xray import**.
4. **Reject** another test to verify status.
5. Bulk: select rows → **Approve selected** / **Mark for Xray import**.
6. **Export for Importer** — writes  
   `Trinity/studio/data/exports/creator/{run_id}/importer-payload.json`  
   (only **approved** + **marked** tests).

On a real suite the workspace imports the file itself. Open the Epic, tick the pending tests, and use **Approve selected**. **Send to Xray** stays on each approved test.

**Reset Studio DB** (start clean): delete `Trinity/studio/data/qa-studio.db` and restart `start.sh`.

---

## 3. Creator (Cursor agent)

After **Copy Creator prompt** on the workspace (or a hand-written prompt):

1. Paste the handoff prompt into Cursor; run **trinity-creator**.
2. Ensure parameters: `review_ref`, Epic key, `suite_mode: release_slice_e2e`, product config (`bigpicture` or `default`).
3. Agent writes e.g.  
   `Trinity/creator/artifacts/{EPIC-KEY}/suite-payload.json`  
   (+ `suite-report.md`).
4. The workspace imports that file. **More → Creator** can import the path when it does not.
5. Complete operator review (section 2c).

**Offline check (no agent):** use the committed demo batch only (step 2c).

---

## 4. Importer (Studio)

Full steps: **[`GUIDE.md` §6](GUIDE.md#6-importer-studio--xray)** (instance, mapping, **project key override**, folder, `project.id` resolution, production confirm, Execute batch).

Quick check:

1. On the workspace, mark the approved tests and open **Plan Xray import**. **More → Creator → Export for Importer** is the fallback.
2. Select instance + mapping → set **Jira project for new Tests** if not TC.
3. **Preview import plan** → **Write to Xray**, or copy the Cursor prompt from **More → Importer** (includes PM summary + coverage matrix when the batch has `coverage_report`).

---

## 5. End-to-end checklist (~30 min)

| Step | Pass? |
|------|--------|
| `install-trinity-skills.sh` links reviewer + creator | ☐ |
| `render_report.py` on demo epic sample | ☐ |
| `start.sh` — health + Personas save | ☐ |
| `seed-demo.sh` → **Open workspace** shows the demo Epic and **Next step** | ☐ |
| Approve the review → **Copy Creator prompt** | ☐ |
| Import `demo-story.suite.json` from **More → Creator** | ☐ |
| Approve + mark for Xray on the workspace, or **Approve selected** on ticked tests | ☐ |
| Workspace **Preview import plan** (write stays disabled until the plan is ready) | ☐ |
| Optional: **Export for Importer** and `importer-payload.json` under `studio/data/exports/creator/` | ☐ |

---

## 6. Troubleshooting

| Issue | Fix |
|-------|-----|
| UI blank / API errors | `curl http://127.0.0.1:8765/api/health`; restart `start.sh` |
| Import run finds 0 units | Folder must contain `{EPIC}/review-payload.json` per epic |
| Cannot mark for Xray import | Test must be **approved** first |
| Export for Importer 400 | No tests both approved and marked — mark at least one |
| Creator skill not found | Re-run `install-trinity-skills.sh`; restart Cursor |
| Old schema / missing columns | Delete `qa-studio.db` and re-import batches |

## 7. What is not wired yet

- **Studio Execute button** for batch Xray submit (CLI + Cursor prompt today).
- **Studio** does not run Reviewer/Creator agents (Cursor only).
- **Suite HTML** report renderer for Creator batches (Markdown only).
