# Trinity Studio (developer notes)

User-facing docs: **[`../README.md`](../README.md)** · **[`../PREFLIGHT.md`](../PREFLIGHT.md)**

## CI (IQ-14)

```bash
cd Trinity/studio && pip install -r requirements.txt && pytest tests -q
cd Trinity/studio/web && npm ci && npm test && npm run build
```

GitHub Actions: [`.github/workflows/trinity-studio-ci.yml`](../../.github/workflows/trinity-studio-ci.yml) on changes under `Trinity/studio/` and `Trinity/shared/`.

## Start

```bash
./Trinity/studio/scripts/start.sh
```

API **8765** · Vite UI **5173** (Vite uses `--strictPort` — will not silently move to 5174).

If ports are busy (old Studio or a stray API from an agent session):

```bash
./Trinity/studio/scripts/stop.sh
# or
STUDIO_FORCE=1 ./Trinity/studio/scripts/start.sh
```

## Import CLI

```bash
./Trinity/studio/scripts/import-run.sh Trinity/reviewer/runs/<run-id>
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
| `POST /api/import/reviewer-run` | Import Reviewer run folder |
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
| `POST /api/importer/record-results` | Persist `xray_test_key` from import report JSON (IQ-05) |
| `GET /api/telemetry/summary`, `/export`, `/events` | Local metrics ([`METRICS.md`](../METRICS.md)) |
| `POST /api/telemetry/flush` | Best-effort BigQuery ingest when `TRINITY_TELEMETRY_URL` set |
| `/api/units/...`, `/api/creator-runs/...` | Review and Creator batches |

UI: **Personas** nav → edit role prompts used by Reviewer run config.

Data: `Trinity/studio/data/` (gitignored SQLite and exports).
