# Trinity Studio (developer notes)

User-facing docs: **[`../README.md`](../README.md)** · **[`../PREFLIGHT.md`](../PREFLIGHT.md)**

## Start

```bash
./Trinity/studio/scripts/start.sh
```

API **8765** · Vite UI **5173**

## Import CLI

```bash
./Trinity/studio/scripts/import-run.sh Trinity/reviewer/runs/<run-id>
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
| `POST /api/creator-runs/{id}/bulk-test-review` | Bulk approve / reject / mark for Xray |
| `POST /api/creator-runs/{id}/export-for-importer` | Write `data/exports/creator/{id}/importer-payload.json` |
| `/api/units/...`, `/api/creator-runs/...` | Review and Creator batches |

UI: **Personas** nav → edit role prompts used by Reviewer run config.

Data: `Trinity/studio/data/` (gitignored SQLite and exports).
