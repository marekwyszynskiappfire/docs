# Trinity — Overview & architecture

<!-- Confluence title: Trinity — Overview & architecture -->
<!-- Labels: trinity, qa, external-safe -->

**Last reviewed:** 2026-10-13

## What Trinity is

Trinity is an **AI-assisted QA pipeline** for Jira-backed products:

1. **Reviewer** (Cursor) — requirement quality, questions, findings, portfolio HTML.
2. **Trinity Studio** (local web app) — human triage, approvals, metrics, handoffs.
3. **Creator** (Cursor) — E2E test-case drafts from approved reviews.
4. **Importer** (Studio + Cursor) — approved tests into **Xray** with dry-run planning.

Studio does **not** replace Cursor for gather/generation in v1; it is the **control plane** for operators.

## Architecture diagram

Attach from the repository:

`Trinity/confluence/assets/trinity-operator-pipeline.svg`

## Components

| Component | Location in repo | Operator interface |
|-----------|------------------|-------------------|
| Reviewer skill | `Trinity/reviewer/` | Cursor chat |
| Creator skill | `Trinity/creator/` | Cursor chat |
| Importer skill | `Trinity/importer/` | Studio + Cursor |
| Studio API + UI | `Trinity/studio/` | Browser :5173 |
| Personas | `Trinity/personas/` | Studio → Personas |
| Run configs | `Trinity/reviewer/config/runs/` | Studio → Reviewer configs |

## Data flow (one epic)

1. Reviewer writes `review-payload.json` under `reviewer/runs/<run>/<EPIC-KEY>/`.
2. Studio imports run → SQLite revisions + `studio_qa` overlay.
3. Operator approves → export under `studio/data/exports/`.
4. Creator writes `suite-payload.json` → Studio test rows.
5. Importer creates Xray tests → keys persisted in Studio.

Contracts: `Trinity/CONTRACTS.md` (in git).

## Who should read which child page

| Role | Pages |
|------|--------|
| New operator | 02 → 03 → (04 if using live Jira) |
| QA lead | All; focus 05–08 |
| PM / BA | 01, 05 (readiness & questions only) |
| Platform admin | 02, 04 |

## Linear setup in git

Single checklist: `Trinity/OPERATOR-SETUP.md`.
