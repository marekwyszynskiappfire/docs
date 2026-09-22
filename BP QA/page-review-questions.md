# Page review — questions arising

A second review, this time of the drafted pages in `Ways of Working/` rather than the original `WoW.md`, read through all seven personas in `personas.md`.

**Scope of this review.** The first round settled *what the team does*. This round asks whether the pages can be **used** by each audience without asking a person — and whether anything in them is now wrong, unowned, or quietly assumed.

**Last updated:** 2026-09-21

**Session in progress.** Questions are being worked one at a time, in the order below. Answers are recorded here as they land; **the pages themselves are corrected at the end of the session**, in one pass, not question by question.

| Status | Item |
|--------|------|
| **Complete** | All findings and all assumptions answered |
| Next | Correct the pages in one pass |

| Severity | Count | Meaning |
|----------|-------|---------|
| **Blocking** | 6 | Publish without resolving these and the pages will mislead someone |
| **Important** | 11 | Should be settled before wide circulation |
| **Worth settling** | 7 | Improves the pages; will not break anything if deferred |
| **Assumptions to confirm** | 8 | Statements written into the pages that nobody actually decided |

Two personas produced most of the new material: **Inês Duarte (Product Manager)**, because the pages assign her work she was never asked about, and **Priya Raman (QA Engineer)**, because she is the one who has to apply the rules to a colleague standing at her desk.

---

## Contradictions in the current pages

These are not questions. They are places where the pages disagree with each other and one version has to go.

### X1 — Production verification arrives through a door the pages have closed

**Pages 1, 2, 3, 5** · **Personas:** Priya, Elena

Page 1 says QA "verifies absolutely Critical production issues **when asked**". Page 5 classifies the same activity as **Portal — QA-raised**. Page 3 puts it at the top of the priority order but never says how it arrives. And page 3 also says, absolutely, that work arriving outside the portal is never tackled.

All four cannot be true. A Critical production incident will arrive through an incident channel, at speed, from someone who is not going to fill in a form. Either that is a stated exception to the portal-only rule, or QA raises the portal ticket itself after the fact so the work stays visible.

**Recommendation:** QA raises the ticket itself, retrospectively if necessary, and the pages say so. That keeps the portal-only rule intact and keeps the work visible in the queue.

> ### ✅ Resolved — 2026-09-21
>
> **There is no exception. The escalation path is ordered, and QA is third in line.**
>
> | Step | Who |
> |------|-----|
> | 1. The issue is spotted | **Support** |
> | 2. Support contacts Engineering | **Engineering provides L3 support** |
> | 3. If QA assistance is needed, Support or Engineering — **mostly Engineering** — requests it | **Strictly through the QA Portal, from now on** |
>
> The recommendation is **declined in its mechanism and met in its intent**. QA does not raise the ticket; the requester does, through the portal, like everything else. The portal-only rule survives intact with no carve-out, and the work stays visible because it is a real ticket from the start.
>
> **Two things this fixes beyond the contradiction.** Page 1's "when asked" becomes a defined path with a named requester. And page 5's classification changes from *QA-raised* to **requestable, in an incident context, by Engineering or Support** — a narrower intake than the other requestable categories, and the pages should say so rather than implying anyone can file one.
>
> **The ordering is itself a boundary worth publishing.** QA is not first responder and not second. Support triages, Engineering owns L3, and QA is reached only when Engineering needs verification. That reinforces the *verify, do not investigate* limit with a sequence, which is harder to erode than an adjective.
>
> **"From now on" makes this a change, not a description** — see **P1**. Support and Engineering are being asked to adopt a new route into QA during incidents, when friction is least welcome. If they have not agreed to it, the first Critical incident will go around it. This needs explicit agreement from both before publication, and it is now the strongest instance of the "nobody asked the other functions" problem.

### X2 — "Submit early" and "test it when it is complete" pull against each other

**Page 1** · **Personas:** Tomasz, Daniel, Elena

Page 1 asks requesters to submit as early as possible, ideally at the start of the quarter. Feature testing, though, validates a *complete* feature. So an early ticket describes work that cannot start for weeks.

Nobody has said what happens to it in the meantime. Does it sit in the queue ageing, ordered by a "Needed by" date months away? Does it occupy a slot? Is there a state for "accepted, waiting for the feature"?

Tomasz will do the right thing, see nothing happen for six weeks, and conclude that submitting early achieved nothing.

**Recommendation:** name the state — a scheduled or accepted-not-started status — and say at triage when the work will begin. Early submission buys preparation time for QA; the page should say that is its purpose, rather than implying it speeds anything up.

> ### ✅ Resolved — 2026-09-21
>
> **The ticket goes on hold until the work can actually start, shown by an appropriate Jira status and a comment.**
>
> No new state is invented — this reuses the hold mechanism already settled in the first round, where a hold carries both a **reason** and a **point in time**. An early submission therefore reads as *on hold until the feature is complete, expected week N*, which is exactly the information Tomasz needs and does not currently get.
>
> **This changes what the hold list is, and P12 gets more important as a result.** Holds were conceived as the exception — work parked because the team is at capacity. If early submission is encouraged and every early submission is held, the hold list becomes the team's **forward book**: the largest and most informative view of upcoming demand, not a pile of problems. Two consequences for the rewrite:
>
> - it needs a **review cadence** far more than when it was an exception list (P12)
> - the two kinds of hold — *not yet startable* and *parked for capacity* — mean different things to a requester and should be distinguishable, whether by comment wording or by a reason field
>
> **Default carried forward, unaddressed:** page 1 should say what early submission actually buys. It does not make the work finish sooner; it gives QA time to prepare test cases and automation ahead of the work, and it makes upcoming demand visible so the queue can be planned. Stated that way, the request to submit early is persuasive. Left as it is, it reads as a request to wait longer.
>
> A held ticket has not been pulled, so it consumes no WIP slot. The related question — whether a ticket held *after* being picked up frees the slot — is still P7.

### X3 — The response commitment is weaker on paper than in practice

**Pages 1, 3, 4** · **Personas:** Tomasz, Elena

The pages promise triage within **24 business hours**. Taken literally that is three working days. But triage runs **every working day at 10:00 CET**, so in practice almost everything is read the next working morning.

The pages are under-promising by a factor of three, and the weaker number is the one requesters will plan around.

**Recommendation:** promise **the next working day's triage**, which is what actually happens, and keep 24 business hours only as the outer bound for submissions arriving just before a weekend.

> ### ✅ Resolved — 2026-09-21
>
> **The finding was a misreading, and the phrase is the problem rather than the commitment.**
>
> "24 business hours" means **24 hours of elapsed business time** — so a request submitted just after the daily meeting is triaged at the next one, **the next business day at the latest**. It was never the three-working-day promise that "24 business hours" suggests when read as 24 × working hours.
>
> So the commitment is already the strong one. What needs fixing is the wording, which is ambiguous enough that a reader can arrive at three days without misreading anything.
>
> **The rewrite states the mechanism, then the bound:**
>
> > Your request is read at the next daily triage meeting — **10:00 CET every working day**. At the latest that is the **next business day**, if you submit just after a meeting has finished.
>
> That is concrete, self-evidently true given a daily meeting, and it makes the daily meeting visibly the thing delivering the commitment rather than an implementation detail.
>
> **Still open as P13:** whose business day. A requester in New York or Bangalore needs to know the clock runs on CET working days, and the worked example should show it.

---

## Blocking

### P4c — Does the 2.0 FTE include release work, or sit alongside it?

**Personas:** Anna, Elena · **Page:** 4 · **Follow-up to P4b**

**This is not a question about how much capacity the team has.** That is settled at 2.0 FTE. It is a question about what the number on page 4 *counts*, because the page has to say, and the two readings produce very different guidance for requesters.

Three figures are now published together: **4 engineers**, a **50/50 split** between portal work and automation, and **about one week of release work every two weeks**. Those do not compose without knowing where release time sits.

| Reading | What 2.0 FTE means | What page 4 then says |
|---------|--------------------|-----------------------|
| **A — release sits inside the portal half** | 2.0 FTE covers portal requests *and* release work. Release consumes much of it, and what is left for requests is the remainder | Requesters should expect the queue to move mainly in the gaps between releases |
| **B — release comes off the top** | Release work is deducted first; 2.0 FTE is what remains, split with automation | The 2.0 FTE is the planning figure and needs no further discounting |

Elena needs this to answer "can we take this on?" at triage. Anna needs it because a capacity figure whose basis is unstated cannot be defended to a peer — the first person to do the arithmetic will ask, and the answer needs to be on the page rather than in someone's head.

**Recommendation:** state reading **A** explicitly — release work and portal work come out of the same half, and the queue moves between freezes. It matches the lived pattern the team has just described, it explains why completion times are not published, and it is the version a requester can act on. Whichever is chosen, page 4 should show the figure with its basis in one line, so nobody has to reconstruct it.

> ### ✅ Resolved — 2026-09-21
>
> **Reading A. The 2.0 FTE includes release work. During a freeze, only release work and automation happen; no requests are taken in.**
>
> This finally makes the three figures compose, and it corrects something I wrote into page 3:
>
> | | During a freeze | Between freezes |
> |---|---|---|
> | **Automation half (2.0 FTE)** | **Continues** | Continues |
> | **Portal half (2.0 FTE)** | Entirely on release work | On portal requests |
>
> **Page 3 is wrong as written.** It says that while a release is running "no other work is submitted and none is tackled", which reads as the whole team stopping. The truth is narrower and better: **no portal requests are taken, and automation carries on**. That matters — it means the automation half is protected even during releases, which is a stronger statement of the 50/50 commitment than the pages currently make.
>
> **An implication page 4 should state, not leave to the reader.** With freezes every two weeks and a week of release work in each, roughly half of the portal half goes to releases across a quarter. The 2.0 FTE is real, and the share of it reaching requests is smaller. This is not a reopening of capacity — it is the consequence of the numbers the team has given, and it is the single best explanation available for why completion dates are not published. Anna can defend "our capacity is consumed on a published rhythm"; she cannot defend a figure whose basis a peer has to reconstruct.
>
> **Rewrite consequences:** page 3's freeze description is corrected as above; page 4 shows the 2.0 FTE with its basis in one line and states what release consumes; page 1 tells requesters the queue moves between freezes, which is also the real argument for submitting early.

### P1 — Nobody has asked the Product Manager

**Personas:** Inês, Sarah · **Pages:** 2, 3

The pages make Product Management responsible for four things: authoring clear acceptance criteria, jointly defining RUM performance thresholds, signing off Definition of Done, and being a source of truth on whether a feature is really shipping — which changes a request's priority.

That is a substantial set of obligations assigned by another function's document. If no PM has agreed to them, the first time one reads these pages will be the moment they stop being credible. Sarah's version of the question is simpler: *who else has agreed to what this document assumes of them?*

**Recommendation:** review pages 2 and 3 with Product Management before publication, and record the agreement. If any obligation is not accepted, the page states the reality rather than the intention.

> ### ✅ Resolved — 2026-09-21
>
> **The affected functions will be walked through the pages, with Q&A sessions where needed, supported by a comms plan. Most of this is not new — people are already aware of the decisions.**
>
> That closes the finding as a process matter: publication is preceded by a walkthrough rather than an announcement, which is what the personas were asking for.
>
> **One distinction to hold on to while doing it: awareness is not agreement, and most is not all.** The walkthrough is cheap for the parts people already know, so it should spend its time on the parts that are genuinely new. Two items are new by the team's own account:
>
> | Genuinely new | Who has to change | Why it will not survive assumed awareness |
> |---------------|-------------------|-------------------------------------------|
> | **Incident assistance strictly through the QA Portal** — *"from now on"* (X1) | Engineering, Support | It changes behaviour during an incident, when friction is least tolerated. The first time someone skips it, the exception becomes the precedent |
> | **Observability assets inherited by Engineering** (P6) | Engineering | An inheritance is not a decision the inheritor can be assumed into. If nobody has accepted it, the assets return as an argument |
>
> Everything else — the scope rule, the pull model, the service commitments, the DoR and DoD split — is documentation of existing practice, and the walkthrough can move through it quickly.
>
> **Two things to produce alongside the pages:**
>
> - a **comms plan**, now an explicit deliverable rather than an afterthought
> - a **"reviewed with"** line on pages 2 and 3, naming the functions and the date. It costs one line and converts the pages from QA's statement about others into a shared one — which is exactly what makes them citable later

### P2 — There is no page for the Product Manager

**Persona:** Inês · **Pages:** all

Six pages, and the audience with the most obligations has none. Inês has to reconstruct her responsibilities from a scope page written for requesters and a process page written for the QA team.

**Recommendation:** either a short seventh page — *What QA needs from Product Management* — or a clearly headed section on page 2 that collects her obligations in one place. The seventh page is better; obligations buried in someone else's page get missed.

> ### ✅ Resolved — 2026-09-21
>
> **No dedicated page for Product Management.** The seventh page is declined; the page count stays at six.
>
> The underlying problem does not go away with it, though — Inês still has four obligations spread across two pages written for other audiences, and one of them silently decides whether a release can be assessed. So the fallback applies, and it is better than the PM-only page it replaces.
>
> **Default carried into the rewrite:** a single clearly headed section on **page 2**, *What QA needs from other functions*, collecting in one place what is expected of **Product Management, Engineering and Support** — the three functions the pages now make assumptions about, after X1 added the incident route. One section, three short lists, each stating what happens when the input is missing:
>
> | Function | Owes QA | If it is missing |
> |----------|---------|------------------|
> | Product Management | Clear acceptance criteria; RUM thresholds, jointly with Engineering; DoD sign-off; a reliable signal on whether a feature is shipping | No threshold means the module is recorded **not assessable**, not passed. Missing acceptance criteria make a request incomplete |
> | Engineering | RUM thresholds and the RUM Events portal; fixing regressions; the inherited observability assets; requesting incident assistance through the portal | The release gate cannot be assessed; incident work becomes invisible to the queue |
> | Support | Requesting incident assistance through the portal, after Engineering L3 | Work arrives outside the portal and is redirected, costing time during an incident |
>
> Collecting all three in one section is a better outcome than a Product Management page would have been: it gives the P1 walkthrough a single thing to walk through, and it puts the three functions' obligations side by side where the dependencies between them are visible.

### P3 — "Absolutely Critical" has no decider

**Personas:** Elena, Priya, Inês · **Pages:** 2, 3

The production carve-out turns entirely on the word *absolutely Critical*, and nobody is named to decide it. When Support or an incident commander says an issue is Critical, can QA disagree? If QA can, the pages should say so plainly, because Priya will be the one saying it. If QA cannot, the carve-out is effectively "whatever someone else labels Critical", which is unbounded.

The same problem, smaller, applies to **"substantially incomplete documentation"** in the priority-demotion rule.

**Recommendation:** name the decider. The most workable version is that QA accepts the severity assigned by the existing incident process — deferring to a rule that already exists — while the *activity* limit stays QA's own and absolute. For documentation, the bar is the Definition of Ready list, which is already written down and objective enough to cite.

> ### ✅ Resolved — 2026-09-21
>
> **Support assesses severity, from the customer's request. Absolutely Critical means the system is down and unusable, or there has been a major data loss incident.**
>
> | | |
> |---|---|
> | **Decider** | Support, based on what the customer reported |
> | **Definition** | The system is **down and cannot be used**, or a **major data loss incident** |
> | **QA's part** | Accepts the assessment. Verifies. Does not argue the label and does not investigate |
>
> As recommended in substance: QA defers to an assessment made elsewhere, so Priya never has to dispute severity with an engineer mid-incident. The definition is narrower than "Critical" in most severity scales — two named system states, not a judgement about business impact — which is what makes the carve-out bounded.
>
> **Write the definition down, even though it is widely known.** This is the same pattern as the release freeze in the first review: something the team considers common knowledge and therefore never records. It costs one sentence, and these pages are read by people who do not have the common knowledge. The sentence above is the whole of it.
>
> **The second half of this finding is unresolved and moves to P9** — "substantially incomplete documentation" is still an adjective with no published bar and no route to contest it.

### P4 — How much of the quarter is release?

**Personas:** Sarah, Anna, Daniel · **Page:** 3, 4

The pages state that release work pre-empts everything and that nothing else is tackled while a release runs. They never say **how often releases happen or how long they last**.

Without that, the capacity model on page 4 is unreadable. If releases consume one week in eight, 2.0 FTE is roughly right. If they consume one week in three, portal capacity is a third lower than the page claims, and every expectation built on it is wrong. Daniel cannot plan around a freeze of unknown frequency and duration.

**Recommendation:** publish release cadence and typical freeze duration on page 4, and state the resulting portal capacity after the freeze is deducted. This is arithmetic the team already knows and readers cannot do for themselves.

> ### 🔁 Partly resolved — 2026-09-21
>
> **Releases happen roughly every two weeks — 5 to 6 per quarter, varying with public holidays.**
>
> **This reframes the release freeze from an event into a rhythm, and the pages currently describe it as an event.** Phrases like *"while a release is running"* imply something occasional. At a fortnightly cadence, a freeze is not an interruption to the normal pattern; it **is** the pattern, recurring six times a quarter. Three things follow:
>
> - Page 3 should describe the release cycle as the **team's operating rhythm**, with portal work happening in the gaps between freezes — not as an exception that suspends normal service.
> - The "submit early" advice on page 1 becomes much more persuasive, and should carry the reason: a request submitted late has to fit between freezes, and there may not be room.
> - **Everything about elapsed time changes.** A ticket picked up just before a freeze does not simply take longer — it stops, and resumes after. The estimate an engineer gives at pickup needs to say whether it accounts for that.
>
> **Still missing: how long each freeze lasts** — see P4b. Cadence without duration does not give the capacity deduction the finding asked for. Six freezes of two days is about 18% of the quarter; six of four days is about 37%, which would put real portal capacity well below the 2.0 FTE on page 4.

### P4b — How long does each release freeze last?

**Personas:** Anna, Sarah, Daniel · **Page:** 3, 4 · **Follow-up to P4**

Six freezes a quarter is only half of the multiplier. Two days each takes roughly a fifth of the quarter out of portal capacity; four days each takes well over a third, and the 2.0 FTE figure on page 4 becomes indefensible.

The question is also *what counts as the freeze*. Test Regression, Sanity and the RUM review are all release activities, and they do not all last the same length or involve the whole team. If the whole team is committed for the full duration, the deduction is the full figure; if TR is two engineers for three days while the others keep pulling tickets, it is much smaller — but page 3 currently says **nothing else is tackled at all**, which asserts the larger version.

**Recommendation:** give the typical duration in working days from the start of release testing to release, and confirm whether the freeze genuinely occupies all four engineers or only some. Then state portal capacity on page 4 **net of release time**, so the published figure is the one people should plan with. If the honest answer is that the freeze varies from one release to the next, give the range and say what drives it.

> ### ✅ Resolved — 2026-09-21
>
> **QA is occupied for about a week per release.**
>
> | Release activity | Effort |
> |------------------|--------|
> | Testing | ~2 days |
> | Verification of fixes | ~2 days — **the team is working to reduce this** |
> | CI-related work | **1 FTE per release**, split across the 4 engineers |
>
> **Capacity is settled at 2.0 FTE and is not open for discussion.** Recorded as stated. Nothing below reopens it.
>
> **The fix-verification line is worth publishing as an improvement target.** Two of the five days per release go on verifying fixes, and the team is actively working to reduce that. Named on page 4, it turns a cost into a visible efficiency programme, which is a stronger position than leaving it inside an undifferentiated "release week".
>
> **One definitional point remains before page 4 can state anything — see P4c.** Not a question about how much capacity exists, but about what the published number counts.

### P5 — Measurement is described but not assigned

**Personas:** Anna, Sarah · **Page:** 4

Page 4 lists four things worth measuring, and correctly says that until intake is measured, capacity conversations are about impressions. It then stops. No owner, no start date, no reporting venue.

This is the finding that decides whether the next capacity conversation is different from the last one. Anna cannot argue for headcount from a page that says the numbers do not exist yet.

**Recommendation:** name an owner and a date for intake measurement, and a venue where it is reported — the monthly retrospective is the obvious one. One number, intake by category, is worth more than a measurement plan.

> ### ✅ Resolved — 2026-09-21
>
> **The QA Team owns measurement, mostly through Marek Wyszyński.**
>
> The owner question is answered, and page 4 can now name one rather than listing intentions.
>
> **Defaults carried into the rewrite, to be corrected if wrong:**
>
> - measurement **starts when the pages go live** — there is no reason to wait, and the first quarter of data is the most valuable
> - it is reported at the **monthly Team Retrospective**, alongside the page review that already happens there, so no new meeting is created
> - **intake by category** is the first and most important number; the other three on page 4 follow once it exists
> - page 4 states **when the provisional figures will be revisited** in light of it
>
> **This concentrates more on one person — see P17.** Marek is already the first point of contact on every page, and is now also the owner of the measurement that underpins the capacity argument. Each assignment is sensible on its own; together they make a single person the dependency for the process, the escalation path and the evidence base. That is the substance of the key-person finding, and it is now larger than when it was written.

### P6 — The observability exit assumes an inheritor who has not spoken

**Personas:** Sarah, Anna, Daniel · **Pages:** 2, 5

Page 2 says Kibana, DataStudio, Grafana, BigQuery and RUM rollout are "inherited by Engineering". Page 5 marks them **Exited**. The justification — that nobody acts on their output — is sound, but it is QA's assessment of someone else's need.

If Engineering has not accepted the handover, these come back, and they come back as an argument. Sarah in particular reacts badly to learning about a capability exit after the fact.

**Recommendation:** get explicit acceptance from Engineering, with a date, before publishing. If some assets genuinely have no owner, say that they are being **retired**, not transferred — that is a different and more honest statement.

> ### ✅ Resolved — 2026-09-21
>
> **Engineering will accept, because they never stopped being involved.** They participated heavily in building and maintaining these assets. There is little maintenance and practically no development. Any new work is theirs; **QA will provide training or documentation if needed, requested through the QA Portal.**
>
> The finding is largely dissolved by a fact the pages never stated: this is **not a handover to a stranger**. Engineering is an existing co-owner, and what is changing is that QA **withdraws from shared ownership**. That is a far smaller claim than "inherited by Engineering", and a far easier one to get agreement on.
>
> **Reword rather than renegotiate.** "Inherited by Engineering" invites the question *when did they agree to that?* The accurate phrasing is that these assets were **built and maintained jointly, and Engineering continues as sole owner**. Same outcome, no implied transfer, and it matches what people already experienced.
>
> **The residual obligation is bounded and visible, which is the right shape.** QA has not walked away entirely — training and documentation remain available — but they are requested through the portal like anything else, so the cost is capped and appears in the queue rather than as a favour. This is also a good **worked example for the enablement category** on page 2: the clearest illustration so far of what a training request looks like and why the category exists.
>
> **Severity downgraded.** No longer blocking. It remains on the P1 walkthrough list so Engineering hears it said out loud, but the risk of the assets bouncing back is low.

---

## Important

### P7 — A blocked ticket and the WIP limit

**Persona:** Priya · **Page:** 3

Carried over unresolved from the first round. Priya has two tickets; one is returned to the requester for missing information and the clock has stopped. Can she pull a third?

If yes, her real WIP can reach four. If no, her week stalls on someone else's response time. Both are defensible, neither is written.

**Recommendation:** a ticket waiting on a requester **frees the slot** and returns to the queue, keeping its priority. Otherwise QA's capacity is governed by other teams' response times.

> ### ✅ Resolved — 2026-09-21
>
> **Yes. A blocked ticket frees the slot.** As recommended.
>
> The WIP limit now measures what an engineer is **actively working on**, not what is nominally theirs — which is the only version that means anything. QA throughput stops being governed by other teams' response times.
>
> **Defaults carried into the rewrite:**
>
> - the ticket **returns to the queue keeping its priority**, so waiting on someone else does not cost a requester their place
> - when the answer arrives it is **pulled by whoever has capacity**, not necessarily the original engineer — consistent with nothing being assigned, and with the generalist model
> - the rule covers **anything waiting on someone outside QA**: a requester, DevOps, an environment, another team's fix
>
> **Worth stating on page 3 with the reason attached.** A reader who sees "blocked tickets free the slot" without the reasoning may read it as QA finding a way to look busy. Stated as *"we do not hold capacity hostage to other teams' response times"*, it is obviously the right rule and it reinforces why the clock stops as well.

### P8 — When the estimate does not fit the deadline

**Personas:** Priya, Daniel · **Pages:** 1, 3

The estimate arrives when an engineer picks the ticket up. So the moment where work turns out to be three weeks against a Friday deadline happens **mid-flight**, after triage, with one engineer holding it.

Page 1 tells requesters to say something if the timing is a problem. It does not tell Priya what to do when she is the one who discovers it.

**Recommendation:** the engineer comments with the estimate and takes it back to triage; triage handles the conversation, not the individual. Consistent with the principle that the team, not the person, carries difficult messages.

> ### ✅ Resolved — 2026-09-21
>
> **"We reach out to the requestor and start the discussion."**
>
> **"We", not "I"** — the team carries it, which is the substance of the recommendation. Defaults carried forward: the estimate goes on the ticket as a comment, and the discussion is opened from triage rather than left to the individual engineer to negotiate alone.
>
> **This is now the third distinct situation with the same answer, and the rewrite should say it once.** The pages currently describe three separate mechanics that are really one behaviour:
>
> | Situation | Settled in | Response |
> |-----------|-----------|----------|
> | Nobody picks up a ticket with a tight deadline | Q6b | Comment, start a discussion |
> | The team is at the ceiling and something must be parked | Q18b | Comment with the reason and the point in time |
> | The estimate does not fit the deadline | P8 | Comment, start a discussion |
>
> Written as one principle — **when QA cannot meet what a requester expected, it says so on the ticket and opens a conversation, as a team** — it is shorter, more memorable, and applies to the situations nobody has thought of yet. Written as three rules, it reads as three special cases and the fourth case has no answer.
>
> **One addition for the estimate case, given the fortnightly cadence:** the estimate should say whether it **spans a release freeze**. That is now a routine reason for a date not fitting, and it is information the requester cannot work out for themselves.

### P9 — The documentation bar is judged but not published

**Personas:** Inês, Daniel · **Pages:** 1, 3

Requests with substantially incomplete documentation are deprioritised. That rule is sound and it is well argued. But the bar is not published, the judgement happens in a meeting the requester is not in, and there is no route to contest it.

Inês will experience this as her feature being delayed by a standard she never saw. Daniel will experience it as a quality bar applied to his team that was never agreed.

**Recommendation:** cite the Definition of Ready list as the bar, since it is already written and agreed with Engineering; require the demotion to be recorded as a ticket comment naming what is missing; and state that supplying it restores priority.

> ### ✅ Resolved — 2026-09-21
>
> **The SDLC already defines what a complete Epic looks like, and the AI Requirement Reviewer judges against those objective criteria.**
>
> Better than the recommendation, on both counts. The bar is not a QA standard at all — it is the organisation's own SDLC definition, so QA is applying a rule it did not write and cannot be accused of inventing. And the judgement is made against stated criteria by tooling, rather than formed in a meeting the requester is not in.
>
> **This also answers the traceability half by construction.** The reviewer produces findings, so a demotion comes with its evidence attached rather than as an assertion. Inês can see exactly which criterion failed, fix it, and say so.
>
> **Defaults carried into the rewrite:**
>
> - the pages **link the SDLC definition** rather than restating it, so the two cannot drift — a new action item, below
> - the reviewer's findings are **recorded on the ticket** when they lead to a priority change
> - **supplying what is missing restores priority**, making the rule a prompt rather than a penalty
> - **the human-in-the-loop rule from Q16 still applies.** QA reviews the tool's output before it is acted on. A priority change should not be the one place where the AI's verdict lands unreviewed — that is the scenario where an automated judgement about someone's documentation quality goes wrong most visibly
>
> **Supersedes an earlier note.** The first round said to align `requirements-review` and `templates/requirement_standard.md` with the Definition of Ready list. The alignment target is the **SDLC epic-completeness definition**; if DoR and the SDLC say different things, that gap is worth raising with Engineering separately.

### P10 — An informal conversation can move the queue, invisibly

**Personas:** Inês, Anna · **Page:** 3

Priority is lowered when Engineering or Product Management "indicate" a feature is not shipping soon. That information arrives in a corridor, a standup, a Slack thread. It changes a queue position, and nothing records who said it or when.

Inês's objection is the sharp one: her request was deprioritised on the strength of something somebody said about her product area, possibly out of date, and she cannot correct it because she cannot see it.

**Recommendation:** any priority change is recorded as a ticket comment stating the reason and the source. Cheap, and it converts a rumour into something correctable.

> ### ✅ Resolved — 2026-09-21
>
> **The target shipping date should be part of the requirements, authored by Product Management.**
>
> This removes the problem rather than mitigating it. There is no corridor conversation to record, because the shipping date stops being hearsay and becomes a **documented attribute of the epic** — authored by the person best placed to know, visible to everyone, and correctable by its author at source.
>
> **Both halves of the demotion rule now rest on the same foundation.** P9 put the documentation bar on the SDLC definition of a complete epic; P10 puts the shipping signal in the requirements themselves. Neither is QA's judgement, both are checkable, and both are fixed by the requester rather than argued with QA. That is a considerably stronger position than the pages had an hour ago.
>
> **A useful side effect:** a documented target date can be compared with the requester's **"Needed by…"**. Where they disagree, the discrepancy is visible at triage and can be raised, instead of QA silently trusting one over the other.
>
> **"Should be" makes this an ask, not a description.** The pages should state it as an expectation of Product Management — which is exactly what the page 2 *What QA needs from other functions* section is for (P2) — and it goes on the P1 walkthrough list. If a target date is missing, the epic is incomplete under the P9 rule, so the two reinforce each other without needing a separate sanction.
>
> **Alignment item:** the SDLC epic-completeness criteria and `templates/requirement_standard.md` should both include the target shipping date, or the reviewer will not check for it.

### P11 — No forum for a conflict between managers

**Personas:** Daniel, Anna · **Pages:** 1, 4

Escalation is "comment on the ticket, then Marek Wyszyński". That works for one request. It does not work when two engineering managers need QA the same week and one of them is going to miss a commitment.

Daniel wants to know whether he can be in the room. Anna needs the decision to be defensible to the manager who loses.

**Recommendation:** name the forum where cross-team priority conflicts are settled — an existing planning or delivery meeting if one exists — and state that the outcome is recorded on the tickets. A decision a requester can see the reasoning for is one they can accept.

> ### ✅ Resolved — 2026-09-22
>
> **There is no standing forum. An ad-hoc session is held when a conflict arises.**
>
> Proportionate — a recurring meeting for a problem that may happen twice a quarter is overhead, and inventing one to satisfy a document is how process bloat starts.
>
> **But "ad-hoc" needs a trigger, or it means "whenever someone escalates hardest"** — which is the outcome the finding was about. Three details make it a mechanism rather than an absence, and they cost nothing:
>
> | Detail | Default carried into the rewrite |
> |--------|----------------------------------|
> | **Trigger** | Daily triage cannot resolve the conflict between two requesters' dates |
> | **Convened by** | QA — Marek Wyszyński — within a stated time of triage identifying it |
> | **Attendees** | The requesting managers and QA, together rather than separately |
> | **Outcome** | Recorded as a comment on both tickets, with the reasoning |
>
> **"Together rather than separately" is the part that protects QA.** Two bilateral conversations put QA in the middle, arbitrating between people who never hear each other's case, and the outcome looks like a QA decision that favoured someone. One session makes it a decision the managers reach with QA present, which is both more defensible and considerably less exposed.
>
> Page 4 can state this in two sentences: conflicts are normally settled at triage; where they cannot be, QA convenes a session with the managers involved and records the outcome on the tickets.

### P12 — Parked tickets have no review cadence

**Personas:** Elena, Anna · **Pages:** 1, 3

Tickets go on hold "until a stated point, with the reason given". Good. But nothing says the hold list is ever revisited, and Elena has seen exactly this become the new invisible backlog: a growing pile of work that was never declined and is never done.

**Recommendation:** review held tickets at triage weekly, and state a maximum hold before the ticket is either scheduled or closed with an explanation. An honest close beats an indefinite hold.

> ### ✅ Resolved — 2026-09-22
>
> **Held tickets are reviewed daily, and the intention is to keep it that way.** It may move to twice a week if ticket volume grows.
>
> Stronger than the recommendation, and in the opposite direction — I suggested relaxing to weekly, the team reviews daily and would only reduce under load. The invisible-backlog risk is effectively closed: nothing can age unnoticed when the whole hold list is read every working day.
>
> **Worth publishing, because it is a service promise and reads as one.** "Every held ticket is looked at every working day" is a strong statement for a requester whose work is parked, and it is the natural companion to *"there will never be silence on our end"*. Page 1 should say it.
>
> **This is also the first stated scaling trigger in the whole set** — a cadence that changes when volume grows. It is a small instance of what P20 asks for at the level of the whole model, and it should be written as a deliberate plan rather than left implicit: *reviewed daily today; twice weekly if volume makes daily impractical.*
>
> **Defaults carried into the rewrite:**
>
> - the two hold reasons stay **distinguishable** — *not yet startable* versus *parked for capacity* — since they mean different things to a requester and lead to different follow-up
> - **no maximum hold duration** while review is daily; the daily read is what an expiry rule would otherwise be protecting against. Worth revisiting if the cadence ever drops

### P13 — Whose business hours?

**Personas:** Elena, Tomasz · **Pages:** 1, 3, 4

The response commitment is in business hours and triage is at 10:00 CET. The company is international and the pages say so. A requester submitting at 17:00 in New York, or working in Bangalore, cannot tell when their clock starts or when they will hear back.

**Recommendation:** state the working hours and time zone the commitments run in, and give the worked example — submitted Friday afternoon CET, triaged Monday morning.

> ### ✅ Resolved — 2026-09-22
>
> **The entire QA team operates within CET, so CET is the business day.**
>
> Unambiguous, and it means one sentence fixes every time zone at once rather than needing a table.
>
> **Defaults carried into the rewrite,** on page 1 and page 4:
>
> - commitments run on **CET working days**; triage is **10:00 CET** every working day
> - a **worked example** — submitted 15:00 CET on Friday, triaged Monday morning — because an example is read where a rule is skimmed
> - the **team's public holidays** shift the clock. These are not the reader's holidays, so the pages should link a calendar or list them rather than leaving a requester in another country to guess
>
> The holiday point is the one that actually bites. A requester elsewhere has no reason to know the QA team is off, and a two-day silence with no explanation is precisely the failure mode the *never silence* commitment exists to prevent.

### P14 — What triggers QA-raised work?

**Personas:** Elena, Anna · **Pages:** 2, 5

Regression after initiative delivery is a QA-raised ticket because "the team knows when it is due". This is the same pattern the first review flagged as C14: practice that is real, reliable, and written down nowhere.

If it depends on someone noticing, it will eventually not be noticed.

**Recommendation:** state the trigger — an initiative reaching a defined state, a release milestone, whatever it actually is — so the ticket does not depend on memory.

> ### ✅ Resolved — 2026-09-22
>
> **Three triggers, none of them memory.**
>
> | | |
> |---|---|
> | **Full regression** | Driven by the **quarterly release schedule**, planned each quarter and known across the software department — PMs, Engineers and QA |
> | **Feature-level regression** | Planned from the **ETA or desired date recorded in the Epic** alongside the feature definition |
> | **Quarterly intake** | **All Epics should be defined and delivered to QA as Jira items at the start of the quarter** |
>
> **The third point is the largest thing to come out of this review, and it changes how the pages are shaped.** What page 1 currently offers as advice — *submit early, ideally at the start of the quarter* — is not advice. It is a **defined quarterly intake cycle**, and the team has a specific use for it: feeding the epics into the AI tooling, identifying missing information, and preparing test scenarios and automation placeholders before any work is requested.
>
> So the operating model is **quarterly batch intake plus continuous pull execution**, and the pages describe only the second half. Three consequences:
>
> - **Page 1's "submit early" section gets rewritten as a cycle**, not a preference. It finally answers the question left open in X2 — what early submission buys — with something concrete: your epic goes through the requirement reviewer, gaps come back to you early, and test scenarios and automation placeholders exist before the work starts.
> - **Page 3 gains a quarterly rhythm above the fortnightly one.** Quarter start is intake and preparation; the quarter itself is pull execution punctuated by release freezes. Those two cycles together are the team's actual operating pattern, and neither page currently shows it.
> - **The quarterly release schedule should be linked.** It is the trigger for full regression and, per Q11c, the thing a requester needs in order to know when freezes fall. It is a stronger artefact than the Slack channel for planning purposes.
>
> **This is also a substantial ask of Product Management and Engineering** — every epic defined and in Jira at quarter start. It belongs in the page 2 *What QA needs from other functions* section and near the top of the P1 walkthrough, because it is the input the entire preparation cycle depends on.
>
> **Consistent with P10.** The ETA in the epic is the same field that keeps priority demotion honest. One attribute, authored by Product Management, now serves planning, prioritisation and regression scheduling.

### P15 — Does standing intake consume capacity?

**Personas:** Priya, Anna · **Pages:** 2, 3

BugCrowd is standing intake and QA raises the issues. Nothing says whether a BugCrowd item occupies a WIP slot, how it is prioritised, or how much time it typically takes.

If it consumes capacity invisibly, the 2.0 FTE on page 4 is overstated, and Priya's protected automation time is the thing that gets spent.

**Recommendation:** state whether BugCrowd work takes a WIP slot and how it is prioritised. If volume is unpredictable, say so on page 4 as a known variable in the capacity model.

> ### ✅ Resolved — 2026-09-22
>
> **BugCrowd work consumes WIP slots and requires a portal ticket, created by the QA Team.**
>
> No special treatment: it competes for the same eight slots as everything else, and it is visible in the queue rather than absorbed. That keeps the capacity model honest, which was the point of the finding.
>
> **This is now the second confirmed instance of the same pattern, and the pages should name it.** BugCrowd findings and Critical production verification (X1) both originate outside QA's planning, and both are handled the same way: **the work enters through a portal ticket, whoever raises it.** Stated as a principle — *everything QA does is a portal ticket, including the work QA raises for itself* — it explains the portal's role far better than the current three-kinds-of-work table, which reads as taxonomy rather than as a rule.
>
> **Defaults carried into the rewrite:**
>
> - BugCrowd tickets are **Medium by default** like everything else, with the finding's severity able to raise them — consistent with Q13 and with the deference to externally assigned severity in P3
> - **volume is externally driven and unpredictable**, and page 4 should say so as a known variable rather than letting the 2.0 FTE look more solid than it is. It is the only intake the team neither schedules nor is asked for

### P16 — Training and enablement does not fit the queue it is in

**Personas:** Elena, Anna · **Pages:** 2, 5

Training and courses are listed as a requestable category alongside feature testing. But building a course is weeks of work with no natural "done by testing" point, and page 1 asks for none of the information that would make it triageable — no audience, no format, no duration, no date.

Dropped into a WIP-limited queue, one training request consumes an engineer for a long time and distorts everything behind it.

**Recommendation:** either give it its own required-information list and treat it as planned work scheduled outside the WIP queue, or remove it from the requestable categories and handle it as a commitment made at quarter planning.

> ### ✅ Resolved — 2026-09-22
>
> **Planned outside the queue, but it affects team capacity and must be properly tracked in Jira.**
>
> Both halves matter. Outside the queue, so a three-week course does not occupy a WIP slot and distort the pull model. Tracked in Jira and counted against capacity, so it does not become invisible work — which would have replaced one problem with a worse one.
>
> **This establishes a third handling mode the pages do not currently have:**
>
> | Mode | Tracked | WIP slot | Consumes capacity |
> |------|---------|----------|-------------------|
> | Portal queue work | Portal ticket | **Yes** | Yes |
> | **Scheduled work** — enablement, training | **Jira, outside the queue** | **No** | **Yes** |
> | Internal absorbed work | Not individually | No | Yes, inside other work |
>
> **The consequence page 4 must state: the ceiling of eight slots is not a constant.** While scheduled enablement work is running, fewer engineers are available to pull, so the effective queue capacity is lower even though the published limit has not changed. Left unsaid, a requester sees eight slots, sees four in use, and cannot understand why nothing is moving.
>
> **Recommendation for the rewrite:** active scheduled work is **declared at triage** and the available slots reduced accordingly, exactly as the release freeze reduces them to zero. That makes it the same mechanism as the release ticket rather than a new concept — large planned work is tracked separately and visibly reduces what the queue can absorb.
>
> **Defaults carried forward:** enablement requests are agreed at **quarter start**, alongside the P14 intake cycle, rather than arriving mid-quarter; and they need their own required information — audience, format, duration, delivery date. The P6 training offer to Engineering is the first live instance.

### P17 — Key-person risk is presented as a feature

**Personas:** Sarah, Elena · **Pages:** all

Every page names Marek Wyszyński as first point of contact. That answers Anna's ownership question and creates Sarah's succession question. Elena's version is operational: who runs triage when he is on leave?

**Recommendation:** name a deputy, or state that the QA team collectively answers and the named contact is for escalation only. Either is fine; silence is not.

> ### ✅ Resolved — 2026-09-22
>
> **Marek Wyszyński is the named contact; the whole four-person QA team acts as deputies. Most requests will in practice be redirected to the team.**
>
> This resolves the Anna/Sarah tension in the persona map rather than picking a side: a name, so it is clear who to approach, and collective deputising, so there is no single point of failure. At four people it is proportionate — a designated second name would be ceremony.
>
> **Say the redirection out loud, because it is a feature.** "Most of the time I will redirect to the team" is worth publishing: it tells a requester their question is going to the person best placed to answer, not being passed around, and it stops the named contact reading as a gatekeeper. It also matches the pull model — no assignment, whoever has capacity responds.
>
> **One default, to make collective deputising real rather than nominal:** when a decision is needed and the named contact is unavailable, **daily triage makes it and the decision stands**. Without that, "the team deputises" becomes the thing Anna warns about — everyone responsible, nobody deciding. With it, the existing daily meeting is the fallback, so nothing new has to be invented.
>
> Page 3 already implies the operational half: triage is owned by the team, not a chair, so it runs with whoever is present, and the daily hold review runs with it.

---

## Worth settling

### P18 — Reopening a closed ticket

**Persona:** Tomasz · **Page:** 1

Page 1 invites the requester to reopen or comment if the closing note does not answer their question, without a window or a rule. Left open deliberately in the first round; worth a sentence now.

**Recommendation:** any ticket can be reopened within a stated window — two weeks is generous — after which a new request is cleaner than reviving an old thread.

> ### ✅ Resolved — 2026-09-22
>
> **A ticket can be reopened up to one week from closure.**
>
> Tighter than the two weeks proposed, and it fits the fortnightly rhythm better: a week keeps any reopening inside the same release cycle as the original work, so the context and often the same engineer are still current.
>
> **Defaults carried forward:** reopening is for *"this does not answer my question"* — correcting or completing the original work, not adding new scope to the same feature. Beyond a week, a new request is the cleaner route, and it lands in the current quarter's priorities rather than carrying an old ticket's.

### P19 — When a request spans categories

**Persona:** Tomasz · **Pages:** 1, 6

Page 6 tells requesters to submit the closest match and let triage reclassify, which is the right instinct. Page 1 never mentions it, and page 1 is the one people read.

**Recommendation:** move that sentence onto page 1. It removes a real hesitation before submitting.

> ### ✅ Resolved — 2026-09-22
>
> **Accepted.** The guidance moves onto page 1, beside the request-type list: submit the closest match, say so in the description, and triage reclassifies. *Guessing wrong is not a problem; not submitting is.*
>
> It stays on page 6 too — the two pages serve different moments, and this is the rare instance where repeating a sentence is right rather than redundant.

### P20 — Where does the model stop working?

**Persona:** Sarah · **Pages:** 3, 4

Page 3 says the unclaimed-ticket mechanism should be revisited "if the team grows", without a threshold. Sarah wants the trigger point, not the intention.

**Recommendation:** name the condition — a team size, or an intake volume — at which the pull model, the WIP limit and the single daily triage stop being adequate.

> ### ✅ Resolved — 2026-09-22
>
> **The team will never grow beyond four engineers.** The model's breaking point is therefore **inflow**, not size, and the threshold is stated: **more than 8 tickets per week**, at which point every ticket above that number is **automatically put on hold**.
>
> A real tripwire with a number and an automatic consequence — exactly what the finding asked for, and considerably firmer than most answers of this kind.
>
> **The fixed team size is itself a significant statement and should be published as one.** It converts the capacity figure from provisional to permanent, and it settles in advance what happens when demand rises: **scope is reduced or work waits — headcount is not the lever.** Sarah's question about what breaks first now has an answer that does not end in a hiring request, which is a stronger position to publish than an implicit hope.
>
> **The automatic hold is the best mechanism in the whole model.** It needs no judgement, no negotiation and no meeting: past eight in a week, the rest are held, visibly, with a reason. Demand above capacity becomes a number anyone can see rather than an argument QA has to win. Pair it with the P5 measurement and Anna has her case made for her.
>
> **One observation for page 4, not a challenge to the figure.** Eight per week equates the eight WIP slots to weekly throughput, which holds when the average ticket takes about a week and no freeze falls in that week. During a release week the portal half is on release work, so throughput is near zero — meaning sustained inflow somewhat below eight will still accumulate over a quarter. The page should either state the eight as a **peak-week** limit or note that freeze weeks reduce it. This is precisely what the P5 intake measurement will settle, and it is worth saying that too: the number is stated, and it will be checked against reality.

### P21 — The trade is stated for QA but not for the company

**Persona:** Sarah · **Page:** 4

Page 4 explains honestly why QA does not publish completion dates. It does not say what that costs everyone else: dependent teams hold buffer, or they gamble. That cost is real and currently invisible.

**Recommendation:** one paragraph naming the trade at organisational level — predictability is exchanged for honesty, and the exchange is revisited when intake is measured. Sarah can endorse a stated trade; she cannot endorse an omission.

> ### ✅ Resolved — 2026-09-22
>
> **"The trade-off is everything we have put in the column that says Out of scope, Won't Do, Don'ts."**
>
> Sharper than the recommendation, and it changes what the out-of-scope list is for. I framed the cost as lost predictability, which is abstract and hard to argue about. The team's framing is **concrete and countable**: the price of a four-person team with protected automation time is a specific list of work that no longer happens — filing bugs for other people, routine fix verification, support reproduction, instance creation as a service, the observability dashboards, business questions.
>
> **So the out-of-scope list stops being a boundary and becomes the bill.** That is a much stronger thing to publish, and it needs a cross-reference rather than a rewrite: page 4 states that the cost of this model is enumerated on page 2, and page 2 says that the list is not a preference but the price of the capacity model. Each item is work that either stops or is absorbed by someone else, and both pages should say which.
>
> **Sarah can act on this.** A list of withdrawn activities is something a director can review, accept, or push back on item by item. "We are trading predictability" is not. It also makes the P1 walkthrough sharper: the conversation with Engineering and Product Management is about specific work changing hands, not about a philosophy.
>
> **The predictability question is answered elsewhere, and the pages should connect the two.** Dependent teams plan against the **quarterly intake cycle** (P14) rather than per-ticket estimates — that is what replaces the completion dates QA does not publish. Stated together, page 4 says: here is what we no longer do, here is how you plan around what we do.

### P22 — Is QA a shared service by decision or by drift?

**Persona:** Sarah · **Pages:** 3, 4

The pages describe a central shared service with a queue. That is an organisational choice with alternatives — embedded QA in feature teams, for one — and it is asserted rather than argued.

**Recommendation:** one sentence saying this is a deliberate choice at the current size, and what would prompt reconsidering it. It costs nothing and pre-empts the question being raised as a challenge.

> ### ✅ Resolved — 2026-09-22
>
> **The four-person team is the outcome of a transformation** — people were let go, others moved to different teams, and four remained with the BigPicture team.
>
> So the question was wrongly framed. The shared-service model is not QA choosing a structure; it is **the best operating model available at a size the organisation already set**. That is a considerably stronger position than the one the pages currently imply, and it reframes several things at once:
>
> - **The model is a response to a constraint, not a preference.** Generalist working, the documentation bar, the automation split, the inflow ceiling — each is a consequence of four people, not an ideology.
> - **It reinforces P21.** The out-of-scope list is the consequence of a capacity decision taken above QA, not a service the team chose to withdraw. Written that way it protects the team and gives the list a legitimacy it would not have as a QA preference.
> - **It answers Sarah's question about reconsidering the model** — the size is fixed by a decision already made, so the alternative structures do not arise.
>
> **Editorial judgement for the rewrite, worth flagging.** These pages are published company-wide, and the reorganisation's details do not belong in them. State the constraint neutrally — *"following the team's reorganisation, BigPicture QA is a four-person team, and this operating model is built for that size"* — without reference to people leaving. The reasoning survives; the sensitivity does not need to.

### P23 — Automation has no visible commitment

**Personas:** Priya, Anna · **Pages:** 4, 5

Half the team's time is automation, and the pages treat it almost entirely as the thing that must be protected from portal work. There is no statement of what it produces or how its progress is judged.

Priya's concern is practical: a protected half with no visible output is the half that gets raided first.

**Recommendation:** a short paragraph on page 4 stating what the automation half is for and how it is reported, so it appears as work rather than as slack.

> ### ✅ Resolved — 2026-09-22
>
> **At least one test case automated per day, per engineer.** With **2.5 business days a week** available for automation, that is **2 to 3 test cases created or fixed each week per engineer**, all tracked transparently in Jira.
>
> A measurable commitment with a stated rate — the strongest possible answer to the finding. Automation stops being reserved time and becomes work with an output anyone can check: roughly **8 to 12 test cases a week across the team**, and on the order of a hundred or more per quarter.
>
> **It also pins the 50/50 split to a number.** 2.5 days of five is the split stated as hours rather than as an intention, which makes it far harder to erode quietly. Page 4 should carry it in exactly those terms.
>
> **And it gives the release-freeze commitment its point.** P4c established that automation continues through freezes; with a daily rate attached, that now means the automation output is **uninterrupted year-round** while portal throughput goes to zero during freeze weeks. That is a genuinely strong thing to publish, and it was invisible before.
>
> **The arithmetic this completes — page 4 needs to reconcile it.** Not a challenge to any figure, all of which are settled, but the numbers now interlock and a reader will do the sum:
>
> | | |
> |---|---|
> | Automation | 2.5 days per engineer per week, every week including freezes |
> | Portal half | 2.5 days per engineer per week — 10 engineer-days across the team |
> | Inflow ceiling | 8 tickets per week, implying roughly **1.25 engineer-days per ticket** |
> | Freeze weeks | Around 5 to 6 of the 13 weeks in a quarter, when portal throughput is near zero |
>
> So portal work runs at full rate in roughly half the quarter. A sustained inflow at the 8-per-week ceiling would therefore accumulate, which is the P20 observation now quantified. The cleanest resolution is to publish **8 per week as a peak-week limit** and note that the sustainable quarterly average is lower because of freezes — with the P5 intake measurement confirming the real figure. Stated that way every number on the page is consistent, and the automatic-hold rule becomes the mechanism that manages the gap rather than a contradiction of it.

### P24 — Confirm the portal is where the pages say it is

**Persona:** Tomasz · **Page:** 6

Page 6 describes a Jira Service Management project with a specific field set, derived from the agreed scope rather than read off the live form. It needs checking against reality, along with the three missing links.

> ### ✅ Resolved — 2026-09-22
>
> **The portal instructions will be written by the team and submitted here for review.**
>
> Correct division of labour — page 6 depends on access to the live form, and no amount of inference substitutes for having it open.
>
> **Default carried forward:** publish the other five pages without waiting for it. Page 6 is the only one that depends on external artefacts, and holding the ready material for screenshots delays the parts people need. The index marks it as coming.

---

## Assumptions written into the pages that nobody decided

I inferred these while drafting. Each is defensible and each needs a yes or no, because they are currently stated as fact.

| # | Assumption | Page |
|---|------------|------|
| A1 | Helping developers reproduce a bug is out of scope **as a task**, though a conversation is fine | 5 |
| A2 | Support ticket review is out of scope and "being wound down" | 5 |
| A3 | Filing bugs for Support has stopped, not merely been deprecated | 5 |
| A4 | Unit tests and database tests are internal, not a requestable category | 5 |
| A5 | Azure DevOps testing is available to request now, rather than "soon" | 2, 5 |
| A6 | Release management and app releases are QA release-process work, not a separate function | 5 |
| A7 | Refactoring and fixing automated test cases are internal, never requestable | 5 |
| A8 | The QA Portal is a Jira Service Management project | README, 6 |

A1 to A3 matter most. They describe work the team does today and the pages say it stops — which is a decision, not a description.

> ### ✅ All eight confirmed — 2026-09-22
>
> Confirmed as written, and they stand as decisions rather than inferences. A1 to A3 in particular are now deliberate: bug reproduction, Support ticket review and filing bugs for Support **stop**, and the pages say so without hedging.
>
> **One phrase to fix rather than keep.** A2 currently reads "being wound down", which I wrote as a softener. With the assumption confirmed it should say the work has **stopped**, consistent with A1 and A3 — a boundary described as in progress is one people will keep testing.
>
> **A5 is the one to sanity-check against reality when the pages are reviewed.** The original draft said Azure DevOps testing was coming "soon" and handled by one person. The pages now offer it as requestable today. If the transition is not complete, *"available from [date]"* is the safer phrasing; it is a one-line change either way.
>
> These three confirmations belong in the P1 walkthrough. Each has someone on the other end — a developer who used to get reproduction help, Support who used to get bugs filed — and they are the changes most likely to be discovered by being refused rather than by being read.

---

## What the review did not find

Worth recording, so the next reader knows where not to spend effort.

**The scope rule holds.** Read against all seven personas, the three carve-outs and the out-of-scope list are consistent and applyable. Nobody found a case the rule could not decide, except the production-severity decider in P3.

**The capacity model is internally consistent.** Four engineers, a 50/50 split, WIP of 2 and a ceiling of 8 hang together, and page 4 does the arithmetic honestly rather than hiding it. The only gap is the release deduction in P4.

**The generalist principle carries its weight.** Stated once and used to explain the documentation bar, the artifact linking and the pull model, it survives being read by every persona. Priya and Inês read it differently — she sees protection, Inês sees a bar — but neither finds it incoherent.

**Page 1 works for Tomasz.** He can determine scope, submit correctly, and know what happens next, in about two minutes. That was the first review's C8, and it is closed.
