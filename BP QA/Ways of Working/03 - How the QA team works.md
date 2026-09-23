# How the QA team works

**Audience:** the QA team and managers
**Maintained by:** the QA Team · **Contact:** the Manager of the BP QA Team · **Version:** 3.0 (draft for review) · **Last reviewed:** 2026-09-23
**Reviewed with:** Product Management `[date TBC]` · Engineering `[date TBC]` · Support `[date TBC]`

---

## The operating principle

**The team is four engineers, and the model is built for that size.** It does not assume growth.

**QA runs as a service.** Work is requested, queued and pulled; engineers are not allocated to teams or products, and requests for dedicated or embedded QA are declined. One engineer assigned permanently to a single team is a quarter of the organisation's QA capacity removed from everyone else.

Four people cannot divide the product into owned areas, so the team is **generalist by necessity**: any engineer can pick up any request, and nobody owns a domain.

The mitigation for the depth this costs is not "everyone learns everything". It is to **reduce the knowledge a piece of work requires**:

| Mechanism | How it lowers the bar |
|-----------|----------------------|
| Documented test cases, linked on every ticket | Knowledge lives in artifacts, not in individuals |
| A clear description of the feature, judged against the SDLC standard | The request carries its own context |
| AI-assisted requirement review, with QA reviewing the output | The first pass does not depend on familiarity |
| Preparation before testing starts | Nobody meets an epic for the first time when the testing begins |
| A required handover note when an engineer comes off a ticket | The one case where knowledge would otherwise sit in someone's head |

This explains a rule that otherwise looks bureaucratic: **requests with substantially incomplete documentation are deprioritised**. Incomplete documentation is the single input that shared knowledge cannot compensate for. The model protects the thing it depends on.

**It is a trade, and worth naming as one.** Depth is exchanged for flow. The model holds while requirements are good; where they are not, the demotion rule is the release valve.

---

## Two rhythms

The team runs on a quarterly cycle and a fortnightly one at the same time. Neither is an interruption to the other; together they are the operating pattern.

### Quarterly — intake and preparation

**Everything starts from a portal request.** QA does not review epics that nobody has asked about, and does not take work from any other channel.

**Epic-related requests go through the requirement tooling whenever they arrive.** QA then:

1. feeds the requirement through the review tooling
2. reviews the output and sends the gaps back to the author
3. prepares test scenarios
4. creates automation placeholders

**Submitting early is strongly advocated but it is not a gate.** The earlier a request arrives, the more of this preparation can happen before the deadline closes in, and the sooner it is in the queue.

**The one case the team pushes back on** is a **large epic arriving mid-quarter with an ETA of about a week** — the preparation cannot be compressed into that lead time, so QA says what it can deliver and by when, and the conversation is about the date or the scope.

### Fortnightly — the release cycle

A release roughly **every two weeks**, following the **[quarterly release schedule](LINK-TBC)** `[LINK TBC]`. A freeze runs **3 to 5 working days**; the team plans on five.

**During a freeze the entire portal-and-release half goes to the release.** No new portal requests are picked up. Automation time is protected.

Across a quarter that closes **about a third** of the working days to new pickups — five to six releases at three to five days each. Portal work happens between freezes, and that is the single most useful thing for a requester to understand about timing.

The figures are on **[Service levels and measures](04%20-%20Service%20levels%20and%20measures.md)**, which is the source of truth for every number in this collection.

> **CI is not QA work.** The only CI activity in a release is triggering the builds. Troubleshooting the pipeline, fixing agents and handling CI requests are DevOps. QA keeps its **own failing automated tests** — with one exception, below: analysing failing e2e runs during a release is release work.

---

## Capacity

- Each engineer splits the week **half portal and release work, half automation**.
- **Two tickets at a time** per engineer, because everyone also automates test cases daily.
- **When no slot is free, new work goes On Hold.** That is the whole mechanism — no counting, and it is automatically right during freezes and while scheduled work is running.
- **QA's own work has ceilings too:** at most one engineer on scheduled work at a time, and at most two of the eight slots on BugCrowd before triage escalates.

**The slot rule is what protects everything else.** It needs no judgement, no negotiation and no meeting, and it makes demand above capacity a visible number rather than an argument QA has to win.

---

## Daily triage

**Every working day, 10:00 CET.** Owned by the team, not by a chair, so it runs with whoever is present. The whole team operates in CET, which is what the response commitment is measured in, and the team's public holidays move it.

**Quorum is two.** Below that, new requests still get their comment, but priority decisions wait until the next day. A decision made by one engineer alone is not the team position the rules on these pages depend on.

**When the room disagrees**, it goes to the Manager of the BP QA Team. If they are away, the decision waits a day rather than being taken alone.

At triage the team:

1. reads every new request and checks it has the required information
2. corrects Urgency where the work does not fit it
3. sets or re-assesses priority
4. orders the queue
5. **reviews every held and every returned ticket**
6. comments on every triaged ticket

### Every triaged ticket gets a comment

One of four, always:

| Outcome | Comment says |
|---------|--------------|
| **Picked up** | An engineer has taken it |
| **Urgency corrected** | The work does not fit the Urgency chosen, what does, and why |
| **Awaiting info from Requestor** | Exactly what information is missing. The clock stops |
| **On Hold** | The reason, and what it is waiting for. **The clock is paused** |

Four things cause a hold: **a release is running**, the **work cannot start yet**, **no slot is free**, or the ticket is **blocked on someone else**.

**There is never silence from QA.** Triage runs even during a release, when the only outcome may be adding comments to waiting tickets. Slippages, blockers and displaced work are always communicated on the ticket, at the latest at the next day's triage.

### The four-week horizon

Held and returned tickets are reviewed daily, but neither state is open-ended. **At four weeks QA goes back to the requester:**

- if the work is **progressing and simply not ready**, the wait continues
- if there has been **no progress**, QA contacts the requester and **closes the ticket**

Closure is not a refusal; the work is resubmitted when it is ready. This keeps the hold list an honest number rather than somewhere requests accumulate, and a "no" at four weeks costs far less than one at twelve.

---

## How work is taken on

**Pull, with no assignment by anyone** — not Engineering, not Product Management, not the QA lead.

- Queue items have **no assignee until pulled**.
- Engineers take the **highest-priority** ticket they have capacity for.
- **Two tickets maximum** in progress per engineer.
- **A blocked ticket goes On Hold, which frees the slot.** The assignee comes off, the ticket keeps its priority, and whoever has capacity picks it up when the blocker clears. QA does not hold capacity idle waiting on other teams' response times.
- **Coming off a ticket requires a handover note** on the ticket: what was done, what was ruled out, what environment exists. The next engineer resumes rather than restarts.

### Urgency and the resolution SLA

**Urgency is mandatory on every request** — 48 hours, a week, two weeks or a month — and it sets a **time-to-resolution SLA** visible to the requester. It is also the main determinant of ordering among everything at Medium.

**Triage corrects Urgency where the work does not fit it**, records the reason, and tells the requester. That correction is the only ration on the field: anyone can select 48 hours, so the control is the team's correction rather than a restriction on the form.

The SLA is paused in **On Hold** and **Awaiting info from Requestor**, so it measures time from being workable to resolution. Page 4 explains why that makes attainment insufficient on its own as a measure.

### Priority

The standard Jira scale. Every request arrives at **Medium**; requesters cannot raise it.

| Level | When |
|-------|------|
| **High / Highest** | Release-related work; absolutely Critical production issues needing QA verification |
| **Medium** (default) | Everything else, ordered by **Urgency** |
| **Lowered** | The epic is substantially incomplete against the **[SDLC definition](LINK-TBC)** `[LINK TBC]`, or the **Planned release date** shows the feature is not shipping soon |

Neither demotion reason is QA's judgement: one is checked by the requirement review tooling against a published standard, the other is a documented attribute of the request. Both are **recorded as a ticket comment naming what is missing**, and **supplying it restores priority**.

**A requester who disagrees** raises it on the ticket; triage settles it, and it escalates to the Manager of the BP QA Team if triage cannot. Where the planned release date is the issue, the fix is to correct the date — QA follows the field rather than arguing about it.

> The Planned release date on the request and the target date in the epic **must match**. The requester updates both when the plan moves, and the four-week review is the backstop. **Where they disagree, QA works to the later date.**

### Estimates

An engineer estimates the work **when they pick it up**, and QA gives the requester **a completion time in business days and a delivery date** — for example, *"10 business days, delivered by 6 October"*.

**The estimate is elapsed time, not effort.** It accounts for the engineer's other ticket and for any release freeze in the window. With two tickets in progress and half a week on portal work, a ticket in progress receives roughly a day and a quarter a week, so three days of effort is around two and a half weeks of calendar time.

The estimate is given **by the team**, never by an individual engineer negotiating alone. **Where a hold makes the date unachievable it is pushed out, and the requester is told.**

### When QA cannot meet what a requester expected

One rule, covering every case:

> QA says so **on the ticket** and opens a conversation, **as a team** — never leaving an individual engineer to negotiate alone.

That applies when nobody picks up a ticket with a tight deadline, when the queue is full and something has to wait, when an estimate does not fit the requester's date, when Urgency has to be corrected, and when a large epic arrives mid-quarter with too little lead time.

Where two requesters genuinely conflict and triage cannot settle it, QA convenes an **ad-hoc session with the managers involved — together, not separately** — and records the outcome on both tickets.

---

## Automation

Half of every engineer's week and it is protected, including through release freezes.

**The commitment: at least one test case automated per automation day**, which comes to **2 to 3 test cases created or fixed each week per engineer**. All of it is tracked in Jira.

**Output is lower in freeze weeks** — the time is protected but the release takes the attention around it, and e2e analysis during a release counts as release work. Each release also produces a batch of test-fix work items that land in the automation half afterwards. This improves as more of the release work is automated.

This is not reserved time with no output. The test cases it produces are what makes generalist working possible, and the automation placeholders created during preparation are what stop each new feature starting from zero.

---

## Delivering and closing

At completion, QA:

1. **closes the ticket as Done**
2. leaves a **comment** explaining what was tested and the result
3. **links the artifacts** produced — test cases, test runs, recordings, reports

There is no delivery-report template and no testing-report template. A comment plus artifact links does the same job, and a template nobody has time to complete is a template nobody completes.

**QA closes the ticket. There is no requester acceptance step.** A ticket is Done when the testing is complete, whatever the outcome. Bugs found are raised as separate linked issues; the portal ticket does not stay open waiting on another team's fixes.

**A requester can reopen within one week** if the result does not answer their question. A reopened ticket goes back to the original engineer where possible — triage may redirect it — takes a slot, keeps its original priority and Urgency, and gets a new date. If no slot is free it waits like anything else. The window is a right to reopen, not a promise of speed.

---

## Bugs

QA files the bugs **it finds**. QA does not file bugs on behalf of Engineering, Product Management or Support, does not verify routine fixes, and does not reproduce bugs on request.

QA does raise **BugCrowd** tickets, which consume slots like any other work, up to the stated ceiling of two of eight.

---

## Shift-left: requirement review

An **asynchronous review**, not meeting attendance, and it starts from a request like everything else.

1. AI-assisted tooling reviews the requirement against the **SDLC definition of a complete epic**.
2. **QA reviews the tool's output.**
3. QA returns **additional questions** to the requester.
4. The clock stops while those questions are outstanding.

Two things about how this is described matter. The **human-in-the-loop step is the headline** — the deliverable is QA's judgement, not a tool's output. And the deliverable is **questions, not a verdict**: requirement review is not a pass/fail gate.

The same review underpins the priority-demotion rule, which is why QA reviews the output before any priority changes rather than acting on the tool directly.

The tooling is the `requirements-review` skill in the `AI in QA/Skills/` folder of this repository, with `templates/requirement_standard.md`. Both check against the SDLC definition, including the planned release date.

---

## Release process

Release work is **not portal intake**. It happens because a release is happening.

### It pre-empts portal work

- **One Release ticket** in the portal represents the effort.
- The detail lives in **linked Jira tickets**, visible in the **[QA work Jira project](LINK-TBC)** `[LINK TBC]`.
- Release status is communicated in **[`#bp-status-release-feature`](LINK-TBC)** `[LINK TBC]`; dates are on the **[quarterly release schedule](LINK-TBC)** `[LINK TBC]`.
- New requests are accepted, triaged and placed **On Hold**. The portal is never closed to submission.
- Triage still runs daily, and waiting tickets still get comments.
- **Automation time continues.**

### What a release consists of

The freeze runs **3 to 5 working days** and consumes the **whole portal-and-release half** of the team's week. It is not two activities but a sequence of them:

- preparing environments
- **Test Regression (TR) and Sanity cycles**, led by QA
- triggering the software builds on CI
- **triggering the canary release**
- running e2e tests and **analysing their output** — release work, not automation work
- **reviewing the RUM event dashboards** a couple of days into the canary
- verifying fixes and re-releasing to test environments
- maintaining the Jira record of the release
- communicating with stakeholders throughout
- **recommending go/no-go**, then telling DevOps to proceed with the worldwide rollout

**What makes a freeze three days rather than five:** how many issues are found, how many fix-and-verify cycles they take, how many re-releases to test environments are needed, and how many e2e tests fail and how long the analysis takes.

**Broken test cases found during a release are not fixed during the freeze.** Work items are raised and the fixes land in the automation half afterwards.

### Release blockers

**Release Testing means the whole freeze window** — from the start of release testing to the worldwide rollout. A bug of **severity ≥ Medium raised anywhere in that window, by anyone**, is a release blocker. Who found it and which activity surfaced it do not matter; the window does.

Severity follows the **[existing written rules](LINK-TBC)** `[LINK TBC]`, which are owned outside QA. **QA recommends no-go while a blocker is open.**

### The canary and the RUM performance gate

QA triggers the canary release, waits a couple of days for real usage to accumulate, and reviews the RUM event dashboards to judge whether performance has regressed.

| Owner | Responsibility |
|-------|----------------|
| **Engineering** | The RUM Events portal, the data, and fixing regressions |
| **Product Management + Engineering** | Defining the performance thresholds |
| **QA** | Reviewing the data against those thresholds, and recommending |

Within thresholds, QA recommends proceeding. Below threshold:

1. QA raises a ticket to Engineering, naming the affected module and events.
2. Engineering owns the fix.
3. QA re-reviews afterwards, and **recommends no-go** in the meantime.

**A module with no result is recorded as "not assessable" — never as a pass — and it does not block.** Two different things produce it, and they are recorded separately:

| Cause | What it means |
|-------|---------------|
| **No canary traffic** through that module | Normal. Nobody exercised it during the canary window |
| **No threshold defined** | Outstanding work for Product Management and Engineering. Reported at the monthly review |

### Who decides

**QA recommends. Product Management and Engineering decide**, including whether to release against a QA no-go. That decision is **explicit and recorded against the release**.

QA reviews the data, applies published criteria and presses the button it is told to press. It does not own the tooling, set the thresholds, or make the call. **QA holds the trigger, not the discretion** — the same shape as the production-issue rule and the DoD boundary.

---

## Work that arrives outside the portal

**It is not tackled. The requester is redirected, every time.**

There is no exception for small favours. A rule with a size threshold requires every engineer to estimate the work before refusing it, which is exactly the negotiation the rule exists to prevent. An absolute rule also moves the refusal from the individual to the team — which is what makes it applyable by someone sitting next to the person asking.

**Answering a question is not work.** Anything that needs an environment, a test run, or produces a result someone will act on, goes through the portal.

**Feedback on these pages is the deliberate exception.** It needs no environment and produces nothing anyone acts on, so it goes directly to the Manager of the BP QA Team rather than through the portal.

This protects every number these pages publish. Out-of-band work consumes the same capacity while being invisible to triage.

---

## Ownership of these pages

Maintained by the **QA Team**. Reviewed **monthly at the Team Retrospective**. First point of contact: the **Manager of the BP QA Team**, with the whole team acting as deputies. When a decision is needed and that role is unavailable, daily triage decides — except a priority call below quorum, which waits a day.

**Escalation beyond QA:** the **Senior QA Manager**, then the **SW Director for BigPicture**.

**Proposing a change:** contact the Manager of the BP QA Team. Change proposals do not go through the QA Portal. Changes are made at the monthly review and published with a new version number.
