# Mateusz POC — answers (requirements → evidence)

**Source:** [Mateusz.MD](Mateusz.MD) (deadlines 14/10 solution, 16/10 docs + dashboards).  
**Operator narrative:** [POC-TC-GENERATOR.md](POC-TC-GENERATOR.md) · **Scorecard:** [SCORECARD-TC-GENERATOR.md](SCORECARD-TC-GENERATOR.md) · **Slides:** [POC-GOOGLE-SLIDES-BULLETS.md](POC-GOOGLE-SLIDES-BULLETS.md)  
**Decisions:** [ADR 0002](../docs/adr/0002-trinity-importer-telemetry-decisions.md) · **Grill:** [GRILL-SESSION-2026-10-12.md](GRILL-SESSION-2026-10-12.md)

This page answers Mateusz’s sections **before** the final scorecard + Slides pass (human-owned closure).

---

## §1 — Working solution by 14/10

| Requirement | Answer | Evidence |
|-------------|--------|----------|
| Generate scenarios / test cases from input | **Yes** — Reviewer `review-payload.json` → **trinity-creator** → `suite-payload.json` / batch JSON | [GUIDE.md](GUIDE.md), [creator/SKILL.md](creator/SKILL.md) |
| Persist to **Xray on Jira PROD** (dedicated test project) | **Yes** — Importer GraphQL create; default project **TC** (override in Studio); prod policy [ADR 0002](../docs/adr/0002-trinity-importer-telemetry-decisions.md) | Example keys **TC-6704–6708** ([SCORECARD](SCORECARD-TC-GENERATOR.md)); Studio **Execute batch** + CLI |
| Agent / skill / workflow ready for practical use | **Yes** — `trinity-reviewer`, `trinity-creator`, `trinity-importer` + **Trinity Studio** (import, review, export, plan, execute) | `./Trinity/scripts/install-trinity-skills.sh`, [TESTING.md](TESTING.md) |
| Control structure and granularity | **Yes** — golden corpus, personas, 3–5 journeys/Epic, Studio edit; see control table below | [POC-TC-GENERATOR.md §2](POC-TC-GENERATOR.md#2-how-we-control-output-mateusz-§1) |

### Control levers (not “demo only”)

| Control area | How we control it | How we **measure** it |
|--------------|-------------------|------------------------|
| **Granularity** | Golden v2 + test-architect persona; reject `granularity_too_high` / `granularity_too_low` | Rejection reason enum + Studio summary |
| **Quality** | Reviewer findings/questions; Studio approve/reject; Importer validation | `test_case_review` events; acceptance rate |
| **Repeatability** | Schemas, versioned skills, `golden_sampling` on batches | Same input → comparable batch shape; revision history in SQLite |
| **Maintainability** | Style rules, `automation_fit`, journey pattern | Reason `maintainability`; edit + re-approve in Studio |
| **Team standards** | TC golden + per-product config/mappings | Mapping README; product table in Creator tab |
| **Human intervention** | Required approve + optional reject reason; PROD typed confirm; soft Reviewer gate on Importer | Telemetry + scorecard “Human review” row |

**POC scope (grill):** BigQuery/Looker and **hard** redaction/idempotency blocks are **post-POC**; local `metric_event` + export is sufficient for sign-off ([GRILL-SESSION](GRILL-SESSION-2026-10-12.md) Q1–Q4).

---

## §2 — Scorecard (one-pager)

| Scorecard field | Where it lives |
|-----------------|----------------|
| Template + example | [SCORECARD-TC-GENERATOR.md](SCORECARD-TC-GENERATOR.md) |
| Filled pilot #1 | Example **ONE-228469** (5/5 Xray) — extend with Studio telemetry export for runs that used bulk reject |
| Filled pilot #2+ | **Human:** second project row (§5) — same template |

**Checklist before sharing:** telemetry export, Xray folder screenshot, limitations note ([POC §9](POC-TC-GENERATOR.md#9-known-limitations-honest-poc)).

---

## §3 — Required metrics

| Metric | Implemented? | Where |
|--------|--------------|--------|
| # AI-generated test cases | **Yes** | `creator_batch_imported` payload; `test_cases` in `/api/telemetry/summary` |
| # accepted after human review | **Yes** | `test_cases_approved`; events with `human_review_status: approved` |
| # rejected | **Yes** | `test_cases_rejected`; reject + **required** `rejection_reason` |
| **Acceptance rate** | **Yes** | `/api/telemetry/summary` → `acceptance_rate` |
| Rejection reasons (granularity, duplicates, missing scenarios, wrong assumptions, weak steps, requirements mismatch, maintainability, other) | **Yes** | Enum in [METRICS.md](METRICS.md); aggregated in summary |
| Time to generate + review | **Partial** | Event timestamps in `metric_event` / export — **no** built-in wall-clock dashboard; record manually on scorecard until BQ |
| Comparison to non-AI process | **Manual** | Scorecard **Impact**; no automated baseline study in POC |

```bash
curl -s http://127.0.0.1:8765/api/telemetry/summary | jq .
curl -s http://127.0.0.1:8765/api/telemetry/export -o trinity-telemetry-export.json
```

Stable run IDs for BigQuery joins: `pr-…` / `cr-…` ([METRICS.md](METRICS.md)).

---

## §4 — Documentation and dashboards by 16/10

| Deliverable | Status | Location |
|-------------|--------|----------|
| Architecture / workflow | **Done** | [GUIDE.md](GUIDE.md), [PIPELINE.md](PIPELINE.md), [POC-TC-GENERATOR.md §3](POC-TC-GENERATOR.md#3-architecture-one-paragraph) |
| How to use | **Done** | [GUIDE.md](GUIDE.md), [MANUAL.md](MANUAL.md), [TESTING.md](TESTING.md) |
| Required input | **Done** | Reviewer payloads, Creator batch schema, Importer handoff |
| Configuration | **Done** | `.env.example`, mappings, `creator/config`, Studio Importer UI |
| Quality control rules | **Done** | Skills, `validate_for_xray`, Importer plan, grill ADR |
| Human review rules | **Done** | [MANUAL.md](MANUAL.md), Studio Creator run UI, rejection reasons |
| Granularity control | **Done** | Golden + personas + [creator/SKILL.md](creator/SKILL.md) |
| Known limitations | **Done** | [POC-TC-GENERATOR.md §9](POC-TC-GENERATOR.md#9-known-limitations-honest-poc) |
| Scorecard | **Template + example** | [SCORECARD-TC-GENERATOR.md](SCORECARD-TC-GENERATOR.md) — **fill** for each pilot |
| **Preconfigured dashboards** | **Partial** | **Local:** `/api/telemetry/summary`, portfolio rollup on Dashboard. **Looker/BigQuery:** blocked on ingest URL + credentials ([METRICS.md § BigQuery](METRICS.md#optional-bigquery-when-credentials-exist)); track in [GITHUB-BACKLOG.md](GITHUB-BACKLOG.md) |

---

## §5 — Multi-project validation

| Question | Answer |
|----------|--------|
| Ready to run before POC end? | **Yes** — do not wait; second mapping/product via `creator/config` + neutral golden ([IQ-12](REVIEW-PRODUCT-AND-DOCS.md)) |
| Different requirement types | Supported via different `product_id` / mapping; **evidence** = 2+ scorecard rows |
| Repeatable quality | Same pipeline; compare `acceptance_rate` and `rejection_reasons` per run in export |
| Config differences between projects | [mappings/README.md](importer/config/mappings/README.md), Creator products table |
| Granularity rules sufficient? | Grill + rejection reasons surface gaps; adjust golden/persona per product |
| Top rejection causes | `/api/telemetry/summary` → `rejection_reasons` |
| Scale beyond one test project | IQ-09: QA lead owns mappings; Studio stable `pr-`/`cr-` IDs for analytics |

**Action for Marek:** Add **pilot 2** row to scorecard (non-TC or second Epic) and attach telemetry export.

---

## Closing questions (must be answerable at POC end)

| Question | Answer today | Evidence still needed for leadership |
|----------|--------------|--------------------------------------|
| **Does it work?** | **Yes** — prod path proven (ONE-228469 → TC-6704–6708); Studio E2E + CI | One **fresh** documented run in scorecard + optional short recording |
| **Did people actually use it?** | **Operator-driven POC** — `operator_id` / `JIRA_EMAIL` in telemetry; scorecard **Who used it** | Names of reviewers beyond operator; second pilot user |
| **What % accepted?** | **Measurable** per Creator run: `acceptance_rate` in summary | Export after runs with real reject mix (not only pre-import validation fixes) |
| **Why rejected?** | **Measurable** — `rejection_reasons` breakdown | Narrative 2–3 bullets in Slides from summary JSON |
| **Impact on time / quality / cost?** | **Qualitative in scorecard** until baseline study | Fill **Impact** row; optional time notes from event timestamps |

---

## Recommendation and scaling (draft for Slide 10)

- **Recommendation:** Widen pilot to **2–3 products** with filled scorecards; keep **production-only** Xray write policy.
- **Scale enablers already in repo:** Studio run IDs, local telemetry, Importer execute, mappings registry, grill decision log.
- **Post-POC engineering:** See [GITHUB-BACKLOG.md](GITHUB-BACKLOG.md) (GitHub issues to create).

---

## Human closure (Mateusz deadlines)

| By | Owner | Artifact |
|----|-------|----------|
| 14/10 | Engineering | Working path (done); **one** filled scorecard beyond template example |
| 16/10 | QA + presenter | Slides from [POC-GOOGLE-SLIDES-BULLETS.md](POC-GOOGLE-SLIDES-BULLETS.md); telemetry export file; honest dashboard slide (local now, BQ later) |
