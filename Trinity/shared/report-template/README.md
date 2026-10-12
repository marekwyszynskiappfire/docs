# Report template (Profile B)

Copy this layout for new **interactive facet** reports. Do not copy TC-6504 data.

**Canonical examples:**

- Creator **test suite** — [`creator/suite-report-template/`](../creator/suite-report-template/) + [`creator/runs/demo-story/suite-report/`](../creator/runs/demo-story/suite-report/)
- Creator **bug/triage** — [`Creator/runs/TC-6504/report/`](../../Creator/runs/TC-6504/report/)

**Rules:** [`../html-report-guidelines.md`](../html-report-guidelines.md)

When starting a new report:

1. Duplicate the **structure** of `TC-6504/report/` (not the bug-specific filters).
2. Implement facet predicates and columns in `assets/app.js`.
3. Add a run-level build script that writes `data/report-data.js` only.
4. Add `report/README.md` for share instructions.
