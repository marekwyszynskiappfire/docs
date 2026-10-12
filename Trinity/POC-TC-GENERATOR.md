# Trinity — POC test case generator (operator narrative)

English guide for the **Mateusz POC**: working generator, controls, evidence, and metrics. Deadlines in [Mateusz.MD](Mateusz.MD): solution **14/10**, documentation + scorecard + dashboards **16/10**.

| Topic | Document |
|-------|----------|
| Metrics & telemetry | [METRICS.md](METRICS.md) |
| One-pager evidence | [SCORECARD-TC-GENERATOR.md](SCORECARD-TC-GENERATOR.md) |
| Google Slides bullets | [POC-GOOGLE-SLIDES-BULLETS.md](POC-GOOGLE-SLIDES-BULLETS.md) |
| Day-to-day operations | [GUIDE.md](GUIDE.md) |
| Decisions (Importer, telemetry) | [ADR 0002](../docs/adr/0002-trinity-importer-telemetry-decisions.md) |

---

## 1. What “working solution” means

End-to-end path:

1. **Input** — Jira Epic/Story (Reviewer gather) or imported `review-payload.json`.
2. **Generate** — **trinity-creator** skill → `suite-payload.json` / batch JSON.
3. **Control** — Human triage in **Trinity Studio** (edit, approve, reject with reason).
4. **Export** — Studio **Export for Importer** → `importer-payload.json`.
5. **Persist to Xray** — **trinity-importer** on **Jira PROD** (dedicated test project, default **TC** unless overridden).

Demonstrated on production: ONE-228469 → TC-6704–6708 (see scorecard example).

---

## 2. How we control output (Mateusz §1)

| Control | Mechanism |
|---------|-----------|
| **Granularity** | Golden corpus v2 (TC manual style), Creator test-architect persona, coverage catalog; operators edit in Studio |
| **Quality** | Reviewer findings + questions; Studio human review; reject with **reason enum** ([METRICS.md](METRICS.md)) |
| **Repeatability** | JSON schemas (`TestCaseDraft`, review payload), versioned skills, golden sampling metadata on batches |
| **Maintainability** | Golden style rules; `automation_fit` / tiers; rejection reason `maintainability` tracked in metrics |
| **Team standards** | Golden filter-17844-bigpicture-manual; per-product mappings when project ≠ TC ([importer/config/mappings/README.md](importer/config/mappings/README.md)) |
| **Human intervention** | Reviewer Q&A; Studio approve/reject; Importer plan validation; production typed confirm (**planned**, ADR 0002) |

---

## 3. Architecture (one paragraph)

**Trinity** = Reviewer (requirements) + Creator (tests) + Importer (Xray) + **Studio** (SQLite hub). Agents run in Cursor with skills; Studio imports runs, records **metric_event** telemetry, and hands off Importer prompts. Optional BigQuery upload is best-effort ([METRICS.md](METRICS.md)).

---

## 4. Configuration and policy

- **Credentials:** `Trinity/studio/.env` — Jira + Xray (see [GUIDE.md §3](GUIDE.md#3-credentials-setup)).
- **Xray import:** **Production only** for create/update; sandbox for read/plan ([ADR 0002](../docs/adr/0002-trinity-importer-telemetry-decisions.md)).
- **Project / folder:** Mapping JSON default **TC**; override project key in Studio; folder path operator-defined (e.g. `/TC Importer/ONE-228469`).
- **Future:** `creator/config` defaults for project + folder template ([RQ-01](REVIEW-PRODUCT-AND-DOCS.md)).

---

## 5. Human review workflow

1. Import Creator batch → filter **Pending / edited**.
2. Edit cases that need fixes.
3. **Approve** or **Reject** (reject requires reason).
4. **Mark for Xray import** on approved rows.
5. **Export for Importer** → open Importer tab → plan → execute via agent/CLI.

Metrics update on each step; export JSON for scorecard: `GET /api/telemetry/export`.

---

## 6. Multi-project validation (Mateusz §5)

Run the same path on **2–3 requirement types** (e.g. TC story, another product key once mapping exists). Record per project:

- Mapping file used
- Project key override (if any)
- Acceptance rate and top rejection reasons from telemetry summary

Do not wait until POC end date to start the second project if mapping is ready.

---

## 7. Closing questions (Mateusz §5)

| Question | Where to answer |
|----------|-----------------|
| Does it work? | Scorecard + Xray keys + demo recording |
| Did people use it? | Scorecard **Who used it**; `operator_id` in telemetry |
| % accepted? | `/api/telemetry/summary` → `acceptance_rate` |
| Why rejected? | `rejection_reasons` in summary |
| Impact on time/quality/cost? | Scorecard **Impact** (qualitative until baseline study) |

---

## 8. Presentation (Google Slides)

Suggested deck outline (build after one filled scorecard):

1. Problem & use case  
2. Trinity pipeline diagram  
3. Control levers (§2 table)  
4. Live demo screenshots (Reviewer → Studio → Xray)  
5. Scorecard one-pager  
6. Metrics snapshot (summary JSON or charts after BQ)  
7. Multi-project plan  
8. Roadmap (ADR 0002 implementation items)  

---

## 9. Known limitations (honest POC)

- Studio **Execute** for Importer is prompt/CLI-led (not a single button).
- **IQ-02** typed `PRODUCTION` confirm is required in Studio Importer UI for production instance.
- **IQ-04** shared schema validation and **RQ-01** creator/config defaults are not implemented yet.
- Timing metrics and non-AI baseline are manual in scorecard.
- Looker Studio waits on BigQuery credentials.
