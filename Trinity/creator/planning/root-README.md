# The Creator

Product-agnostic test suite generation, interactive triage reports, and **explicit opt-in** Xray submission (after human approval in the report).

**Status:** Under construction. Skill bodies and schemas are built in [`The Creator/Output/Creator/`](../The%20Creator/Output/Creator/) and promoted here at cutover (decision **CR0**).

**Planning hub:** [`The Creator/`](../The%20Creator/) (`ACTION-PLAN.md`, `INPUT-REVIEW.md`, `Input/`)  
**Decision memory:** [`The Reviewer/DECISIONS.md`](../The%20Reviewer/DECISIONS.md) (shared with The Reviewer)  
**Upstream gate:** [`The Reviewer/`](../The%20Reviewer/)

## HTML reports

All Creator HTML deliverables must follow [`../shared/html-report-guidelines.md`](../shared/html-report-guidelines.md):

- **Test suite catalog** — Profile A (single self-contained `test-suite-report.html`; see test-case-creation skill §9b).
- **Execution / triage / analytics tables** — Profile B: portable `report/` folder (`index.html`, `assets/`, `data/report-data.js`), combinable AND filters, dynamic facet counts.

**Reference implementation:** [`runs/TC-6504/report/`](runs/TC-6504/report/).

Install from this folder once `SKILL.md` exists (same pattern as The Reviewer).
