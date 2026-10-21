# TestCase_Cleanup

Inventory and clean up **Test** issues in the Jira/Xray **TC** project on Appfire production.

This is **not** part of Trinity. Trinity Importer *creates* Tests in TC; this project is for reviewing, classifying, and (only when you ask) changing or retiring existing ones.

## Target

| Item | Value |
|------|--------|
| Jira site | `https://appfire.atlassian.net` |
| Project key | `TC` |
| Project id | `10356` |
| Xray GraphQL | `https://xray.cloud.getxray.app/api/v2/graphql` |

Reuse Studio credentials locally (`Trinity/studio/.env`). Never commit secrets.

## Contents

- [`SKILL.md`](SKILL.md) — agent workflow and safety rules.
- [`reference.md`](reference.md) — JQL, Xray queries, classification hints.
- [`config/project.json`](config/project.json) — site and TC project identifiers.
- [`examples/inventory-manifest.json`](examples/inventory-manifest.json) — inventory run template.
- [`artifacts/`](artifacts/) — local inventories and dry-run plans (gitignored dumps).

## Operating principle

1. **Inventory** Tests (and related Xray folder / execution data).
2. **Classify** candidates (duplicate, orphan, obsolete, Trinity import, never executed).
3. **Propose** a dry-run plan (Jira transitions, labels, folder moves, saved filters).
4. **Execute** only after you confirm the host, the issue keys, and the action.

Default mode is read-only. Prefer archive / deprecate / label over delete. Do not delete Tests with execution history unless you name those keys and ask for delete.

## Credentials

```bash
# Same vars as Trinity Importer / Studio
export JIRA_BASE_URL=https://appfire.atlassian.net
export JIRA_EMAIL=you@example.com
export JIRA_API_TOKEN=...
export XRAY_CLIENT_ID=...
export XRAY_CLIENT_SECRET=...
```

Confirm `JIRA_BASE_URL` is production **TC** before any write. Do not infer the site from a local `.env` alone.
