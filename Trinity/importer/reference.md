# Trinity Importer — reference

## Handoff input

Studio export: `Trinity/studio/data/exports/creator/{creator_run_id}/importer-payload.json`

| Field | Meaning |
|-------|---------|
| `export_kind` | `creator_importer_handoff` |
| `creator_run_id` | Studio Creator run |
| `tests[]` | Approved TestCaseDraft objects |

## Operator config schema

[`schemas/import-operator-config.schema.json`](schemas/import-operator-config.schema.json)

## Jira instances

[`config/instances.json`](config/instances.json) lists stable `id`, human `label`, `jira_site`, and `default_mapping`.

## Mapping file (`jira_xray_mapping`)

| Section | Purpose |
|---------|---------|
| `project.key` | Jira project for Tests |
| `project.id` | Numeric id — **required** for `createFolder` when `create_folder_if_missing` |
| `defaults.folder_path` | Suggested default in UI only |
| `defaults.jira_required_fields` | Custom fields on create (site-specific IDs) |
| `jira.site_url` | Must match selected instance |
| `requirement_link` | Jira link type + inward/outward roles for coverage |

Sandbox mappings often use empty `jira_required_fields` until field IDs are confirmed.

## Folder behaviour

| `create_folder_if_missing` | Behaviour |
|----------------------------|-----------|
| `false` | `createTest` uses `folderPath`; folder must exist in Test Repository |
| `true` | Plan includes `createFolder(projectId, path)` before tests; needs `project.id` |

Normalize paths with a leading `/` (Studio and `normalize_folder_path` in script).

## Studio API

| Method | Path |
|--------|------|
| GET | `/api/importer/instances` |
| GET | `/api/importer/mappings` |
| POST | `/api/importer/plan` — body: `jira_instance_id`, `folder_path`, `create_folder_if_missing`, optional `mapping_path`, `creator_run_id` or `payload_path` |

Response `mode`: `dry_run_plan` — no Xray calls.

## Execute (roadmap)

1. Optional `createFolder` when configured.
2. Per test: `createTest` (GraphQL).
3. Per requirement key: Jira issue link (`Test` type by default).

Dry-run CLI today: `xray_graphql_import.py` without `--execute`.
