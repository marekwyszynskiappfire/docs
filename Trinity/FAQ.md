# Trinity — FAQ

Answers for engineers and QA operators adopting the **Reviewer → Creator → Studio → Importer** pipeline. For step-by-step operations, start with [GUIDE.md](GUIDE.md). For contracts and schemas, see [PIPELINE.md](PIPELINE.md) and [CONTRACTS.md](CONTRACTS.md).

Related: [POC-TC-GENERATOR.md](POC-TC-GENERATOR.md) (operator narrative) · [METRICS.md](METRICS.md) · [SCORECARD-TC-GENERATOR.md](SCORECARD-TC-GENERATOR.md) · [ADR 0002](../docs/adr/0002-trinity-importer-telemetry-decisions.md)

---

## What does the solution do end to end?

| Capability | How it works | Where to read |
|------------|--------------|---------------|
| Generate test scenarios / cases from requirements | Reviewer `review-payload.json` → **trinity-creator** → `suite-payload.json` / batch JSON | [creator/SKILL.md](creator/SKILL.md), [GUIDE.md](GUIDE.md) |
| Persist approved tests to **Xray on Jira production** | Importer GraphQL create; default project **TC** (override in Studio) | [importer/SKILL.md](importer/SKILL.md), [ADR 0002](../docs/adr/0002-trinity-importer-telemetry-decisions.md) |
| Practical agent / skill / workflow | `trinity-reviewer`, `trinity-creator`, `trinity-importer` + **Trinity Studio** (import, review, export, plan, execute) | `./Trinity/scripts/install-trinity-skills.sh`, [TESTING.md](TESTING.md) |
| Control structure and granularity | Golden corpus, personas, coverage catalog, Studio edit; 3–5 journeys per Epic guidance in Creator skill | [POC-TC-GENERATOR.md §2](POC-TC-GENERATOR.md#2-how-we-control-output) |

Demonstrated production path: ONE-228469 → Xray **TC-6704–6708** ([SCORECARD-TC-GENERATOR.md](SCORECARD-TC-GENERATOR.md) example).

---

## How do we control output quality (beyond “AI generated some tests”)?

| Control area | Mechanism | Measurement |
|--------------|-----------|-------------|
| **Granularity** | Golden v2 + test-architect persona; operators edit in Studio | Reject with `granularity_too_high` / `granularity_too_low` ([METRICS.md](METRICS.md)) |
| **Quality** | Reviewer findings; Studio approve/reject; Importer validation | `test_case_review` events; acceptance rate in telemetry summary |
| **Repeatability** | JSON schemas, versioned skills, `golden_sampling` on batches | Comparable batch shape; revision history in SQLite |
| **Maintainability** | Style rules, `automation_fit`, journey patterns | Rejection reason `maintainability`; edit + re-approve in Studio |
| **Team standards** | Golden filter + per-product config/mappings | [importer/config/mappings/README.md](importer/config/mappings/README.md) |
| **Human intervention** | Required approve/reject; optional reject reason; PROD execute confirmation (per ADR) | Telemetry + scorecard **Human review** row |

---

## How much does Cursor cost per pipeline step?

When Trinity runs in **Cursor IDE**, use **[CURSOR-COST.md](CURSOR-COST.md)**:

1. **Arm** the stage in Studio (Reviewer analyze, MCP questions, Creator, Importer).
2. Run the matching **Agent / skill** in a **new chat** per stage.
3. Hooks record **model** and **conversation id**; **Backfill** pulls **USD** and tokens when `CURSOR_ADMIN_API_KEY` is set.

Studio shows **per-stage cost**, **total**, and **models used** on the Reviewer run page. Cursor does not put dollars in hooks — cost is async from the Team Admin API (or manual entry).

---

## What metrics are available?

| Metric | Implemented | Source |
|--------|-------------|--------|
| Count of AI-generated test cases | Yes | `creator_batch_imported`; `test_cases` in `/api/telemetry/summary` |
| Accepted after human review | Yes | `test_cases_approved`; `human_review_status: approved` |
| Rejected | Yes | `test_cases_rejected`; `rejection_reason` on events |
| Acceptance rate | Yes | `/api/telemetry/summary` → `acceptance_rate` |
| Rejection reason breakdown | Yes | Enum in Studio; aggregated in summary |
| Wall-clock time (generate + review) | Partial | Timestamps in `metric_event` / export — no built-in dashboard yet |
| Comparison to manual-only process | Manual | Scorecard **Impact**; no automated baseline in repo |

```bash
curl -s http://127.0.0.1:8765/api/telemetry/summary | jq .
curl -s http://127.0.0.1:8765/api/telemetry/export -o trinity-telemetry-export.json
```

Stable run IDs for analytics joins: `pr-<uuid>` (Reviewer import) and `cr-<uuid>` (Creator batch) — see [METRICS.md](METRICS.md).

**Dashboards:** Local summary and export are always available. BigQuery / Looker requires `TRINITY_TELEMETRY_URL` and ingest credentials ([GITHUB-BACKLOG.md](GITHUB-BACKLOG.md)).

---

## What documentation should a new engineer read?

| Topic | Document |
|-------|----------|
| Install and first run | [README.md](README.md), [GUIDE.md](GUIDE.md) |
| End-to-end pipeline | [PIPELINE.md](PIPELINE.md) |
| Studio UI and review workflow | [MANUAL.md](MANUAL.md), [studio/README.md](studio/README.md) |
| Importer project and mappings | [GUIDE.md §6](GUIDE.md), mappings README |
| Quality rules in agents | Reviewer/Creator/Importer `SKILL.md` under each component |
| Known limitations | [POC-TC-GENERATOR.md §9](POC-TC-GENERATOR.md#9-known-limitations) |
| Pilot evidence template | [SCORECARD-TC-GENERATOR.md](SCORECARD-TC-GENERATOR.md) |

---

## How do we run validation across multiple products or projects?

Do not wait for a single “demo complete” milestone if a second mapping is ready.

| Question | Answer |
|----------|--------|
| Different requirement types | Use different `product_id` / mapping; record one scorecard row per pilot |
| Repeatable quality | Same pipeline; compare `acceptance_rate` and `rejection_reasons` per run in export |
| Config differences | [mappings/README.md](importer/config/mappings/README.md), Creator products table in Studio |
| Granularity gaps | Rejection reasons surface them; adjust golden/persona per product |
| Scale beyond one test project | QA lead owns mappings; stable `pr-`/`cr-` IDs for analytics ([REVIEW-PRODUCT-AND-DOCS.md](REVIEW-PRODUCT-AND-DOCS.md)) |

---

## Sign-off questions (evidence, not slides alone)

Leadership and QA leads should be able to answer these from **scorecard + telemetry + Xray keys**:

| Question | Where to answer |
|----------|-----------------|
| Does it work? | Scorecard example + Xray keys; [TESTING.md](TESTING.md) path |
| Did operators actually use it? | Scorecard **Who used it**; `operator_id` / `JIRA_EMAIL` in telemetry |
| What percentage was accepted? | `/api/telemetry/summary` → `acceptance_rate` per Creator run |
| Why were cases rejected? | `rejection_reasons` in summary; narrative in scorecard |
| Impact on time, quality, or cost? | Scorecard **Impact** (qualitative until baseline study) |

---

## What is intentionally out of scope in the current release?

See [POC-TC-GENERATOR.md §9](POC-TC-GENERATOR.md#9-known-limitations) and post-release tracking in [GITHUB-BACKLOG.md](GITHUB-BACKLOG.md). Examples: hard redaction block on execute, idempotency hard block, `automation_fit` → Xray Automated field mapping, centralized Looker dashboards without BigQuery ingest.

---

## Where are engineering decisions recorded?

- Importer production policy, telemetry: [ADR 0002](../docs/adr/0002-trinity-importer-telemetry-decisions.md)
- Product open questions: [REVIEW-PRODUCT-AND-DOCS.md](REVIEW-PRODUCT-AND-DOCS.md)
- Stress-test session log (2026-10-12): [GRILL-SESSION-2026-10-12.md](GRILL-SESSION-2026-10-12.md)
