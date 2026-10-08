# Trinity Importer (pillar 3)

**Status:** v0.2 — instance + mapping + folder targeting in Studio; dry-run plan API; CLI execute for single tests.

Approved Creator exports → Xray on **production** or **sandbox** Jira.

## Quick start

1. Export from Studio: Creator run → **Export for Importer**.
2. Open **Importer** in Studio (or `./Trinity/studio/scripts/start.sh` → http://127.0.0.1:5173/importer).
3. Select **Appfire sandbox (774)** or **production**, mapping file, folder path, and whether to **create folder**.
4. **Preview import plan** — validates payload and shows credential/folder readiness.

## Sandbox credentials

**Do not paste secrets in chat or commit them.** Use a local file:

```bash
cp Trinity/studio/.env.example Trinity/studio/.env
# Edit .env — Xray API keys + Jira API token for appfire-sandbox-774
./Trinity/studio/scripts/stop.sh && ./Trinity/studio/scripts/start.sh
```

Studio loads `Trinity/studio/.env` on API startup. Importer **Preview import plan** shows ✓/✗ for each variable; `GET /api/importer/credentials` returns the same (no secret values).

| Variable | Source |
|----------|--------|
| `XRAY_CLIENT_ID`, `XRAY_CLIENT_SECRET` | Xray → Settings → API Keys (on **sandbox** Jira) |
| `JIRA_EMAIL`, `JIRA_API_TOKEN` | [Atlassian API token](https://id.atlassian.com/manage-profile/security/api-tokens) |
| `JIRA_BASE_URL` | `https://appfire-sandbox-774.atlassian.net` |

Update [`config/mappings/appfire-sandbox.json`](config/mappings/appfire-sandbox.json): set `project.id` (Jira project settings) before using **create folder**.

## Layout

| Path | Role |
|------|------|
| [`SKILL.md`](SKILL.md) | Agent skill |
| [`config/instances.json`](config/instances.json) | Production vs sandbox targets |
| [`config/mappings/`](config/mappings/) | Per-site Jira/Xray field mapping |
| [`scripts/xray_graphql_import.py`](scripts/xray_graphql_import.py) | GraphQL import CLI |
| [`schemas/`](schemas/) | Operator config JSON Schema |

## Next

- Studio **Execute batch** (createFolder + createTest loop + link requirements).
- Per-instance credential profiles (optional env prefix).
- Import result tracking in Studio (`test_cases_imported_xray`).
