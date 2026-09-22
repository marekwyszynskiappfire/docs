# Using the QA Portal

**Audience:** requesters — a walkthrough of the form itself
**Maintained by:** the QA Team · **Contact:** Marek Wyszyński · **Version:** 0.2 (draft skeleton) · **Last reviewed:** 2026-09-22

> **This page is being written by the QA team from the live portal.** What follows is a skeleton: the process decisions are settled and the structure is correct, but the screenshots and exact field list must be captured from the form itself. Marked `[TBC]` where confirmation is needed.
>
> **Pages 1 to 5 do not depend on this one and publish first.** This page follows.

---

## Why this is a separate page

Portal mechanics and ways of working change at different rates. A field gets renamed, a form gets reorganised, someone adds a dropdown — none of which changes how the team operates. Keeping the walkthrough separate means the process pages do not go stale every time the form is edited.

If the form and this page disagree, **the form is right and this page is out of date**. Tell Marek Wyszyński.

---

## Getting to the portal

The QA Portal is a **Jira Service Management** project. `[TBC: confirm]`

**[QA Portal](LINK-TBC)** `[LINK TBC]`

`[TBC: screenshot of the portal landing page]`

The landing page also links the self-service instructions, including how to create your own QA instance — which is not a portal request.

---

## Choosing a request type

Pick the type that matches your work. It determines which fields you are asked for and how the request is categorised at triage.

| If you need | Choose |
|-------------|--------|
| A complete feature validated | Feature testing |
| Automation built for a feature | Test automation |
| Performance measured | Performance testing |
| New test cases written | Test design |
| Requirements reviewed before build | Shift-left requirement review |
| Data Center to Cloud migration tested | JCMA / migration testing |
| Azure DevOps integration tested | Azure DevOps testing |
| Event Manager sanity or regression | Event Manager testing |
| Documentation tested | Documentation testing |
| Training or a course | Training and enablement |

Not sure? Submit the closest match and say so in the description. Triage will reclassify it. **Guessing wrong is not a problem; not submitting is.**

`[TBC: screenshot of the request type picker]`

---

## The fields

### "Needed by…"

**The most important field on the form.** It is the main determinant of how your request is ordered against everything else at Medium priority.

Some guidance on using it well:

- **Give the real date.** Not a safety margin, not "as soon as possible". An early date on work that is not actually urgent is checked against the target shipping date in the epic, and if the feature is not shipping soon the priority is **lowered**.
- **A date does not create capacity.** If the work is not feasible in the time available, triage will say so and discuss it with you rather than silently miss it.
- **Check where the release freezes fall.** QA works no portal requests for about a week around each release, every two weeks. A date inside a freeze is a date QA cannot meet. **[Quarterly release schedule](LINK-TBC)** `[LINK TBC]`
- **Empty is worse than approximate.** A request with no date sits below every request that has one.

`[TBC: screenshot of the Needed by field]`

### Priority

You will see a priority field. **Leave it alone** — everything is submitted at Medium and QA sets priority at triage.

This is deliberate. A priority field that requesters can raise stops distinguishing anything within a quarter. Urgency is communicated through "Needed by…" and through the conversation on the ticket.

### Description and context

The required information depends on request type, and the full list is on **[Requesting QA work](01%20-%20Requesting%20QA%20work.md)**. The short version, for everything:

- link to the epic or dev ticket in GitHub
- Confluence documentation
- Figma design, if UI-related
- feature flags and what each controls
- what kind of testing, and which roles and permissions
- manual, automated, or both
- what you want to learn, and what counts as success

A request missing these is returned, and the clock stops until you answer. It is faster to fill them in now.

`[TBC: screenshot of the description fields for feature testing]`

### Attachments

`[TBC: confirm what the form accepts and whether there is a size limit]`

---

## After you submit

`[TBC: screenshot of a submitted ticket showing the triage comment]`

Your request is read at the **next daily triage meeting, 10:00 CET** — so the next business day at the latest if you submit just after one. You will get a comment saying the ticket is picked up, that information is missing, or that it is on hold until a stated point, with the reason. The full description of what happens next is on [Requesting QA work](01%20-%20Requesting%20QA%20work.md).

When the ticket is closed, you can **reopen it for one week** if the result does not answer your question.

---

## Tracking your request

**[All QA tickets — Jira filter](LINK-TBC)** `[LINK TBC]`

Use it to see where your ticket sits and what else is in the queue. During a release, check **[`#bp-status-release-feature`](LINK-TBC)** `[LINK TBC]` — while a release is running, other work waits.

---

## To finish this page

| Outstanding | Notes |
|-------------|-------|
| Screenshots throughout | Landing page, type picker, Needed by, description fields, a triaged ticket |
| Confirm the exact request types on the live form | The table above is derived from the agreed scope, not read off the portal |
| Confirm the portal is a Jira Service Management project | Assumed while drafting |
| Confirm field names | Particularly whether "Needed by…" is labelled exactly that |
| Confirm Azure DevOps testing is live | If the transition is not complete, say *"available from [date]"* rather than listing it as requestable |
| Confirm the reopen window is configured | One week, per the agreed process |
| Portal URL, Jira filter URL, Slack channel link | Also needed by pages 1 and 4 |
| Attachment behaviour | Types and limits |
