# Creator artifacts (local runs)

Gitignored output from **trinity-creator** agent runs. Studio imports **one `suite-payload.json` at a time** — there is no combined portfolio batch.

## Folder layout

```
Trinity/creator/artifacts/
  {portfolio_or_run_id}/          # e.g. q4-backlog, ONE-377773, 2026-10-14-my-epic
    {EPIC_KEY}/                   # one subfolder per Epic (CR-EPIC-01)
      suite-payload.json          # ← Studio **Creator → Import batch** (this file)
      suite-report.md
      suite-report/index.html     # Profile B HTML
      golden-sampling.json        # optional audit trail
    index.json                    # optional catalog (multi-epic only; not importable)
```

**Single-epic run:** `artifacts/{EPIC_KEY}/suite-payload.json` (no nested key folder) is also valid when `run_id` equals the epic key.

## Operator workflow (multi-epic)

After Creator finishes a portfolio program (e.g. Reviewer run `q4-backlog`):

1. Open **`Trinity/creator/artifacts/{portfolio_id}/`** — every epic is **`{EPIC_KEY}/suite-payload.json`**.
2. In Studio → **Creator** → **Import batch**, import **each** `suite-payload.json` **separately** (one Creator run in SQLite per file).
3. Triage tests on each Creator run (approve / reject / mark for Xray).
4. Skip or defer epics marked **`not_fit`** in Reviewer (payload may have 0 tests).

There is **no** merged `suite-payload.json` for the whole portfolio unless you build one yourself (not supported by default Studio import).

## Examples

| Program | Artifacts root |
|---------|----------------|
| Q4 backlog (30 epics) | `Trinity/creator/artifacts/q4-backlog/` |
| Demo | `Trinity/creator/samples/demo-story.suite.json` (committed, not under `artifacts/`) |

See program-specific notes under `artifacts/{portfolio_id}/README.md` when present.
