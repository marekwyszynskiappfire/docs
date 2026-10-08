# Trinity — hands-on testing guide

One path from zero to Reviewer → Studio → Creator → Importer handoff file.  
Hub: [`README.md`](README.md) · Preflight: [`PREFLIGHT.md`](PREFLIGHT.md) · Pipeline: [`PIPELINE.md`](PIPELINE.md)

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

1. Studio → **Reviewer configs** → **Copy Cursor prompt** (or follow interview in `reviewer/SKILL.md`).
2. In Cursor, run **trinity-reviewer** with your portfolio scope.
3. Outputs land under **`Trinity/reviewer/runs/{portfolio_run_id}/`** (gitignored), e.g.  
   `{run}/ONE-12345/review-payload.json` + `review-report.html`.

**Quick demo without Jira:** copy sample into a fake run folder:

```bash
RUN=Trinity/reviewer/runs/demo-local-test
mkdir -p "$RUN/ONE-DEMO"
cp Trinity/reviewer/samples/demo-epic.payload.json "$RUN/ONE-DEMO/review-payload.json"
cp Trinity/reviewer/samples/demo-epic.report.md "$RUN/ONE-DEMO/review-report.md" 2>/dev/null || true
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

### 2a. Dashboard

- **Import Reviewer run** — path: `Trinity/reviewer/runs/demo-local-test` (or your real run).
- Confirm pipeline run appears; open it.

### 2b. Review workflow

1. **Dashboard** → open run → open an epic **unit**.
2. Edit payload / QA workflow → **Approve & export** (or export for Creator).
3. **Send to Creator** — copies Cursor prompt with `review_ref` (disabled for `not_fit`).
4. **Personas** — edit Reviewer/Creator persona markdown (writes to `Trinity/personas/`).

### 2c. Creator workflow (UI only, no Cursor)

1. **Creator** tab → import path:  
   `Trinity/creator/samples/demo-story.suite.json`
2. Open the run → table of tests.
3. **Edit** a test → change steps, **automation fit**, blockers → **Save & approve** → check **Fit for Xray import**.
4. **Reject** another test to verify status.
5. Bulk: select rows → **Approve selected** / **Mark for Xray import**.
6. **Export for Importer** — writes  
   `Trinity/studio/data/exports/creator/{run_id}/importer-payload.json`  
   (only **approved** + **marked** tests).

**Reset Studio DB** (start clean): delete `Trinity/studio/data/qa-studio.db` and restart `start.sh`.

---

## 3. Creator (Cursor agent)

After **Send to Creator** from Studio (or manual):

1. Paste the handoff prompt into Cursor; run **trinity-creator**.
2. Ensure parameters: `review_ref`, Epic key, `suite_mode: release_slice_e2e`, product config (`bigpicture` or `default`).
3. Agent writes e.g.  
   `Trinity/creator/artifacts/{EPIC-KEY}/suite-payload.json`  
   (+ `suite-report.md`).
4. Studio → **Creator** → import that JSON path.
5. Complete operator review (section 2c).

**Offline check (no agent):** use the committed demo batch only (step 2c).

---

## 4. End-to-end checklist (~30 min)

| Step | Pass? |
|------|--------|
| `install-trinity-skills.sh` links reviewer + creator | ☐ |
| `render_report.py` on demo epic sample | ☐ |
| `start.sh` — health + Personas save | ☐ |
| Import `demo-local-test` Reviewer folder | ☐ |
| Approve unit → Send to Creator (prompt copies) | ☐ |
| Import `demo-story.suite.json` in Creator tab | ☐ |
| Approve + mark for Xray → Export for Importer | ☐ |
| `importer-payload.json` exists under `studio/data/exports/creator/` | ☐ |

---

## 5. Troubleshooting

| Issue | Fix |
|-------|-----|
| UI blank / API errors | `curl http://127.0.0.1:8765/api/health`; restart `start.sh` |
| Import run finds 0 units | Folder must contain `{EPIC}/review-payload.json` per epic |
| Cannot mark for Xray import | Test must be **approved** first |
| Export for Importer 400 | No tests both approved and marked — mark at least one |
| Creator skill not found | Re-run `install-trinity-skills.sh`; restart Cursor |
| Old schema / missing columns | Delete `qa-studio.db` and re-import batches |

---

## 6. What is not wired yet

- **Importer** — Studio **Preview import plan** + **Copy Cursor prompt**; production execute via `Trinity/importer/scripts/xray_graphql_import.py` (sandbox Xray keys: TBD in `.env`).
- **Studio** does not run Reviewer/Creator agents (Cursor only).
- **Suite HTML** report renderer for Creator batches (Markdown only).
