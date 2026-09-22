# MEMORY — BP QA Way of Working session

Persistent state for this workstream. Read this first when starting a new conversation or context window; it should contain everything needed to resume without re-reading the whole history.

**Last updated:** 2026-09-22 · **Pages at v2.1**, three review rounds complete

---

# ⚠️ Open uncertainties and ambiguities

**Read this section before changing anything in `Ways of Working/`.** Three grilling rounds settled the model, but the following are either unconfirmed, unverified, or deliberately unresolved. They are ordered by how much damage they would do if wrong.

## A. Interpretations written into the pages as fact but never explicitly confirmed

These were inferred while applying answers. Each is defensible and each was flagged to the user at the time, but none was confirmed in words. **They currently read as settled fact in published-ready pages.**

| # | What the pages assert | Why it is uncertain | Blast radius if wrong |
|---|----------------------|---------------------|----------------------|
| **U1** | A release costs **~10 engineer-days**, derived from ~2 days release testing + ~2 days fix verification, read as **elapsed days with the team working in parallel** | The source statement was *"testing takes about two days, verification maybe another two"*. If those are **per-engineer** rather than elapsed, the release consumes far more than a week and the whole capacity model shifts | **High.** "About a week per release" justifies roughly half the quarter being closed to requesters. It is the single most load-bearing derived number in the set |
| **U2** | The four-week hold horizon has **two outcomes** — a planned wait with a known date **continues**, a hold with no engineering progress is **closed** | The user only specified the closure branch. The "continues" branch was added because a blanket four-week closure would destroy the quarterly forward book, which is clearly not the intent — but it was not asked | **High.** Get it wrong in the other direction and every epic submitted at quarter start gets auto-closed in week four |
| **U3** | QA keeps **its own failing automated tests**; the **CI platform** (agents, pipelines, build infra) is DevOps | The user said only *"CI-related work is out of scope… just triggering the builds"*. The carve-out for QA's own test code was added because pages 2 and 5 would otherwise contradict each other | **Medium-high.** If QA's failing E2E runs are also out of scope, the automation half of the week loses a large recurring activity |
| **U4** | **"Push back"** on a large mid-quarter epic means QA states what it can deliver and opens a conversation about date or scope — **not a refusal** | Flagged explicitly when recorded; never confirmed. The user's phrasing (*"we will push back on those tickets"*) could mean an outright decline | **Medium.** Changes whether page 1 describes a negotiation or a rejection, which is the difference in tone PMs will react to |
| **U5** | A ticket closed at the four-week horizon comes back as a **new request**, not a reopen | Inferred from the one-week reopen window covering *"this does not answer my question"* | **Low-medium.** Mostly affects portal configuration and requester expectations |
| **U6** | The severity absolute is **both asserted and attributed** — the pages cite the existing severity rules *and* state that no release ships with a blocker | The user said *"We do not release with blockers. period."* The attribution framing was the reviewer's addition, intended to strengthen rather than soften | **Low.** But if the severity rules do not actually say this, QA is citing a document that does not support the claim |
| **U7** | The estimate is given **by the QA team**, not by the individual engineer | The user wrote *"a delivery date from the QA Team"*, read as team-not-individual. Consistent with the existing page 3 rule, so probably right | **Low** |
| **U8** | Support ticket review has **stopped**, not "is being wound down" | The assumption was confirmed; the wording change to the harder form was the reviewer's | **Low**, but it is one of three activities people will discover by being refused |

## B. Facts to verify against reality before publishing

Nothing here is a decision — it is all checkable, and all of it is currently asserted in the pages.

| # | To verify |
|---|-----------|
| **V1** | The **QA work Jira project does not exist yet.** Pages 1, 2, 4, 5, 6 and the README all point to it, and several capacity claims depend on it being visible. This is the largest gap between what the pages describe and what exists |
| **V2** | **On hold pauses the SLA clock.** The user stated it does; confirm in the portal configuration, because pages 1, 3 and 4 all rely on it |
| **V3** | The **one-week reopen window** is actually configured |
| **V4** | **Azure DevOps testing is genuinely available now** (assumption A5). The original draft said "soon, currently handled by one person". If the transition is incomplete, the pages should say *"available from [date]"* |
| **V5** | The **QA Portal is a Jira Service Management project** — assumed while drafting |
| **V6** | **5 to 6 releases per quarter at about a week each** really does mean roughly half the quarter is closed to portal work. Stated as "roughly half"; arithmetic gives 5–6 of ~13 weeks |
| **V7** | The **average ticket size of ~1.25 engineer-days** implied by eight per week. Named on page 4 as the weakest number in the set. **Measured from go-live, revisited at end of year** |

## C. Unresolved, and nobody has agreed to it yet

| # | Open |
|---|------|
| **O1** | **No function has actually agreed to any of this.** Pages 2 and 3 carry `Reviewed with: [date TBC]` for Product Management, Engineering and Support. The incident route, the observability ownership and the CI boundary all require someone else to accept work |
| **O2** | **"Every epic in Jira at quarter start" is the largest external dependency in the collection**, and Product Management has not signed up to it. The quarterly cycle is the spine of the model and rests entirely on this |
| **O3** | **Product Management has no dedicated page** (declined in round two). Their only content is the *what QA depends on* section on page 2, which has never been tested with a PM |
| **O4** | **Page 6 is unwritten** — the user is preparing it from the live portal. Pages 1–5 publish first |
| **O5** | **Six `[LINK TBC]` placeholders** remain: QA work project, QA Portal, SDLC epic definition, quarterly release schedule, severity rules, Slack channel |
| **O6** | **No comms plan.** Walkthroughs and Q&A sessions are agreed in principle (round two, P1) but not scheduled |
| **O7** | **Escalation uses roles, not names.** Senior QA Manager and SW Director for BigPicture are unnamed in the pages — deliberate, but someone must confirm those roles will accept the routing |

## D. Gaps nobody has raised yet — candidates for a fourth round

Found while applying the third round; not yet put to the user.

| # | Gap |
|---|-----|
| **G1** | **BugCrowd volume is unbounded and consumes slots.** In a bad month it could take most of the queue. There is no cap, no policy, and no stated behaviour when it crowds out requester work |
| **G2** | **Scheduled work has no capacity limit.** Training and enablement is "declared at triage" but nothing says how much of the team can be committed to it at once |
| **G3** | **A reopened ticket has no defined priority or WIP behaviour.** Does it return at its original priority, or to the back of the queue? |
| **G4** | **Absolutely Critical verification displaces committed work**, and nothing says the displaced requester is told. The pages promise no silence, so this is a live inconsistency |
| **G5** | **A requester who disagrees with a priority demotion** has no arbitration route. Supplying the missing information restores priority, but there is no path for "the tooling is wrong" |
| **G6** | **Public holidays move the clock**, but the holiday calendar reference was removed (E6) and nothing replaced it. Requesters outside CET have no way to know when the team is off |

## E. Decisions overturned across rounds — do not reinstate

| Overturned | Was | Now |
|---|---|---|
| **RUM waiver** | Round 2: a known regression may ship under a recorded waiver | Round 3: **no waiver.** The gate blocks absolutely |
| **CI effort** | Round 2: "the entire CI related work is 1 FTE per release" | Round 3: **CI is out of scope.** Only release build triggering remains |
| **Inflow ceiling mechanism** | v2.0 drafting: more than 8 new tickets a week, hold the excess | Round 3: **slot-based.** Held when no WIP slot is free; 8/week is a planning figure only |
| **"The team will not grow beyond four"** | v2.0: published as permanent policy | Round 3: **planning basis only** — *"the model is built for that size and does not assume growth"* |
| **Reorganisation backstory** | v2.0: on the README and pages 2 and 3 | Round 3: **removed from all pages.** Retained here in MEMORY only |
| **Completion commitment** | v2.0: "no completion promise" | Round 3: **no published SLA, but a date per ticket** once picked up. Different claims, previously blurred |

## F. Deliberate tensions — correct as written, and they will still be challenged

Not problems. Recorded so a future session does not "fix" them.

- **No published completion SLA.** Intentional until intake is measured. The quarterly cycle is the substitute.
- **No exceptions to the out-of-portal rule**, regardless of task size. An absolute rule so individual engineers can apply it without estimating first.
- **Fixed team size.** The answer to insufficient capacity is scope reduction, never headcount.
- **Generalist model.** Depth is knowingly traded for flow at four engineers.
- **The out-of-scope list framed as a bill.** Meant to be challenged item by item, not accepted.

---

## Objective

Turn the draft `BP QA/WoW.md` into a series of **Confluence pages** describing the QA team's ways of working, shareable across the company. The draft is explicitly a work in progress. The route to a finished set of pages is a **grilling session**: rounds of questions that resolve the open decisions, with answers recorded as they are settled.

---

## Where things came from

| Artefact | Origin |
|----------|--------|
| `WoW.md` | Generated from the Confluence whiteboard [Process Vision - Sticky Notes](https://appfireteam.atlassian.net/wiki/spaces/~7120202c1c597e249542f89ace1bdf6605ba70/whiteboard/99900981543), read via the Atlassian MCP integration |
| Related page | [QA Portal Workshop Outcomes](https://appfireteam.atlassian.net/wiki/spaces/~7120202c1c597e249542f89ace1bdf6605ba70/pages/99901308933/QA+Portal+Workshop+Outcomes) |
| Whiteboard sections | "What tasks do we want in the QA Portal?", "What tasks we don't want", "What information do we need in a request?", "How do we envision the Process?", "What are the Risks?", plus "What you do? / Do / Don't do" |

The whiteboard is the source of truth for what the team *said*; `WoW.md` is a structured rendering of it, and several contradictions in the document are faithful reproductions of unresolved disagreements on the board.

---

## Files in this folder

| File | Purpose |
|------|---------|
| `Ways of Working/` | **The rewritten pages.** Six pages plus an index. This is the deliverable |
| `WoW.md` | The original draft, rendered from the whiteboard. **Superseded** by `Ways of Working/`; kept as the record of what the whiteboard said |
| `personas.md` | **Seven** review personas: Tomasz Nowak (SW Engineer), Priya Raman (QA Engineer), Daniel Okonkwo (SW Engineering Manager), Elena Rossi (QA Manager), Anna Kowalska (Senior QA Manager), Sarah Whitfield (Director of SW Engineering), Inês Duarte (Product Manager). Expanded from two on 2026-09-21; Anna keeps her name so existing *Lens: Anna* findings still read correctly |
| `page-review-questions.md` | **Second review**, of the drafted pages rather than `WoW.md`. 3 contradictions, 6 blocking, 11 important, 7 worth settling, 8 assumptions to confirm. **All answered** |
| `page-review-round-3.md` | **Third review**, of the whole collection as a published set — asking where the argument starts rather than whether the model is right. 7 defects, 10 discussion generators, 7 editorial fixes. **All answered and applied** |
| `review-report.md` | Findings against the draft: 8 Critical, 9 Major, 7 Minor, plus what works and a proposed Confluence page structure |
| `open-questions.md` | The grilling tracker. Round 1 asked; Rounds 2 and 3 mapped but blocked |
| `MEMORY.md` | This file |

---

## State of play

**Completed**
- Whiteboard content extracted and structured into `WoW.md`
- `WoW.md` committed and pushed (commit `e40def3`, remote `marekwyszynskiappfire/docs`)
- Personas written
- Review completed; findings recorded
- Round 1 of grilling asked (8 questions)
- **Q1 settled**: five-page Confluence structure
- **Q2 settled**: English only, plus an acronym glossary
- **Q3 settled**: scope principle plus three scope calls
- **Q3b settled**: full observability exit, RUM retained as a pre-release gate
- **Q3c settled**: RUM review is a release-process step; engineering owns the portal; PM and Engineering own the thresholds
- **Q3d settled**: the RUM gate blocks; failures go to Engineering as a ticket and QA re-reviews after the fix
- **Q3e settled**: not-assessable modules and the waiver path. **RUM branch closed**
- **Q4 settled**: the bug boundary is "on whose behalf"; blocker = severity ≥ Medium; BugCrowd issues are QA-created
- **Q4b settled**: blockers are bound to Release Testing; no severity ≥ Medium bug ships. **Bug branch closed**
- **Q5 settled**: deadline-aware prioritisation via the existing "Needed by…" field; portal mechanics split into a sixth document
- **Q6 settled**: pure pull, daily triage, no assignment by anyone
- **Q6b settled**: ordered pull by priority; 4 engineers, WIP 2; unclaimed tickets raised by comment
- **Q7 settled**: 24 business hours; daily triage meeting at 10:00 CET
- **Q7b partly settled**: the clock stops on return; stale-return closure still open
- **Q8 settled**: QA Team maintains; monthly review at Team Retrospectives; Marek Wyszyński is the contact
- **ROUND 1 COMPLETE** — all 8 foundation questions plus 7 branched follow-ups settled

- **Q9 settled**: 50/50 split, ceiling never exceeded, early submission encouraged

- **Q10 settled**: two-tier service levels — firm response, indicative completion
- **Q11 settled**: three kinds of work — requestable, QA-raised portal tickets, and release-process
- **Q11b settled**: release work pre-empts everything; one Release ticket plus linked Jira issues
- **Q11c settled**: Slack channel plus a Jira filter; daily meetings continue during releases
- **Q12 settled**: QA builds instances for its own work, but runs no instance-creation service
- **Q13 settled**: standard Jira scale, default Medium, QA re-assesses at triage
- **Q13b settled**: date drives ordering, release and production incidents escalate, weak dates get demoted
- **Q14 settled**: production help is verification only, and only for absolutely Critical issues
- **Q14b settled**: QA closes as Done with a comment and artifact links; no report templates
- **Q15 settled**: out-of-band work is always redirected to the portal, no exceptions
- **Q16 settled**: shift-left is an AI-assisted async review, QA-reviewed, returning questions
- **Q17 settled**: DoR/DoD are epic-level standards shared with Engineering; PM sign-off is outside QA
- **Q18 settled**: no published completion ranges; the engineer who picks up the ticket estimates it
- **Q18b settled**: triage always comments — picked up, needs information, or on hold with a reason
- **Q19 settled**: generalist by design; the process lowers the knowledge the work requires

**Grilling complete.** Nineteen questions settled across two rounds. No substantive decisions remain open.

**Rewrite complete.** The six pages are drafted in `BP QA/Ways of Working/`, plus a `README.md` index carrying the glossary, the organising principle, and the outstanding links.

| File | Page |
|------|------|
| `README.md` | Index, glossary, organising principle |
| `01 - Requesting QA work.md` | Requesters |
| `02 - QA Portal scope.md` | Requesters and managers |
| `03 - How the QA team works.md` | QA team and managers |
| `04 - Service levels and measures.md` | Managers |
| `05 - Appendix - QA activity inventory.md` | QA internal |
| `06 - Using the QA Portal.md` | Requesters — **v0.1, needs screenshots** |

How the remaining findings were handled in the rewrite:

| Finding | Handled |
|---------|---------|
| C8 | Page 1 carries the full required-information list, the submission route and what happens next |
| M9 | Page 2 leads with the scope *rule*; the lists are demoted to worked examples |
| M17 | Page 2 references DoR/DoD as a shared Engineering standard and states only QA's part |
| N5 | Page 4 gives every risk a mitigation, and says plainly that the bottleneck risk has none |
| N6 | **Left open — see below.** Not inferred |
| N7 | Page 3 links the `requirements-review` skill; page 5 places the test-case library in the model |

**Action items arising** (things that must exist before the pages can be published)

| Action | Raised in |
|--------|-----------|
| Create the **Jira filter showing all QA tickets** — the requester page links to it | Q11c |
| Obtain the link to the **severity rules** that define a release blocker | Q4 |
| Confirm the link to **`#bp-status-release-feature`** | Q11c |
| **Comms plan** for the rollout, plus walkthrough sessions with Product Management, Engineering and Support | P1 |
| Explicit acceptance of the **incident portal route** from Engineering and Support | X1, P1 |
| Explicit acceptance of the **observability inheritance** from Engineering | P6 |
| Link to the **SDLC definition of a complete Epic** — the objective bar for requirement review and priority demotion | P9 |
| Link to the **quarterly release schedule** — trigger for full regression, and how requesters see when freezes fall | P14 |

**Parked, unanswered, do not assume**
- Whether an unanswered returned ticket is ever closed (Q7b, second half)
- **N6** — whether a ticket on hold or blocked mid-work frees the engineer's WIP slot. Deliberately left out of the pages rather than guessed
- Whether a requester can reopen a closed ticket, and within what window (Q14b)

**Defaults written into the pages that the team should confirm or correct**

| Default | Page | From |
|---------|------|------|
| A ticket is Done when testing completes, whatever the outcome; bugs are separate linked issues | 3 | Q14b |
| §6's four old SLA figures are **withdrawn**, not relabelled | 4 | Q18b |
| The §5 "environments to test" field applies only to existing shared environments | 1 | Q12 |
| Answering a question is not "work"; anything needing an environment or test run is | 1, 3, 5 | Q15 |

**Known capacity facts** (for the Round 2 capacity question)

| Fact | Value |
|------|-------|
| QA Engineers | 4 |
| WIP limit per engineer | 2 tickets |
| Ceiling on portal work in progress | 8 tickets, never exceeded |
| Split, portal work vs test automation | **50 / 50**, a company expectation, trending toward automation |
| Effective portal capacity | **2.0 FTE** |
| At the ceiling | Case-by-case at daily triage: negotiate the deadline, or park other work |
| Requester guidance | Submit early, ideally at the start of the quarter |
| Still unknown | **Intake volume** — not yet measured, believed modest |

**Emerging pattern worth carrying into the rewrite:** two activities settled so far — the RUM review and release blocker testing — are **release-process work, not portal intake**. The portal category list in §2 currently mixes the two kinds together. Expect other §2 entries to sort the same way during the rewrite.

**External dependency for the rewrite:** the severity rules that define "release blocker" exist outside this repository (Confluence or Jira — confirmed absent from the repo by search on 2026-09-21). The published pages must **link** them rather than restate them, or the two will drift.

**Division of labour on the RUM release gate** (settled across Q3b–Q3d)

| Owner | Responsibility |
|-------|----------------|
| Engineering | The RUM Events portal, and fixing regressions |
| Product Management + Engineering | Defining the performance thresholds |
| QA | Reviewing the data before release, escalating by ticket with module and events named, re-reviewing after the fix |

**The agreed scope principle**

> The QA Portal covers **testing the product and maintaining the assets used to test it**. It does not cover infrastructure and tooling operations, customer support, or decisions about how the product should behave. Reactive work enters the portal only when it is **release-critical** or **security-related**; routine defect verification stays with the feature team.

**Second review complete (2026-09-21).** Personas expanded to seven, and the drafted pages reviewed through all of them. Findings in `page-review-questions.md`. The headline: the scope rule, the capacity model and the generalist principle all hold; what does not hold is everything the pages assume of **other functions** — Product Management was assigned four obligations without being asked, Engineering was assigned an observability inheritance it has not accepted, and release cadence is missing from the capacity arithmetic.

**Second-round Q&A in progress.** Same method as round one: one question at a time, recommendation attached, answers recorded in `page-review-questions.md`. **The pages are corrected in a single pass at the end of the session**, at the user's instruction — not question by question.

| Q | Decision |
|---|----------|
| A1–A8 | **All eight assumptions confirmed as written.** Bug reproduction help, Support ticket review and filing bugs for Support all **stop**; unit/DB tests and automation maintenance are internal; Azure DevOps testing is requestable; release management is QA release-process work; the portal is a JSM project | Change A2's "being wound down" to **stopped** — a boundary described as in progress keeps getting tested. **Sanity-check A5** against reality; if the Azure DevOps transition is incomplete, use *"available from [date]"*. A1–A3 go on the P1 walkthrough: each has someone on the other end who will otherwise discover the change by being refused |
| P24 | **The team writes the portal instructions** and submits them for review | **Default**: publish the other five pages without waiting — page 6 is the only one depending on external artefacts, and the index marks it as coming |
| P23 | Automation commitment: **at least one test case automated per day per engineer** — with **2.5 business days a week** for automation, that is **2–3 test cases created or fixed weekly per engineer**, tracked transparently in Jira | Turns reserved time into measurable output (~8–12 test cases a week across the team). **Pins the 50/50 split to hours** — 2.5 of 5 days — which is much harder to erode. Gives the P4c freeze commitment its point: automation output is **uninterrupted year-round** while portal throughput drops to zero in freeze weeks. **Arithmetic page 4 must reconcile**: 10 engineer-days a week on portal work against an 8-ticket ceiling implies ~1.25 engineer-days per ticket, and only ~7 of 13 weeks are freeze-free — so publish **8/week as a peak-week limit**, note the lower sustainable quarterly average, and let P5 measurement confirm it |
| P22 | **The four-person team is the outcome of a transformation** — people let go, others moved, four left with BigPicture | Reframes the model: not QA choosing a shared-service structure, but **the best operating model at a size the organisation already set**. Strengthens P21 — the out-of-scope list is the consequence of a capacity decision taken above QA, which gives it legitimacy and protects the team. **Editorial**: state the constraint neutrally in published pages ("following the team's reorganisation, BigPicture QA is a four-person team") with **no reference to people leaving** |
| P21 | **The trade-off is the out-of-scope / won't-do column itself** | Sharper than the proposed "predictability for honesty" framing because it is **concrete and countable**. The out-of-scope list stops being a boundary and becomes **the bill**: page 4 states the cost of this model is enumerated on page 2; page 2 states the list is the price of the capacity model, and says for each item whether the work stops or moves. Sarah can review a list of withdrawn activities item by item. The predictability question is answered by the **quarterly intake cycle** (P14) — connect the two on page 4 |
| P20 | **The team will never grow beyond 4 engineers.** The breaking point is **inflow**: more than **8 tickets per week** and every ticket above that is **automatically put on hold** | Fixed team size is a publishable strategic statement — capacity is permanent, so **scope reduction or waiting is the lever, not headcount**. The automatic hold is the strongest mechanism in the model: no judgement, no negotiation, demand above capacity becomes a visible number. **Observation for page 4**: 8/week equates slots to weekly throughput, which assumes ~1-week tickets and no freeze that week; freeze weeks push throughput near zero, so sustained inflow below 8 still accumulates. State 8 as a **peak-week** limit or note the freeze effect — and say P5 measurement will check it |
| P19 | **"Submit the closest match, triage reclassifies" moves onto page 1**, beside the request-type list | Kept on page 6 as well — different moments, and repeating this one sentence is right rather than redundant |
| P18 | **A ticket can be reopened up to one week from closure** | Tighter than the two weeks proposed, and it fits the fortnightly rhythm — a reopening stays inside the same release cycle. **Default**: reopening is for *"this does not answer my question"*, not new scope; beyond a week, a fresh request lands in current priorities |
| P17 | **Marek is the named contact; the whole 4-person team acts as deputies**, and most requests will be redirected to the team | Resolves the Anna/Sarah tension without picking a side — a name plus collective deputising, proportionate at four people. **Publish the redirection as a feature**: it signals the question goes to whoever can best answer, and stops the contact reading as a gatekeeper. **Default**: when a decision is needed and Marek is unavailable, **daily triage decides and the decision stands** — otherwise collective deputising means nobody decides |
| P16 | Training and enablement is **planned outside the queue**, but **affects team capacity** and must be **tracked in Jira** | Establishes a **third handling mode**: scheduled work — tracked in Jira, no WIP slot, still consumes capacity. Consequence page 4 must state: **the ceiling of eight is not a constant** — active scheduled work reduces effective slots. Mechanism mirrors the release ticket: **declared at triage, slots reduced accordingly**. **Defaults**: agreed at quarter start alongside the P14 intake cycle; needs its own required info (audience, format, duration, date). P6's training offer to Engineering is the first live instance |
| P15 | **BugCrowd work consumes WIP slots** and requires a **portal ticket, created by the QA Team** | No special treatment — competes for the same eight slots and stays visible. Second instance of a pattern worth naming: *everything QA does is a portal ticket, including the work QA raises for itself* — a better framing than the three-kinds-of-work taxonomy. **Defaults**: Medium by default, severity can raise it; page 4 notes volume is **externally driven and unpredictable**, the only intake the team neither schedules nor is asked for |
| P14 | Three triggers: **full regression** follows the **quarterly release schedule** (planned per quarter, known across the software department); **feature regression** is planned from the **ETA in the Epic**; and **all Epics should be defined and delivered to QA as Jira items at the start of the quarter** | **Biggest structural finding of this review.** "Submit early" is not advice, it is a **defined quarterly intake cycle** whose purpose is feeding epics to the AI tooling, surfacing gaps, and preparing test scenarios and automation placeholders. The operating model is **quarterly batch intake + continuous pull execution**, and the pages show only the second half. Rewrite page 1's early-submission section as a cycle; give page 3 a quarterly rhythm above the fortnightly one; **link the quarterly release schedule**. Large ask of PM and Engineering → page 2 section and top of the P1 walkthrough. Consistent with P10 — one ETA attribute serves planning, prioritisation and regression scheduling |
| P13 | **The whole QA team operates within CET**, so CET working days define the business day | **Defaults**: state CET working days and 10:00 CET triage; give a worked example (Friday 15:00 CET → Monday morning); **link or list the team's public holidays**, since a requester elsewhere has no reason to know the team is off and unexplained silence is the exact failure mode *never silence* exists to prevent |
| P12 | **Held tickets are reviewed daily**, and the intention is to keep it that way; possibly **twice a week** if volume grows | Stronger than recommended, in the opposite direction. Closes the invisible-backlog risk. **Publish it as a service promise** — "every held ticket is looked at every working day" pairs with *never silence*. Also the **first stated scaling trigger** in the set; write it as a plan, not an aside. **Defaults**: keep the two hold reasons distinguishable; **no maximum hold duration** while review is daily |
| P11 | **No standing forum for cross-team priority conflicts.** An **ad-hoc session** is held when one arises | Proportionate, but needs a trigger or it means "whoever escalates hardest". **Defaults**: triggered when daily triage cannot resolve it; convened by QA (Marek); **the managers attend together, not separately**; outcome recorded on both tickets. Together-not-separately is what keeps QA out of the middle as arbiter |
| P10 | **The target shipping date should be part of the requirements, authored by Product Management** | Removes the problem rather than mitigating it — the shipping signal becomes a documented epic attribute, not hearsay. Both halves of the demotion rule now rest on documented inputs (P9 the SDLC bar, P10 the target date), neither is QA's judgement. Side effect: a documented target date can be compared with **"Needed by…"** and the discrepancy raised at triage. **"Should be" = an ask** — goes in the page 2 *What QA needs from other functions* section and on the P1 walkthrough list. **Alignment**: add target date to the SDLC criteria and `requirement_standard.md` |
| P9 | **The SDLC defines what a complete Epic looks like**, and the **AI Requirement Reviewer judges against those objective criteria** | The bar is the organisation's own standard, not QA's — QA applies a rule it did not write. Traceability comes free: the reviewer's findings are the evidence for a demotion. **Defaults**: link the SDLC rather than restate it; record findings on the ticket; supplying what is missing **restores priority**; the **Q16 human-in-the-loop rule still applies** — QA reviews the output before a priority change. **Supersedes** the earlier note to align `requirement_standard.md` with the DoR list — the target is the **SDLC definition** |
| P8 | When the estimate does not fit the deadline, **"we reach out to the requestor and start the discussion"** — the team, not the individual | Third situation with the same answer (Q6b unclaimed deadline, Q18b parking, P8 estimate overrun). **Consolidate into one published principle**: *when QA cannot meet what a requester expected, it says so on the ticket and opens a conversation, as a team*. One rule covers the cases nobody has thought of. Estimates should also state whether they **span a release freeze** |
| P7 | **A blocked ticket frees the WIP slot** | WIP now measures what is actively being worked, not what is nominally held. **Defaults**: the ticket returns to the queue keeping its priority; whoever has capacity pulls it when the answer arrives; the rule covers anything waiting on someone outside QA. State the reason on page 3 — *capacity is not held hostage to other teams' response times* |
| P6 | **Engineering will accept the observability assets** — they co-built and co-maintained them. Little maintenance, practically no development. **New work is theirs**; QA provides **training or documentation on request, through the portal** | Not a handover to a stranger but QA **withdrawing from shared ownership** — reword page 2 from "inherited by Engineering" to "built and maintained jointly; Engineering continues as sole owner". Residual obligation is bounded and visible because it is requestable. Use it as the **worked example for the enablement category**. **Severity downgraded from blocking** |
| P5 | **The QA Team owns measurement, mostly through Marek Wyszyński** | **Defaults carried forward**: measurement starts when the pages go live; reported at the monthly Team Retrospective; **intake by category** first; page 4 says when provisional figures get revisited. **Feeds P17** — Marek is now contact point *and* measurement owner, making the key-person finding larger than when written |
| P4c | **The 2.0 FTE includes release work.** During a freeze, **only release work and automation happen** — no requests are taken in | **Corrects page 3**, which says "no other work is tackled": automation *continues* through a freeze, so the automation half is protected even during releases. Page 4 should state the consequence — with a freeze every fortnight, roughly half the portal half goes to releases — as the explanation for why completion dates are not published. Page 1: the queue moves **between** freezes, which is the real argument for submitting early |
| P4b | **QA is occupied about a week per release**: ~2 days testing, ~2 days verifying fixes (**the team is working to reduce this**), plus **1 FTE of CI work per release** split across the 4 engineers. **Capacity is 2.0 FTE and is not open for discussion** | Recorded as stated; capacity is not reopened. Publish the fix-verification reduction as a **named improvement target** — it turns a cost into a visible efficiency programme. **P4c open**: purely definitional — does 2.0 FTE include release work or sit alongside it |
| P4 | **Releases roughly every two weeks — 5 to 6 per quarter**, varying with public holidays | **Reframes the freeze from an event into a rhythm.** The pages say *"while a release is running"*, implying something occasional; at a fortnightly cadence it is the operating pattern, with portal work happening in the gaps. Makes "submit early" far more persuasive, and means an estimate given at pickup must say whether it spans a freeze. **P4b open**: duration, and whether the freeze occupies all four engineers |
| P3 | **Support assesses severity**, from the customer's request. **Absolutely Critical = the system is down and unusable, or a major data loss incident.** QA accepts the assessment and verifies | Bounded by two named system states rather than a judgement about impact, so the carve-out cannot inflate. QA never argues the label. **Write the definition down despite it being "widely known"** — same pattern as the release freeze. Documentation-bar half moves to **P9** |
| P2 | **No dedicated Product Management page.** Page count stays at six | **Default carried forward**: one headed section on page 2 — *What QA needs from other functions* — covering **Product Management, Engineering and Support**, each with what happens when the input is missing. Better than a PM page: it gives the P1 walkthrough a single artefact and shows the three functions' dependencies side by side |
| P1 | Affected functions will be **walked through the pages**, with **Q&A sessions** where needed and a **comms plan**. Most decisions are **not new** — people are already aware | Awareness ≠ agreement, and two items *are* new: **incident assistance strictly via the portal** (changes Engineering and Support behaviour mid-incident) and the **observability inheritance** (an inheritor cannot be assumed into accepting). Spend the walkthrough there. Add a **"reviewed with [function], [date]"** line to pages 2 and 3 |
| X3 | **"24 business hours" means 24 hours of elapsed business time** — triage at the next daily meeting, **next business day at the latest**. The commitment was always the strong one; the phrase is what misleads | Rewrite as "read at the next daily triage meeting, 10:00 CET every working day — at the latest the next business day". P13 (whose business day) still open |
| X2 | An early submission is **put on hold until the work can start**, shown by a **Jira status and a comment**. Reuses the existing hold mechanism (reason + point in time) | Consequence: the hold list becomes the team's **forward book**, not an exception list — so P12's review cadence matters more, and the two kinds of hold (*not yet startable* vs *parked for capacity*) need distinguishing. **Default carried forward**: page 1 should say early submission buys preparation, not speed |
| X1 | **No exception to portal-only.** Critical production issues run **Support → Engineering (L3) → QA**, and QA assistance is requested **strictly through the QA Portal**. QA is third in line, not first responder. Reclassify on page 5 from *QA-raised* to *requestable in an incident context by Engineering or Support*. **"From now on" = a change** needing Support and Engineering agreement (feeds P1) |

## Third review — complete, pages at v2.1 (2026-09-22)

Full re-grill of all six pages as a published set, in `page-review-round-3.md`. Question: **where does the argument start when this is published?** Found 7 defects (C1–C7), 10 discussion generators (D1–D10), 7 editorial fixes being applied without asking (E1–E7).

| # | Decision | Notes |
|---|----------|-------|
| C1 | **The hold mechanism is slot-based: a ticket is held when no WIP slot is free.** Eight per week stays as the **published planning figure**, not as the trigger | Was the original intent; the arrival-counting phrasing was the drafter's. Automatically correct during freezes, while scheduled work runs, and when long tickets still occupy slots — none needs a special case. Also verifiable by the requester against the Jira filter |
| D2 | **The quarter-start expectation covers only feature/initiative/epic testing.** Everything else is normal mid-quarter business. Within that scope, **a large epic arriving mid-quarter with an ETA of ~a week is pushed back** — because the preparation cannot be compressed, not because it arrived late | Pages scope the ask explicitly so other categories stop looking non-compliant. Pushback written as a conversation about date or scope, not a refusal — reuses the page 3 rule that QA raises it on the ticket, as a team |
| D5+D6 | **Drop both the reorganisation backstory and "the team will not grow beyond four".** The sentence becomes *"The team is four engineers, and the model is built for that size — it does not assume growth"* | Fixed on README, pages 2, 3 and the page 4 capacity table. "The lever is scope, not headcount" survives and does not depend on either framing. Out-of-scope list keeps the consequence, drops the history — it is what four engineers cannot cover. Reorg context stays here in MEMORY only |
| D9 | **Do not publish the ~50–55 requests/quarter throughput figure yet.** It assumes a fixed ticket size that has not been measured. **Revisit at end of year** | Refinement applied: 8/week and 2.0 FTE are both already published, so ~1.25 engineer-days/ticket is derivable by anyone. Page 4 therefore **acknowledges the unmeasured ticket-size assumption and names end of year as the checkpoint**, while publishing no quarterly total |
| D4 | **Holds get a four-week review horizon.** Where there is **no progress on the engineering side**, QA contacts the requester and **closes the ticket** | Written as **two outcomes** so it does not collide with the quarterly forward book: a planned wait with a known date **continues**; a hold with no progress and no date is **closed after contacting the requester**. Closure is not a refusal — resubmit when engineering is ready. Comes back as a **new request**, not a reopen (the one-week reopen window covers "this does not answer my question") |
| D7 | **Reframe page 2's "What QA needs from other functions".** Heading becomes **what QA depends on**; columns become **what QA relies on** / **what happens without it** | Mechanics, not obligation and penalty. Content identical. **DoD sign-off row cut** — the epic not closing is the SDLC working normally, not a QA consequence, and it made the table look padded |
| D8 | **Escalation continues past QA:** ticket → daily triage → Marek Wyszyński → **Senior QA Manager** → **SW Director for BigPicture** | Published as **roles, not names**. Underwrites the absolute rules elsewhere (no out-of-portal work, no exceptions by size, QA does not argue the severity label) — an absolute rule with a published appeal route reads as a team position rather than stubbornness |
| C4+C5 | **No waiver. The team does not release with blockers, period.** The round-two "known regression may ship under a recorded waiver" edge case is **overturned** | Removes the contradiction outright — no grantor to name. Pages 2 and 3 collapse to one position: a below-threshold RUM result and a bug of severity ≥ Medium both stop the release, no exception path. **"Not assessable"** survives as the only nuance (no defined threshold is never a pass). C5's absolute **stays and is also attributed** to the existing severity rules — citing organisational policy is harder to argue with than asserting QA's own |
| C7 | **CI work is out of scope.** QA only **triggers the software builds as part of a release** — no troubleshooting, no CI requests. **Overturns the round-two "1 FTE per release for CI"** | Release cost resolves to ~2 days release testing + ~2 days fix verification ≈ **10 engineer-days, one week of the portal-and-release half**, derived rather than asserted. **Boundary that must be stated:** QA still investigates its **own failing automated tests** (its test code, automation half); the **CI platform** — agents, pipelines, build infra — is DevOps. Without it, pages 2 and 5 look self-contradictory. Page 2 out-of-scope list gains CI troubleshooting; page 5 marks CI platform work Stopped |
| C2 | **Daily review of held tickets, full stop.** Twice-weekly hedge deleted from page 3 | |
| C3 | **A blocked ticket is put On hold** — the status the team has, and it **pauses the SLA clock** | Simpler than the finding assumed: no fourth state. Page 1 keeps three outcomes, gains *blocked on someone else* as a hold reason and explains why the assignee comes off |
| C6 | **Training and enablement is requestable any time**, and is **scheduled rather than queued** — planned into the next cycle | |
| D3 | **A dedicated Jira project holds everything the QA team handles** — portal counterparts, automation, BugCrowd, training prep, release activity | Strongest answer in the round. Converts *"we are full"* from an assertion into something a requester can **verify**, which is what makes the C1 slot rule credible |
| D10 | **Change proposals go through the QA Portal.** Read at triage, changed at the monthly review, published with a new version | |
| D1 | **An estimate is a completion time in elapsed business days plus a delivery date** (e.g. "10 business days, delivered by 6 October"), given **by the QA team**, not an effort figure | Closes the highest-frequency trigger in the set. Page 1 also gains the WIP arithmetic openly — 2 tickets at a time, 1.25 engineer-days each per week — so a 10-day estimate on 3 days of work reads as mechanics rather than padding. Page 4's "no completion promise" needs tightening: no completion **SLA** up front, but a **date per ticket** once picked up |

---

**Second-round Q&A complete, pages corrected (2026-09-22).** All three contradictions, all 24 findings and all 8 assumptions answered, and all six pages rewritten to match. Pages are now **v2.0, draft for review**.

What the rewrite changed, beyond applying each answer:

- **Response commitment** reworded everywhere to "read at the next daily triage, 10:00 CET — next business day at the latest", on CET working days. The misleading "24 business hours" phrase is gone from the published pages.
- **The quarterly cycle is now the spine**, not an aside. Every epic in Jira at quarter start; QA prepares scenarios and automation placeholders before anything is requested. It is what replaces a completion-time promise, and it is stated as such on page 4.
- **Two rhythms** — quarterly intake and the fortnightly release — are described together on page 3, since neither makes sense alone.
- **The out-of-scope list is reframed as the bill** for a four-engineer team, on page 2, cross-referenced from page 4. It is meant to be challenged item by item.
- **Team size is stated as fixed** wherever capacity is discussed, so the answer to "what if this is not enough" is scope, never headcount.
- **A2 reworded from "being wound down" to stopped.** Page 6 carries a TBC to sanity-check A5 (Azure DevOps availability) against the live portal.
- **Page 5 gained a "Scheduled" classification** for enablement work, which consumes capacity without taking a WIP slot.
- **Page 6 is marked as being written by the QA team**; pages 1–5 publish without it.

**Added by the third review**
- Set up the **QA work Jira project** holding everything the team handles — the visibility mechanism several capacity claims now rest on
- Confirm the **On hold** status pauses the SLA clock in the portal configuration
- Confirm the **one-week reopen window** is configured
- Agree the **CI boundary** with DevOps and Engineering: QA triggers release builds only; CI platform work and CI requests go to DevOps
- Measure **average ticket size** from go-live; revisit the eight-per-week assumption **at end of year**

**Not started**
- Publishing to Confluence
- Capturing the screenshots page 6 needs
- Creating the Jira filter, and collecting the severity-rules and Slack links

---

## Decisions settled

All nineteen, below. This table is the authoritative record of what was decided and why.

When a decision is settled, record it here as a row with the question number, the decision in one sentence, and the reasoning if it was not the recommended answer.

| # | Decision | Reasoning if it differed from the recommendation |
|---|----------|--------------------------------------------------|
| Q1 | The ways of working are published as **Confluence pages, one audience each** (see structure below) — five at the time of answering, **extended to six by Q5** | Recommended answer accepted as-is |
| Q2 | **English only**, on all five pages including the internal appendix, with a glossary expanding the internal acronyms | Stronger than the recommendation, which had allowed Polish to remain in the appendix. Rationale given: the company is international |
| Q3 | **Single scope principle**, with the existing lists demoted to worked examples. Three specific calls: release blocker testing **in scope**; BugCrowd **in scope** and staying with the QA team; Kibana, DataStudio and dashboards **out of scope**, the team is exiting those tools | The proposed "planned versus reactive" rule was rejected by the answers themselves — blockers and BugCrowd are both reactive and both in. Principle rewritten around *subject* instead of timing |
| Q3b | **Full observability exit. All dashboard and reporting assets are inherited by engineering.** RUM is retained in a changed role: QA **reviews RUM event dashboards before a release** to check for performance regression across modules | Went further than the recommendation, which had proposed a phased handover with a date. Rationale: apart from RUM these dashboards have no audience left — nobody acts on their results — so there is no live obligation to transfer, only maintenance cost to stop paying |
| Q3c | The RUM review is **part of the release process, not a portal request**. **Engineering owns the RUM Events portal**; QA only reviews the data shown there. Regression is judged against **thresholds set by Product Management and Engineering**, not by QA | Modelling followed the recommendation. Ownership did not: the recommended carve-out of RUM dashboards to QA was declined, leaving QA as an assessor working to criteria and tooling owned by others |
| Q3d | The RUM gate **blocks**. Within thresholds, the release proceeds. Below threshold, QA raises a **ticket to Engineering** naming the affected module and events, Engineering owns the fix, and **QA re-reviews** afterwards | Stronger than the recommendation, which had proposed an advisory report with the release manager deciding. The team chose a blocking loop instead |
| Q3e | A module with **no threshold is recorded as "not assessable"**, never as a pass. A **known regression may ship under a recorded waiver**, with the escalation ticket left open | Both as recommended, and confirmed to be current practice already — the gap was in the documentation, not the process. **RUM branch closed** |
| Q4 | **QA files bugs it finds; QA does not file bugs on behalf of Engineering, Product Management or Support.** A **release blocker is severity ≥ Medium**, under severity rules that already exist and will be linked. **QA does create BugCrowd issues** | The distinction is *on whose behalf*, which is sharper than the recommended framing |
| Q4b | A release blocker is a bug raised **during the Release Testing activity** — severity alone is not enough. **No bug of severity ≥ Medium is ever released.** Severity assignment follows existing written rules and is not reopened | Structural consequence: because blockers come from QA's own Release Testing rather than from a request, **release blocker testing is a release-process activity, not a portal intake category** — the same pattern as the RUM review. This also cancels the earlier worry that out-of-scope bug testing would shrink to Low severity only; requester-submitted bug testing stays out of scope at every severity |
| Q5 | **Deadline-aware prioritisation**, using the **"Needed by…"** field that already exists in the portal form. But a deadline does not create capacity: some requests, such as testing a whole feature at the last minute, are **not feasible at short notice** regardless of the date given. **Portal mechanics — form, fields, screenshots — become a separate sixth document** | Mostly the recommended option (c). The feasibility limit was added by the user and matters: deadline ordering decides what comes first among things that *can* be done. What QA does with an unachievable date folds into the Round 2 capacity question |
| Q6 | **Pull, with no assignment by anyone** — not Engineering, not PM, not the QA lead. Tickets are **triaged daily** and whoever has capacity picks one up. Queue items have **no assignee until pulled** | Option (a), not the recommended hybrid. Consequence: the §7 area-ownership risk becomes an **accepted risk** rather than an open question, since the team is now generalist by policy and needs a mitigation for uneven product knowledge |
| Q6b | **Ordered pull**: tickets are taken **by priority**, set at the **daily triage meeting**. The team is **4 QA Engineers** with a **WIP limit of 2 each**, the limit existing because engineers also **automate test cases as part of daily work**. An unclaimed ticket with a tight deadline gets a **comment and a discussion** | Ordered pull as recommended. The unclaimed-ticket rule is lighter than the recommended age-based trigger — it relies on the daily triage noticing. Acceptable at four people; the first thing to revisit if the team grows |
| Q7 | The triage window is **24 business hours**, not 24 hours flat. The **triage meeting is daily at 10:00 CET** and is owned by the team, not a rotating individual | As recommended on the business-hours point. A standing daily meeting replaced the recommended rotating duty, which suits a team of four |
| Q7b | When a ticket is returned for missing information, **the clock stops** and resumes when the requester responds. Settles the §4 vs §5.1 contradiction in favour of *return*, not *block* | As recommended. **The second half is still open**: whether an unanswered return is ever closed. Not assumed — parked as an explicit gap |
| Q8 | The pages are **maintained by the QA Team**, **reviewed monthly during Team Retrospective Sessions**, with **Marek Wyszyński as first point of contact** | Collective ownership with a named contact, rather than the recommended single owner. The review rides on an existing meeting instead of a new cycle, and stays monthly rather than dropping to quarterly |
| Q9 | **50/50 split** between portal work and test automation — a company expectation, expected to shift further toward automation. **Intake not yet measured**, believed modest. **The WIP ceiling is never exceeded**; at the ceiling the team negotiates the deadline or parks other work, case by case at daily triage. Requesters are asked to **submit early, ideally at the start of the quarter** | Gives 2.0 FTE of portal capacity. Two things must be stated rather than hidden: the split is moving, so SLAs derived from it will need revising; and intake is unmeasured, so the SLA numbers are provisional until it is |
| Q10 | **Two-tier service levels.** A **firm response commitment** — triage within 24 business hours at the daily meeting — plus **typical completion ranges** per category that are indicative, not guaranteed, and assume the queue is below the ceiling. At the ceiling the date is **negotiated at triage**. The page states the assumed 50/50 split and that intake is unmeasured, so figures are provisional | As recommended. Replaces the §6 table, whose numbers were unachievable once the capacity model was known: 2.0 FTE across up to 8 in-progress tickets gives each about a quarter of an engineer, so 3 days of work takes ~12 business days against a published 3–5 day SLA |
| Q11 | **Three kinds of work, not two.** Ten categories are **requestable by anyone** (feature testing, automation, performance, new test cases, JCMA, Azure DevOps, shift-left review, documentation, training, Event Manager). **Regression after initiative delivery is a QA-raised portal ticket** — the team knows when it is due and raises it itself. **Release blocker testing, the RUM review, TR and Sanity are release-process work.** **BugCrowd is standing intake** from the platform | The sorting was as proposed, but the answer added a third kind: the portal is **not only an external intake**, QA also raises tickets in it for planned work nobody requests. The requester page must not imply everything in the portal came from a requester |
| Q11b | **Release work pre-empts everything.** While a release is running, no other work is submitted and none is tackled — long-standing practice, not changing. **One Release ticket** in the portal represents the effort; the detail lives in **linked Jira tickets visible to everyone** | The recommendation to track release work as multiple WIP-consuming portal tickets was declined, and does not need to be adopted — one ticket plus linked Jira issues already gives visibility. Obliges the pages to state that completion ranges exclude release periods, and that requests submitted during a release wait, urgent ones included |
| Q11c | Release status is visible through Slack **`#bp-status-release-feature`** (exists) and a **Jira filter showing all QA tickets** (**to be created**). **Daily meetings run even during a release**, if only to add comments to tickets — **"there will never be silence on our end"** | Publish the no-silence commitment as a stated service promise, not a process detail. The Jira filter is an **action item**, a prerequisite for the requester page |
| Q19 | **Generalist by design** — the team is too small to specialise. Depth is replaced by **knowledge sharing, AI tooling, documented test cases and a required clear feature description**, so the **need for in-depth knowledge is minimised** | **This is the organising principle of the whole model** — state it once, explicitly, and derive the rest from it. It also explains Q13b's documentation-demotion rule: incomplete docs are the one thing shared knowledge cannot compensate for. **Residual risk to state honestly**: the model holds while requirements are good; depth is genuinely traded for flow |
| Q18b | Triage **always leaves a comment**, one of three: the issue is **picked up**, it **needs additional information**, or it is **on hold until a stated point with the reason clearly given** | Closes the silence gap Q18 opened and makes good on Q11c. The **hold comment** is the valuable one — a reason plus a date lets the requester re-plan, escalate or reduce scope. Also supplies the **parking rule** outstanding from the WIP-ceiling discussion. **Default carried forward**: §6's four figures are no longer commitments — drop them or relabel as *typical past durations* |
| Q18 | **No published completion ranges.** Effort is **estimated by the QA engineer who picks the ticket up**, communicated only then. The banded small/medium/large proposal was **declined** | Removes the second tier of the two-tier service model: QA commits to a **response**, not a completion date. The pages must say this is deliberate, or it reads as an omission. **Q18b open**: what the requester hears between triage and pickup, and whether §6's four existing numbers survive |
| Q17 | **DoR and DoD are epic-level standards shared with Engineering, not QA portal rules.** DoR: clear functionality description, very clearly defined acceptance criteria, stated implementation out-of-scope, relevant Figma designs. DoD: Eng + QA work complete **and PM sign-off**, which is **outside QA scope** — *"we provide the results of testing the implementation and that is it"* | The earlier idea of collapsing DoR into §5 required-info and DoD into Q14b closure was **withdrawn as wrong**. **Keep two pairs distinct with different names**: epic DoR vs. portal request completeness; epic DoD vs. portal closure. Acceptance criteria are an **input QA consumes**, authored in the epic. QA supplies results and does not sign off — same pattern as Q14 (verify, not own) and RUM (review, not set thresholds). **Raises M17**: the QA pages should reference DoR/DoD, not define them. Align `requirements-review` skill and `templates/requirement_standard.md` with the DoR list |
| Q16 | Shift-left is an **asynchronous review** using **AI-assisted tooling**, with **QA reviewing the tool output** before returning **additional questions** to the requester. **Not** meeting attendance | Settles §2/§6 against §7 in favour of the queued async reading, so it stays inside the pull model and the 2-business-day service level; downgrade the §7 *meeting overload* risk. **Publish the human-in-the-loop step**, not the AI — the deliverable is QA's judgement. Deliverable is **questions, not a verdict**. Tooling already exists: `AI in QA/Skills/requirements-review/` plus `templates/requirement_standard.md` — link it (partly answers N7). Clock stops once questions go back (Q7b) |
| Q15 | **No work arriving outside the portal is tackled.** The requester is **always redirected**. The proposed trivial-question carve-out was **declined** | "Always" is the point: no threshold means no estimating, and the refusal belongs to the team rather than the engineer. **Rewrite note**: define "work" so the rule does not read as "do not talk to QA" — answering a question is not work; anything needing an environment, a test run, or producing an actionable result is |
| Q14 | **No production-issue handling**, with one exception: **absolutely Critical** issues where **QA verification is needed**. Verification is the only help provided | Two limits, both load-bearing: severity (*absolutely Critical*) and activity (**verify only** — no investigation, reproduction, triage or ownership). Publish close to the original wording. Becomes the **third scope carve-out** alongside release-critical testing and BugCrowd. Closes C15 |
| Q14b | At completion QA **closes the ticket as Done**, adds a **fitting comment**, and **links any artifacts** produced | Dissolves both §5.4 TBDs — no delivery-report template, no testing-report template; a comment plus artifact links replaces them. QA closes; there is **no requester acceptance step**. **Default carried forward**: Done when testing completes *whatever the outcome*, bugs raised as separate linked issues, so WIP is never held hostage to other teams' fixes. Reopen window left to the rewrite |
| Q13b | **"Needed by…" is the main determinant** of ordering. **High/Highest** is reserved for **release-related work** and **Critical production issues** needing QA assistance. Priority is **lowered** when Engineering or PM indicate the feature is not shipping soon, or documentation is massively incomplete | The demotion path is the counterweight to a date-driven queue: a date is a claim QA verifies, not a fact. Publish it as expected behaviour on the requester page. Incomplete documentation demotes rather than rejects, giving triage a third option. **Raises C15**: production-incident support is a scope carve-out not yet listed |
| Q13 | **Standard Jira priority scale.** Every request arrives as **Medium** by default; **QA assesses and re-assesses at triage**, taking the **"Needed by…"** field into consideration | Default-to-Medium is deliberate and removes the priority field as a requester lever — say so on the requester page. Priority is re-assessed as dates approach, so no resubmission or escalation is needed. **Q13b open**: what moves a ticket above Medium |
| Q12 | QA **creates instances for its own work** — release process, testing and verifying features — but does **not provide instance creation as a service** to external parties | §3 and §8.3 were never in conflict: §3 means "not for you", §8.3 is internal enablement. Environment effort is **absorbed into the completion range** of the category it serves, never quoted separately. §5's "environments to test" field applies only to **existing shared environments** (AAN, develop, preprod) |

---

## Critical findings — all closed

Fifteen Critical findings were raised. Fourteen are resolved, one was withdrawn. The full record, including the original wording of each, is in `review-report.md`. Nothing Critical now blocks publication except the three missing links.

---

## Confluence page structure

Confirmed by Q1 on 2026-09-21, **extended to six pages** by Q5.

1. **Requesting QA work** — requesters
2. **QA Portal scope** — requesters and managers
3. **How the QA team works** — QA team and managers. Also holds **release-process activities** (the RUM review, release blocker testing) which are *not* portal intake
4. **Service levels and measures** — managers
5. **Appendix: QA activity inventory** — QA internal
6. **Using the QA Portal** — requesters. A walkthrough of the portal itself: the form, its fields (including **"Needed by…"**), and screenshots. Agreed as a separate document because portal mechanics and ways of working change at different rates

---

## Working method

The session follows the `grilling` skill: work the decision tree, always with a recommended answer attached to each question, and recompute the frontier as answers land. Facts are researched rather than asked about; only decisions go to the user. The session ends when the frontier is empty.

**Delivery mode: one question at a time**, at the user's request (2026-09-21), rather than a whole round per message. Round grouping in `open-questions.md` still sets the order and the dependencies.

Relevant skills installed globally at `~/.cursor/skills/`: `grilling`, `grill-me`, `grill-with-docs`, `domain-modeling`, `setup-matt-pocock-skills`.

---

## Repository context

- Repo: `/Users/marek.wyszynski/repo/DOCS`, remote `docs` → `https://github.com/marekwyszynskiappfire/docs`
- `AGENTS.md` and `docs/agents/` were scaffolded on 2026-09-21 and are intentionally **uncommitted** at the user's request
- Related material elsewhere in the repo: `AI in QA/` (Xray import, AI-assisted test creation) and `QA Work Tracking/`. Finding N7 flags that the portal process and the Xray work are not yet cross-referenced

---

## How to resume

The grilling and the rewrite are both done. What remains is publication.

1. Read this file, then the pages in `Ways of Working/`.
2. Fill the three `[LINK TBC]` placeholders: the Jira filter, the severity rules, the Slack channel.
3. Capture the screenshots page 6 needs, and confirm the live form's request types and field names.
4. Confirm or correct the defaults table above, and settle N6 and the two parked questions.
5. Publish to Confluence via the Atlassian MCP integration (authentication may need renewing — it has timed out before), one page per audience.

`WoW.md` is superseded by the six pages. Keep it until publication as the record of the original whiteboard rendering, then archive it.
