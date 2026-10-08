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
