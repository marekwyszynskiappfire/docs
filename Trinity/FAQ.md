# Trinity — FAQ

Answers for engineers and QA operators adopting the **Reviewer → Creator → Studio → Importer** pipeline. Start with [FIRST-RUN.md](FIRST-RUN.md) and [GUIDE.md](GUIDE.md). Contracts: [CONTRACTS.md](CONTRACTS.md).

Related: [METRICS.md](METRICS.md) · [MATEUSZ-CRITERIA.md](MATEUSZ-CRITERIA.md) · [ADR 0002](../docs/adr/0002-trinity-importer-telemetry-decisions.md)

---

## What does the solution do end to end?

| Capability | How it works | Where to read |
|------------|--------------|---------------|
| Generate test scenarios / cases from requirements | Reviewer `review-payload.json` → **trinity-creator** → `suite-payload.json` | [creator/SKILL.md](creator/SKILL.md), [GUIDE.md](GUIDE.md) |
| Persist approved tests to **Xray on Jira** | Importer GraphQL create; default project **TC** (override in Studio) | [importer/SKILL.md](importer/SKILL.md), [ADR 0002](../docs/adr/0002-trinity-importer-telemetry-decisions.md) |
| Agent / skill workflow | `trinity-reviewer`, `trinity-creator`, `trinity-importer` + **Trinity Studio** | `./Trinity/scripts/install-trinity-skills.sh`, [TESTING.md](TESTING.md) |
| Control structure and granularity | Golden corpus, personas, Studio edit; 3–5 journeys per Epic | [creator/SKILL.md](creator/SKILL.md), [creator/golden/](creator/golden/) |

---

## How do we control output quality?

| Control area | Mechanism | Measurement |
|--------------|-----------|-------------|
| **Granularity** | Golden v2 + test-architect persona; operators edit in Studio | Reject with `granularity_too_high` / `granularity_too_low` ([METRICS.md](METRICS.md)) |
| **Quality** | Reviewer findings; Studio approve/reject; Importer validation | `test_case_review` events; acceptance rate in telemetry summary |
| **Repeatability** | JSON schemas, versioned skills | Revision history in SQLite |
| **Human intervention** | Required approve/reject; PROD execute confirmation | Telemetry export |

---

## What metrics are available?

See [METRICS.md](METRICS.md). Summary endpoint:

```bash
curl -s http://127.0.0.1:8765/api/telemetry/summary | jq .
```

BigQuery / Looker requires `TRINITY_TELEMETRY_URL` (optional; track setup in GitHub Issues if needed).

---

## What should a new engineer read?

| Topic | Document |
|-------|----------|
| First run | [FIRST-RUN.md](FIRST-RUN.md) |
| Install and credentials | [GUIDE.md](GUIDE.md), [PREFLIGHT.md](PREFLIGHT.md) |
| Full reference | [MANUAL.md](MANUAL.md) |
| Reviewer reports | [reviewer/MANUAL.md](reviewer/MANUAL.md) |

---

## Where are engineering decisions recorded?

- Importer production policy, telemetry: [ADR 0002](../docs/adr/0002-trinity-importer-telemetry-decisions.md)
- Releases and roadmap: [`CHANGELOG.md`](CHANGELOG.md) · [`PATH-TO-1.0.md`](PATH-TO-1.0.md) · [`VERSIONING.md`](VERSIONING.md)
