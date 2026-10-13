# Importer & Xray

<!-- Confluence title: Trinity — Importer & Xray -->

## Purpose

Move **approved, marked** Creator tests into Xray Test Repository folders, linked to Jira requirements where configured.

## Prerequisites

- `JIRA_*` and `XRAY_*` in `Trinity/studio/.env`.
- Creator run exported (**Export for Importer**).
- Mapping file under `Trinity/importer/config/mappings/`.

## Studio flow

1. **Importer** tab (optionally `?creator_run_id=<id>`).
2. Select **Jira instance** — sandbox for learning; production only with care.
3. **Mapping** + **project key** + **folder path** (e.g. `/TC Importer/ONE-12345`).
4. **Preview import plan** — fix validation errors; acknowledge **Reviewer gate** if required.
5. **Copy Cursor prompt** → run Importer in Cursor **or** **Execute import batch** in Studio.
6. **Persist Xray keys** — point to `xray-import-report.json` or report folder.

## Production safety

When instance `risk_tier` is **production**, type **`PRODUCTION`** before preview copy or execute (same pattern as Jira epic comment post on production host).

## PM-safe summary

Import plan includes a short summary suitable for stakeholders (no raw test steps).

## Deeper reference

- `Trinity/GUIDE.md` §6
- `Trinity/importer/README.md`
- ADR 0002 (telemetry decisions)
