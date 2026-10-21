# Trinity → BigQuery → Looker Studio

Operator setup for saving Trinity pipeline telemetry in BigQuery and visualizing
complete runs in Looker Studio (formerly Data Studio).

The step a new operator follows is in [`MANUAL.md`](MANUAL.md) (New operator, §5) and [`OPERATOR-SETUP.md`](OPERATOR-SETUP.md) step 17. This file is the reference for IAM, tables, hosted ingest, and Looker.

**Wiki:** [BigQuery and Looker](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3779068614/Trinity+BigQuery+and+Looker)

The default target is:

- GCP project: `qa-coe`
- BigQuery dataset: `trinity`
- Events table: `telemetry_events`
- Current run table: `pipeline_run_reports`

## What “complete E2E run” means

Trinity stores two complementary records:

1. **Step events** — an append-only audit trail in `telemetry_events`.
2. **Current run snapshot** — one up-to-date row per `pipeline_run_id` in
   `pipeline_run_reports`.

The snapshot covers Reviewer import through Xray persistence: epics, findings,
questions, readiness, drafted/amended/imported tests, phase timing, product,
and the operator who started the run.

For complete linkage:

1. Import the Reviewer run folder into Studio.
2. Import each Creator suite through Studio. The suite must retain `review_ref`;
   Studio uses it to link the Creator batch to the Reviewer `pipeline_run_id`.
3. Review and export tests through Studio.
4. Run Importer through Studio and persist returned Xray keys.

Reviewer Agent work before folder import is represented by the run folder,
handoff timestamps, and file timestamps. It is not an event-by-event Agent log.
Cursor cost/session data is separate and requires the Cursor hooks documented in
[`CURSOR-COST.md`](CURSOR-COST.md).

## Identity model

The GCP service account is only the technical BigQuery writer. It is not the
person shown in analytics.

- `operator_id`: `TRINITY_OPERATOR_ID`, falling back to `JIRA_EMAIL`
- `operator_name`: `TRINITY_OPERATOR_NAME`, falling back to the local account
- `product_id`: Reviewer handoff or Creator suite, for example `bigpicture`
- `product_name`: product config display name, for example `BigPicture`

Every event records the person performing that Studio step. The run snapshot
uses the operator who first imported the Reviewer run.

## One-time GCP setup

The service account needs:

- BigQuery Job User on project `qa-coe`
- BigQuery Data Editor on dataset `qa-coe.trinity`

Keep its JSON key outside the repository. Recommended local path:

```bash
mkdir -p ~/.config/trinity
chmod 700 ~/.config/trinity
mv ~/Downloads/<downloaded-key>.json \
  ~/.config/trinity/qa-coe-bigquery.json
chmod 600 ~/.config/trinity/qa-coe-bigquery.json
```

Never paste the JSON into chat, commit it, or store it under `Trinity/`.

## Studio environment

Copy [`studio/.env.example`](studio/.env.example) to `studio/.env` if needed.
Add:

```bash
# Human identity shown in BigQuery and Looker Studio
TRINITY_OPERATOR_ID=you@appfire.com
TRINITY_OPERATOR_NAME="Your Name"

# BigQuery target
BQ_PROJECT=qa-coe
BQ_DATASET=trinity

# Absolute path; `~` is not expanded inside .env values
GOOGLE_APPLICATION_CREDENTIALS=/Users/<mac-login>/.config/trinity/qa-coe-bigquery.json
```

Do not add the JSON contents to `.env`.

For the local ingest started by `start.sh`, leave these unset:

```bash
# TRINITY_TELEMETRY_URL=
# TRINITY_TELEMETRY_API_KEY=
```

`start.sh` generates a local API key under the gitignored `studio/data/`
directory and exports the local URL automatically.

For a shared hosted ingest, configure instead:

```bash
TRINITY_TELEMETRY_URL=https://<host>/v1/events
TRINITY_TELEMETRY_API_KEY=<shared-ingest-secret>
```

In hosted mode, operators do not need a service-account JSON on their laptops.
The hosted ingest owns the GCP credentials.

## Start and automatic synchronization

Start Studio normally:

```bash
./Trinity/studio/scripts/start.sh
```

When a local credential file is available, this command:

1. Installs the BigQuery Python client in Studio’s virtual environment.
2. Creates or upgrades the two tables and reporting views.
3. Starts local ingest on `127.0.0.1:8787`.
4. Starts Studio.
5. Backfills pending events and recomputes all run snapshots.
6. Flushes after every later Studio event.

BigQuery failure never blocks Reviewer, Creator, or Importer. Failed writes
remain in SQLite `telemetry_outbox` for retry.

## Manual synchronization and checks

Force a complete backfill:

```bash
curl -s -X POST http://127.0.0.1:8765/api/telemetry/sync | jq .
```

Expected healthy result:

```json
{
  "report_errors": [],
  "failed": 0,
  "pending": 0
}
```

Check local status:

```bash
curl -s http://127.0.0.1:8765/api/telemetry/summary | jq .
```

Check BigQuery:

```sql
SELECT
  pipeline_run_id,
  pipeline_label,
  operator_name,
  product_name,
  computed_at
FROM `qa-coe.trinity.v_run_summary`
ORDER BY computed_at DESC;
```

If credentials are added before Studio is started, schema-only setup is:

```bash
cd Trinity/studio
GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/key.json \
  .venv/bin/python scripts/bq_ingest.py --setup-only
```

## Looker Studio setup

1. Open Looker Studio and select **Create → Report**.
2. Add a **BigQuery** data source.
3. Select project `qa-coe`, dataset `trinity`.
4. Use `v_run_summary` for portfolio/run scorecards.
5. Add `v_run_phases` for duration charts.
6. Add `v_run_epics` for epic-level drill-down.
7. Add `v_event_details` for funnel, acceptance, and rejection analysis.
8. Add report controls for date, `product_name`, `operator_name`, and
   `pipeline_run_id`.

Recommended first page:

- Scorecards: runs, epics reviewed, tests drafted, tests imported to Xray
- Filters: date, product, operator
- Table: run label, operator, product, readiness, drafted/imported tests
- Bar chart: overall duration by run

Looker viewers need permission to read the dataset, or the data source must use
owner credentials according to Appfire policy.

## Reporting views

- `v_run_summary`: one row per run, flattened summary metrics
- `v_run_phases`: one row per run phase
- `v_run_epics`: one row per epic in a run
- `v_event_details`: one row per recorded Studio action

Connect Looker Studio to these views rather than parsing JSON directly.

## Completeness checklist

A run is complete when:

- `pipeline_run_reports` contains its `pipeline_run_id`
- `operator_id`, `operator_name`, `product_id`, and `product_name` are populated
- Creator runs are linked to the same `pipeline_run_id`
- the snapshot reports expected drafted and Xray-imported test counts
- `/api/telemetry/sync` returns `failed: 0`, `pending: 0`, and no report errors

Runs created before product metadata existed may show a blank product. Re-import
the Reviewer folder or its Creator suite with `product_id` to repair that link,
then run the sync endpoint again.
