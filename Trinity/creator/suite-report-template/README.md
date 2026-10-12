# Creator test suite report (Profile B)

Portable interactive suite catalog for Trinity Creator batches.

## Open

1. Unzip the folder (or use from `Trinity/studio/data/exports/creator/{run_id}/suite-report/`).
2. Open **`index.html`** in a browser.

## Regenerate

From a TestCaseDraft batch JSON:

```bash
python3 Trinity/creator/scripts/build_suite_report.py \
  --batch Trinity/creator/samples/demo-story.suite.json \
  --out Trinity/creator/runs/demo-story/suite-report
```

From Studio (after importing a Creator run):

```bash
# POST /api/creator-runs/{run_id}/export-suite-report
```

Guidelines: [`../../shared/html-report-guidelines.md`](../../shared/html-report-guidelines.md).
