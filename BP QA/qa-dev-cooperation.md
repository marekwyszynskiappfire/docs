# BP QA–Development Cooperation Process

**Audience:** BP QA and Engineering  
**Status:** draft — pending stakeholder review  
**Last updated:** 2026-10-15  
**Reviewed with QA:** date TBC · **Reviewed with Engineering:** date TBC · **Reviewed with Product Management:** date TBC

How QA and Development work together on BigPicture. One page. Tool how-tos stay in their own docs.

## How to read this page

| Label | Meaning |
|-------|---------|
| **Draft** | Defined in this working session, pending stakeholder review. |
| **Agreed** | Reviewed and accepted by the necessary participants. In force. |
| **Open** | Needs a decision before it is treated as process. |
| **TBD** | Fact or link missing. |

Do not infer policy. **Everything remains Draft until stakeholder review.**

---

## 1. Purpose

The BP QA–Development cooperation needs a new working model following the
changes made to the QA team at the end of August 2026. With reduced capacity,
BP QA can no longer provide the previous operating model and must transition
to a **Quality Assurance as a Service (QAaaS)** approach. This page defines
how QA and Development will cooperate under that model. Content is **Draft**
until the necessary participants review it. Unresolved items stay visible.

---

## 2. Roles and decision rights (RACI)

For **new epics**. Cells are filled only after each role on that row is confirmed.

| Letter | Meaning |
|--------|---------|
| **R** | Responsible — does the work |
| **A** | Accountable — owns the outcome (one **A** per row unless we explicitly decide otherwise) |
| **C** | Consulted — two-way input before or during the work |
| **I** | Informed — told of progress or result |
| **—** | No role on this area |

A cell may combine letters (for example **R, A**). Several groups may share **R**, **C**, or **I**.

| # | Area | Product Management | Development | QA | Status |
|---|------|--------------------|-------------|----|--------|
| R1 | Define and document requirements | **R, A** | **C** | **I** | Draft |
| R2 | Analyse requirements with Trinity | **C** | **C** | **R, A** | Draft |
| R3 | Create test cases with Trinity | **C** | **I** | **R, A** | Draft |
| R4 | Develop the solution | **C** | **R, A** | **I** | Draft |
| R5 | Quality of the delivered solution | **C** | **R, A** | **R** | Draft |
| R6 | Test against the created scenarios | **I** | **R, A** | **R** | Draft |
| R7 | Automate selected test scenarios | **C** | **R** | **R, A** | Draft |
| R8 | Maintain automated test cases | **I** | **R** | **R, A** | Draft |
| R9 | Acceptance-test the final solution | **R, A** | **I** | **R** | Draft |

**R1 — Define and document requirements.** PM writes the spec and owns whether it is complete. Development is asked whether it is buildable and clear. QA is told when the spec exists so Trinity analysis can start.

**R2 — Analyse requirements with Trinity.** QA runs the analysis and owns its quality. PM answers product questions. Development answers technical/feasibility questions.

**R3 — Create test cases with Trinity.** QA creates the tests and owns them. PM is asked about expected behaviour and acceptance criteria. Development is told which tests now exist.

**R4 — Develop the solution.** Development builds it and owns delivery. PM clarifies product intent during the work. QA is told of progress and readiness for testing.

**R5 — Quality of the delivered solution.** Development owns the quality of what ships and does the work to get there. QA performs the defined quality activities. PM is asked what “good” means (expected behaviour and acceptance criteria).

**R6 — Test against the created scenarios.** Development executes the scenarios and owns this testing. QA also executes the scenarios. PM is told the outcomes.

**R7 — Automate selected test scenarios.** QA automates the selected cases and owns delivery. Development shares the implementation work. PM is asked which cases are **business-critical** so the selection is right.

**R8 — Maintain automated test cases.** QA maintains the suite and owns its health. Development shares the maintenance work. PM is told about coverage and maintenance risk.

**R9 — Acceptance-test the final solution.** PM performs acceptance testing and owns the accept/reject call. QA also executes the acceptance tests. Development is told the result.

---

## 3. Epic path

**Status: draft for review — not agreed.**

Not every epic requires explicit QA work. QA participates in quarterly planning
for the whole portfolio; the dedicated QA path applies only to the epics
selected afterwards within available QA capacity.

| Step | What happens | Primary parties | Outcome |
|------|--------------|-----------------|---------|
| 1. Define the epic | PM documents the requirements and PRD in Confluence and, with UX, provides the required Figma designs. | PM, UX | Defined epic with supporting documentation |
| 2. Plan the quarter | Quarterly Planning decides which epics enter the quarter and their expected delivery timing. QA participates in the planning. | PM, Development, QA | Prioritised quarterly plan |
| 3. Select QA coverage | Immediately after planning, the BigPicture QA Manager and Software Engineering Managers identify epics that may need QA work. They assess QA capacity and determine how much prioritised work can be covered. Mid-quarter additions or removals require them to reassess scope and capacity together. | QA Manager, Software Engineering Managers | Epics selected for QA coverage |
| 4. Analyse and prepare | QA runs Trinity on selected epics for requirement analysis and preliminary test-case creation. Questions or gaps are returned to PM when needed. | QA, with PM and Development consulted | Trinity review and preliminary test cases |
| 5. Build | Development implements the solution and remains accountable for its quality. | Development | Testable implementation |
| 6. Revalidate the epic | When the implementation is ready, QA decides whether meaningful changes are suspected. If so, QA reruns Trinity to check the epic definition, work-item decomposition, and supporting documentation. | QA, with PM and Development consulted | Updated review and test cases, if needed |
| 7. Test and accept | Development owns scenario testing; QA also executes the scenarios. QA and PM perform acceptance testing; PM owns the acceptance decision. | Development, QA, PM | Test and acceptance results |
| 8. Automate selected cases | Where required and feasible, QA automates selected scenarios. Engineering contributes when QA lacks capacity. The expected split should ideally be agreed during post-planning QA capacity assessment. Incomplete automation may continue as tracked follow-up work after delivery. | QA, Development; PM consulted on business criticality | Automated coverage or tracked follow-up |
| 9. Address findings | Every issue found during testing is fixed or documented in Jira and explicitly accepted or deferred by PM. | Development, QA, PM | No unaddressed findings |
| 10. Deliver and close | Once testing is complete, findings are addressed, and acceptance is obtained, PM gives final approval to deliver the epic to customers and close it. Outstanding automation does not block closure when it is tracked as follow-up work. | PM accountable; Development and QA informed | Delivered and closed epic |

**If an epic is not selected for QA coverage:** it does not go through steps
4, 6, or QA-led parts of steps 7–8. PM and Development retain their RACI
responsibilities for requirements, implementation quality, acceptance,
delivery, and closure.

**Legion is not part of an individual epic path.** It is used during the
release process to determine additional QA work across the release.

---

## 4. Trinity

AI-assisted requirement analysis and preliminary test-case creation for epics
**selected for QA coverage**. Operator how-to stays in Trinity docs; this page
only states when it is used and what each party owes.

- **Docs:** [Trinity — Start here](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754590489/Trinity+Start+here)
- **When:** immediately after QA coverage is selected (epic path step 4). QA may
  rerun it when the implementation is ready if meaningful change is suspected
  (step 6).
- **Who runs it:** QA.
- **What Development owes:** answers on feasibility and technical intent when
  consulted during analysis.
- **What PM owes:** answers on expected behaviour and gaps returned from the
  review.
- **What QA returns:** requirement-analysis findings and preliminary test
  cases. Gaps go back to PM. Test cases are the starting asset for later
  scenario testing and selected automation.

| Item | Status | Notes |
|------|--------|-------|
| When Trinity is used | Draft | Selected QA epics after coverage planning; optional second run at test readiness |
| Who runs it | Draft | QA |
| Who acts on gaps | Draft | PM, with Development consulted on technical points |
| How output becomes test assets | Draft | Preliminary Trinity test cases owned by QA (R3) |

---

## 5. Legion

Legion is a **release-level coverage analysis**, not an individual epic step.

- **Docs:** [Legion](https://docs-dts.appfire.net/platform-documentation/qa-coe/legion/)
- **When:** after the release branch is cut and e2e tests have run against it.
- **Trigger:** QA starts the analysis.
- **Decision:** QA reviews the recommendations and selects the additional
  manual tests to execute.
- **Execution:** QA performs the selected additional manual tests.
- **Current inputs:** e2e results, changes in the BigPicture codebase, and the
  manual test cases used for release regression.
- **Planned inputs:** unit- and integration-test results.
- **Output:** recommendations for additional manual test cases that should be
  executed to maximise release coverage.

| Item | Status | Notes |
|------|--------|-------|
| Placement in the process | Draft | Release process, after branch cut and e2e execution |
| Purpose and inputs | Draft | Compare automated results and code changes with manual regression coverage |
| Recommended additional tests | Draft | Legion identifies manual cases needed to improve coverage |
| Documentation | Draft | https://docs-dts.appfire.net/platform-documentation/qa-coe/legion/ |
| Who triggers Legion | Draft | QA |
| Who reviews and approves recommendations | Draft | QA |
| Who executes the additional tests | Draft | QA |

---

## 6. Epic acceptance testing and QA involvement

Applies to epics **selected for QA coverage**. PM still owns acceptance on
epics that QA does not cover.

| Question | Answer | Status |
|----------|--------|--------|
| Who owns epic acceptance? | PM (**R, A**). QA executes acceptance tests (**R**). Development is informed. | Draft |
| What QA executes vs reviews vs advises | QA executes scenario tests (**R**; Development is **R, A**) and acceptance tests. QA does not own the accept/reject call. | Draft |
| What stays with the feature team | Development owns implementation and the quality of what ships. QA is not allocated to the squad. | Draft |
| What “done” means for QA on an epic | Scenario testing is complete; findings are fixed or documented in Jira and accepted or deferred by PM; QA’s part of acceptance testing is done. Outstanding automation may remain as tracked follow-up. | Draft |
| How results and bugs are handed back | Issues found in testing are raised in Jira. An issue is addressed when it is fixed, or when it is recorded and PM explicitly accepts or defers it. | Draft |

---

## 7. Test automation and maintenance

| Question | Answer | Status |
|----------|--------|--------|
| Who creates new automation | QA owns creation of selected automated scenarios (**R, A**). Development shares implementation (**R**) when QA lacks capacity. PM is consulted on business criticality. The expected split should be set in the post-planning capacity assessment. | Draft |
| Who maintains failing tests | QA owns suite health (**R, A**). Development shares maintenance (**R**). PM is informed of coverage and maintenance risk. | Draft |
| CI / pipeline ownership vs test-code ownership | Automated test code is owned by QA and Development (per R7/R8). CI and pipelines sit with Development or DevOps, not as QA operational work. | Draft |
| When automation is prepared vs executed | Preliminary cases come from Trinity after coverage selection. Automation of selected scenarios starts when required and feasible, ideally planned at quarterly QA capacity assessment. Incomplete automation may continue as tracked follow-up and does not block epic closure. | Draft |

---

## 8. Capacity

No headcount or SLA numbers are stated here until stakeholders confirm them.
What is decided so far is **how** capacity is allocated.

| Question | Answer | Status |
|----------|--------|--------|
| How QA capacity is shared | As a service across the portfolio, not reserved for a squad. Coverage is chosen against available QA capacity after Quarterly Planning. | Draft |
| How work is requested / sequenced | Epics are defined by PM, then prioritised in Quarterly Planning (QA present). Immediately afterwards, the BigPicture QA Manager and Software Engineering Managers select which epics QA will cover. | Draft |
| What happens when demand exceeds capacity | Only as much prioritised work as QA can cover is selected. Unselected epics proceed without the dedicated QA path. Mid-quarter add/remove requires the same parties to reassess together. | Draft |
| Where work in progress is visible | In Jira project **ONE**: a Story with sub-tasks is created for every epic that needs QA work. | Draft |

---

## 9. Additional QA responsibilities

Work besides the new-epic path. Sourced from the previous Ways of Working
scope; **Draft** until stakeholder review. No capacity numbers from that
model are carried forward.

| Area | What QA does |
|------|----------------|
| Release testing | Sanity, Test Regression, canary, release-blocker testing, and RUM review against thresholds owned by PM and Engineering. QA recommends; PM and Engineering decide go/no-go. |
| Legion (release) | After the release branch and e2e run, select and execute extra manual tests (section 5). |
| BugCrowd | QA owns intake from BugCrowd, raises the resulting work, and handles the findings. Volume is external; it competes for the same QA capacity as other work. |
| Other product testing | JCMA / migration, Event Manager, Azure DevOps, performance (manual and JMeter), and documentation testing when included in capacity planning. |
| Enablement | Training and documentation for other teams, planned rather than queued. |
| Environments | Create and prepare instances for QA’s own testing and release work. |
| Defects QA finds | File them. Verify fixes for those findings. |

---

## 10. Out of scope for QA

Sourced from the previous Ways of Working scope; **Draft** until stakeholder
review.

| Out of scope | Who owns it |
|--------------|-------------|
| Dedicated, embedded, or reserved QA capacity | Declined. QA is a shared service. |
| Release go/no-go | Product Management and Engineering. QA recommends only. |
| Support tickets and support-ticket review | Support. QA has stopped this. |
| Production issues, except verification of an **absolutely Critical** incident (system unusable or major data loss), after Support and Engineering L3 | Support, then Engineering; QA verifies only if asked. |
| Routine bug verification and reproducing bugs for a developer | The feature team. A short conversation is fine; the effort is not QA work. |
| Filing bugs on behalf of Engineering, PM, or Support | The person who found the issue. |
| Product questions (“how should this work?”) | Product Management. |
| Vague “something is broken” reports | Not actionable until there is a reproducible report on a named environment. |
| DevOps, infrastructure, and CI platform (agents, pipelines, build infra) | DevOps / Development. QA keeps its automated **test code**; QA may trigger release builds. |
| Observability assets (Kibana, Grafana, DataStudio, BigQuery, RUM rollout) | Engineering. Exception: QA still **reviews** RUM at canary. |
| Creating QA instances for other teams | Self-service. QA builds instances only for its own work. |

---

## 11. Active initiatives

Work in flight that this process must account for. Add or remove rows as we go.

| Initiative | Intent | Owner | Status | Blocks | Link |
|------------|--------|-------|--------|--------|------|
| Trinity adoption | Use Trinity for requirement analysis and preliminary test cases on QA-covered epics | QA | Draft | Operator setup and epic documentation quality | [Start here](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754590489/Trinity+Start+here) |
| Legion adoption | After each release branch cut and e2e run, analyse coverage vs code change and recommend extra manual tests | QA | Draft | Later: unit and integration results as inputs | [Legion](https://docs-dts.appfire.net/platform-documentation/qa-coe/legion/) |
| Self-healer | AI-based solution that repairs broken automated tests by fixing test code or seeding the right data into test environments | QA | Draft | Awaiting Engineering assessment | |
| Jira-independent testbed | Environment for testing BigPicture without a full Jira setup underneath | Engineering | Draft | Still in discovery | |
| QAaaS operating model | Replace the pre–August 2026 model with the process on this page | QA, Development, PM | Draft | Stakeholder review of this page | This document |

---

## 12. Agreements and loose ends

### Agreed

| # | Decision | Date | Who |
|---|----------|------|-----|
| | _None until stakeholder review._ | | |

### Draft decisions pending review

| # | Decision |
|---|----------|
| D-01 | RACI for new epics (R1–R9), section 2 |
| D-02 | Epic path and QA coverage model, section 3 |
| D-03 | Legion placement, inputs, ownership, and execution, section 5 |
| D-04 | Trinity usage on selected epics, section 4 |
| D-05 | Acceptance testing and QA involvement, section 6 |
| D-06 | Test automation and maintenance, including CI vs test-code ownership, section 7 |
| D-07 | Capacity allocation and WIP visibility in ONE, section 8 |
| D-08 | Additional QA responsibilities, section 9 (from previous Ways of Working) |
| D-09 | Out of scope for QA, section 10 (from previous Ways of Working) |

### Open

| # | Question | Owner | Needed to close |
|---|----------|-------|-----------------|
| | _None._ | | |

---

## 13. Links

| Resource | URL |
|----------|-----|
| This page (Confluence) | https://appfireteam.atlassian.net/wiki/spaces/~7120202c1c597e249542f89ace1bdf6605ba70/pages/100002922580/BP+QA+Development+Cooperation+Process |
| Trinity | https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754590489/Trinity+Start+here |
| Legion | https://docs-dts.appfire.net/platform-documentation/qa-coe/legion/ |
| Related Jira / filters | ONE — one Story with sub-tasks per QA-covered epic |
