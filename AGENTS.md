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

**Trinity** (Reviewer, Creator, Importer, Studio) **canonical repo:** [`appfire-team/qa-coe/Trinity`](https://github.com/appfire-team/qa-coe/tree/main/Trinity). A legacy copy remains under [`Trinity/`](Trinity/README.md) in this docs repo for Confluence sync until removed.

HTML reports must follow [`Trinity/shared/html-report-guidelines.md`](Trinity/shared/html-report-guidelines.md) (Profile A/B) — same path in qa-coe.

### Trinity Creator (test suites)

After **trinity-creator**, point the operator at `Trinity/creator/artifacts/{portfolio_or_run_id}/` and **one `suite-payload.json` import per epic** in Studio — see [`Trinity/creator/artifacts/README.md`](Trinity/creator/artifacts/README.md).

### BP QA–Development cooperation

When documenting BP QA–Development cooperation, follow [`BP QA/SKILL.md`](BP%20QA/SKILL.md). This workstream starts fresh: do not inherit the retired BP QA Ways of Working agreements. Treat only explicitly confirmed decisions as agreed and keep unresolved matters visible.

### Release Process

When documenting the BigPicture release process, follow [`Release Process/SKILL.md`](Release%20Process/SKILL.md). Keep process in `process.md` and how-tos in Cloud/DC technical files. The PPM Release Checklist is a technical source, not current ownership. Do not publish Confluence until the markdown is reviewed.

### Release stats canvas

When the user asks for release statistics, a train section (e.g. 8.77), or `/release-stats`, follow [`.cursor/skills/release-stats/SKILL.md`](.cursor/skills/release-stats/SKILL.md): interactive run config; create or enrich `Release Process/stats/data/{version}.json` (full pipeline — comparison table, Xray, bugs, production date, customer-reported, optional known issues, **failed test links**); then `render_canvas.py`.

### Trinity pilot scorecard (Google Sheet)

When the user pastes the scorecard prompt, RUN DATA, or asks to update the **Usage Scorecard** / pilot spreadsheet after a Trinity run, follow [`.cursor/skills/trinity-scorecard/SKILL.md`](.cursor/skills/trinity-scorecard/SKILL.md). Default workflow: **Cursor + Google Drive** using [`Trinity/pilot-scorecard-cursor-prompt.md`](Trinity/pilot-scorecard-cursor-prompt.md) — not Studio Sheets API unless explicitly requested.

### Trinity Studio (edit + analytics)

Human edits and pipeline stats live in [`Trinity/studio/`](Trinity/studio/README.md). Import Reviewer run folders after Agent gather; export approved `review-payload.json` for Creator.

### Monorepo cleanup (outside Trinity only)

**Do not modify `Trinity/` for repository hygiene** (removing legacy folders, deduping docs elsewhere, root `.gitignore`, etc.). Trinity is the shipped product tree — changes there are releases, features, and operator docs, not monorepo cleanup.

Cleanup targets: legacy root skill stubs (`The Reviewer/`, `The Creator/`, `TestCaseCreator/`, `Creator/`), retired `QA_TRANSPARENCY/` and `QA Work Tracking/`, and other non-Trinity paths that belong in local-only **`archive/`** (gitignored). Update root [`README.md`](README.md) and [`.gitignore`](.gitignore) as needed; leave `Trinity/` to its own maintainers.
