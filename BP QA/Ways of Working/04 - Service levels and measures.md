# Service levels and measures

**Audience:** managers
**Maintained by:** the QA Team · **Contact:** Marek Wyszyński · **Version:** 2.1 (draft for review) · **Last reviewed:** 2026-09-22

> **This page is the source of truth for every number in the collection.** The other pages explain consequences and link here rather than restating figures.

---

## What QA commits to, and what it does not

| | Commitment |
|---|---|
| **Response** | Every request is read at the **next daily triage meeting — 10:00 CET every working day**. Submitted just after a meeting, that means the next business day |
| **Visibility** | Every triaged ticket gets a comment: picked up, information needed, or on hold with a reason. **Every held ticket is reviewed again daily**, and at four weeks QA comes back to the requester |
| **A date per ticket** | Once an engineer picks the ticket up, QA gives **a completion time in business days and a delivery date** |
| **A published completion time** | **None.** There is no per-category SLA, and there will not be one until intake has been measured |

**The distinction in the last two rows is the whole of QA's position on delivery**, and it is easy to misread. QA declines to publish a completion time *in advance of reading the work*. It does commit to a date *once it has*.

**Why no published SLA.** Publishing a per-category range for work that has never been measured produces numbers the team misses and requesters quote back. A response QA can guarantee and a date it can stand behind are worth more than a range it cannot.

**What replaces it is a planning cycle, not silence.** Dependent teams plan against the **quarterly intake cycle** — epics in Jira at quarter start, prepared by QA before they are requested — rather than against per-ticket estimates.

### The estimate is elapsed time, not effort

This is stated plainly because it is the single most likely thing to cause a dispute on a ticket.

Each engineer runs **two tickets at a time** and spends **half the week** on portal and release work. A ticket in progress therefore receives roughly **1.25 engineer-days per week**. Three days of effort is around **two and a half weeks of calendar time**, and longer if a release freeze falls inside it.

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
| When no slot is free | New work goes **On hold**, with the reason |
| Sustainable inflow | **About 8 new tickets per week in a normal week** — a planning figure, not a rule |
| Release cadence | Every ~2 weeks — **5 to 6 per quarter** |
| Cost per release | **About one week of the portal-and-release half** |
| Intake volume | **Not yet measured** |

### What the numbers mean together

**The hold mechanism is slot-based, not a weekly count.** A ticket waits when there is no free slot. That needs no counting, is automatically correct during a freeze and while scheduled work is running, and is **verifiable by the requester** against the QA work project. The eight-per-week figure describes what the team can sustain; it is not the rule that fires.

**Release work comes out of the portal half, not in addition to it.** A release costs about one week of that half — roughly two days of release testing and two of fix verification, with the team working in parallel. During a freeze no requests are taken; automation continues throughout. So portal work runs at full rate in roughly half of any quarter, and the queue moves between freezes.

**CI is not in these figures**, because CI is not QA work. The only CI activity in a release is triggering the builds. Pipeline troubleshooting and CI requests are DevOps.

**The team size is fixed, so the lever is scope, not headcount.** When demand rises, work waits or scope reduces. This is the answer to "what happens when this is not enough", and it does not end in a hiring request.

**Fix verification is a live improvement target.** Two of the roughly four days per release go on verifying fixes, and the team is actively working to reduce that. It is the clearest available lever on release cost.

### The assumption underneath the eight

Eight tickets a week against ten engineer-days implies **about 1.25 engineer-days per request**. That is an assumed average ticket size, and **it has never been measured**. A feature test is plainly larger than that, so the true sustainable figure may be materially lower.

This is stated rather than left to be derived, because it is the weakest number on the page and it is exactly what intake measurement exists to settle. **The assumption is revisited at the end of the year**, once a quarter of real data exists. No quarterly throughput total is published until then — it would be read as a commitment, and the assumption underneath it has not been earned.

---

## What the automation half produces

Half of every engineer's week, protected — including through release freezes.

**The commitment is at least one test case automated per automation day**: 2 to 3 test cases created or fixed per engineer per week, all tracked in Jira.

This is not reserved time. It is the work that makes generalist testing possible — the documented test cases are the team's knowledge base — and the automation placeholders built at quarter start are what stop each new feature starting from zero.

---

## What is excluded from any expectation

**Release periods.** No portal requests are worked during a freeze. Requests submitted during one are triaged and told when to expect pickup.

**Time waiting on the requester.** When a ticket is returned for missing information, the clock stops and resumes when the requester replies.

**Time on hold.** A held ticket's clock is paused. A ticket blocked mid-flight goes On hold, frees the slot, and returns to the queue at its existing priority.

**Scheduled work.** While training or enablement work is running, fewer engineers are available to pull, so not all slots are available. This is declared at triage.

**Absolutely Critical production verification.** Rare by expectation, but it sits at the top of the queue and displaces committed work.

---

## When the queue is full

Each case is assessed at daily triage, and one of three things happens:

1. the deadline is negotiated with the requester
2. something already in progress is parked, with a reason and a date on the ticket
3. the new work goes On hold, and the requester is told when to expect pickup

**Holds are not open-ended.** At four weeks QA returns to the requester: a hold on work that is progressing continues, and a hold with no progress on the engineering side is **closed after contacting the requester**, to be resubmitted when the work is ready.

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
| **Work bypassing the portal** | Redirected without exception, so it cannot quietly consume capacity. An absolute rule rather than a judgement call, so individual engineers can apply it |
| **Automation time squeezed by ticket load** | The split is stated in days — 2.5 of 5 — not as an intention, the WIP limit protects it, and it continues through release freezes. Output is measured weekly |
| **Uneven product knowledge across a generalist team** | Documented test cases linked on every ticket, the quarterly preparation cycle, and an objective documentation bar. Depth is knowingly traded for flow |
| **Shallower testing from lower product familiarity** | The same, plus the rule that substantially undocumented requests are deprioritised rather than tested badly |
| **Meeting overload from shift-left** | Resolved: requirement review is asynchronous, not meeting attendance |
| **Release cost crowding out request work** | Fix verification, about half the release cost, is an active reduction target. CI work has moved out of QA scope entirely |
| **Key-person dependency** | A named contact with the whole team as deputies; triage is owned by the team and runs with whoever is present; when a decision is needed and the contact is away, triage decides |

The first risk has no mitigation in the usual sense, only a mechanism for making it visible. That is deliberate. A four-engineer team cannot mitigate insufficient capacity; it can only stop concealing it.

---

## What this model costs the organisation

**The cost is itemised on [QA Portal scope](02%20-%20QA%20Portal%20scope.md), in the out-of-scope list.** That list is not a statement of preference — it is the work that had to stop for a four-person team to run this way. Filing bugs for other people, routine fix verification, bug reproduction, support ticket review, instance creation as a service, CI work, the observability dashboards, business questions.

Each entry either ceases or is absorbed by another team, and page 2 says which. It is meant to be read as a bill and challenged item by item, rather than accepted as a boundary.

---

## Measurement

**Owned by the QA Team, principally Marek Wyszyński.** Reported at the **monthly Team Retrospective**, alongside the review of these pages. Measurement begins when these pages go live.

**First and most important: intake by category, and average ticket size.** Together they are the precondition for any future completion commitment, the check on whether eight per week is the right figure, and the difference between arguing about QA capacity with data and arguing about it with impressions.

Following those:

- **time from submission to pickup** — the part of the wait requesters actually feel
- **how often the queue is full**, and what goes On hold when it is
- **how many holds reach four weeks**, and how they resolve
- **how often requests are returned for missing information** — a direct measure of whether the required-information list and the quarterly cycle are working
- **automation output** against the one-test-case-per-automation-day commitment

The provisional figures on this page are revisited once a quarter of intake data exists, and the ticket-size assumption at the end of the year.

---

## Escalation, and changing these pages

Raise it on the ticket first — triage reads every ticket daily and will respond. Then **Marek Wyszyński**, with the QA team as deputies. If it cannot be resolved with QA, it goes to the **Senior QA Manager**, and then the **SW Director for BigPicture**.

**To propose a change to these pages,** submit it through the QA Portal. It is read at triage like anything else, and changes are made at the monthly review and published with a new version number.

A commitment here that is not being met should be changed on the page, not quietly missed.
