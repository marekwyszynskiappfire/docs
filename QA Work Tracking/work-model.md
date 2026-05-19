# QA work model — Metric, team, and project

From [improving_visibility_of_qa_work_in_jellyfish.md](../../../QA_TRANSPARENCY/improving_visibility_of_qa_work_in_jellyfish.md).

Use this when the skill needs to set **Metric**, **Team**, and **project** for creates/updates.

**Jira fields that affect Jellyfish:** status, Metric, team, project (+ Product and Host Platform when applicable).

---

## 1. Product work

**Includes:** acceptance testing, new/updated TC for a feature, TC automation for a new feature.

| Field | Value |
| --- | --- |
| Metric | **Feature** |
| Team | **Engineering team** delivering the feature (BigPicture team) |
| Project | App QA project (e.g. BigPicture QA / `TC`) |

**Rules:**

- Link tasks to the **feature Epic** (`parent` = epic).
- One or more QA tasks per Epic; **per-milestone** acceptance → separate task per milestone.
- Workflow: **In Progress** while testing → **Done** when complete.
- Separate phases → separate tasks; continuous retest → reopen same task to In Progress.
- Extra acceptance (migration, prod-like) → **new task**, don’t extend the original.
- **PO environment prep:** assign to QA → In Progress → complete setup → Ready to Start (or equivalent) → reassign to PO.

---

## 2. Maintenance

**Includes:** reproducing production issues, support verification, testing/retesting fixes.

| Field | Value |
| --- | --- |
| Metric | **Maintenance** or **L3 Support** |
| Team | **Engineering team** |
| Project | App QA project |

**Rules:**

- Track **every investigation**, even when no bug is confirmed.
- Tasks under team/quarter **maintenance Epic** when your org uses one.
- Issue type: usually **Task** (repro) or **Test Execution** (retest) per [activity-mapping.md](activity-mapping.md).

---

## 3. Release work

**Includes:** test run execution, sanity before deployment.

| Field | Value |
| --- | --- |
| Metric | **Feature** (feature release) or **Maintenance** (hotfix) |
| Team | **Engineering team** (doc also notes QA team visibility for coordinated release activity—confirm with engineer which field your project uses) |
| Project | App QA project |

**Rules:**

- **Each QA** creates at least: one **test run** + one **sanity** item.
- Issue types: **Test Execution** (see activity mapping).
- Feature release vs hotfix drives Metric (ask if unclear).

---

## 4. Test automation

**Includes:** learning tools (Playwright, Cypress), writing/maintaining E2E tests.

| Field | Value |
| --- | --- |
| Metric | See table below |
| Team | **QA team** (CoE) |
| Project | App QA project; Epic often owned by QA team |

| Scenario | Metric |
| --- | --- |
| Automation for new feature before production | **Feature** |
| Fix/update automation for live feature | **Maintenance** |
| Automation added long after release (coverage gap) | **Technical Debt** |

---

## 5. QA Operational Excellence

**Includes:** process improvements, TC repository cleanup, testing practice refinement.

| Field | Value |
| --- | --- |
| Metric | **Tech debt** |
| Team | **QA team** |
| Project | App QA project |

**Rules:**

- One concrete unit per task (e.g. “Refactor smoke TC set for module X”).
- Not feature delivery or production firefighting.

---

## Horizon vs engineering team (CoE mapping)

From [qa_work_tracking_in_jira.md](../../../QA_TRANSPARENCY/qa_work_tracking_in_jira.md):

| Assignment | When |
| --- | --- |
| **Eng team** (PPM) | Product delivery QA: PR testing, exploration, bugs, new TC, most feature-linked work |
| **Horizon** (QA CoE) | Test run, sanity (per CoE table), analyses, documentation; **Training** uses **QA CoE project** |

When Jellyfish doc says “Engineering team” and CoE table says “Horizon” for the same activity (e.g. sanity), **ask the engineer** which applies in their project’s Team field configuration.

---

## Scenario examples (quick match)

| Scenario | Work type | Typical issue type |
| --- | --- | --- |
| Sanity for 8.72 release | Release | Test Execution |
| Repro support ticket, no bug yet | Maintenance | Task |
| Acceptance on Epic PROJ-100 | Product | Task |
| Learning Playwright | Test automation | Task |
| Dedupe manual TCs in module X | Operational Excellence | Task |
| PO env setup for demo | Product | Task |

Full list: Jellyfish doc § “Examples of QA Work Scenarios”.
