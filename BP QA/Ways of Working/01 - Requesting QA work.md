# Requesting QA work

**Audience:** anyone who needs something from the QA team
**Maintained by:** the QA Team · **Contact:** Marek Wyszyński, with the whole QA team as deputies · **Version:** 2.1 (draft for review) · **Last reviewed:** 2026-09-22

---

## In one paragraph

All QA work is requested through the **QA Portal**. Your request is read at the next daily triage meeting — 10:00 CET every working day — and you always get a comment telling you where it stands. There is no published completion time, but once an engineer picks your ticket up you are given a **delivery date**. Requests that arrive any other way are redirected back to the portal.

**[QA Portal — submit a request](LINK-TBC)** `[LINK TBC]` · **[QA work — Jira project](LINK-TBC)** `[LINK TBC]`

---

## The quarterly cycle — for features, initiatives and epics

**If you are asking QA to test a new feature, initiative or epic, it should be defined and in Jira at the start of the quarter.** Not when you need testing. At the start.

This is not planning for its own sake. QA does specific work with those epics before anyone asks for anything:

- runs them through the requirement review tooling and sends you back the gaps
- prepares test scenarios for the features they describe
- creates automation placeholders so the automation is not starting from zero when the work arrives

**Submitting early does not make your work finish sooner.** It makes it better prepared, and for a large epic it is what makes the request feasible at all. That is the honest version, and it is why the ask is worth honouring.

### Mid-quarter requests are normal

**The quarterly cycle is about preparation, not eligibility.** Everything else — test design, migration testing, performance work, documentation testing — arrives mid-quarter as ordinary business and is triaged like anything else. You are not doing something wrong by submitting in week seven.

**There is one case QA will push back on:** a **large epic arriving mid-quarter with an ETA of about a week**. Not because it arrived late, but because the preparation it depends on — requirement review, test scenarios, automation placeholders — cannot be compressed into that lead time.

Pushing back means QA tells you **what it can deliver and by when**, and the conversation is about moving the date or reducing the scope. It is a conversation, not a refusal.

---

## Before you submit

### Is it QA work?

The short version: QA tests the product and maintains the assets used to test it. It does not run infrastructure, answer product questions, or handle support tickets. The full rule, with the borderline cases and the things QA has stopped doing, is on **[QA Portal scope](02%20-%20QA%20Portal%20scope.md)**.

### Not sure which request type?

Submit the closest match and say so in the description. Triage will reclassify it. **Guessing wrong is not a problem; not submitting is.**

---

## What your request must contain

A request missing this information is returned to you, and the clock stops until you answer.

### Everything needs

- link to the epic or dev ticket in GitHub
- Confluence documentation
- Figma design, if the work is UI-related
- feature flag names, and what each one controls if there are several
- what kind of testing you need
- which roles and permissions need to be covered
- any setup required before testing can start
- manual, automated, or both
- tests only, or documentation as well
- **Needed by…** — the date you need this by
- what you want to learn — the purpose of the testing and what counts as success
- how deep the analysis should go
- for documentation requests: who the audience is

### Feature testing also needs

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

> **A note on "Needed by…".** Check where the release freezes fall before you pick a date. QA works no portal requests for about a week around each release, every two weeks — a date inside a freeze is a date QA cannot meet. **[Quarterly release schedule](LINK-TBC)** `[LINK TBC]`

---

## What happens after you submit

### At the next triage meeting

Every new request is read at the **daily QA triage, 10:00 CET**. Submit just after one finishes and yours is read the next working day — that is the outer bound of the commitment.

> **Whose working day.** The whole QA team works in **CET**, so the clock runs on CET working days, and the team's public holidays move it. Submit at 15:00 CET on Friday and your request is read on Monday morning.

You will get a comment saying one of three things:

| You are told | What it means |
|--------------|---------------|
| **Picked up** | An engineer has taken the ticket and is working on it |
| **More information needed** | Exactly what is missing. The clock stops until you reply |
| **On hold** | Accepted but not being worked, with the reason given. **The clock is paused** |

**Every held ticket is reviewed again every working day.** A waiting ticket is never a forgotten one.

### Why a ticket goes On hold

Three reasons, and the comment will always say which:

| Reason | What it means |
|--------|---------------|
| **The work cannot start yet** | An epic submitted at quarter start for a feature that ships in week eight. This is the commonest case, and it is the system working |
| **No free slot** | Each engineer works two tickets at a time. When all slots are taken, new work waits |
| **Blocked on someone else** | Waiting on a fix, an environment, or a feature flag being switched on |

**On hold is also the status used when work already in progress becomes blocked.** The ticket returns to the queue at its existing priority and the assignee comes off it — so if you see your ticket lose its assignee, that is what happened, and it may well be picked up by a different engineer when the blocker clears. QA does not hold a slot idle waiting for another team.

### Holds do not last forever

**At four weeks, QA comes back to you.** If the work is progressing and simply is not ready — the normal case for an epic submitted at quarter start — the hold continues. If there has been **no progress on the engineering side**, QA contacts you and then **closes the ticket**.

That closure is not a refusal. It is an accurate statement that the work is not ready to be tested, and you resubmit when it is. A "no" at four weeks costs everyone far less than one at twelve.

### When you get a date

When an engineer picks the ticket up, **QA gives you a completion time in business days and a delivery date** — for example, *"10 business days, delivered by 6 October"*. Not before, because until someone has read the work there is nothing to base it on.

**That is elapsed time, not effort.** It already accounts for the engineer's other ticket and for any release freeze in the window. Two things are worth knowing so the number is not a surprise:

- Each engineer runs **two tickets at a time** and spends **half their week** on portal and release work. So a ticket in progress receives roughly a day and a quarter a week — **work in progress is not work being worked on continuously**.
- Three days of effort is therefore around two and a half weeks of calendar time, and longer if a freeze lands in it.

The estimate comes **from the QA team**, not from one engineer negotiating alone. If it does not fit your date, QA says so on the ticket and starts the conversation.

### How your request is ordered

Every request arrives at **Medium** priority. You cannot set it higher, and that is deliberate — a priority field everyone can raise stops meaning anything within a quarter.

What orders the queue instead:

- **Your "Needed by…" date** is the main determinant among everything at Medium.
- **Release work and absolutely Critical production issues** sit above everything else.
- **Priority is re-assessed**, not set once. A ticket moves up as its date approaches, without you needing to chase it.

**Priority can also go down**, for two reasons, and both are recorded as a comment naming exactly what is missing:

| Reason | The bar |
|--------|---------|
| The epic is substantially incomplete | The organisation's **[SDLC definition of a complete epic](LINK-TBC)** `[LINK TBC]`, checked by the requirement review tooling and reviewed by QA |
| The feature is not shipping soon | The **target date recorded in the epic** by Product Management |

Neither is QA's opinion, both are checkable, and **supplying what is missing restores the priority**. This is a prompt, not a penalty.

---

## What you are competing with

Your request is not only queued against other people's requests. The same slots are taken by work QA raises for itself:

- **Regression after initiative delivery**, driven by the release schedule and the dates in epics
- **BugCrowd security findings**, whose volume is externally driven and outside anyone's control

So a queue that looks short from the portal may still be full. **All of it is visible** — everything the QA team handles, including automation, training preparation and release activity, is tracked in the **[QA work Jira project](LINK-TBC)** `[LINK TBC]`. If you are told there is no free slot, you can check.

---

## The release rhythm

A release happens roughly **every two weeks**. For about a week around each one, QA takes on **no portal requests**; the team is testing the release and verifying fixes. Automation continues throughout.

**The queue moves between freezes.** That is the single most useful thing to understand about timing, and it is the real reason the quarterly cycle matters.

You can still submit during a freeze. Your ticket is triaged as normal and you will be told when it is likely to be picked up. To see where a freeze falls, use the **[quarterly release schedule](LINK-TBC)** `[LINK TBC]`; for live status, **[`#bp-status-release-feature`](LINK-TBC)** `[LINK TBC]`.

The capacity behind all of this is set out on **[Service levels and measures](04%20-%20Service%20levels%20and%20measures.md)**.

---

## What you get at the end

QA closes the ticket as **Done**, and leaves:

- a comment explaining what was tested and what the result was
- links to any artifacts produced — test cases, test runs, recordings, reports

If QA finds bugs, they are raised as **separate, linked issues**. The portal ticket still closes, because the testing is complete. It does not stay open waiting for someone else's fixes.

**You can reopen a closed ticket for one week.** That is for *"this does not answer my question"* — correcting or completing the original work. New scope on the same feature is a new request.

---

## Things QA will not do

| Not this | Instead |
|----------|---------|
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

---

## Who to talk to, and how to change this

**Marek Wyszyński** is the first point of contact, with the QA team as deputies — most questions get passed to whichever engineer can answer fastest.

**If something cannot be resolved with QA**, it goes to the **Senior QA Manager**, and then to the **SW Director for BigPicture**.

**If you think a rule on this page is wrong**, submit it through the QA Portal. It is read at triage like anything else, and changes are made at the monthly QA Team Retrospective and published with a new version number.
