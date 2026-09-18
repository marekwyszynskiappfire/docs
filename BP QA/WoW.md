# BP QA — Way of Working (WoW)

> Source: [Process Vision - Sticky Notes](https://appfireteam.atlassian.net/wiki/spaces/~7120202c1c597e249542f89ace1bdf6605ba70/whiteboard/99900981543)  
> Related: [QA Portal Workshop Outcomes](https://appfireteam.atlassian.net/wiki/spaces/~7120202c1c597e249542f89ace1bdf6605ba70/pages/99901308933/QA+Portal+Workshop+Outcomes)

This document captures the agreed vision for how QA work is requested, triaged, and delivered through the QA Portal. It defines what belongs in the portal, what does not, what information requesters must provide, and how the team operates day to day.

---

## 1. Purpose

The QA Portal is the single entry point for structured QA work. It helps the team:

- Prioritize work against capacity
- Ensure requests contain enough context to start
- Keep ad-hoc and out-of-scope work out of the queue
- Deliver predictable turnaround through SLAs and standardized reporting

---

## 2. In scope — tasks we want in the QA Portal

| Category | Examples |
|----------|----------|
| Feature testing | End-of-quarter or 100%-complete feature validation |
| Test automation | Automation for a particular feature |
| Regression | Regression after whole initiative delivery on `develop` |
| Performance | Manual and automated performance tests after development |
| Test design | New test cases needed after delivering a new feature |
| Event Manager | Sanity and regression testing |
| Release blockers | Release blocker testing (TBD) |
| Integrations | JCMA tests; Azure DevOps testing |
| Observability | Kibana and DataStudio features; dashboard updates |
| Shift-left | QA as a service while analyzing new features |
| Documentation | Testing documentation |
| Security | BugCrowd |
| Enablement | Training and courses for devs and others |

---

## 3. Out of scope — tasks we do not want in the QA Portal

These should be redirected or handled outside the portal:

| Item | Redirect / handling |
|------|---------------------|
| Support tickets | Not a QA Portal task |
| DevOps / infrastructure issues and requests | Redirect to DevOps |
| Creating bugs | Out of scope |
| Bug reporting | Out of scope |
| Regular / simple bug testing | Out of scope |
| Creating QA instances | Instructions should live in Confluence; not a portal request |
| Business questions (“how should this work?”) | Redirect to PO/PM |
| Vague environment reports | e.g. “Something is not working on AAN / develop / preprod — please verify” |

**Standard out-of-scope response template:**

> This request falls outside QA Portal scope. Redirected to [DevOps / PO / PM / etc.].

---

## 4. Required information in a request

Every request must include enough context for triage and execution. Missing information blocks the 24h triage window.

### 4.1 General (all request types)

- Link to epic or dev ticket in GitHub
- Confluence documentation
- Figma design (if UI-related)
- Feature flag name(s); if multiple flags, describe what each controls
- What kind of tests are needed
- What roles / permissions need to be tested
- Entry setup required before testing (if any)
- Manual vs automated?
- Tests only, or documentation as well?
- Deadline
- What we want to measure — purpose of tests, dashboards, success criteria
- How granular / deep the analysis should be
- For documentation requests: who is the audience?

### 4.2 Feature testing

- Linked Epic
- Figma design
- Feature flag(s) with descriptions
- Contact details for designer and PM

### 4.3 JCMA / migration testing

- Source DC version (Jira 10 or Jira 11)
- Target Cloud version
- Apps to migrate: BP, BG, or BT

### 4.4 Event Manager testing

- Names and numbers of environments to test

---

## 5. Process

### 5.1 Intake and triage

1. A ticket arrives in the QA Portal queue.
2. **24h triage SLA** — within 24 hours, QA verifies the ticket has all required information.
3. If information is missing, return the ticket to the requester with a clear list of gaps.
4. If the request is out of scope, return it using the standard template above.

### 5.2 Definition of Ready / Done (epic or main story)

Before work starts on an epic or main story, the following must be defined:

- **Definition of Ready (DoR)** — criteria for when QA can begin
- **Definition of Done (DoD)** — criteria for when QA work is complete
- **Acceptance criteria** — what must be checked and working before QA can approve

### 5.3 Planning and assignment

- Tickets are **not assigned top-down**.
- During daily planning, the team reviews the **prioritized queue**.
- Available QA engineers pull the **highest-priority** ticket into their active WIP.
- Team estimates effort and checks who has open capacity.
- **WIP limit:** max **2 tasks in progress** per person.

### 5.4 Delivery and reporting

- Use a **standardized QA delivery report** when closing work.
- Use a **single template** for testing reports (define: screenshot, comment, recording — TBD).
- QA Portal main page should link to self-service instructions (e.g. creating QA instances).

### 5.5 Open questions

- Should all tickets in the queue/filter have an assignee? What if there are dozens of unassigned tickets?

---

## 6. SLAs by task category

| Task category | SLA |
|---------------|-----|
| Requirement review (Shift-left) | 2 business days |
| Automation task | 3–5 business days |
| Full regression | 4–7 business days |
| Performance tests | 3–5 business days |

*Triage: 24 hours to analyze whether required information is present.*

---

## 7. Risks and mitigations

| Risk | Notes |
|------|-------|
| Lack of shared knowledge base | Do we need internal training / a common knowledge base? |
| Lack of knowledge about product areas | QAs may not know all domains |
| QA as a bottleneck | Not enough QAs for incoming demand |
| Ad-hoc requests outside the portal | Developers bypass the portal (“wrzutki”) |
| Ownership model unclear | Does everyone test everything, or do we own specific areas? How do we build knowledge? |
| Automation time squeezed | Too many tickets, not enough time to maintain/create automated test cases |
| Meeting overload | Shift-left participation in feature meetings may create too many meetings |
| Lower product familiarity | Less depth → weaker tests |

---

## 8. Current QA activities (team inventory)

Activities the team performs today. Use this to map what moves into the portal vs. what stays as team-internal work.

### 8.1 Core testing

- Requirements analysis (*Analiza wymagań*)
- Test scenario design (*Projektowanie scenariuszy testowych*)
- Feature testing
- API testing
- Unit tests and database tests
- Sanity testing
- Full test regression (*Full TR*)
- Regression and exploratory testing
- Fix verification (*Weryfikacja fixów*)
- Release blocker / critical bug testing within the team
- JCMA / migration testing
- Event Manager testing
- Performance tests — manual and automated (JMeter)
- BugCrowd handling
- Azure DevOps testing (soon; currently handled by Robson)

### 8.2 Automation and test assets

- Creating new test cases
- Refactoring existing test cases
- Test case automation
- Fixing automated test cases
- Environment/repo/tool configuration for automation
- Verifying failed E2E runs; fixing steps in Jira; fixing data on images
- Data generation and generation scripts

### 8.3 Environments and infrastructure

- Creating test environments
- Environment preparation (tests, TR, sanity, PM, local automation)
- Instance parameter tuning for tests
- Image instance updates; monitoring active user counts
- DevOps requests (broken jobs, instance extensions, missing project fields)

### 8.4 Observability and data

- Log verification during specific story/bug or exploratory testing
- Kibana / Grafana charts and dashboards
- DataStudio creation and maintenance
- BigQuery maintenance
- RUM event requirements and rollout
- Error analysis across tools (Anomaly detector)

### 8.5 Collaboration and support

- Consultations with dev and PO on bugs
- Help with bug reproduction for dev
- Support ticket reproduction help (private consultations with support)
- Answering domain questions on various channels
- Soft work: meetings, brainstorming, syncs, quick help

### 8.6 Process and planning

- Initiative planning
- Creating and adapting processes from scratch
- Pipeline adjustments
- Estimation, prioritization, pain-point analysis
- Presentations and training
- Performance requirements authoring
- Documentation creation
- Team story creation (occasionally)
- Team statistics presentations
- Support ticket review (team subset)
- Bug filing for support (team)
- Release management (soon)
- App releases (soon)

### 8.7 Team-level recurring work

- Participating in many meetings (noted: team member out from 16.09)
- Checking causes of failing automations
- Leading releases, TR, sanity cycles

---

## 9. Portal vs. team work — mapping guide

| Move to QA Portal | Keep outside portal / self-service |
|-------------------|-------------------------------------|
| Feature testing (with full request info) | Simple bug verification |
| Automation for a feature | Creating bugs / bug reports |
| Regression after initiative on `develop` | Support tickets |
| Performance testing | DevOps / infra requests |
| Shift-left requirement review | QA instance creation (Confluence instructions) |
| JCMA / Event Manager structured requests | Vague “something is broken” reports |
| Documentation and training requests | Business/product questions → PO/PM |

---

## 10. Next steps / open decisions

- [ ] Finalize release blocker testing scope in the portal
- [ ] Agree testing report template (screenshot / comment / recording)
- [ ] Publish self-service Confluence links on QA Portal home page
- [ ] Decide assignee model for unassigned queue items
- [ ] Define area ownership vs. generalist testing model
- [ ] Stand up shared knowledge base and internal training plan
