# Trinity — operator validation (sign-off)

**Wiki:** [Operator onboarding](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3755311111/Trinity+Operator+onboarding) · **Prerequisite:** all gates in [OPERATOR-ONBOARDING.md](OPERATOR-ONBOARDING.md).

QA lead (P2) records that an operator completed the path **without live coaching**. Persona definition: [operator-first-time.md](personas/operator-first-time.md). Latest doc review: [NEWBIE-PERSONA-REVIEW.md](NEWBIE-PERSONA-REVIEW.md). **Session script:** [UAT-SESSION.md](UAT-SESSION.md). **File friction:** [GitHub issue template](../.github/ISSUE_TEMPLATE/trinity-pilot-feedback.yml) (label `trinity-support`).

| Field | Value |
|-------|--------|
| Operator name | |
| Date | |
| Machine OS | |
| Trinity version | `cat Trinity/VERSION` |
| Profile | Sandbox / Production |
| Epic used (real path) | |

---

## Part A — Setup (~45 min)

| # | Step | Pass | Notes |
|---|------|------|-------|
| A1 | Clone repo; open root in Cursor | ☐ | |
| A2 | `./Trinity/scripts/install-trinity-skills.sh` | ☐ | |
| A3 | MCP per [CURSOR-MCP-SETUP.md](CURSOR-MCP-SETUP.md) | ☐ | Site URL(s): |
| A4 | `./Trinity/scripts/pilot-preflight.sh` all PASS | ☐ | |
| A5 | Studio `.env` for chosen Jira site | ☐ | |

---

## Part B — Demo (~15 min)

| # | Step | Pass | Notes |
|---|------|------|-------|
| B1 | `seed-demo.sh`; **Open workspace** on DEMO-4500 | ☐ | Verdict and Next step visible |
| B2 | Understand readiness labels | ☐ | |
| B3 | Top bar is Workspace, Personas, Statistics. Creator and Importer are under More | ☐ | |
| B4 | Personas list shows the heading in the file; the filename stays above the editor | ☐ | |

---

## Part C — Live Epic (~45 min)

| # | Step | Pass | Notes |
|---|------|------|-------|
| C1 | Prompt 1; `review-payload.json` | ☐ | Portfolio: |
| C2 | Workspace URL opened; verdict matches the report | ☐ | |
| C3 | Approve the review on the workspace | ☐ | |
| C4 | Copy Creator prompt; suite appears on the workspace | ☐ | |
| C5 | Approve tests and mark Send to Xray | ☐ | |
| C6 | Plan Xray import preview OK | ☐ | |
| C7 | Sandbox write, or dry-run per policy. Write stays one Epic | ☐ | Test keys: |

---

## Part D — Knowledge check

| # | Topic | Pass |
|---|--------|------|
| 1 | Ready vs reservations vs not ready ([METRICS.md](METRICS.md)) | ☐ |
| 2 | Where three prompts are copied ([PROMPTS-AND-INPUTS.md](PROMPTS-AND-INPUTS.md)) | ☐ |
| 3 | Project key vs mapping ([GUIDE.md](GUIDE.md) / [FAQ](FAQ.md)) | ☐ |
| 4 | Dual vs single MCP ([CURSOR-MCP-SETUP.md](CURSOR-MCP-SETUP.md)) | ☐ |

---

## Sign-off

| Role | Name | Date |
|------|------|------|
| Operator | | |
| QA lead (P2) | | |

**Result:** ☐ Solo sandbox · ☐ Production Epics · ☐ Remediation
