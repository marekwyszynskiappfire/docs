# Trinity preflight

Run once on a new machine before a portfolio review.  
**New operators:** [`START-HERE.md`](START-HERE.md) · [`FAQ.md`](FAQ.md) · [`OPERATOR-ONBOARDING.md`](OPERATOR-ONBOARDING.md) · **Demo:** [`QUICKSTART.md`](QUICKSTART.md)

1. **Clone** the docs repo and `cd` to repo root.
2. **MCP** — [`CURSOR-MCP-SETUP.md`](CURSOR-MCP-SETUP.md) (dual-site detail: [`reviewer/config/DUAL-ATLASSIAN-MCP.md`](reviewer/config/DUAL-ATLASSIAN-MCP.md)).
3. **Skills** — `./Trinity/scripts/install-trinity-skills.sh` (or symlink `Trinity/reviewer` into `.cursor/skills/`).
3b. **Mechanical check** — `./Trinity/scripts/pilot-preflight.sh` (after skills; Studio optional).
4. **Reviewer renderer** —  
   `python3 Trinity/reviewer/scripts/render_report.py Trinity/reviewer/samples/demo-epic.payload.json --strict`
5. **Trinity Studio** —  
   `./Trinity/studio/scripts/start.sh` (installs Python deps from `Trinity/studio/requirements.txt`, including **jsonschema**).  
   UI http://127.0.0.1:5173 · `curl -sf http://127.0.0.1:8765/api/health` (check `features` includes `importer_execute`).  
   Smoke: open **Personas** and **Reviewer configs**; save should write under `Trinity/personas/` and `Trinity/reviewer/config/runs/`.  
   Importer UI: [`GUIDE.md` §6](GUIDE.md#6-importer-studio--xray) (project key selector, mapping, folder).
6. **Import** —  
   `./Trinity/studio/scripts/import-run.sh Trinity/reviewer/runs/<folder-that-directly-contains-EPIC-KEY>` after a Reviewer portfolio scan (runs are gitignored).
7. **Pipeline** — skim [`PIPELINE.md`](PIPELINE.md); hands-on walkthrough: [`TESTING.md`](TESTING.md).
8. **Optional Jira REST** (Studio scope resolve) — copy `Trinity/studio/.env.example` → `.env` with API token; otherwise use **Copy JQL resolve prompt** in Reviewer configs.
9. **Optional Cursor cost** — enable [`.cursor/hooks.json`](../.cursor/hooks.json) (open repo root in Cursor); arm stages in Studio per [`CURSOR-COST.md`](CURSOR-COST.md). Set `CURSOR_ADMIN_API_KEY` in `.env` to backfill USD.
10. **BigQuery release gate** — BigQuery is optional for pipeline work but required
    before release/UAT when credentials are available. Put the service-account key
    at `~/.config/trinity/qa-coe-bigquery.json`, restart Studio, then run:
    ```bash
    curl -s -X POST http://127.0.0.1:8765/api/telemetry/sync | jq .
    curl -s http://127.0.0.1:8765/api/telemetry/summary | jq .
    ```
    Pass when sync reports `failed: 0`, `pending: 0`, and `report_errors: []`,
    summary reports `bigquery_configured: true`, and the run is visible in
    `qa-coe.trinity.v_run_summary`. Without a local key, Studio must still start
    and pipeline work remains available; record live BigQuery verification as an
    environment-dependent precondition. Full setup: [`BIGQUERY.md`](BIGQUERY.md).
