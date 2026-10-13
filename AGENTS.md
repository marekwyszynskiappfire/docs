# Agent instructions (DOCS)

Personal and team documentation repository (QA process, releases, AI-in-QA initiative, 1:1 templates). Not an application codebase.

## Agent skills

### Issue tracker

Work is tracked in **GitHub Issues** on `marekwyszynskiappfire/docs` via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Domain docs

**Single-context** layout: root `CONTEXT.md` (when present) and `docs/adr/`. See `docs/agents/domain.md`.

### Shareable HTML reports

**Trinity** (Reviewer, Creator, Importer, Studio) lives under [`Trinity/`](Trinity/README.md). HTML reports must follow [`Trinity/shared/html-report-guidelines.md`](Trinity/shared/html-report-guidelines.md) (Profile A/B).

### Trinity Studio (edit + analytics)

Human edits and pipeline stats live in [`Trinity/studio/`](Trinity/studio/README.md). Import Reviewer run folders after Agent gather; export approved `review-payload.json` for Creator.

### Monorepo cleanup (outside Trinity only)

**Do not modify `Trinity/` for repository hygiene** (removing legacy folders, deduping docs elsewhere, root `.gitignore`, etc.). Trinity is the shipped product tree — changes there are releases, features, and operator docs, not monorepo cleanup.

Cleanup targets: legacy root skill stubs (`The Reviewer/`, `The Creator/`, `TestCaseCreator/`, `Creator/`), retired `QA_TRANSPARENCY/` and `QA Work Tracking/`, duplicate initiative copies under `AI in QA/` when instructed, and other non-Trinity paths. Update root [`README.md`](README.md) and [`.gitignore`](.gitignore) as needed; leave `Trinity/` to its own maintainers.
