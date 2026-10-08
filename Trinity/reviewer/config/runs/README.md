# Portfolio run configuration

One JSON file per **stable portfolio id**: `{portfolio_id}.json`

Validated against [`../../schemas/run-config.schema.json`](../../schemas/run-config.schema.json).

The Reviewer **interactive interview** creates or updates these files. On later runs it asks whether config changed; if not, it confirms scope and reuses the file.

Example: [`example.demo-portfolio.json`](example.demo-portfolio.json) (sanitized).

**Private configs:** name files `{portfolio_id}-local.json` — `*-local.json` is gitignored.

**Do not commit** files that embed internal Jira filter URLs with secrets; use `example.*` or `*-local.json`.
