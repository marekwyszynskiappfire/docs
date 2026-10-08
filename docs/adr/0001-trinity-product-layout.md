# ADR 0001: Trinity product layout in monorepo

## Status

Accepted (2026-10-08)

## Context

Reviewer, Creator, Importer, and Studio were scattered at the repo root (`The Reviewer/`, `qa-studio/`, etc.), which made internal sharing and onboarding unclear.

## Decision

- **Trinity** is the product name for the full solution.
- All runnable skill roots and **Trinity Studio** live under **`Trinity/`** in this monorepo.
- Legacy top-level paths keep stub READMEs pointing to `Trinity/`.
- Operator documentation is centralized under `Trinity/` (README, PREFLIGHT, MANUAL, PIPELINE).

## Consequences

- Import paths and Studio API resolution use repo-root-relative paths such as `Trinity/reviewer/runs/...`.
- `shared/html-report-guidelines.md` moves to `Trinity/shared/`.
- Phase 1+ will sanitize committed runs and dedupe old docs.
