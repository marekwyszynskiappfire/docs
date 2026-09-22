# How the QA team works

**Audience:** the QA team and managers
**Maintained by:** the QA Team · **Contact:** Marek Wyszyński · **Version:** 2.1 (draft for review) · **Last reviewed:** 2026-09-22
**Reviewed with:** Product Management `[date TBC]` · Engineering `[date TBC]` · Support `[date TBC]`

---

## The operating principle

**The team is four engineers, and the model is built for that size.** It does not assume growth.

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

**Epics, initiatives and new features** should be defined and delivered to QA as Jira items at the start of the quarter. QA then:

1. feeds them through the requirement review tooling
2. reviews the output and sends the gaps back to the authors
3. prepares test scenarios
4. creates automation placeholders

By the time a request arrives, the team has read the epic, knows what is missing, and has somewhere for the automation to go.

**This is about preparation, not eligibility.** Other categories arrive mid-quarter as ordinary business. The one case the team pushes back on is a **large epic arriving mid-quarter with an ETA of about a week** — the preparation cannot be compressed into that lead time, so QA says what it can deliver and by when, and the conversation is about the date or the scope.

### Fortnightly — the release cycle

A release roughly **every two weeks**, following the **[quarterly release schedule](LINK-TBC)** `[LINK TBC]`.

| Per release | |
|-------------|---|
| Release testing | ~2 days |
| Verification of fixes | ~2 days — **actively being reduced** |
| Triggering the release builds on CI | minor, inside the above |
| **Team capacity consumed** | **about one week of the portal-and-release half** |

**During a freeze, no portal requests are worked. Automation continues.** That distinction matters: the automation half of the team's time is protected even here.

Portal work therefore happens **between freezes**, and that is the single most useful thing for a requester to understand about timing.

> **CI is not QA work.** The only CI activity in a release is triggering the builds. Troubleshooting the pipeline, fixing agents and handling CI requests are DevOps. QA does keep its **own failing automated tests** — that is QA's test code, and it sits in the automation half.

---

## Capacity

The figures are on **[Service levels and measures](04%20-%20Service%20levels%20and%20measures.md)**, which is the source of truth for every number in this collection. What matters operationally:

- Each engineer splits the week **half portal and release work, half automation**.
- **Two tickets at a time** per engineer, because everyone also automates test cases daily.
- **When no slot is free, new work goes On hold.** That is the whole mechanism — no counting, and it is automatically right during freezes and while scheduled work is running.

**The slot rule is what protects everything else.** It needs no judgement, no negotiation and no meeting, and it makes demand above capacity a visible number rather than an argument QA has to win.

---

## Daily triage

**Every working day, 10:00 CET.** Owned by the team, not by a chair, so it runs with whoever is present. The whole team operates in CET, which is what the response commitment is measured in.

At triage the team:

1. reads every new request and checks it has the required information
2. sets or re-assesses priority
3. orders the queue
4. **reviews every held ticket**
5. comments on every triaged ticket

### Every triaged ticket gets a comment

One of three, always:

| Outcome | Comment says |
|---------|--------------|
| **Picked up** | An engineer has taken it |
| **Incomplete** | Exactly what information is missing. The clock stops |
| **On hold** | The reason, and what it is waiting for. **The clock is paused** |

Three things cause a hold: the **work cannot start yet**, **no slot is free**, or the ticket is **blocked on someone else**. The first is the commonest, since epics arrive at quarter start for features that ship later — the hold list is the team's forward book, not a pile of problems.

**There is never silence from QA.** Triage runs even during a release, when the only outcome may be adding comments to waiting tickets.

### The four-week horizon

Held tickets are reviewed daily, but a hold is not open-ended. **At four weeks QA goes back to the requester:**

- if the work is **progressing and simply not ready**, the hold continues — this is the forward book working as designed
- if there has been **no progress on the engineering side**, QA contacts the requester and **closes the ticket**

Closure is not a refusal; the work is resubmitted when it is ready. This keeps the hold list an honest number rather than somewhere requests accumulate, and a "no" at four weeks costs far less than one at twelve.

---

## How work is taken on

**Pull, with no assignment by anyone** — not Engineering, not Product Management, not the QA lead.

- Queue items have **no assignee until pulled**.
- Engineers take the **highest-priority** ticket they have capacity for.
- **Two tickets maximum** in progress per engineer.
- **A blocked ticket goes On hold, which frees the slot.** The assignee comes off, the ticket keeps its priority, and whoever has capacity picks it up when the blocker clears. QA does not hold capacity idle waiting on other teams' response times.

### Priority

The standard Jira scale. Every request arrives at **Medium**; requesters cannot raise it.

| Level | When |
|-------|------|
| **High / Highest** | Release-related work; absolutely Critical production issues needing QA verification |
| **Medium** (default) | Everything else, ordered by **"Needed by…"** |
| **Lowered** | The epic is substantially incomplete against the **[SDLC definition](LINK-TBC)** `[LINK TBC]`, or the **target date in the epic** shows the feature is not shipping soon |

Neither demotion reason is QA's judgement: one is checked by the requirement review tooling against a published standard, the other is a documented attribute of the epic. Both are **recorded as a ticket comment naming what is missing**, and **supplying it restores priority**.

### Estimates

An engineer estimates the work **when they pick it up**, and QA gives the requester **a completion time in business days and a delivery date** — for example, *"10 business days, delivered by 6 October"*.

**The estimate is elapsed time, not effort.** It accounts for the engineer's other ticket and for any release freeze in the window. With two tickets in progress and half a week on portal work, a ticket in progress receives roughly a day and a quarter a week, so three days of effort is around two and a half weeks of calendar time. The pages say this openly, because the alternative is discovering it on every ticket.

The estimate is given **by the team**, never by an individual engineer negotiating alone.

### When QA cannot meet what a requester expected

One rule, covering every case:

> QA says so **on the ticket** and opens a conversation, **as a team** — never leaving an individual engineer to negotiate alone.

That applies when nobody picks up a ticket with a tight deadline, when the queue is full and something has to wait, when an estimate does not fit the requester's date, and when a large epic arrives mid-quarter with too little lead time.

Where two requesters genuinely conflict and triage cannot settle it, QA convenes an **ad-hoc session with the managers involved — together, not separately** — and records the outcome on both tickets.

### The clock

The response clock runs on **CET working days**, and the team's public holidays move it. It **stops** when a ticket is returned for missing information, and **pauses while a ticket is On hold**.

---

## Automation

Half of every engineer's week and it is protected, including through release freezes.

**The commitment: at least one test case automated per automation day**, which comes to **2 to 3 test cases created or fixed each week per engineer**. All of it is tracked in Jira.

This is not reserved time with no output. The test cases it produces are what makes generalist working possible, and the automation placeholders created at quarter start are what stop each new feature starting from zero.

---

## Delivering and closing

At completion, QA:

1. **closes the ticket as Done**
2. leaves a **comment** explaining what was tested and the result
3. **links the artifacts** produced — test cases, test runs, recordings, reports

There is no delivery-report template and no testing-report template. A comment plus artifact links does the same job, and a template nobody has time to complete is a template nobody completes.

**QA closes the ticket. There is no requester acceptance step.** A ticket is Done when the testing is complete, whatever the outcome. Bugs found are raised as separate linked issues; the portal ticket does not stay open waiting on another team's fixes. A requester can **reopen within one week** if the result does not answer their question.

---

## Bugs

QA files the bugs **it finds**. QA does not file bugs on behalf of Engineering, Product Management or Support, does not verify routine fixes, and does not reproduce bugs on request.

QA does raise **BugCrowd** tickets, which consume slots like any other work. Volume is externally driven and outside anyone's control.

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
- The detail lives in **linked Jira tickets**, visible in the **[QA work Jira project](LINK-TBC)** `[LINK TBC]`.
- Release status is communicated in **[`#bp-status-release-feature`](LINK-TBC)** `[LINK TBC]`; dates are on the **[quarterly release schedule](LINK-TBC)** `[LINK TBC]`.
- Triage still runs daily, and waiting tickets still get comments.
- **Automation continues.**

### Release activities

**Test Regression (TR) and Sanity cycles** — run as part of the release, led by QA.

**Release blocker testing** — a release blocker is a bug of severity ≥ Medium raised **during Release Testing**. Severity follows the **[existing written rules](LINK-TBC)** `[LINK TBC]`, which are owned outside QA and define what blocks a release. **A release does not go out with a blocker open, and there is no waiver.**

### The RUM performance gate

Before a release, QA reviews the RUM event dashboards to judge whether performance has regressed.

| Owner | Responsibility |
|-------|----------------|
| **Engineering** | The RUM Events portal, the data, and fixing regressions |
| **Product Management + Engineering** | Defining the performance thresholds |
| **QA** | Reviewing the data against those thresholds before release |

**The gate blocks, with no exception.** Within thresholds, the release proceeds. Below threshold:

1. QA raises a ticket to Engineering, naming the affected module and events.
2. Engineering owns the fix.
3. QA re-reviews afterwards, and the release waits.

One edge case: a module with **no defined threshold** is recorded as **"not assessable"** — never as a pass.

QA reviews the data. QA does not own the tooling and does not set the thresholds. This is the same shape as the production-issue rule and the DoD boundary: **QA assesses against criteria owned by others, and reports.**

---

## Work that arrives outside the portal

**It is not tackled. The requester is redirected, every time.**

There is no exception for small favours. A rule with a size threshold requires every engineer to estimate the work before refusing it, which is exactly the negotiation the rule exists to prevent. An absolute rule also moves the refusal from the individual to the team — which is what makes it applyable by someone sitting next to the person asking.

**Answering a question is not work.** Anything that needs an environment, a test run, or produces a result someone will act on, goes through the portal.

This protects every number these pages publish. Out-of-band work consumes the same capacity while being invisible to triage.

---

## Ownership of these pages

Maintained by the **QA Team**. Reviewed **monthly at the Team Retrospective**. First point of contact: **Marek Wyszyński**, with the whole team acting as deputies. When a decision is needed and the named contact is unavailable, **daily triage decides and the decision stands**.

**Escalation beyond QA:** the **Senior QA Manager**, then the **SW Director for BigPicture**.

**Proposing a change:** submit it through the QA Portal. Changes are made at the monthly review and published with a new version number.
