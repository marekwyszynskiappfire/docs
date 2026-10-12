# Trinity Importer (pillar 3)

**Status:** v0.3 — Studio plan + **Execute batch** (`POST /api/importer/execute`); CLI for single-test and automation.

Approved Creator exports → Xray on **production** or **sandbox** Jira.

## Quick start

1. Export from Studio: Creator run → **Export for Importer**.
2. Open **Importer** in Studio (`./Trinity/studio/scripts/start.sh` → http://127.0.0.1:5173/importer).
3. Set **instance**, **mapping**, **Jira project key**, **folder** — see **[GUIDE.md § Getting Started](../GUIDE.md#getting-started)** (canonical project selector).
4. **Preview import plan** → optional **Execute batch** (production requires typed confirmation).
5. Or **Copy Cursor prompt** → **trinity-importer** / CLI.

Operator depth: [GUIDE.md §6](../GUIDE.md#6-importer-why-tc-by-default-choosing-another-project) · [MANUAL.md §Importer](../MANUAL.md) · [SKILL.md](SKILL.md).

## Credentials (production default)

**Do not paste secrets in chat or commit them.** Use a local file:

```bash
cp Trinity/studio/.env.example Trinity/studio/.env
# Edit .env — production Xray API keys + Jira API token (appfire.atlassian.net)
./Trinity/studio/scripts/stop.sh && ./Trinity/studio/scripts/start.sh
```

Studio loads `Trinity/studio/.env` on API startup. Importer defaults to **Appfire production**; switch instance in the UI for sandbox. **Preview import plan** shows ✓/✗ for each variable; `GET /api/importer/credentials` returns the same (no secret values).

| Variable | Source |
|----------|--------|
| `XRAY_CLIENT_ID`, `XRAY_CLIENT_SECRET` | Xray → Settings → API Keys (for the **selected** Jira site) |
| `JIRA_EMAIL`, `JIRA_API_TOKEN` | [Atlassian API token](https://id.atlassian.com/manage-profile/security/api-tokens) |
| `JIRA_BASE_URL` | `https://appfire.atlassian.net` (production) or sandbox URL if testing there |

Sandbox mapping: update [`config/mappings/appfire-sandbox.json`](config/mappings/appfire-sandbox.json) (`project.id`, field IDs) before **create folder** on sandbox.

## Layout

| Path | Role |
|------|------|
| [`SKILL.md`](SKILL.md) | Agent skill |
| [`config/instances.json`](config/instances.json) | Production vs sandbox targets |
| [`config/mappings/`](config/mappings/) | Per-site Jira/Xray field mapping |
| [`scripts/xray_graphql_import.py`](scripts/xray_graphql_import.py) | GraphQL import CLI |
| [`schemas/`](schemas/) | Operator config JSON Schema |

## Next

- Per-instance credential profiles (optional env prefix).
- Post-POC: hard redaction block on execute; block/skip duplicate Xray keys (warn today).
