# Payload schemas

| File | Purpose |
|------|---------|
| `TestCaseDraft.schema.json` | **Current** batch shape (`tests[]`) — Trinity Studio import |
| `suite-payload.schema.json` | Planned canonical suite + coverage (evolves from TestCaseDraft) |
| `import-payload.schema.json` | Importer dry-run / submit outcomes per test |

Agent runs should write **`suite-payload.json`** validated against `TestCaseDraft.schema.json` until the dedicated suite schema ships.

Plan: [`../../The Creator/ACTION-PLAN.md`](../../The%20Creator/ACTION-PLAN.md) Phase 1–2.
