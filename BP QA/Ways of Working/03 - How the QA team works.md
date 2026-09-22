# How the QA team works

**Audience:** the QA team and managers
**Maintained by:** the QA Team · **Contact:** Marek Wyszyński · **Version:** 2.0 · **Last reviewed:** 2026-09-22
**Reviewed with:** Product Management `[date TBC]` · Engineering `[date TBC]` · Support `[date TBC]`

---

## The operating principle

Following the team's reorganisation, **four QA engineers** remain with BigPicture, and the team will not grow beyond that. Everything here is the operating model built for that size — not a preference about how QA should work.

Four people cannot divide the product into owned areas, so the team is **generalist by necessity**: any engineer can pick up any request, and nobody owns a domain.

The mitigation for the depth this costs is not "everyone learns everything". It is to **reduce the knowledge a piece of work requires**:

| Mechanism | How it lowers the bar |
|-----------|----------------------|
| Documented test cases, linked on every ticket | Knowledge lives in artifacts, not in individuals |
| A clear description of the feature, judged against the SDLC standard | The request carries its own context |
| AI-assisted requirement review, with QA reviewing the output | The first pass does not depend on familiarity |
| The quarterly preparation cycle | Nobody meets an epic for the first time when the work arrives |

This explains a rule that otherwise looks bureaucratic: **requests with substantially incomplete documentation are deprioritised**. Incomplete documentation is the single input that shared knowledge cannot compensate for. The model protects the thing it depends on.

**It is a trade, and worth naming as one.** Depth is exchanged for flow. The model holds while requirements are good; where they are not, the demotion rule is the release valve.

---

## Two rhythms

The team runs on a quarterly cycle and a fortnightly one at the same time. Neither is an interruption to the other; together they are the operating pattern.

### Quarterly — intake and preparation

Every epic should be **defined and delivered to QA as Jira items at the start of the quarter**. QA then:

1. feeds them through the requirement review tooling
2. reviews the output and sends the gaps back to the authors
3. prepares test scenarios
4. creates automation placeholders

By the time a request arrives, the team has read the epic, knows what is missing, and has somewhere for the automation to go. This is what "submit early" actually buys, and it is why the ask is worth making.

### Fortnightly — the release cycle

A release roughly **every two weeks**, five or six a quarter, following the **[quarterly release schedule](LINK-TBC)** `[LINK TBC]`.

For about a week around each release, QA is occupied with:

| Activity | Effort |
|----------|--------|
| Release testing | ~2 days |
| Verification of fixes | ~2 days — **actively being reduced** |
| CI-related work | ~1 FTE per release, spread across the four engineers |

**During a freeze, no portal requests are worked. Automation continues.** That distinction matters: the automation half of the team's time is protected even here.

Portal work therefore happens **between freezes**, and that is the single most useful thing for a requester to understand about timing.

---

## Capacity

| | |
|---|---|
| QA Engineers | **4 — and this will not grow** |
| Split of effort | **2.5 business days per engineer per week** on portal and release work; **2.5 on automation** |
| Effective portal capacity | **2.0 FTE — release work comes out of this half** |
| WIP limit | **2 tickets per engineer** |
| Ceiling on work in progress | **8 tickets** |
| Inflow ceiling | **8 new tickets per week.** Above that, the excess is **automatically put on hold** |

The WIP limit exists because every engineer also automates test cases as part of daily work. The ceiling is a hard limit, not a guideline.

**The automatic hold is the mechanism that protects all of this.** Past eight new tickets in a week, the rest are held with a reason. It needs no judgement, no negotiation and no meeting, and it makes demand above capacity a visible number rather than an argument QA has to win.

**The eight slots are not always all available.** While scheduled work — training, enablement — is running, fewer engineers can pull, and that is declared at triage. A release freeze reduces available slots to zero.

---

## Daily triage

**Every working day, 10:00 CET.** Owned by the team, not by a chair, so it runs with whoever is present. The whole team operates in CET, which is what the response commitment is measured in.

At triage the team:

1. reads every new request and checks it has the required information
2. sets or re-assesses priority
3. orders the queue
4. **reviews every held ticket**
5. comments on every triaged ticket

Holds are reviewed **daily** today; this may move to twice weekly if ticket volume makes daily impractical.

### Every triaged ticket gets a comment

One of three, always:

| Outcome | Comment says |
|---------|--------------|
| **Picked up** | An engineer has taken it |
| **Incomplete** | Exactly what information is missing. The clock stops |
| **On hold** | Parked until a stated point, **with the reason given** |

Two things cause a hold, and the comment distinguishes them: the **work cannot start yet**, or the team is **at capacity**. The first is now the common case, since epics arrive at quarter start for features that ship later — the hold list is the team's forward book, not a pile of problems.

**There is never silence from QA.** Triage runs even during a release, when the only outcome may be adding comments to waiting tickets.

---

## How work is taken on

**Pull, with no assignment by anyone** — not Engineering, not Product Management, not the QA lead.

- Queue items have **no assignee until pulled**.
- Engineers take the **highest-priority** ticket they have capacity for.
- **Two tickets maximum** in progress per engineer.
- **A blocked ticket frees the slot.** It returns to the queue keeping its priority, and whoever has capacity picks it up when the answer arrives. QA does not hold capacity hostage to other teams' response times.

### Priority

The standard Jira scale. Every request arrives at **Medium**; requesters cannot raise it.

| Level | When |
|-------|------|
| **High / Highest** | Release-related work; absolutely Critical production issues needing QA verification |
| **Medium** (default) | Everything else, ordered by **"Needed by…"** |
| **Lowered** | The epic is substantially incomplete against the **[SDLC definition](LINK-TBC)** `[LINK TBC]`, or the **target date in the epic** shows the feature is not shipping soon |

Neither demotion reason is QA's judgement: one is checked by the requirement review tooling against a published standard, the other is a documented attribute of the epic. Both are **recorded as a ticket comment naming what is missing**, and **supplying it restores priority**.

### When QA cannot meet what a requester expected

One rule, covering every case:

> QA says so **on the ticket** and opens a conversation, **as a team** — never leaving an individual engineer to negotiate alone.

That applies when nobody picks up a ticket with a tight deadline, when the ceiling forces something to be parked, and when an engineer's estimate does not fit the date. In the last case the estimate should also say whether it **spans a release freeze**.

Where two requesters genuinely conflict and triage cannot settle it, QA convenes an **ad-hoc session with the managers involved — together, not separately** — and records the outcome on both tickets.

### The clock

The response clock runs on **CET working days**, and the team's public holidays move it. When a ticket is returned for missing information, **the clock stops** and resumes when the requester responds.

Completion is not on a clock at all — see [Service levels and measures](04%20-%20Service%20levels%20and%20measures.md).

---

## Automation

Half of every engineer's week — **2.5 business days** — and it is protected, including through release freezes.

**The commitment: at least one test case automated per engineer per day**, which is **2 to 3 test cases created or fixed each week per engineer**, or roughly 8 to 12 across the team. All of it is tracked in Jira.

This is not reserved time with no output. The test cases it produces are what makes generalist working possible, and the automation placeholders created at quarter start are what stop each new feature starting from zero.

---

## Delivering and closing

An engineer estimates the work **when they pick it up**, and communicates the estimate then.

At completion, QA:

1. **closes the ticket as Done**
2. leaves a **comment** explaining what was tested and the result
3. **links the artifacts** produced — test cases, test runs, recordings, reports

There is no delivery-report template and no testing-report template. A comment plus artifact links does the same job, and a template nobody has time to complete is a template nobody completes.

**QA closes the ticket. There is no requester acceptance step.** A ticket is Done when the testing is complete, whatever the outcome. Bugs found are raised as separate linked issues; the portal ticket does not stay open waiting on another team's fixes. A requester can **reopen within one week** if the result does not answer their question.

---

## Bugs

QA files the bugs **it finds**. QA does not file bugs on behalf of Engineering, Product Management or Support, does not verify routine fixes, and does not reproduce bugs on request.

QA does raise **BugCrowd** tickets, which consume WIP slots like any other work. Volume is externally driven and outside anyone's control.

---

## Shift-left: requirement review

An **asynchronous review**, not meeting attendance.

1. AI-assisted tooling reviews the requirement against the **SDLC definition of a complete epic**.
2. **QA reviews the tool's output.**
3. QA returns **additional questions** to the requester.
4. The clock stops while those questions are outstanding.

Two things about how this is described matter. The **human-in-the-loop step is the headline** — the deliverable is QA's judgement, not a tool's output. And the deliverable is **questions, not a verdict**: requirement review is not a pass/fail gate.

The same review underpins the priority-demotion rule, which is why QA reviews the output before any priority changes rather than acting on the tool directly.

The tooling is the `requirements-review` skill in the `AI in QA/Skills/` folder of this repository, with `templates/requirement_standard.md`. Both should check against the SDLC definition, including the target shipping date.

---

## Release process

Release work is **not portal intake**. It happens because a release is happening.

### It pre-empts portal work

- **One Release ticket** in the portal represents the effort.
- The detail lives in **linked Jira tickets, visible to everyone**.
- Release status is communicated in **[`#bp-status-release-feature`](LINK-TBC)** `[LINK TBC]`; dates are on the **[quarterly release schedule](LINK-TBC)** `[LINK TBC]`.
- Triage still runs daily, and waiting tickets still get comments.
- **Automation continues.**

### Release activities

**Test Regression (TR) and Sanity cycles** — run as part of the release, led by QA.

**Release blocker testing** — a release blocker is a bug of severity ≥ Medium raised **during Release Testing**. No bug of severity ≥ Medium is released. Severity follows the existing written rules: **[Severity rules](LINK-TBC)** `[LINK TBC]`.

### The RUM performance gate

Before a release, QA reviews the RUM event dashboards to judge whether performance has regressed.

| Owner | Responsibility |
|-------|----------------|
| **Engineering** | The RUM Events portal, the data, and fixing regressions |
| **Product Management + Engineering** | Defining the performance thresholds |
| **QA** | Reviewing the data against those thresholds before release |

**The gate blocks.** Within thresholds, the release proceeds. Below threshold:

1. QA raises a ticket to Engineering, naming the affected module and events.
2. Engineering owns the fix.
3. QA re-reviews afterwards.

Two edge cases are settled:

- A module with **no defined threshold** is recorded as **"not assessable"** — never as a pass.
- A **known regression may ship under a recorded waiver**, with the escalation ticket left open.

QA reviews the data. QA does not own the tooling and does not set the thresholds. This is the same shape as the production-issue rule and the DoD boundary: **QA assesses against criteria owned by others, and reports.**

---

## Work that arrives outside the portal

**It is not tackled. The requester is redirected, every time.**

There is no exception for small favours. A rule with a size threshold requires every engineer to estimate the work before refusing it, which is exactly the negotiation the rule exists to prevent. An absolute rule also moves the refusal from the individual to the team — which is what makes it applyable by someone sitting next to the person asking.

**Answering a question is not work.** Anything that needs an environment, a test run, or produces a result someone will act on, goes through the portal.

This protects every number these pages publish. Out-of-band work consumes the same capacity while being invisible to triage.

---

## Ownership of these pages

Maintained by the **QA Team**. Reviewed **monthly at the Team Retrospective**. First point of contact: **Marek Wyszyński**, with the whole four-person team acting as deputies — most questions are passed to whichever engineer can best answer them. When a decision is needed and the named contact is unavailable, **daily triage decides and the decision stands**.

Each page carries a version and a last-reviewed date. If a decision here is overtaken, change it at the retrospective rather than letting practice and page drift apart.
