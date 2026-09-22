# Service levels and measures

**Audience:** managers
**Maintained by:** the QA Team · **Contact:** Marek Wyszyński · **Version:** 2.0 · **Last reviewed:** 2026-09-22

---

## What QA commits to, and what it does not

| | Commitment |
|---|---|
| **Response** | Every request is read at the **next daily triage meeting — 10:00 CET every working day**. Submitted just after a meeting, that means the next business day |
| **Visibility** | Every triaged ticket gets a comment: picked up, information needed, or on hold with a reason and a point in time. **Every held ticket is reviewed again daily** |
| **Completion** | **None published.** The engineer who picks the ticket up estimates it, and communicates the estimate then |

**The absence of completion times is deliberate, not an omission.** Publishing a per-category range for work that has never been measured produces numbers the team misses and requesters quote back. The team would rather commit to a response it can guarantee and an estimate it can stand behind.

**What replaces the completion promise is a planning cycle, not silence.** Dependent teams plan against the **quarterly intake cycle** — every epic in Jira at quarter start, prepared by QA before it is requested — rather than against per-ticket estimates. That is the predictability on offer, and it is more useful than a date attached to work nobody has looked at yet.

### Consequence worth understanding

A manager planning around QA cannot read a date off this page. They can:

- see the queue and its state in the **[all QA tickets filter](LINK-TBC)** `[LINK TBC]`
- see when release freezes fall on the **[quarterly release schedule](LINK-TBC)** `[LINK TBC]`
- get an estimate as soon as an engineer takes the ticket
- rely on their epic having been read and prepared, if it was in Jira at quarter start

---

## The capacity behind it

| Fact | Value |
|------|-------|
| QA Engineers | **4 — the team will not grow beyond this** |
| Each engineer's week | **2.5 business days** portal and release work · **2.5 days** automation |
| Effective portal capacity | **2.0 FTE, release work included** |
| WIP limit per engineer | 2 tickets |
| Ceiling on work in progress | 8 tickets |
| Inflow ceiling | **8 new tickets per week in a normal week.** Above that, the excess is automatically held |
| Release cadence | Every ~2 weeks — **5 to 6 per quarter**, about a week of QA effort each |
| Intake volume | **Not yet measured** |

### What the numbers mean together

**Release work comes out of the portal half, not in addition to it.** During a freeze the portal half is entirely on release work and no requests are taken; automation continues throughout. So portal work runs at full rate in roughly half of any quarter, and the queue moves between freezes.

**The eight-per-week inflow ceiling is a peak-week figure.** Eight tickets against ten engineer-days implies about 1.25 engineer-days per ticket, which holds in a normal week. Because five or six weeks a quarter are freeze weeks with near-zero portal throughput, **sustained inflow at the ceiling would accumulate** — which is exactly what the automatic hold is for. The sustainable quarterly average is lower than eight per week, and the intake measurement below will establish what it actually is.

**The team size is fixed, so the lever is scope, not headcount.** When demand rises, work waits or scope reduces. This is stated deliberately: it is the answer to "what happens when this is not enough", and it does not end in a hiring request.

**Fix verification is a live improvement target.** Two of the roughly five days per release go on verifying fixes, and the team is actively working to reduce that. It is the clearest available lever on release cost.

---

## What the automation half produces

Half of every engineer's week, protected — including through release freezes.

**The commitment is at least one test case automated per engineer per day**: 2 to 3 test cases created or fixed per engineer per week, roughly **8 to 12 across the team**, all tracked in Jira.

This is not reserved time. It is the work that makes generalist testing possible — the documented test cases are the team's knowledge base — and the automation placeholders built at quarter start are what stop each new feature starting from zero.

---

## What is excluded from any expectation

**Release periods.** No portal requests are worked during a freeze. Requests submitted during one are triaged and told when to expect pickup.

**Time waiting on the requester.** When a ticket is returned for missing information, the clock stops and resumes when the requester replies. A blocked ticket also frees the engineer's WIP slot and returns to the queue at its existing priority.

**Scheduled work.** While training or enablement work is running, fewer engineers are available to pull, so the eight slots are not all available. This is declared at triage.

**Absolutely Critical production verification.** Rare by expectation, but it sits at the top of the queue and displaces committed work.

---

## At the ceiling

When the queue is full, each case is assessed at daily triage, and one of three things happens:

1. the deadline is negotiated with the requester
2. something already in progress is parked, with a reason and a date on the ticket
3. the new work is held, and the requester is told when to expect pickup

Past **eight new tickets in a week**, the excess is held automatically. No judgement, no negotiation — demand above capacity becomes a visible number.

Where two requesters genuinely conflict and triage cannot settle it, QA convenes an **ad-hoc session with the managers involved, together rather than separately**, and records the outcome on both tickets.

---

## What this model costs the organisation

**The cost is itemised on [QA Portal scope](02%20-%20QA%20Portal%20scope.md), in the out-of-scope list.** That list is not a statement of preference — it is the work that had to stop for a four-person team to run this way. Filing bugs for other people, routine fix verification, bug reproduction, support ticket review, instance creation as a service, the observability dashboards, business questions.

Each entry either ceases or is absorbed by another team, and page 2 says which. It is meant to be read as a bill and challenged item by item, rather than accepted as a boundary.

---

## Risks, and what is being done about them

| Risk | Mitigation |
|------|------------|
| **Demand exceeds four engineers** | The inflow ceiling is enforced automatically, so the shortfall is visible in held tickets rather than hidden in slipping dates. Intake measurement will size the gap |
| **Work bypassing the portal** | Redirected without exception, so it cannot quietly consume capacity. An absolute rule rather than a judgement call, so individual engineers can apply it |
| **Automation time squeezed by ticket load** | The split is stated in days — 2.5 of 5 — not as an intention, the WIP limit protects it, and it continues through release freezes. Output is measured weekly |
| **Uneven product knowledge across a generalist team** | Documented test cases linked on every ticket, the quarterly preparation cycle, and an objective documentation bar. Depth is knowingly traded for flow |
| **Shallower testing from lower product familiarity** | The same, plus the rule that substantially undocumented requests are deprioritised rather than tested badly |
| **Meeting overload from shift-left** | Resolved: requirement review is asynchronous, not meeting attendance |
| **Release cost crowding out request work** | Fix verification, two of five release days, is an active reduction target |
| **Key-person dependency** | A named contact with the whole team as deputies; triage is owned by the team and runs with whoever is present; when a decision is needed and the contact is away, triage decides |

The first risk has no mitigation in the usual sense, only a mechanism for making it visible. That is deliberate. A four-engineer team with a fixed size cannot mitigate insufficient capacity; it can only stop concealing it.

---

## Measurement

**Owned by the QA Team, principally Marek Wyszyński.** Reported at the **monthly Team Retrospective**, alongside the review of these pages. Measurement begins when these pages go live.

**First and most important: intake by category.** It is the precondition for any future completion commitment, the check on whether the eight-per-week ceiling is the right number, and the difference between arguing about QA capacity with data and arguing about it with impressions.

Following it:

- **time from submission to pickup** — the part of the wait requesters actually feel
- **how often the inflow ceiling is hit**, and what gets held when it is
- **how often requests are returned for missing information** — a direct measure of whether the required-information list and the quarterly cycle are working
- **automation output** against the one-test-case-per-day commitment

The provisional figures on this page are revisited once a quarter of intake data exists.

---

## Escalation

Raise it on the ticket first — triage reads every ticket daily and will respond. If that does not resolve it, **Marek Wyszyński** is the first point of contact, with the QA team as deputies.

These pages are reviewed monthly at the QA Team Retrospective. A commitment here that is not being met should be changed on the page, not quietly missed.
