# Releases

Reusable Jira release-quality dashboard automation.

The project skill in [`SKILL.md`](SKILL.md) finds release Test Executions,
validates actual Xray execution activity when required, and creates or updates
Jira dashboards containing one Filter Results gadget per release.

## Contents

- `SKILL.md` — agent workflow and safety rules.
- `reference.md` — Jira/Xray queries and selection rules.
- `scripts/jira_release_dashboard.py` — idempotent dashboard/filter automation.
- `examples/dashboard-manifest.json` — manifest template.

## Quick start

```bash
export JIRA_BASE_URL=https://example.atlassian.net
export JIRA_EMAIL=you@example.com
export JIRA_API_TOKEN=...

python3 Releases/scripts/jira_release_dashboard.py \
  Releases/examples/dashboard-manifest.json

python3 Releases/scripts/jira_release_dashboard.py \
  Releases/examples/dashboard-manifest.json \
  --execute
```

The first command is a dry run. `--execute` creates or updates Jira objects and
writes a local state file beside the manifest. Never commit credentials.
