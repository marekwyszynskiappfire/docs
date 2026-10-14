# Agent instructions (DOCS)

Repository for **Trinity** and **Cursor/agent/GitHub** documentation (`docs/agents`, `docs/adr`). Not an application codebase.

## Agent skills

### Issue tracker

Work is tracked in **GitHub Issues** on `marekwyszynskiappfire/docs` via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Domain docs

**Single-context** layout: root `CONTEXT.md` (when present) and `docs/adr/`. See `docs/agents/domain.md`.

### Trinity Reviewer (requirement review)

When the user asks for a **review** of Jira epics/requirements, run **`trinity-reviewer`** with full MCP gather per [`Trinity/reviewer/SKILL.md`](Trinity/reviewer/SKILL.md). Do **not** use `portfolio_testing_sweep.py` unless they explicitly want a REST-only quick sweep. See [`.cursor/rules/trinity-reviewer-mandatory.mdc`](.cursor/rules/trinity-reviewer-mandatory.mdc).

### Shareable HTML reports

**Trinity** (Reviewer, Creator, Importer, Studio) lives under [`Trinity/`](Trinity/README.md). HTML reports must follow [`Trinity/shared/html-report-guidelines.md`](Trinity/shared/html-report-guidelines.md) (Profile A/B).

### Trinity Creator (test suites)

After **trinity-creator**, point the operator at `Trinity/creator/artifacts/{portfolio_or_run_id}/` and **one `suite-payload.json` import per epic** in Studio — see [`Trinity/creator/artifacts/README.md`](Trinity/creator/artifacts/README.md).

### Trinity Studio (edit + analytics)

Human edits and pipeline stats live in [`Trinity/studio/`](Trinity/studio/README.md). Import Reviewer run folders after Agent gather; export approved `review-payload.json` for Creator.

### Monorepo cleanup (outside Trinity only)

**Do not modify `Trinity/` for repository hygiene** (removing legacy folders, deduping docs elsewhere, root `.gitignore`, etc.). Trinity is the shipped product tree — changes there are releases, features, and operator docs, not monorepo cleanup.

Cleanup targets: legacy root skill stubs (`The Reviewer/`, `The Creator/`, `TestCaseCreator/`, `Creator/`), retired `QA_TRANSPARENCY/` and `QA Work Tracking/`, and other non-Trinity paths that belong in local-only **`archive/`** (gitignored). Update root [`README.md`](README.md) and [`.gitignore`](.gitignore) as needed; leave `Trinity/` to its own maintainers.
