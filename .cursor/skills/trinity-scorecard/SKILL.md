---
name: trinity-scorecard
description: >-
  Record a completed Trinity pipeline run on the Trinity Usage Scorecard Google
  Sheet. Use when the operator pastes the scorecard prompt, RUN DATA, or asks to
  update the pilot scorecard / Excel / spreadsheet after Studio Statistics.
disable-model-invocation: true
---

# Trinity Usage Scorecard (Google Sheet)

**Interim evidence store** (BigQuery deferred). One row per run on the product tab.

**Spreadsheet (fixed):** https://docs.google.com/spreadsheets/d/123L4BTTTrgghlLHni-vqCAEiJperj-pu1tDKuEyg6oo/edit

**Copy-paste prompt for operators:** [`Trinity/pilot-scorecard-cursor-prompt.md`](Trinity/pilot-scorecard-cursor-prompt.md)

**Column mapping and workflow:** [`Trinity/SCORECARD.md`](Trinity/SCORECARD.md)

## When triggered

1. Operator provides **RUN DATA** (Statistics export JSON, bullets, or `pipeline_run_id` + ask to read Studio export if local).
2. Use **Google Drive** MCP (`read_file` / sheet update tools) on spreadsheet id `123L4BTTTrgghlLHni-vqCAEiJperj-pu1tDKuEyg6oo`.
3. **Product tab:** `BigPicture` (default), `TimeTracker`, or `JMWE` from product in RUN DATA.
4. **Run ID:** next free id on that tab (`BP-`, `TT-`, `JMWE-` prefix). Never reuse ids.
5. **Append one row** — columns in header order on that tab (see SCORECARD.md table).
6. Do **not** edit **Dashboard** or **_Config** formulas.

## RUN DATA sources (Studio)

- Statistics page or `GET /api/runs/{pipeline_run_id}/statistics/export` on local Studio (`8765`).
- Map: epics reviewed/approved, TC gen/appr/rej, Xray count, phase minutes (TC review + overall), coverage depth, operator name, use case (`create` | `review` | `modify`).

## Optional (not default workflow)

Studio can push via Sheets API when `TRINITY_SCORECARD_CREDENTIALS` is set (`POST /api/runs/{id}/scorecard/push`). Prefer **Cursor + prompt** unless the operator explicitly asks for Studio push.
