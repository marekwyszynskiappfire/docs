---
name: trinity-importer
description: >-
  Import approved Creator handoffs into Xray on a chosen Jira instance (production
  or sandbox). Operator selects mapping config, Test Repository folder, and whether
  to create the folder. Dry-run plan before execute.
---

# Trinity Importer

Consumes **`importer-payload.json`** from Trinity Studio (approved + marked for Xray import). Does **not** invent tests — only maps and submits.

## Operator decisions (required before execute)

1. **Jira instance** — `appfire-production` (`appfire.atlassian.net`) or `appfire-sandbox-774` (`appfire-sandbox-774.atlassian.net`). Registry: [`config/instances.json`](config/instances.json).
2. **Import mapping** — Jira project key, custom fields, labels, link types: [`config/mappings/*.json`](config/mappings/). Copy and edit per product; never commit API secrets.
3. **Test Repository folder** — Xray `folderPath` (e.g. `/BP/Release 2026`). Operator sets path explicitly in Studio or CLI.
4. **Create folder** — If `create_folder_if_missing` is true, Execute calls Xray GraphQL `createFolder` (requires `project.id` in mapping). If false, folder must already exist.

## Credentials (execute only)

Environment variables (never in repo):

- `XRAY_CLIENT_ID`, `XRAY_CLIENT_SECRET` — Xray Global Settings → API Keys for the **target** site.
- `JIRA_EMAIL`, `JIRA_API_TOKEN` — same Atlassian account that can create Tests and issue links on that site.

Switch env vars when switching instance; Studio shows which instance is selected.

## Workflows

### Studio (recommended)

1. Creator run → **Export for Importer**.
2. **Importer** nav → pick instance, mapping, folder, create-folder checkbox.
3. **Preview import plan** — validates tests and shows folder/credential readiness.
4. **Copy Cursor prompt** — paste into Cursor to run **trinity-importer** execute handoff (same pattern as Creator / Reviewer).
5. Execute — batch `createFolder` + `createTest` + requirement links (agent or CLI).

### CLI (single test)

```bash
export XRAY_CLIENT_ID=… XRAY_CLIENT_SECRET=… JIRA_EMAIL=… JIRA_API_TOKEN=…

python3 Trinity/importer/scripts/xray_graphql_import.py \
  --config Trinity/importer/config/mappings/appfire-sandbox.json \
  --batch path/to/importer-payload.json \
  --draft-id TC-001 \
  --folder "/Trinity sandbox/My epic" \
  --dry-run
```

Handoff JSON uses `tests[]` with `draft_id`; for batch files exported from Studio, point `--batch` at a file shaped like Creator batch or use Studio plan API.

## References

- [`reference.md`](reference.md) — contracts, mutations, mapping fields.
- [`../studio/README.md`](../studio/README.md) — API `POST /api/importer/plan`.
- [`scripts/xray_graphql_import.py`](scripts/xray_graphql_import.py) — GraphQL createTest (+ folder helpers).
