# Trinity — operator validation (sign-off)

**Wiki:** [Operator onboarding](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3755311111/Trinity+Operator+onboarding) · **Prerequisite:** all gates in [OPERATOR-ONBOARDING.md](OPERATOR-ONBOARDING.md).

QA lead (P2) records that an operator completed the path **without live coaching**.

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
| B1 | `seed-demo.sh`; DEMO-4500 on Dashboard | ☐ | |
| B2 | Understand readiness labels | ☐ | |
| B3 | Import demo suite in Creator | ☐ | |
| B4 | Importer preview | ☐ | |

---

## Part C — Live Epic (~45 min)

| # | Step | Pass | Notes |
|---|------|------|-------|
| C1 | Prompt 1; `review-payload.json` | ☐ | Portfolio: |
| C2 | Import run; correct readiness | ☐ | |
| C3 | Triage + approve | ☐ | |
| C4 | Prompt 2; Creator batch | ☐ | |
| C5 | Export for Importer | ☐ | |
| C6 | Importer preview OK | ☐ | |
| C7 | Sandbox execute (or policy dry-run) | ☐ | Test keys: |

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
