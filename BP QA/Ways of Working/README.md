# BP QA — Ways of Working

How the BP QA team takes in work, decides what to do next, and delivers it. These pages replace the draft `../WoW.md` and are written to be published as Confluence pages, one audience each.

**Maintained by:** the QA Team · **Reviewed:** monthly, at the Team Retrospective · **First point of contact:** Marek Wyszyński, with the whole QA team acting as deputies
**Version:** 2.0 (draft for review) · **Last reviewed:** 2026-09-22

---

## The pages

| # | Page | Who it is for |
|---|------|---------------|
| 1 | [Requesting QA work](01%20-%20Requesting%20QA%20work.md) | Anyone who needs something from QA |
| 2 | [QA Portal scope](02%20-%20QA%20Portal%20scope.md) | Requesters, managers, and the functions QA depends on |
| 3 | [How the QA team works](03%20-%20How%20the%20QA%20team%20works.md) | The QA team and managers |
| 4 | [Service levels and measures](04%20-%20Service%20levels%20and%20measures.md) | Managers |
| 5 | [Appendix: QA activity inventory](05%20-%20Appendix%20-%20QA%20activity%20inventory.md) | QA internal |
| 6 | [Using the QA Portal](06%20-%20Using%20the%20QA%20Portal.md) | Requesters — **being written by the QA team** |

**If you only read one:** page 1 if you need something from QA, page 4 if you are trying to understand QA's capacity, page 2 if you work in Product Management, Engineering or Support and want to know what QA needs from you.

The split exists because these change at different rates. Scope and service levels are stable; the portal form changes whenever someone edits a field.

---

## The shape of it, in one minute

**The team is four engineers, and it will not grow.** Following the team's reorganisation, four QA engineers remain with BigPicture, and everything below is the operating model built for that size rather than a preference about how QA should work.

**Two rhythms run at once.**

| Rhythm | What happens |
|--------|--------------|
| **Quarterly** | Every epic is defined and in Jira at the start of the quarter. QA runs them through its requirement tooling, sends back gaps, and prepares test scenarios and automation placeholders before any work is requested |
| **Fortnightly** | A release roughly every two weeks. During a release, no portal requests are worked — automation continues |

Between those, work is pulled from the queue: no assignment, two tickets at a time per engineer, priority set at daily triage.

**Half the team's time is automation and it is protected**, including through release freezes. At least one test case automated per engineer per day.

---

## The one idea behind all of it

Four engineers cover the whole product. That is too few to specialise, so **any engineer can pick up any request** — the team is deliberately generalist rather than divided into owned areas.

Everything else follows. Because a request may be picked up by someone who has never worked on that feature, the process is built to **lower the knowledge a piece of work requires** rather than expect everyone to know everything:

- requests must carry a clear description of the functionality, judged against the organisation's SDLC definition of a complete epic
- test cases are documented and linked, so knowledge lives in artifacts rather than in people
- AI-assisted tooling does the first pass on requirement reviews, with QA reviewing the output
- a poorly documented request is deprioritised, because documentation is the one gap shared knowledge cannot close

This is a trade. Depth is exchanged for flow, knowingly. At four engineers it is the right exchange, and it is why the quality of what you submit has a direct effect on what you get back.

**What it costs the organisation is written down, not implied.** The out-of-scope list on page 2 is not a statement of preference — it is the price of running QA at this size, itemised.

---

## Glossary

These pages are written in English, including internal terms the team has historically used in Polish.

| Term | Meaning |
|------|---------|
| **AC** | Acceptance criteria — what must be working for a feature to be accepted. Authored in the epic, not by QA |
| **BP / BG / BT** | The Appfire apps the team tests |
| **BugCrowd** | The external security research platform. Findings arrive from outside and are raised as portal tickets by QA |
| **DoD** | Definition of Done — an epic-level standard shared with Engineering. Includes Product Management sign-off |
| **DoR** | Definition of Ready — an epic-level standard shared with Engineering, defining when work can start |
| **E2E** | End-to-end automated test |
| **Freeze** | The period around a release when QA takes on no portal requests. Roughly a week, every two weeks |
| **Hold** | A ticket that is accepted but not being worked, with a stated reason and point in time. Reviewed daily |
| **JCMA** | Jira Cloud Migration Assistant. Migration testing from Data Center to Cloud |
| **Needed by…** | A field on the portal request form. The main input to how work is ordered |
| **QA Portal** | The Jira Service Management project through which all QA work is requested |
| **RUM** | Real User Monitoring. Performance data reviewed before a release |
| **Sanity** | A short confidence pass over critical paths |
| **Scheduled work** | Large planned work — training, enablement — tracked in Jira outside the queue, which still consumes capacity |
| **SDLC** | The organisation's software development lifecycle, which defines what a complete epic contains |
| **TR** | Test Regression — the full regression cycle run as part of a release |
| **Triage** | The daily QA meeting, 10:00 CET, where new requests are read and ordered |
| **WIP** | Work in progress. Capped at two tickets per engineer |

---

## Before these pages are published

**Links to collect.** Placeholders are marked `[LINK TBC]` in the text.

| Outstanding | Needed for |
|-------------|------------|
| A **Jira filter showing all QA tickets** | Pages 1 and 4 — so requesters can see queue state |
| The **SDLC definition of a complete epic** | Pages 1, 2 and 3 — the objective bar for requirement review and prioritisation |
| The **quarterly release schedule** | Pages 1 and 3 — the trigger for full regression, and how requesters see when freezes fall |
| The **severity rules** defining a release blocker | Pages 2 and 3 |
| The **`#bp-status-release-feature`** Slack channel | Pages 1 and 3 |
| The **QA team's public holiday calendar** | Page 1 — requesters elsewhere have no reason to know when the team is off |

**Conversations to hold.** Pages 2 and 3 describe work that other functions must do. Each is being walked through with the function concerned, and pages 2 and 3 carry a *reviewed with* line once that happens. Most of it is already known practice; the parts that genuinely change are the incident route into QA, the observability ownership, and three activities QA has stopped.

**Page 6** is being written by the QA team from the live portal. The other five pages do not depend on it and publish first.

---

## How these pages were produced

Drafted from the [Process Vision whiteboard](https://appfireteam.atlassian.net/wiki/spaces/~7120202c1c597e249542f89ace1bdf6605ba70/whiteboard/99900981543), then reviewed twice: once against two personas to settle what the team does, and once against seven personas to test whether the pages could actually be used. Nineteen questions in the first round, twenty-four findings and eight assumptions in the second. The working files sit one folder up:

- `../personas.md` — the seven review lenses
- `../review-report.md` — the first review: every contradiction found in the draft, and how it was resolved
- `../page-review-questions.md` — the second review: findings against these pages, and the answers
- `../MEMORY.md` — session state and the full decision record

If you disagree with something here, those files probably explain why it ended up this way.
