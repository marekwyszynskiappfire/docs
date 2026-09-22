# Requesting QA work

**Audience:** anyone who needs something from the QA team
**Maintained by:** the QA Team · **Contact:** Marek Wyszyński, with the whole QA team as deputies · **Version:** 2.0 · **Last reviewed:** 2026-09-22

---

## In one paragraph

All QA work is requested through the **QA Portal**. Your request is read at the next daily triage meeting — 10:00 CET every working day — and you always get a comment telling you where it stands. QA does not promise a completion date up front; you get an estimate when an engineer picks the ticket up. Requests that arrive any other way are redirected back to the portal.

**[QA Portal — submit a request](LINK-TBC)** `[LINK TBC]` · **[All QA tickets — Jira filter](LINK-TBC)** `[LINK TBC]`

---

## The quarterly cycle — the most useful thing on this page

**Every epic should be defined and in Jira at the start of the quarter.** Not when you need testing. At the start.

This is not a request to plan further ahead for its own sake. QA does specific work with those epics before anyone asks for anything:

- runs them through the requirement review tooling and sends you back the gaps
- prepares test scenarios for the features they describe
- creates automation placeholders so the automation is not starting from zero when the work arrives

An epic that arrives at quarter start gets tested by a team that has already read it. One that arrives the week you need it gets tested by a team seeing it for the first time, in whatever gap exists between releases — and there may not be one.

**Submitting early does not make your work finish sooner.** It makes it possible, and it makes it better prepared. That is the honest version, and it is why the ask is worth honouring.

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

---

## What happens after you submit

### At the next triage meeting

Every new request is read at the **daily QA triage, 10:00 CET**. Submit just after one finishes and yours is read the next working day — that is the outer bound of the commitment.

> **Whose working day.** The whole QA team works in **CET**, so the clock runs on CET working days. Submit at 15:00 CET on Friday and your request is read on Monday morning. The team's **public holidays** also move it — see the [holiday calendar](LINK-TBC) `[LINK TBC]`.

You will get a comment saying one of three things:

| You are told | What it means |
|--------------|---------------|
| **Picked up** | An engineer has taken the ticket and is working on it |
| **More information needed** | Exactly what is missing. The clock stops until you reply |
| **On hold** | The ticket is accepted but not started, with the reason and the point in time it is waiting for |

There is no fourth state, and **every held ticket is looked at again every working day**. A waiting ticket is never a forgotten one.

Two things put a ticket on hold, and the comment will say which: the **work cannot start yet** — an epic submitted at quarter start for a feature that ships in week eight — or the team is **at capacity** and something has to wait.

### When you get a date

When an engineer picks the ticket up, they estimate it and tell you. **Not before.** QA commits to reading and responding to your request quickly; it does not commit to a completion date it cannot yet know.

If the estimate turns out not to fit your date, QA will say so on the ticket and start a conversation — the team does that, not the individual engineer, and the estimate will tell you whether it spans a release freeze.

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

## The release rhythm

A release happens roughly **every two weeks** — five or six a quarter. For about a week around each one, QA takes on **no portal requests**; the team is testing the release, verifying fixes and running CI work. Automation continues throughout.

**The queue moves between freezes.** That is the single most useful thing to understand about timing, and it is the real reason the quarterly cycle matters.

You can still submit during a freeze. Your ticket is triaged as normal and you will be told when it is likely to be picked up. To see where a freeze falls, use the **[quarterly release schedule](LINK-TBC)** `[LINK TBC]`; for live status, **[`#bp-status-release-feature`](LINK-TBC)** `[LINK TBC]`.

**There is a ceiling.** Four engineers work two tickets each, so more than **eight new tickets in a week** means the ones above that number are automatically put on hold, with a reason. Demand above capacity is made visible rather than absorbed quietly.

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
| Investigate a production incident | Support assesses, Engineering owns L3. QA verifies when asked — see below |

**On being redirected:** this is not personal, and the engineer redirecting you is not making a judgement call. It is a team rule with no exceptions, because a rule with exceptions requires every engineer to estimate your work before declining it — which is the negotiation the rule exists to avoid.

Asking a QA engineer a question is not "work" and never was. Anything that needs an environment, a test run, or produces a result you will act on goes through the portal.

### Production incidents

QA is not a first responder. **Support** assesses the issue from the customer's report; **Engineering** provides L3 support; if QA verification is needed, **Support or Engineering — usually Engineering — requests it through the QA Portal**, like any other work.

*Absolutely Critical* means the system is down and unusable, or there has been a major data loss incident. QA **verifies**. It does not investigate, reproduce, triage or own the resolution.

---

## Who to talk to

**Marek Wyszyński** is the first point of contact for anything about this process, including disagreements with it — though most questions get passed to whichever engineer can best answer them, which is usually faster.

These pages are reviewed monthly at the QA Team Retrospective.
