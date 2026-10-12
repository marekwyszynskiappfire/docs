# Grill session — Trinity POC (2026-10-12)

**Purpose:** Stress-test solution + code before pilot sign-off. **Tests:** 25 pytest pass. **Live Studio:** restart required if `/api/health` `features` lacks `importer_execute`, `creator_coverage`, `creator_suite_report`.

---

## Agent findings (facts, not decisions)

### Architecture — holds up

- Clear pipeline: Reviewer payload → Studio → Creator batch → Importer handoff → Xray.
- ADR 0002 matches implemented behaviour (IQ-01–02, 08, 16–17, RQ-01, telemetry local-first).
- Shared `validate_for_xray.py` is the right choke point; export preflight + plan validation align.

### Risks / gaps (grill these)

| # | Area | Finding | Severity |
|---|------|---------|----------|
| G1 | **Ops** | Stale Studio process serves old API (`features` only `importer_plan`) | Medium — operator confusion |
| G2 | **Security (P9)** | Redaction is **warn-only** (IQ-17); execute can still push emails/URLs to Xray | Medium — policy call |
| G3 | **Gate (P8)** | Reviewer gate is **soft ack** (IQ-16); release manager cannot rely on hard block | Low if POC accepts |
| G4 | **Execute** | No idempotency — re-run Execute may duplicate tests in Xray | High for production habit |
| G5 | **Sandbox** | IQ-03 prod-only policy; sandbox Xray 403 documented | Low for pilot if prod path proven |
| G6 | **Reviewer ↔ Studio** | `parity-matrix.md` — child inventory, classifications, portfolio link gaps in Studio | Medium for P2 leads |
| G7 | **Schema** | `coverage_catalog_id` vs `linked_ac_ids` dual field (CQ-02 open) | Low — enrich masks it |
| G8 | **Code hygiene** | `importer_plan.py` imports `validate_test` twice (same implementation) | Low — cleanup |
| G9 | **Docs** | ADR 0002 consequences still say “P2 remain backlog” | Trivial — update |
| G10 | **REVIEW §2** | P1/P2 rows predate IQ-11/13 (suite Profile B, coverage UI) | Trivial — refresh scores |

### What is **not** broken for POC

- E2E path ONE-228469 → TC keys (historical).
- Production confirm + project.id resolution + persist keys + Studio Execute.
- Personas P1–P10 doc path; GUIDE/MANUAL Importer chapters.

---

## Round 1 — decisions

Captured via interactive form (not a static question dump). See session transcript / agent memory: grill must stay interactive.

---

❓ **Q1 — Pilot “done” definition**

Is POC-complete **only** scorecard + Slides filled with **one** documented prod (or staging) run — without BigQuery, without sandbox Xray, without hard redaction block?

➡️ **Yes** — treat BQ/sandbox/hard-redaction as post-POC; scorecard cites local `metric_event` + ADR 0002.

---

❓ **Q2 — Redaction at execute (PQ-05 vs IQ-17)**

Keep **warn** on export/plan, or **block** `execute_ready` when preflight finds emails/sensitive URLs?

➡️ **Warn for POC**; add **block** in first post-POC hardening sprint (document in ADR addendum).

---

❓ **Q3 — Reviewer gate (PQ-04 vs IQ-16)**

Keep **soft** gate (ack + re-preview), or **hard** block Importer export/execute when readiness ≠ green?

➡️ **Keep soft** — matches ADR; hard block only for `gate_status: BLOCKED` + CRITICAL if you add that later.

---

❓ **Q4 — Re-execute / idempotency (G4)**

For v1 operators, is manual discipline (“check Xray first”) enough, or must Studio refuse Execute when `xray_test_key` already set?

➡️ **POC:** warn in plan when row has `xray_test_key`; **post-POC:** skip or block duplicates.

---

❓ **Q5 — Next engineering slice (after you answer Q1–Q4)**

Pick **one** for the next ~half day: **(A)** UI round 2 (Importer risk badge, run gate chips), **(B)** doc cleanup only, **(C)** PQ-01 dashboard rollup, **(D)** commit + PR without more code.

➡️ **(D) then (A)** — commit P2 wave, then UI polish; defer PQ-01 until after pilot readout.

---

## Locked decisions (2026-10-12, interactive form)

| # | Decision |
|---|----------|
| Q1 | Pilot done = **scorecard + Slides + one documented run** (no BQ/sandbox/hard-redact required for initial release) |
| Q2 | **Warn** on redaction for POC; hard block post-POC |
| Q3 | **Soft** Reviewer gate (IQ-16 / ADR) |
| Q4 | **Warn** in plan when `xray_test_key` exists; block/skip post-POC → `importer_idempotency.py` |
| Q5 | **Commit → UI round 2 → doc cleanup** |

## Round 2 — locked (2026-10-12, interactive form)

| # | Decision | Implementation |
|---|----------|----------------|
| PQ-01 | **Full** portfolio rollup on Dashboard before POC | `GET /api/portfolio-rollup` + PortfolioRollupPanel |
| RQ-02 | **Child inventory** table first | `GET /api/runs/{id}/child-inventory` + RunPage details |
| PQ-03 | **SKILL + optional JSON**, warn if missing | `policy.test_data_isolation`; warn on Send to Creator |

**Still open:** CQ-01, TQ-02, other RQ-02 gaps (classifications banner, open HTML).

## Round 3 — locked (2026-10-12, interactive form)

| # | Decision | Implementation |
|---|----------|----------------|
| CQ-01 | Coerce at import; **show in Importer plan** | `test_type_coercion` + `xray_test_type` per test |
| TQ-02 | **Document** POC: Manual only in TC; analytics for `automation_fit` | `importer/reference.md`, REVIEW §6 |
| RQ-02 | **Classifications banner** on unit review | `ClassificationsBanner` on `UnitReviewPage` |

**Still open:** hard schema lock on `test_type` (optional post-pilot).  

## Round 4 — locked (2026-10-12, interactive form)

| # | Decision | Follow-up |
|---|----------|-----------|
| Q1 | **Scorecard + Slides** sufficient for pilot; Cursor cost = optional telemetry | [`CURSOR-COST.md`](CURSOR-COST.md) |
| Q2 | **PQ-03** keep warn-only on `test_data_isolation` through pilot | Post-POC enforce in config/Studio |
| Q3 | **CQ-02** `coverage_catalog_id` canonical when present; `linked_ac_ids` legacy | Document in Creator schema/reference |
| Q4 | **Parity:** open local `review-report.html` before pilot | `GET /api/units/{id}/review-report.html` + Run page links |
| Q5 | **RQ-02** optional `environment` / `tenant` in review-payload; no Importer gate | Metadata only until 2nd pilot |
| Q6 | **TQ-03** defer automation backlog export | Telemetry + `automation_fit` columns |

## Round 5 — locked (2026-10-12, interactive form)

| # | Decision | Implementation |
|---|----------|----------------|
| Q1 | **PQ-06** Dashboard panel for failed/unavailable `context_loaded` | `GET /api/context-loaded-alerts` + Dashboard panel |
| Q2 | **QA readiness checklist** in Studio | **Deferred** — use Profile A HTML link (R4) |
| Q3 | Run-level **child status-mix banner** | `run_status_mix` on child-inventory API + Run page |
| Q4 | **CQ-02** doc-only | `creator/reference.md` § Coverage linkage |
| Q5 | Implement R5 only, then **freeze** product code for pilot | This commit wave |
| Q6 | Align **GITHUB-BACKLOG.md** with grill deferrals | Checklist, TQ-03, hardening rows |

## Round 6 — locked (2026-10-12, interactive form) — **session closed**

| # | Decision | Implementation |
|---|----------|----------------|
| Q1 | Refresh **ADR 0002** consequences (G9) | Full grill + cursor + parity links |
| Q2 | **Close grill** — pilot artifacts only until bug | This section; NEXT-STEPS updated |
| Q3 | **`cursor_usage` in telemetry export** | `cursor_usage_export_bundle` in `/api/telemetry/export` |
| Q4 | Scorecard **Cursor cost (USD)** optional row | SCORECARD-TC-GENERATOR.md |
| Q5 | Hygiene only — no new product features | R6 commit |

**Post-pilot (backlog, not grill):** QA checklist in Studio; `coverage_catalog_id` schema warn; hard redaction/idempotency; BQ ingest.

---

## After shared understanding

1. Update ADR 0002 + REVIEW §2 scores from your answers. **Done** — P2 commit `dc5b7ec`, doc pass `parity-matrix` + REVIEW §2.  
2. Log GitHub Issues for G4, G6, and any **block** you chose on Q2/Q3.  
3. Proceed: doc cleanup → UI round 2 → `commit`.
