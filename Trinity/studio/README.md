# Trinity Studio (developer notes)

User-facing docs: **[`../FIRST-RUN.md`](../FIRST-RUN.md)** · **[`../MANUAL.md`](../MANUAL.md)** · **[`../OPERATOR-SETUP.md`](../OPERATOR-SETUP.md)** · **[`../PREFLIGHT.md`](../PREFLIGHT.md)** · **[`../README.md`](../README.md)**

## CI (IQ-14)

```bash
cd Trinity/studio && pip install -r requirements.txt && pytest tests -q
cd Trinity/studio/web && npm ci && npm test && npm run build
```

GitHub Actions: [`.github/workflows/trinity-studio-ci.yml`](../../.github/workflows/trinity-studio-ci.yml) on changes under `Trinity/studio/` and `Trinity/shared/`.

## Start

```bash
./Trinity/studio/scripts/start.sh
./Trinity/studio/scripts/seed-demo.sh   # optional: committed demo Reviewer run
```

Operator quickstart: [`../QUICKSTART.md`](../QUICKSTART.md)

API **8765** · Vite UI **5173** (Vite uses `--strictPort` — will not silently move to 5174).

After `cd web && npm run build`, **8765** serves the React build from `web/dist` (legacy static: `QA_STUDIO_LEGACY_STATIC=1`).

Reviewer close-out imports a manifest and prints one workspace URL. It reuses a compatible Studio. It does not stop another process on the port:

```bash
python3 Trinity/studio/scripts/open_workspace.py --manifest path/to/pipeline-manifest.json
```

If the running Studio is too old, restart it yourself with `STUDIO_FORCE=1 ./Trinity/studio/scripts/start.sh`.

If ports are busy (old Studio or a stray API from an agent session):

```bash
./Trinity/studio/scripts/stop.sh
# or
STUDIO_FORCE=1 ./Trinity/studio/scripts/start.sh
```

## Import CLI

```bash
./Trinity/studio/scripts/import-run.sh Trinity/reviewer/runs/<folder-that-directly-contains-EPIC-KEY>
```

Prune duplicate Reviewer folders, pytest creator runs, and orphan exports:

```bash
./Trinity/studio/scripts/cleanup-local-runs.sh          # dry-run
./Trinity/studio/scripts/cleanup-local-runs.sh --apply  # edit KEEP_REVIEWER inside first
```

## API

| Endpoint | Purpose |
|----------|---------|
| `GET /api/personas` | List `Trinity/personas/*.md` (except README) |
| `GET/PUT /api/personas/{filename}` | Read/write persona markdown in repo |
| `GET /api/reviewer-run-configs` | List portfolio run configs |
| `GET/PUT /api/reviewer-run-configs/{portfolio_id}` | Read/write `reviewer/config/runs/{id}.json` |
| `GET .../new-epics` | Epics in scope without `review-payload.json` under run folder |
| `POST .../resolve-scope` | Inline resolve for epic_keys/epic_url |
| `POST/DELETE .../resolved-keys` | Paste or clear `resolved_epic_keys` snapshot |
| `POST /api/import/pipeline-manifest` | Import `pipeline-manifest.json`; unchanged payload hashes do not add a review revision |
| `GET /api/workspace/{run_id}` | Epics, one next action, and the Cursor handoff prompt |
| `POST /api/workspace/{run_id}/handoffs/{id}/check` | Refresh handoff status from expected files. A missing file while waiting stays `awaiting_cursor` |
| `POST /api/import/reviewer-run` | Import Reviewer run folder |
| `GET /api/jira/status` | Jira credentials chip for epic comment panel |
| `GET/POST /api/units/{id}/jira-comment/*` | Preview, post, history (epic comments) |
| `POST /api/units/{id}/send-to-creator` | Approved export + Creator prompt (blocks not_fit) |
| `PUT/PATCH /api/tests/{id}` | Save case JSON, review status, import mark |
| `GET /api/creator/products`, `/golden-corpora` | Product → golden corpus + Importer defaults (IQ-12) |
| `GET /api/creator-runs/{id}` | Run tests + `coverage` matrix vs approved linkage (IQ-11) |
| `POST /api/creator-runs/{id}/bulk-test-review` | Bulk approve / reject / mark for Xray |
| `POST /api/creator-runs/{id}/export-suite-report` | Profile B `suite-report/index.html` (IQ-13) |
| `POST /api/creator-runs/{id}/export-for-importer` | Write `data/exports/creator/{id}/importer-payload.json` |
| `GET /api/importer/instances`, `/mappings`, `/jira-projects`, `/credentials` | Importer setup (project list needs `JIRA_*` in `.env`) |
| `POST /api/importer/plan` | Dry-run plan + `cursor_prompt` (`project_key_override` supported) |
| `POST /api/importer/execute` | Batch Xray create + auto-persist keys (IQ-10) |
| `GET /api/cursor-agents/status` | Whether the Cursor SDK and `CURSOR_API_KEY` are available |
| `POST /api/cursor-agents/reviewer` | Launch a persisted Reviewer agent |
| `POST /api/cursor-agents/handoff` | Launch a persisted Creator or Importer handoff agent |
| `GET /api/cursor-agent-runs` | List persisted agent runs |
| `POST /api/importer/launch-cursor` | Recompute the Importer plan, then launch its agent |
| `POST /api/importer/record-results` | Persist `xray_test_key` from import report JSON (IQ-05) |
| `GET /api/runs/{id}/statistics`, `/statistics/export` | Per-run E2E report ([`METRICS.md`](../METRICS.md)) |
| `GET /api/statistics/compare?runs=id1,id2` | Compare 2–5 pipeline runs (TC readiness + metrics; first id = baseline) |
| `GET /api/telemetry/summary`, `/export`, `/events` | Local metrics ([`METRICS.md`](../METRICS.md)) |
| `POST /api/telemetry/flush` | Flush pending events to configured ingest |
| `POST /api/telemetry/sync` | Recompute all run reports and backfill BigQuery ([setup](../BIGQUERY.md)) |
| `/api/units/...`, `/api/creator-runs/...` | Review and Creator batches |

UI: **Personas** nav → edit role prompts used by Reviewer run config.

List tables across Studio use **`web/src/components/SortableDataTable.tsx`** — click any column header to sort (asc/desc). Top nav **Statistics**: single-run E2E report and compare 2–5 runs (Run 1 = baseline dropdowns); see [`MANUAL.md`](../MANUAL.md) §5.9.

Data: `Trinity/studio/data/` (gitignored SQLite and exports).
