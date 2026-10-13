# Mateusz POC — criteria traceability

**Source requirements (PL):** [`Mateusz.MD`](Mateusz.MD)  
**Release version:** [`VERSION`](VERSION) · [`VERSIONING.md`](VERSIONING.md)  
**Operator docs:** [`FIRST-RUN.md`](FIRST-RUN.md) · [`MANUAL.md`](MANUAL.md) · [`FAQ.md`](FAQ.md) · [`METRICS.md`](METRICS.md)  
**Decisions:** [ADR 0002](../docs/adr/0002-trinity-importer-telemetry-decisions.md)  
**Engineering backlog:** GitHub Issues on `marekwyszynskiappfire/docs` ([`docs/agents/issue-tracker.md`](../docs/agents/issue-tracker.md)). Suggested titles: *pilot 2 (M2)*, *BigQuery/Looker (M4–M5)*, *Slides + scorecard (M1/M3)* — create when `gh` is authenticated.

Status legend: **Done** · **Partial** · **Open** (human or infra still required)

Update the **Closure** section when pilots complete; link Confluence/Slides/Issue numbers in **Evidence**.

---

## §1 — Working POC (generate → Xray PROD, controlled quality)

| Requirement | Status | Where / how | Gap / next action |
|-------------|--------|-------------|-------------------|
| Generate scenarios / TCs from input | **Done** | Reviewer → **trinity-creator** → Studio | — |
| Persist to **Xray on Jira PROD** (dedicated test project) | **Done** | Importer; default **TC**; prod policy ADR IQ-03 | Document each pilot folder path on scorecard |
| Agent / skill / workflow practical use | **Partial** | Skills + Studio; Importer often via Cursor prompt | Optional: more in-Studio execute polish |
| Control **granularity** | **Done** | Golden v2, personas, Studio edit; reject reasons | — |
| Control **quality** | **Done** | Reviewer + Studio approve/reject; Importer validation | — |
| **Repeatability** | **Partial** | Schemas, golden sampling | No formal A/B rerun report |
| **Maintainability** (long-term) | **Partial** | Style rules; reason `maintainability` | Define how you **measure** maintainability beyond reject enum |
| **Standards** compliance | **Partial** | TC golden; per-product mappings (IQ-09) | Second product mapping + pilot evidence |
| **Human intervention** scope | **Done** | [`FAQ.md`](FAQ.md) control table; MANUAL review flow | — |

**Evidence:** ONE-228469 → TC-6704–6708 (prod import). Add **fresh** run row in scorecard below.

---

## §2 — Scorecard (one-pager)

| Scorecard field | Status | Where |
|-----------------|--------|--------|
| Template | **Done** | § [Scorecard template](#scorecard-template) below |
| Filled example (pilot 1) | **Partial** | ONE-228469 narrative in template example row |
| Filled pilot 2+ | **Open** | Second epic / product |
| Export for numbers | **Done** | `GET /api/telemetry/export` |

---

## §3 — Metrics

| Metric | Status | Where |
|--------|--------|--------|
| # AI-generated TCs | **Done** | `creator_batch_imported`; `test_cases_total` |
| # accepted after review | **Done** | `test_cases_approved`; `test_case_review` events |
| # rejected | **Done** | `test_cases_rejected` |
| Acceptance rate | **Done** | `/api/telemetry/summary` |
| Rejection reasons (full Mateusz list) | **Done** | [`METRICS.md`](METRICS.md) enum |
| Time to generate + review | **Open** | Manual on scorecard; optional from `metric_event` timestamps |
| vs non-AI baseline | **Open** | Scorecard **Impact**; no automated study |
| **BigQuery / Looker** dashboards | **Open** | Local SQLite + outbox; `TRINITY_TELEMETRY_URL` when creds exist |

```bash
curl -s http://127.0.0.1:8765/api/telemetry/summary | jq .
./Trinity/scripts/export-telemetry.sh trinity-telemetry-export.json
```

---

## §4 — Documentation and dashboards (16/10)

| Deliverable | Status | Location |
|-------------|--------|----------|
| Architecture / workflow | **Done** | [`ARCHITECTURE.md`](ARCHITECTURE.md), [`PIPELINE.md`](PIPELINE.md) |
| Usage, input, config | **Done** | [`GUIDE.md`](GUIDE.md), [`FIRST-RUN.md`](FIRST-RUN.md) |
| QC, human review, granularity, limitations | **Done** | [`MANUAL.md`](MANUAL.md), [`FAQ.md`](FAQ.md), skills |
| Confluence operator tree | **Done** | [QACoE Trinity guide](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3750559869/Trinity+AI-assisted+QA+pipeline+operator+guide) |
| Scorecard published | **Open** | Fill template; attach export JSON |
| Preconfigured **org** dashboards | **Partial** | Studio Dashboard + telemetry API; Looker **Open** |

---

## §5 — Multi-project validation

| Question | Status | Next action |
|----------|--------|-------------|
| Run before POC end (don’t wait) | **Open** | Start pilot 2 with mapping from [`importer/config/mappings/README.md`](importer/config/mappings/README.md) |
| Different requirement types | **Partial** | Supported via `product_id` / config |
| Repeatable quality across projects | **Open** | Compare `acceptance_rate` + `rejection_reasons` per run in export |
| Config differences documented | **Done** | GUIDE, mappings README, Creator products API |
| Scale beyond one test project | **Partial** | IQ-09 ownership; needs 2+ scorecard rows |

---

## Closing questions (leadership)

| Question | Status | Evidence still needed |
|----------|--------|------------------------|
| Does it work? | **Done** (technical) | One **current** scorecard + optional recording |
| Did people actually use it? | **Open** | Names in scorecard; second operator |
| What % accepted? | **Done** (when Studio used) | Export after run with real reject mix |
| Why rejected? | **Done** | Summary JSON + 2–3 bullets for Slides |
| Impact on time / quality / cost? | **Open** | Scorecard **Impact**; optional [`CURSOR-COST.md`](CURSOR-COST.md) |

---

## Scorecard template

Copy for each pilot; store filled copies in Confluence or a GitHub Issue (planning templates stay out of git per [`README.md`](README.md)).

| Field | Value |
|-------|--------|
| **Trinity version** | `cat Trinity/VERSION` or `/api/health` → `trinity_version` |
| **Use case** | |
| **Product / solution** | Trinity (Reviewer + Creator + Studio + Importer); skills `trinity-*` |
| **Who used it** | Operator + reviewers (names) |
| **Input** | Jira key(s), review run id, requirement summary |
| **Output** | # generated, # approved, # rejected, Xray keys |
| **Human review** | Who, Studio actions, material edits |
| **Accepted** | Count / list exported to Importer |
| **Rejected** | Count + top reasons from telemetry summary |
| **Impact** | Time vs manual; quality notes; Cursor cost if tracked |
| **Date / environment** | PROD Jira; project key; Xray folder |

**Acceptance rate:** `approved / (approved + rejected)` after review (exclude pending).

### Example — ONE-228469 (reference)

| Field | Value |
|-------|--------|
| **Use case** | AI-assisted manual TCs for custom fields; import to Xray |
| **Input** | ONE-228469 |
| **Output** | 5 tests → TC-6704 … TC-6708 |
| **Human review** | Validation fixes before import (`coverage_catalog_id`, Manual type, field mapping) |
| **Accepted** | 5/5 after plan corrections |
| **Rejected** | N/A (validation caught issues pre-review reject) |

---

## Slides (Google)

**Open:** build deck from this page + filled scorecard + screenshots.

Suggested flow: Problem → Pipeline (ARCHITECTURE diagram) → Control table (FAQ) → Metrics (summary JSON) → ONE-228469 evidence → Multi-project plan → Roadmap (Issues).

---

## Closure checklist (edit as you go)

| ID | Item | Owner | Status |
|----|------|-------|--------|
| M1 | Pilot 1 scorecard + telemetry export | | ☐ |
| M2 | Pilot 2 (different project or epic) | | ☐ |
| M3 | Slides presented to stakeholders | | ☐ |
| M4 | BigQuery ingest URL + first flush | | ☐ |
| M5 | Looker Studio report | | ☐ |
| M6 | Git tag `trinity-v$(cat Trinity/VERSION)` on `main` | | ☑ `trinity-v0.2.0` @ `2f19313` |

**Last updated:** 2026-10-13
