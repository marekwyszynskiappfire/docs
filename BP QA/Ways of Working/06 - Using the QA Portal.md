# Using the QA Portal

**Audience:** requesters — a walkthrough of the form itself
**Maintained by:** the QA Team · **Contact:** the Manager of the BP QA Team · **Version:** 0.4 (draft skeleton) · **Last reviewed:** 2026-09-23

> **This page is being written by the QA team from the live portal.** What follows is a skeleton: the process decisions are settled and the structure is correct, but the screenshots and exact field list must be captured from the form itself. Marked `[TBC]` where confirmation is needed.
>
> **Pages 1 to 5 do not depend on this one and publish first.** This page follows.

---

## Why this is a separate page

Portal mechanics and ways of working change at different rates. A field gets renamed, a form gets reorganised, someone adds a dropdown — none of which changes how the team operates. Keeping the walkthrough separate means the process pages do not go stale every time the form is edited.

If the form and this page disagree, **the form is right and this page is out of date**. Tell the Manager of the BP QA Team.

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

**Two things the portal does not take:** requests for a dedicated or embedded QA engineer, which are declined automatically, and proposals to change QA's ways of working, which go directly to the Manager of the BP QA Team.

`[TBC: screenshot of the request type picker]`

---

## The fields

### Urgency

**Mandatory, and the most important field on the form.** Four values: **48 hours**, **a week**, **two weeks**, **a month**.

It does two things. It sets a **resolution target**, and it is the main determinant of how your request is ordered against everything else at Medium priority. You will see the countdown on your ticket.

Some guidance on using it well:

- **Know what each value buys.** A ticket in progress receives about 1.25 engineer-days a week, so *a week* is roughly one and a quarter days of actual work and *48 hours* is about half a day. The full table is on [Service levels and measures](04%20-%20Service%20levels%20and%20measures.md).
- **QA will correct it if it does not fit.** Choosing 48 hours for a two-week job produces a comment explaining what is actually possible, not a two-day delivery. The correction is made by the team and recorded on the ticket.
- **Urgency does not create capacity.** If the work is not feasible in the time available, triage says so and discusses it with you rather than silently missing it.
- **Check where the release freezes fall.** QA picks up no new requests for three to five working days around each release. **[Quarterly release schedule](LINK-TBC)** `[LINK TBC]`

`[TBC: screenshot of the Urgency field]`

### Planned release date

**Required by QA on feature-related requests** — feature testing, test automation for a feature, performance testing and shift-left requirement review.

The form does not enforce it, because the form is shared across the company and other projects have no such need. **QA enforces it at triage**, and a feature-related request without it is returned.

- **It must match the target date in the epic.** If the plan moves, update both.
- **Where the two disagree, QA works to the later date.** So a release pulled forward will not speed your ticket up until you update it.
- It is also what the priority-demotion check reads. A feature that is not shipping soon is deprioritised, and correcting the date is the remedy.

`[TBC: confirm the exact field name and whether it appears on all request types]`

### Priority

You will see a priority field. **Leave it alone** — everything is submitted at Medium and QA sets priority at triage.

This is deliberate. A priority field that requesters can raise stops distinguishing anything within a quarter. Urgency is where you express timing.

### Description and context

The required information depends on request type, and the full list is on **[Requesting QA work](01%20-%20Requesting%20QA%20work.md)**. The short version, for everything:

- link to the epic or dev ticket in GitHub
- Confluence documentation
- Figma design, if UI-related
- feature flags and what each controls
- what kind of testing, and which roles and permissions
- manual, automated, or both
- what you want to learn, and what counts as success

A request missing these is returned — the ticket moves to **Awaiting info from Requestor** and the clock stops until you answer. It is faster to fill them in now.

`[TBC: screenshot of the description fields for feature testing]`

### Attachments

`[TBC: confirm what the form accepts and whether there is a size limit]`

---

## After you submit

`[TBC: screenshot of a submitted ticket showing the triage comment]`

Your request is read at the **next daily triage meeting, 10:00 CET** — so the next business day at the latest if you submit just after one. You will get a comment saying one of four things: the ticket is **picked up**, your **Urgency has been corrected** and why, information is missing and the ticket is **Awaiting info from Requestor**, or it is **On Hold** with the reason.

Both On Hold and Awaiting info from Requestor **pause the clock**. Both are reviewed daily, and at four weeks QA comes back to you — and closes the ticket if there has been no progress.

Once an engineer picks the ticket up, QA gives you **a completion time in business days and a delivery date**. That is elapsed time, not effort. If anything slips, you are told on the ticket.

When the ticket is closed, you can **reopen it for one week** if the result does not answer your question. It goes back to the engineer who did the work where possible and gets a new date — it is a right to reopen, not a promise of speed.

---

## Tracking your request

**[QA work — Jira project](LINK-TBC)** `[LINK TBC]`

Everything the QA team handles is there — portal counterparts, automation, BugCrowd findings, training preparation and release activity. Use it to see where your ticket sits and what it is competing with, which is not only other people's requests. During a release, check **[`#bp-status-release-feature`](LINK-TBC)** `[LINK TBC]` — while a release is running, new requests are parked.

---

## To finish this page

| Outstanding | Notes |
|-------------|-------|
| Screenshots throughout | Landing page, type picker, Urgency, Planned release date, description fields, a triaged ticket |
| Confirm the exact request types on the live form | The table above is derived from the agreed scope, not read off the portal |
| Confirm the portal is a Jira Service Management project | Assumed while drafting |
| Confirm the exact label of the **Planned release date** field | Referred to as both "planned release timeline" and "planned release date" during drafting |
| Confirm the **Urgency** SLA configuration | Which statuses pause it, and whether the countdown is visible to the requester |
| Confirm Azure DevOps testing is live | If the transition is not complete, say *"available from [date]"* rather than listing it as requestable |
| Confirm the reopen window is configured | One week, per the agreed process |
| Portal URL, QA work project URL, Slack channel link, holiday calendar | Also needed by pages 1 and 4 |
| Attachment behaviour | Types and limits |
