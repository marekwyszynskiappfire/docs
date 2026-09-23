# Requesting QA work

**Audience:** anyone who needs something from the QA team
**Maintained by:** the QA Team · **Contact:** the Manager of the BP QA Team, with the whole QA team as deputies · **Version:** 3.0 (draft for review) · **Last reviewed:** 2026-09-23

---

## In one paragraph

All QA work is requested through the **QA Portal**. Your request is read at the next daily triage meeting — 10:00 CET every working day — and you always get a comment telling you where it stands. You set an **Urgency** on the request, which sets a resolution target; QA corrects it at triage if the work does not fit, and tells you why. Once an engineer picks the ticket up you are given a **delivery date**. Requests that arrive any other way are redirected back to the portal.

**[QA Portal — submit a request](LINK-TBC)** `[LINK TBC]` · **[QA work — Jira project](LINK-TBC)** `[LINK TBC]`

---

## QA is a service, not a person you can be given

**BP QA works as a service.** You request work, it is queued, and it is delivered by whoever picks it up. Engineers are not allocated to teams or products.

**Staffing requests are declined automatically.** A dedicated QA engineer for your team, an embedded tester, or reserved QA capacity are not things the portal can provide, and asking through another route does not change the answer. The capacity is shared and the only lever on it is scope.

---

## The quarterly cycle — for features, initiatives and epics

**If you are asking QA to test a new feature, initiative or epic, submit it as early in the quarter as you can.**

QA reviews every epic-related request through its requirement tooling whenever it arrives, and does real preparation before testing starts: sends you back the gaps in the requirements, prepares test scenarios, and creates automation placeholders so the automation is not starting from zero.

**Nothing happens before you submit.** QA does not reach into Jira and prepare epics nobody has asked about — all work starts from a portal request. Submitting early does not make your work finish sooner, but it gets you into the queue before the quarter's demand builds, and it leaves room for the preparation to happen before your deadline closes in.

### Mid-quarter requests are normal

**Everything else — test design, migration testing, performance work, documentation testing — arrives mid-quarter as ordinary business** and is triaged like anything else. You are not doing something wrong by submitting in week seven.

**There is one case QA will push back on:** a **large epic arriving mid-quarter with an ETA of about a week**. Not because it arrived late, but because the preparation it depends on cannot be compressed into that lead time.

Pushing back means QA tells you **what it can deliver and by when**, and the conversation is about moving the date or reducing the scope. It is a conversation, not a refusal.

---

## Before you submit

### Is it QA work?

The short version: QA tests the product and maintains the assets used to test it. It does not run infrastructure, answer product questions, handle support tickets, or supply people. The full rule, with the borderline cases and the things QA has stopped doing, is on **[QA Portal scope](02%20-%20QA%20Portal%20scope.md)**.

### Not sure which request type?

Submit the closest match and say so in the description. Triage will reclassify it. **Guessing wrong is not a problem; not submitting is.**

---

## What your request must contain

A request missing this information is returned to you. The ticket goes to **Awaiting info from Requestor** and the clock stops until you answer.

### Everything needs

- **Urgency** — 48 hours, a week, two weeks or a month. Mandatory, and explained below
- link to the epic or dev ticket in GitHub
- Confluence documentation
- Figma design, if the work is UI-related
- feature flag names, and what each one controls if there are several
- what kind of testing you need
- which roles and permissions need to be covered
- any setup required before testing can start
- manual, automated, or both
- tests only, or documentation as well
- what you want to learn — the purpose of the testing and what counts as success
- how deep the analysis should go
- for documentation requests: who the audience is

### Feature-related requests also need

Feature testing, test automation for a feature, performance testing and shift-left requirement review also need:

- **Planned release date.** The form does not enforce it, because the form is shared across the company — but QA does. A feature-related request without it is returned
- the linked epic
- Figma design
- feature flags with descriptions
- who to contact — designer and Product Manager

### JCMA / migration testing also needs

- source Data Center version (Jira 10 or Jira 11)
- target Cloud version
- which apps are being migrated: BP, BG or BT

### Event Manager testing also needs

- the names and numbers of the environments to test

> **A note on environments.** This applies when your request targets an existing shared environment such as AAN, develop or preprod. Where testing needs a purpose-built instance, QA builds it — you do not need to prepare anything. QA does not, however, create instances for other people to use; if you need your own, the self-service instructions are in Confluence.

### The Planned release date must match the epic

The date on your request and the target date in the epic **must be the same**. If the plan moves, update both — QA will also check at the four-week review. **Where they disagree, QA works to the later of the two**, so a release pulled forward will not move your ticket up until you update it.

---

## Urgency, and what it actually buys you

**Urgency is mandatory and it sets a resolution target.** You will see the countdown on your own ticket.

| Urgency | Working time it buys |
|---------|---------------------|
| 48 hours | about half an engineer-day |
| A week | about 1.25 engineer-days |
| Two weeks | about 2.5 engineer-days |
| A month | about 5 engineer-days |

Those numbers are small for a reason, and it is worth understanding before you choose. Each engineer runs **two tickets at a time** and spends **half their week** on portal and release work, so a ticket in progress receives roughly **a day and a quarter a week**. **Work in progress is not work being worked on continuously.**

**QA corrects Urgency at triage where the work does not fit it**, records why on the ticket, and tells you. Selecting 48 hours on a two-week job does not make it a two-day job; it produces a comment explaining what is actually possible. The correction is made by the team, not by the engineer sitting nearest to you.

**Urgency is also how the queue is ordered** among everything at Medium priority, so it is worth being accurate rather than defensive.

> **Where freezes fall.** QA picks up no new portal requests for three to five working days around each release, every two weeks. **[Quarterly release schedule](LINK-TBC)** `[LINK TBC]`

> **Whose working day.** The team works in **CET**, so the clock runs on CET working days and the team's public holidays move it. Submit at 15:00 CET on Friday and your request is read on Monday morning. **[Team holiday calendar](LINK-TBC)** `[LINK TBC]`

---

## What happens after you submit

### At the next triage meeting

Every new request is read at the **daily QA triage, 10:00 CET**. Submit just after one finishes and yours is read the next working day — that is the outer bound of the commitment.

You will get a comment saying one of four things:

| You are told | What it means |
|--------------|---------------|
| **Picked up** | An engineer has taken the ticket and is working on it |
| **Urgency corrected** | The work does not fit the Urgency you chose. The comment says what does, and the new target applies |
| **Awaiting info from Requestor** | Exactly what is missing. The clock stops until you reply |
| **On Hold** | Accepted but not being worked, with the reason given. **The clock is paused** |

**Every held and every returned ticket is reviewed again every working day.** A waiting ticket is never a forgotten one.

### Why a ticket goes On Hold

Four reasons, and the comment will always say which:

| Reason | What it means |
|--------|---------------|
| **A release is running** | New requests are parked for the three to five working days of a freeze. This is the commonest reason, and it is predictable from the release schedule |
| **The work cannot start yet** | Submitted for a feature that ships later in the quarter |
| **No free slot** | Each engineer works two tickets at a time. When all eight slots are taken, new work waits |
| **Blocked on someone else** | Waiting on a fix, an environment, or a feature flag being switched on |

**On Hold is also the status used when work already in progress becomes blocked.** The ticket returns to the queue at its existing priority, the assignee comes off, and the engineer leaves a note on the ticket saying where they got to. So if you see your ticket lose its assignee, that is what happened, and a different engineer may well pick it up when the blocker clears. QA does not hold a slot idle waiting for another team. **Your delivery date is pushed out where the hold makes it necessary, and you are told.**

### Holds and returns do not last forever

**At four weeks, QA comes back to you** — whether the ticket is On Hold or Awaiting info from Requestor. If the work is progressing and simply is not ready, the wait continues. If there has been **no progress**, QA contacts you and then **closes the ticket**.

That closure is not a refusal. It is an accurate statement that the work is not ready to be tested, and you resubmit when it is. A "no" at four weeks costs everyone far less than one at twelve.

### When you get a date

When an engineer picks the ticket up, **QA gives you a completion time in business days and a delivery date** — for example, *"10 business days, delivered by 6 October"*. Not before, because until someone has read the work there is nothing to base it on.

**That is elapsed time, not effort.** It already accounts for the engineer's other ticket and for any release freeze in the window. Three days of effort is therefore around two and a half weeks of calendar time, and longer if a freeze lands in it.

The estimate comes **from the QA team**, not from one engineer negotiating alone. If it does not fit your date, QA says so on the ticket and starts the conversation.

**You will always be told about slippage.** If a date moves, if something blocks, or if your work is displaced by a production incident, there is a comment on the ticket — at the latest at the next day's triage.

### How your request is ordered

Every request arrives at **Medium** priority. You cannot set it higher, and that is deliberate — a priority field everyone can raise stops meaning anything within a quarter. What you *can* set is **Urgency**, and QA may correct it.

What orders the queue:

- **Your Urgency** is the main determinant among everything at Medium.
- **Release work and absolutely Critical production issues** sit above everything else.
- **Priority is re-assessed**, not set once. A ticket moves up as its date approaches, without you needing to chase it.

**Priority can also go down**, for two reasons, and both are recorded as a comment naming exactly what is missing:

| Reason | The bar |
|--------|---------|
| The epic is substantially incomplete | The organisation's **[SDLC definition of a complete epic](LINK-TBC)** `[LINK TBC]`, checked by the requirement review tooling and reviewed by QA |
| The feature is not shipping soon | The **Planned release date**, which must match the epic |

Both are checkable, and **supplying what is missing restores the priority**. This is a prompt, not a penalty.

**If you think a demotion is wrong**, say so on the ticket — it is settled at the next triage, and escalates to the Manager of the BP QA Team if it cannot be. Where the issue is the release date, correcting the date is the fix; QA follows the field rather than arguing about it.

---

## What you are competing with

Your request is not only queued against other people's requests. The same slots are taken by work QA raises for itself:

- **Regression after initiative delivery**, driven by the release schedule and the planned release dates
- **BugCrowd security findings**, whose volume is externally driven. Capped at two of the eight slots before triage escalates

So a queue that looks short from the portal may still be full. **All of it is visible** — everything the QA team handles, including automation, training preparation and release activity, is tracked in the **[QA work Jira project](LINK-TBC)** `[LINK TBC]`. If you are told there is no free slot, you can check.

---

## The release rhythm

A release happens roughly **every two weeks**, and for **three to five working days** around each one QA picks up **no new portal requests**. The team is preparing environments, running release testing, triggering the canary release, reviewing performance data, verifying fixes and releasing the software. Automation time continues throughout.

**The queue moves between freezes.** That is the single most useful thing to understand about timing.

You can still submit during a freeze. Your ticket is triaged as normal, placed On Hold, and you are told when it is likely to be picked up. To see where a freeze falls, use the **[quarterly release schedule](LINK-TBC)** `[LINK TBC]`; for live status, **[`#bp-status-release-feature`](LINK-TBC)** `[LINK TBC]`.

The capacity behind all of this is set out on **[Service levels and measures](04%20-%20Service%20levels%20and%20measures.md)**.

---

## What you get at the end

QA closes the ticket as **Done**, and leaves:

- a comment explaining what was tested and what the result was
- links to any artifacts produced — test cases, test runs, recordings, reports

If QA finds bugs, they are raised as **separate, linked issues**. The portal ticket still closes, because the testing is complete. It does not stay open waiting for someone else's fixes.

**You can reopen a closed ticket for one week.** That is for *"this does not answer my question"* — correcting or completing the original work. New scope on the same feature is a new request.

A reopened ticket goes back to the engineer who did the work where possible, takes a slot, keeps its original priority and Urgency, and gets a new date. If no slot is free it waits like anything else. **The reopen window is a right to reopen, not a promise of speed.**

---

## Things QA will not do

| Not this | Instead |
|----------|---------|
| Provide a dedicated or embedded QA engineer | Not available. QA is a shared service and staffing requests are declined |
| Work asked for in Slack, in a meeting, or in person | You will be redirected to the portal. Every time, regardless of size |
| File a bug on your behalf | QA files the bugs it finds. You file the ones you find |
| Verify a routine bug fix | That stays with the feature team |
| Reproduce a bug for you | A conversation is fine. A reproduction effort is not QA work |
| Answer "how should this work?" | Product Owner or Product Manager |
| Create a QA instance for you | Self-service instructions in Confluence |
| Troubleshoot CI, or take CI-related requests | DevOps. QA triggers release builds and nothing else |
| Investigate a production incident | Support assesses, Engineering owns L3. QA verifies when asked — see below |

**On being redirected:** this is not personal, and the engineer redirecting you is not making a judgement call. It is a team rule with no exceptions, because a rule with exceptions requires every engineer to estimate your work before declining it — which is the negotiation the rule exists to avoid. If you think the rule is wrong, there is an escalation path at the bottom of this page.

Asking a QA engineer a question is not "work" and never was. Anything that needs an environment, a test run, or produces a result you will act on goes through the portal.

### Production incidents

QA is not a first responder. **Support** assesses the issue from the customer's report; **Engineering** provides L3 support; if QA verification is needed, **Support or Engineering — usually Engineering — requests it through the QA Portal**, like any other work.

*Absolutely Critical* means the system is down and unusable, or there has been a major data loss incident. **This is an incident condition, not the Jira severity field** — a bug marked Critical in Jira is not automatically this. QA **verifies**. It does not investigate, reproduce, triage or own the resolution.

This work sits at the top of the queue and displaces committed work. If yours is displaced, **you will be told**, and your ticket's status is changed so the delay does not consume your own target.

---

## Who to talk to, and how to change this

The **Manager of the BP QA Team** is the first point of contact, with the QA team as deputies — most questions get passed to whichever engineer can answer fastest.

**If something cannot be resolved with QA**, it goes to the **Senior QA Manager**, and then to the **SW Director for BigPicture**.

**If you think a rule on this page is wrong**, contact the Manager of the BP QA Team directly. This is one of the few things that does *not* go through the portal — feedback is not work, it needs no environment and produces no result anyone acts on. Changes are made at the monthly QA Team Retrospective and published with a new version number.
