# Trinity POC — Google Slides speaker bullets (English)

Copy each block into a slide. Fill bracketed fields from your filled [SCORECARD-TC-GENERATOR.md](SCORECARD-TC-GENERATOR.md) and `GET /api/telemetry/export` when ready.

---

## Slide 1 — Title

- **Trinity:** AI-assisted test case generation with human control
- **POC:** Requirement → Review → Generate → Review in Studio → Xray (PROD)
- **[Date]** · **[Your name / team]**

---

## Slide 2 — Problem

- Manual test design from Jira requirements is slow and inconsistent at scale
- We need **useful** AI output, not demo-only generation
- Stakeholders need evidence: acceptance rate, rejection reasons, who reviewed, PROD traceability

---

## Slide 3 — Solution (one pipeline)

- **Reviewer** — structured requirements review (findings, questions, readiness)
- **Creator** — test cases aligned to golden style and coverage catalog
- **Studio** — human approve/reject with **rejection reasons**; local metrics
- **Importer** — validated handoff to **Xray on Jira PROD** (dedicated test project)

---

## Slide 4 — How we control quality (Mateusz §1)

- **Granularity:** Golden corpus v2 + test-architect persona + edit in Studio
- **Quality:** Reviewer gate + human review; reject with categorized reasons
- **Repeatability:** JSON schemas, versioned skills, golden sampling on batches
- **Standards:** TC manual golden; per-product mappings when project ≠ TC
- **Human role:** Approve/reject/export; Importer plan validation; PROD confirmation in UI

---

## Slide 5 — Architecture

- Cursor skills (agents) + **Trinity Studio** (SQLite hub on operator machine)
- Optional telemetry → BigQuery later (non-blocking; local export today)
- Policy: **Xray create/update on production only**; sandbox for read/plan

---

## Slide 6 — Scorecard snapshot

- **Use case:** [from scorecard]
- **Who used it:** [names] · **Input:** [Jira keys / epics]
- **Output:** [N generated] · [N approved] · [N rejected] · **Acceptance rate:** [%]
- **Xray keys:** [TC-xxxx, …] or folder path
- **Impact:** [time / quality / cost — your narrative]

---

## Slide 7 — Metrics (local → BigQuery)

- Studio records: imports, reviews, exports, importer plans, Xray persist events
- **Top rejection reasons:** [from `/api/telemetry/summary`]
- Next: BigQuery ingest + Looker Studio when credentials are ready
- Export evidence: `curl …/api/telemetry/export`

---

## Slide 8 — Multi-project validation (plan)

- Pilot 1: **[e.g. TC / ONE-xxxxx]** — done / in progress
- Pilot 2–3: **[project keys]** — mapping + acceptance comparison
- Config differences documented in mappings README + creator config (planned)

---

## Slide 9 — Limitations (honest)

- Looker/BigQuery dashboards: planned; local `/api/telemetry/export` today
- Timing vs manual baseline: qualitative in scorecard until measured
- Post-POC: hard redaction block, duplicate-key block on execute, automation_fit → Xray field

---

## Slide 10 — Recommendation & next steps

- **Recommendation:** [Scale / pilot widen / pause — your call]
- Done: PROD guard ✓ · Xray key persist ✓ · Studio execute ✓ · local metrics ✓
- Next: BigQuery/Looker ([GITHUB-BACKLOG.md](GITHUB-BACKLOG.md)) · pilot 2 scorecard · post-POC safety issues
- **Ask:** [budget, license, headcount — if needed]
