# Trinity — post-P2 next steps

P2 implementation backlog (IQ-10–IQ-15) is **closed** as of 2026-10-12. Use this page to sequence what comes before Mateusz POC sign-off and wider rollout.

## 1. Stress-test (grill)

Run a structured **review / grill** of product decisions and code — not another feature wave.

| Track | Scope | Suggested output |
|-------|--------|------------------|
| **Product** | [`REVIEW-PRODUCT-AND-DOCS.md`](REVIEW-PRODUCT-AND-DOCS.md) §2 P1–P10, open RQ/CQ/TQ rows | Decision log or ADR updates |
| **Security** | Production execute, env split, redaction (IQ-17), PII in steps | Checklist sign-off |
| **Code** | Studio server, `shared/validate_for_xray.py`, Importer scripts | Bugbot / manual PR review |
| **E2E** | ONE-228469-class path on staging or prod with creds | Updated [`SCORECARD-TC-GENERATOR.md`](SCORECARD-TC-GENERATOR.md) |

Use Cursor **Grill** skill or a live session with QA lead + EM. Capture outcomes in GitHub Issues on `marekwyszynskiappfire/docs`.

## 2. Documentation cleanup

| Task | Status |
|------|--------|
| Central operator path | [`GUIDE.md`](GUIDE.md) + [`MANUAL.md`](MANUAL.md) §11 |
| Stale REVIEW §8 cross-cutting table | Refresh after each wave |
| Partial doc rows (TESTING, PIPELINE, PREFLIGHT, importer SKILL) | Align with GUIDE §6 project selector |
| Optional screenshot in GUIDE | Still open |
| [`parity-matrix.md`](parity-matrix.md) | Studio vs Reviewer HTML gaps |

Avoid duplicating the same Importer steps in five files — **link to GUIDE §6** from shorter docs.

## 3. Studio UI (pizzazz)

First pass (2026-10-12): pipeline strip, branded header, stat card accents, nav pills.

Still optional:

- Empty-state illustrations and onboarding callouts on Dashboard
- Importer project selector visual hierarchy (risk tier badge)
- Run page: hollow-epic / gate_status chips (R3)
- Light motion (respect `prefers-reduced-motion`)

## 4. Mateusz POC closure (human-owned)

| Artifact | Owner |
|----------|--------|
| [`SCORECARD-TC-GENERATOR.md`](SCORECARD-TC-GENERATOR.md) | QA lead |
| [`POC-GOOGLE-SLIDES-BULLETS.md`](POC-GOOGLE-SLIDES-BULLETS.md) | Presenter |
| Telemetry evidence | [`METRICS.md`](METRICS.md) export after real runs |

## 5. Backlog not in P2 (pick after grill)

- **PQ-01** — Portfolio readiness rollup on Dashboard  
- **PQ-03** — `test_data_isolation` in creator config (T-G6)  
- **RQ-02** — `environment` / `tenant` on Reviewer export  
- **CQ-02** — Canonical `coverage_catalog_id` vs `linked_ac_ids` in schema  
- **TQ-02 / TQ-03** — Automation field mapping + backlog export  
- **BigQuery** telemetry when credentials exist  

---

Questions: [`REVIEW-PRODUCT-AND-DOCS.md`](REVIEW-PRODUCT-AND-DOCS.md) §9 · Decisions: [`docs/adr/0002-trinity-importer-telemetry-decisions.md`](../docs/adr/0002-trinity-importer-telemetry-decisions.md)
