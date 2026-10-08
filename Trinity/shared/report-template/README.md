# Report template (Profile B)

Copy this layout for new **interactive facet** reports. Do not copy TC-6504 data.

**Canonical example:** [`Creator/runs/TC-6504/report/`](../Creator/runs/TC-6504/report/) (`index.html`, `assets/`, `data/report-data.js`, `build_bug_report.py` in parent run folder).

**Rules:** [`../html-report-guidelines.md`](../html-report-guidelines.md)

When starting a new report:

1. Duplicate the **structure** of `TC-6504/report/` (not the bug-specific filters).
2. Implement facet predicates and columns in `assets/app.js`.
3. Add a run-level build script that writes `data/report-data.js` only.
4. Add `report/README.md` for share instructions.
