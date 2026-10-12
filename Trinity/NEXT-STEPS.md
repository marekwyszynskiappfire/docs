# Trinity — post-P2 next steps

P2 implementation backlog (IQ-10–IQ-15) is **closed** as of 2026-10-12. Use this page to sequence pilot sign-off and wider rollout.

## 1. Stress-test (grill)

Grill **closed** (Rounds 1–6) — [`GRILL-SESSION-2026-10-12.md`](GRILL-SESSION-2026-10-12.md). **Pilot focus only:** fill scorecard, Slides, one documented prod run. No new product work unless a **production bug** or explicit EM exception.

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
| Engineering FAQ | [`FAQ.md`](FAQ.md) |
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

## 4. Pilot sign-off (human-owned)

| Artifact | Owner |
|----------|--------|
| [`SCORECARD-TC-GENERATOR.md`](SCORECARD-TC-GENERATOR.md) | QA lead |
| [`POC-GOOGLE-SLIDES-BULLETS.md`](POC-GOOGLE-SLIDES-BULLETS.md) | Presenter |
| Telemetry evidence | [`METRICS.md`](METRICS.md) export after real runs |

Checklist: [FAQ.md — Sign-off questions](FAQ.md#sign-off-questions-evidence-not-slides-alone).

## 5. Backlog (GitHub)

Track post-release work in **[GITHUB-BACKLOG.md](GITHUB-BACKLOG.md)** — create issues with `./Trinity/scripts/create_github_backlog.sh --create`.

Grill R1–R3 closed in repo; product Q&A lives in **[FAQ.md](FAQ.md)** and **[POC-TC-GENERATOR.md](POC-TC-GENERATOR.md)**.

---

Questions: [`REVIEW-PRODUCT-AND-DOCS.md`](REVIEW-PRODUCT-AND-DOCS.md) §9 · Decisions: [`docs/adr/0002-trinity-importer-telemetry-decisions.md`](../docs/adr/0002-trinity-importer-telemetry-decisions.md)
