# Importer Jira/Xray mapping files

Each `*.json` file here is one **import profile**: Jira site, default **project**, Xray folder default, required Jira custom fields on `createTest`, and requirement link types.

**Ownership (IQ-09):** QA lead per product line maintains profiles when project or `jira_required_fields` differ from the shipped **TC** default (PRs to this repo).

## Shipped profiles

| File | Site | Default `project.key` | Notes |
|------|------|------------------------|--------|
| `appfire-production.json` | appfire.atlassian.net | **TC** | QA Test project; matches golden filter 17844. `project.id` set for `createFolder`. |
| `appfire-sandbox.json` | appfire-sandbox-774 | **TC** | Placeholder; fill `project.id` and field IDs after sandbox Xray is licensed. |

**TC is not imposed by Creator or golden at import time** — it is only the default in these files because Appfire QA and the committed golden export use that project. Operators override the project in Studio or via `--project` on the CLI.

## Add a profile for another project

1. Copy the production (or sandbox) template:

   ```bash
   cp appfire-production.json appfire-production-YOURKEY.json
   ```

2. Edit:

   - `project.key` — target Jira project  
   - `project.id` — numeric id (required for `createFolder`)  
   - `defaults.jira_required_fields` — use Jira REST create-meta for Test issue type in that project  
   - `defaults.folder_path` — optional Xray Test Repository default  
   - `jira.site_url` — must match the Jira **instance** selected in Studio  

3. Discover required custom fields (example):

   ```bash
   curl -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
     "https://appfire.atlassian.net/rest/api/3/issue/createmeta?projectKeys=YOURKEY&issuetypeNames=Test&expand=projects.issuetypes.fields"
   ```

4. Select the new file in Studio → **Importer** → **Mapping file**, or pass `--config` to `xray_graphql_import.py`.

## Project key override without a new file

Studio **Importer** → **Project key** overrides `project.key` for a single run. Custom fields still come from the mapping file — if the other project needs different field IDs, add a dedicated mapping JSON.
