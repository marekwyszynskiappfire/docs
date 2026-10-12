# Reviewer runs (local only)

Portfolio and epic review outputs are **not committed** (real Jira keys and planning content).

After a Reviewer scan, artifacts live here:

`Trinity/reviewer/runs/{portfolio_run_id}/{EPIC_KEY}/review-payload.json`

Import into Studio:

```bash
./Trinity/studio/scripts/import-run.sh Trinity/reviewer/runs/<your-run-folder>
```

To prune old portfolio folders and pytest noise from Studio SQLite:

```bash
./Trinity/studio/scripts/cleanup-local-runs.sh          # dry-run
./Trinity/studio/scripts/cleanup-local-runs.sh --apply
```

Edit `KEEP_REVIEWER` in that script if you need to retain additional folders.

To validate the renderer without a live run:

```bash
python3 Trinity/reviewer/scripts/render_report.py Trinity/reviewer/samples/demo-epic.payload.json --strict
```
