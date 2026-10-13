# Pilot runs (Trinity Creator)

Committed run folders (optional) hold **redacted** fixtures for regression: `suite-payload.json`, **`suite-report/`** (Profile B), and notes — not full tenant data.

Regenerate demo report:

```bash
python3 Trinity/creator/scripts/build_suite_report.py \
  --batch Trinity/creator/samples/demo-story.suite.json \
  --out Trinity/creator/runs/demo-story/suite-report
```

**Policy (match Reviewer practice):**

- Prefer demo keys (`DEMO-*`) in `samples/` for renderer CI.
- Real Jira keys may appear in local `artifacts/` only until redacted copies are promoted here.
- Each pilot: add a row in [`SCORECARD.md`](../SCORECARD.md) **Pilot log** (and optional committed run folder here).
