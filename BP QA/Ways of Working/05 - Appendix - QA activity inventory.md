# Appendix: QA activity inventory

**Audience:** QA internal
**Maintained by:** the QA Team · **Contact:** Marek Wyszyński · **Version:** 2.1 (draft for review) · **Last reviewed:** 2026-09-22

---

## What this page is for

An inventory of everything the team does, classified by how it reaches them. It exists so nothing is accidentally dropped when work is sorted into the portal, and so the team can see what is absorbed rather than requested.

This page is **internal**. It is not a menu of things that can be requested — [QA Portal scope](02%20-%20QA%20Portal%20scope.md) is.

**Classification used throughout:**

| Mark | Meaning |
|------|---------|
| **Portal — requestable** | Anyone can request it |
| **Portal — QA-raised** | Tracked in the portal, but QA raises the ticket |
| **Portal — incident** | A portal ticket, raised by Engineering or Support during an incident |
| **Scheduled** | Planned work tracked in Jira outside the queue. No WIP slot, but it consumes capacity |
| **Release** | Happens as part of a release; not requestable |
| **Internal** | Absorbed into other work; never a ticket of its own |
| **Stopped** | No longer done by QA |

---

## Core testing

| Activity | Classification |
|----------|----------------|
| Requirements analysis | **Portal — requestable** (shift-left review) |
| Test scenario design | **Portal — requestable** (test design) |
| Feature testing | **Portal — requestable** |
| API testing | **Internal** — part of feature testing |
| Unit and database tests | **Internal** |
| Sanity testing | **Release** |
| Full Test Regression (TR) | **Release** |
| Regression after initiative delivery | **Portal — QA-raised**, triggered by the quarterly release schedule or the target date in the epic |
| Exploratory testing | **Internal** — part of feature testing |
| Fix verification for QA's own findings | **Internal** |
| Routine fix verification for other teams | **Stopped** — stays with the feature team |
| Release blocker / critical bug testing | **Release** |
| Verification during an absolutely Critical production incident | **Portal — incident.** Support assesses severity, Engineering provides L3, then Engineering or Support raises the ticket. **Verification only** |
| JCMA / migration testing | **Portal — requestable** |
| Event Manager testing | **Portal — requestable** |
| Performance testing, manual and JMeter | **Portal — requestable** |
| BugCrowd handling | **Portal — QA-raised.** Consumes WIP slots; volume is externally driven |
| Azure DevOps testing | **Portal — requestable** |

---

## Automation and test assets

This is the **2.5 days per engineer per week** reserved for automation, protected including through release freezes. The commitment is **at least one test case automated per engineer per day** — 2 to 3 created or fixed weekly, all tracked in Jira.

| Activity | Classification |
|----------|----------------|
| Creating new test cases | **Portal — requestable** when requested as test design; otherwise **Internal** |
| Refactoring existing test cases | **Internal** |
| Test case automation | **Portal — requestable** when for a specific feature; otherwise **Internal** |
| Fixing automated test cases | **Internal** |
| Automation placeholders prepared at quarter start | **Internal** — part of the quarterly preparation cycle |
| Environment, repo and tool configuration for automation | **Internal** |
| Verifying failed E2E runs; fixing steps and image data | **Internal** — QA's own test code |
| Data generation and generation scripts | **Internal** |
| CI platform work — agents, pipelines, build infrastructure | **Stopped** — DevOps |
| Triggering the release builds on CI | **Release** — the only CI activity QA performs |

The documented test cases produced here are what makes the generalist model work — they are the team's knowledge base, not a by-product.

> **The CI boundary.** QA fixes its **own failing automated tests** — that is QA's test code and it belongs here. The **CI platform** — agents, pipelines, build infrastructure — is DevOps, and CI requests are not portal requests. The distinction is ownership of the code, not of the tool. Without it, *"CI is out of scope"* and *"QA investigates failing automations"* look like a contradiction.

---

## Environments and infrastructure

| Activity | Classification |
|----------|----------------|
| Creating test environments for QA's own work | **Internal** — absorbed into the work it serves |
| Environment preparation for tests, TR, sanity, PM demos, local automation | **Internal** |
| Instance parameter tuning | **Internal** |
| Image instance updates; monitoring active user counts | **Internal** |
| Raising DevOps requests — broken jobs, instance extensions, missing project fields | **Internal** — raising the request, not doing the work |
| Creating instances **for other teams** | **Stopped** — self-service instructions in Confluence |

Environment effort is real cost inside the 2.0 FTE. It is never quoted separately to a requester; it is part of whatever the work is.

---

## Observability and data

These assets were **built and maintained jointly with Engineering**, which **continues as sole owner**. QA is withdrawing from shared ownership rather than handing over something unfamiliar, and any new work is Engineering's.

| Activity | Classification |
|----------|----------------|
| Kibana and Grafana charts and dashboards | **Stopped** — Engineering owns them |
| DataStudio creation and maintenance | **Stopped** |
| BigQuery maintenance | **Stopped** |
| Error analysis across tools (Anomaly detector) | **Stopped** |
| RUM event requirements and rollout | **Stopped** — Engineering owns the RUM Events portal |
| **RUM dashboard review before release** | **Release** — retained. QA reviews the data against thresholds set by PM and Engineering |
| Training or documentation for Engineering on these tools | **Portal — requestable** (enablement) |
| Log verification during story, bug or exploratory testing | **Internal** — part of testing, not dashboard work |

---

## Collaboration and support

Most of this is the work the out-of-band rule exists to stop, and three activities here have stopped outright.

| Activity | Classification |
|----------|----------------|
| Consultations with developers and Product Owners on bugs | **Internal** — answering a question is not work |
| Helping developers reproduce a bug | **Stopped** as a task. A conversation is fine; a reproduction effort is a request QA does not take |
| Support ticket reproduction | **Stopped** |
| Support ticket review | **Stopped** |
| Filing bugs for Support | **Stopped** — QA files the bugs it finds, not other people's |
| Answering domain questions on channels | **Internal** — a question is not a request |
| Meetings, brainstorming, syncs, quick help | **Internal** |

The boundary that matters: **answering a question is not work; producing a result someone will act on is.** Anything needing an environment or a test run goes through the portal.

---

## Process and planning

| Activity | Classification |
|----------|----------------|
| Quarterly intake — reviewing epics, preparing scenarios and placeholders | **Internal** — the preparation cycle |
| Initiative planning | **Internal** |
| Creating and adapting processes | **Internal** |
| Pipeline adjustments | **Internal** |
| Estimation, prioritisation, pain-point analysis | **Internal** — daily triage and retrospectives |
| Presentations and training for others | **Scheduled** — agreed at quarter start, tracked in Jira outside the queue |
| Performance requirements authoring | **Internal** |
| Documentation creation | **Portal — requestable** when requested; otherwise **Internal** |
| Team story creation | **Internal** |
| Team statistics presentations | **Internal** |
| Intake and throughput measurement | **Internal** — reported monthly at the retrospective |
| Release management and app releases | **Release** |

---

## Recurring team-level work

| Activity | Classification |
|----------|----------------|
| Meetings | **Internal** |
| Investigating failing automations | **Internal** — QA's own test code, not the CI platform |
| Leading releases, TR and sanity cycles | **Release** |
| Daily triage, 10:00 CET, including the daily review of held tickets | **Internal** — runs every working day, including during releases |
| The four-week hold review — returning to the requester | **Internal** |
| Monthly review of these pages at the Team Retrospective | **Internal** |

---

## Reading this page as a capacity statement

Most of this inventory is **Internal** — absorbed, unrequested, and invisible in the **portal** queue. That is the honest picture: the portal shows part of the team's time, and the queue is not the same thing as the workload.

It is not invisible everywhere, though. All of it is tracked in the **[QA work Jira project](LINK-TBC)** `[LINK TBC]`, which is what lets anyone reasoning about QA capacity see the whole picture rather than the portal slice of it. [Service levels and measures](04%20-%20Service%20levels%20and%20measures.md) has the capacity model.

The **Stopped** rows are worth reading as a set. They are the cost of running QA at four engineers, and they are the entries most likely to be discovered by someone being refused rather than by someone reading this page.
