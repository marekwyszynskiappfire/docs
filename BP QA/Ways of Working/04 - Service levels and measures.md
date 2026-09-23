# Service levels and measures

**Audience:** managers
**Maintained by:** the QA Team · **Contact:** the Manager of the BP QA Team · **Version:** 3.0 (draft for review) · **Last reviewed:** 2026-09-23

> **This page is the source of truth for every number in the collection.** The other pages explain consequences and link here rather than restating figures.

---

## QA as a Service

**BP QA is a service, not a pool of people to allocate.** Work is requested, queued and delivered; engineers are not assigned to teams, products or projects.

**Staffing is out of scope.** Requests for a dedicated QA engineer, an embedded tester, or QA capacity reserved for one team are declined by the team without negotiation. There is no route to buy priority with headcount, and there is no route to acquire a person.

This is the frame for everything below. The capacity is shared, it is finite, and the only lever on it is scope.

---

## What QA commits to

| | Commitment |
|---|---|
| **Response** | Every request is read at the **next daily triage — 10:00 CET every working day**. Submitted just after a meeting, that means the next business day |
| **Visibility** | Every triaged ticket gets a comment: picked up, information needed, on hold with a reason, or Urgency corrected. **Every held and every returned ticket is reviewed again daily**, and at four weeks QA comes back to the requester |
| **A resolution SLA** | Set by the **Urgency** field on the request, and **corrected at triage where it does not fit the work**. See below |
| **A date per ticket** | Once an engineer picks the ticket up, QA gives **a completion time in business days and a delivery date** |
| **No silence** | Slippages, blockers and missed dates are always communicated on the ticket, at the latest at the next day's triage |

---

## The resolution SLA

**Urgency is mandatory on every request**, with four values: **48 hours**, **a week**, **two weeks**, **a month**. It drives a **time-to-resolution SLA**, and the countdown is visible to the requester on their own ticket.

**Urgency is also the main determinant of how work is ordered** among everything at Medium priority.

### What each bucket actually buys

A ticket in progress receives about **1.25 engineer-days per week** — each engineer runs two tickets at a time and spends half the week on portal and release work. So:

| Urgency | Working time available |
|---------|------------------------|
| 48 hours | about **0.5 engineer-days** |
| A week | about **1.25 engineer-days** |
| Two weeks | about **2.5 engineer-days** |
| A month | about **5 engineer-days** |

The assumed average ticket is **1.25 engineer-days**, so *a week* is the average ticket with no slack at all, and *48 hours* is not deliverable for anything beyond a quick look. This is why the next section exists.

### Triage corrects Urgency

**Where the work does not fit the Urgency chosen, triage changes it**, records the reason on the ticket, and tells the requester. The corrected value is what the SLA runs against.

This is the rationing mechanism. Urgency is requester-set and unrestricted — anyone can select 48 hours — so the control is not on the form, it is the correction at triage, made by the team and visible on the ticket. An override changes the requester's commitment, so it is never silent.

### When the clock does not run

The SLA is paused in two statuses, both of which the requester can see:

| Status | Meaning |
|--------|---------|
| **On Hold** | Accepted but not being worked, with a stated reason. Reviewed daily |
| **Awaiting info from Requestor** | Returned for missing information. Reviewed daily |

So the SLA effectively measures **time from being workable to resolution**, not time from submission. That is what makes it meetable — and it is also why attainment on its own is not an honest measure of the service. See *Measurement*.

---

## The estimate is elapsed time, not effort

This is stated plainly because it is the single most likely thing to cause a dispute on a ticket.

Each engineer runs **two tickets at a time** and spends **half the week** on portal and release work, so a ticket in progress receives roughly **1.25 engineer-days per week**. Three days of effort is around **two and a half weeks of calendar time**, and longer if a release freeze falls inside it.

The estimate QA gives already accounts for this. It is given **by the team**, not by an individual engineer negotiating alone.

---

## The capacity behind it

| Fact | Value |
|------|-------|
| QA Engineers | **4.** The model is built for that size and does not assume growth |
| Each engineer's week | **2.5 business days** portal and release work · **2.5 days** automation |
| Effective portal capacity | **2.0 FTE, release work included** |
| WIP limit per engineer | 2 tickets |
| Slots available at once | 8 |
| When no slot is free | New work goes **On Hold**, with the reason |
| Sustainable inflow | **About 8 new tickets in a normal, non-freeze week** — a planning figure, not a rule |
| Release cadence | Every ~2 weeks — **5 to 6 per quarter** |
| Freeze length | **3 to 5 working days. QA plans on five** |
| Cost per release | **The whole portal-and-release half for the freeze week** |
| Quarter closed to new pickups | **About a third** |
| Intake volume | **Not yet measured** |

### What the numbers mean together

**The hold mechanism is slot-based, not a weekly count.** A ticket waits when there is no free slot. That needs no counting, is automatically correct during a freeze and while scheduled work is running, and is **verifiable by the requester** against the QA work project. The eight-per-week figure describes what the team can sustain; it is not the rule that fires.

**Release work comes out of the portal half, and during a freeze it takes all of it.** Environment preparation, release testing, Jira maintenance, releasing the software, triggering the canary, e2e runs and their analysis, the RUM review, fix verification and stakeholder communication together consume the portal-and-release half for the duration. Automation time is protected throughout.

**The team size is fixed, so the lever is scope, not headcount.** When demand rises, work waits or scope reduces. This is the answer to "what happens when this is not enough", and it does not end in a hiring request — nor in a staffing request, which QA as a Service does not accept.

**Two reduction levers are active**, both on release cost: **fix verification**, and **automating more of the release work itself**. Neither is finished.

### The assumptions underneath the numbers

Two figures on this page have never been measured, and both are named here rather than left to be derived.

**Average ticket size.** Eight tickets a week against ten engineer-days implies **about 1.25 engineer-days per request**. A feature test is plainly larger than that, so the true sustainable figure may be materially lower. It is also what every Urgency bucket above is calculated from. **Measured from go-live, revisited at the end of the year.**

**Inflow during freezes.** The eight-per-week figure is a non-freeze week rate, and it holds only because requests arriving during a freeze are expected to be almost entirely release-related, with new work parked. Demand and capacity are then measured over the same 7.5 to 9.7 non-freeze weeks a quarter — roughly 60 to 78 tickets either way. **If ordinary requests do keep arriving during freezes, quarterly demand is closer to 104 against that same capacity**, and the figure is wrong by half again. Freeze-week inflow is on the measurement list for exactly this reason.

No quarterly throughput total is published until both are measured. It would be read as a commitment, and the assumptions underneath it have not been earned.

---

## What the automation half produces

Half of every engineer's week, protected — including through release freezes.

**The commitment is at least one test case automated per automation day**: 2 to 3 test cases created or fixed per engineer per week, all tracked in Jira.

**Output is lower in freeze weeks.** The time is protected but the release consumes attention around it, and analysis of failing e2e runs during a release counts as release work rather than automation. Each release also deposits a batch of test-fix work items into the automation half afterwards. This improves as more of the release work is automated, which is one of the two active reduction levers above.

This is not reserved time. It is the work that makes generalist testing possible — the documented test cases are the team's knowledge base — and the automation placeholders built during preparation are what stop each new feature starting from zero.

---

## Ceilings on QA's own work

Two things consume the queue without being requested by anyone outside QA. Both now have a stated ceiling, and both ceilings are **escalation triggers rather than hard stops**.

| | Ceiling | What happens above it |
|---|---------|----------------------|
| **Scheduled work** (training, enablement) | **One engineer committed at a time** | Agreed at quarter start; more than one requires the Senior QA Manager |
| **BugCrowd findings** | **Two of the eight slots** | Findings are never refused, but triage escalates and comments on affected tickets rather than absorbing the squeeze silently |

---

## What is excluded from any expectation

**Release periods.** No portal requests are picked up during a freeze. Requests submitted during one are triaged and told when to expect pickup, and are placed On Hold.

**Time waiting on the requester.** A ticket returned for missing information sits in **Awaiting info from Requestor** and the SLA stops.

**Time on hold.** A held ticket's SLA is paused. A ticket blocked mid-flight goes On Hold, frees the slot, and returns to the queue at its existing priority.

**Scheduled work.** While training or enablement is running, fewer engineers are available to pull, so not all slots are available. This is declared at triage.

**Absolutely Critical production verification.** Rare by expectation, but it sits at the top of the queue and displaces committed work. **The displaced requester is always told**, and the displaced ticket's status is changed so a QA-caused delay does not consume their SLA.

---

## When the queue is full

Each case is assessed at daily triage, and one of three things happens:

1. the Urgency and the deadline are re-set with the requester
2. something already in progress is parked, with a reason and a date on the ticket
3. the new work goes On Hold, and the requester is told when to expect pickup

**Holds are not open-ended, and neither are returns.** At four weeks QA returns to the requester: work that is progressing continues to wait, and work with no progress on the engineering side is **closed after contacting the requester**, to be resubmitted when it is ready.

Where two requesters genuinely conflict and triage cannot settle it, QA convenes an **ad-hoc session with the managers involved, together rather than separately**, and records the outcome on both tickets.

---

## Seeing the work

Everything the QA team handles is tracked in a **dedicated Jira project** — portal counterparts, automation, BugCrowd findings, training preparation and release activity.

This matters more than it sounds. Requesters compete not only with each other but with QA-raised work, so a queue that looks short from the portal may be full. A capacity claim someone can check is worth several they cannot.

**[QA work — Jira project](LINK-TBC)** `[LINK TBC]`

---

## Risks, and what is being done about them

| Risk | Mitigation |
|------|------------|
| **Demand exceeds four engineers** | The slot rule holds new work automatically, so the shortfall is visible in held tickets rather than hidden in slipping dates, and the four-week horizon stops the hold list becoming a graveyard. Intake measurement will size the gap |
| **The assumed ticket size is wrong** | Stated openly above rather than buried. Measured from go-live, revisited at end of year |
| **Freeze-week inflow is not what is assumed** | Named as an assumption above, and measured from go-live. It is the difference between the published rate being right and being 40% optimistic |
| **The SLA measures what QA sets** | Attainment is published alongside three figures the team cannot adjust: end-to-end time including holds, the override rate, and time to pickup |
| **Work bypassing the portal** | Redirected without exception, so it cannot quietly consume capacity. An absolute rule rather than a judgement call, so individual engineers can apply it |
| **Automation time squeezed by ticket load** | The split is stated in days — 2.5 of 5 — not as an intention, the WIP limit protects it, and it continues through release freezes. Output is measured weekly, and is openly lower in freeze weeks |
| **QA-raised work crowding out requests** | Ceilings on scheduled work and BugCrowd, both visible in the QA work project |
| **Uneven product knowledge across a generalist team** | Documented test cases linked on every ticket, preparation before build, an objective documentation bar, and a required handover note whenever an engineer comes off a ticket. Depth is knowingly traded for flow |
| **Shallower testing from lower product familiarity** | The same, plus the rule that substantially undocumented requests are deprioritised rather than tested badly |
| **Release cost crowding out request work** | Fix verification and automating the release work are both active reduction targets. CI work has moved out of QA scope entirely |
| **Key-person dependency** | Ownership is published as roles, not names. Triage is owned by the team and runs with a quorum of two; when a decision is needed and the Manager of the BP QA Team is away, a priority decision waits a day rather than being made alone |

The first risk has no mitigation in the usual sense, only a mechanism for making it visible. That is deliberate. A four-engineer team cannot mitigate insufficient capacity; it can only stop concealing it.

---

## What this model costs the organisation

**The cost is itemised on [QA Portal scope](02%20-%20QA%20Portal%20scope.md), in the out-of-scope list.** That list is not a statement of preference — it is the work that had to stop for a four-person team to run this way. Filing bugs for other people, routine fix verification, bug reproduction, support ticket review, instance creation as a service, CI work, the observability dashboards, business questions, and dedicated QA staffing.

Each entry either ceases or is absorbed by another team, and page 2 says which. It is meant to be read as a bill and challenged item by item, rather than accepted as a boundary.

---

## Measurement

**Owned by the Manager of the BP QA Team.** Reported at the **monthly Team Retrospective**, alongside the review of these pages. Measurement begins when these pages go live.

**Four figures are published together, and they have to be**, because QA sets the target the first one is measured against:

| Measure | What it tells you |
|---------|-------------------|
| **SLA attainment** | Performance against what was agreed, after any correction |
| **Submission to resolution, including hold time** | What the requester actually lived through |
| **Override rate and direction** | How often requester expectations and capacity disagree. The clearest demand-versus-capacity signal available |
| **Submission to pickup** | Whether the queue or the work is the bottleneck |

Attainment alone would approach 100% by construction — hold time is excluded, tickets wait On Hold when no slot is free, and targets that do not fit are corrected. Published on its own it would prove nothing.

**Then, and most important for planning: intake by category, and average ticket size.** Together they are the check on whether eight per week is right, the basis for any future change to the Urgency buckets, and the difference between arguing about QA capacity with data and arguing about it with impressions.

Following those:

- **inflow during freeze weeks** — the assumption the published inflow rate depends on
- **how often the queue is full**, and what goes On Hold when it is
- **how many holds and returns reach four weeks**, and how they resolve
- **how often requests are returned for missing information** — a direct measure of whether the required-information list is working
- **automation output** against the one-test-case-per-automation-day commitment, separated into freeze and non-freeze weeks

The provisional figures on this page are revisited once a quarter of intake data exists, and the ticket-size assumption at the end of the year.

---

## Escalation, and changing these pages

Raise it on the ticket first — triage reads every ticket daily and will respond. Then the **Manager of the BP QA Team**. If it cannot be resolved with QA, it goes to the **Senior QA Manager**, and then the **SW Director for BigPicture**.

**To propose a change to these pages,** contact the Manager of the BP QA Team. Change proposals do not go through the QA Portal. Changes are made at the monthly review and published with a new version number.

A commitment here that is not being met should be changed on the page, not quietly missed.
