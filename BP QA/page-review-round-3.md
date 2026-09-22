# Third review — the whole collection, read as a published set

**Reviewed:** 2026-09-22 · **Against:** all six pages at v2.0 plus the README · **Lenses:** the seven personas in `personas.md`
**Status: complete.** All 7 defects, all 10 discussion generators and all 7 editorial fixes answered and applied. Pages are now **v2.1**.

### The final five, answered together — 2026-09-22

| # | Decision |
|---|----------|
| **C2** | **Tickets are reviewed daily, full stop.** The twice-weekly hedge is deleted from page 3 rather than carried as a caveat |
| **C3** | **A blocked ticket is put On hold** — that is the status the team has, and it **pauses the SLA clock**. So there is no fourth state after all: page 1 keeps its three outcomes and gains *blocked on someone else* as a third hold reason, plus an explanation of why the assignee comes off |
| **C6** | Training and enablement is **requestable any time**, and the table row now says it is **scheduled rather than queued** — planned into the next cycle instead of pulled from the queue |
| **D3** | **A dedicated Jira project** holds everything the QA team handles: portal counterparts, automation, BugCrowd, training preparation, release activity. Anyone can see the full picture |
| **D10** | **Change proposals go through the QA Portal.** Read at triage like anything else; changes made at the monthly review and published with a new version |

**C3 turned out simpler than the finding assumed.** *On hold* already exists and already pauses the clock, so the fix is descriptive rather than structural — the pages just had to say that blocking uses it.

**D3 is the strongest answer in the round.** The finding asked QA to *assert* that QA-raised work competes for the same slots. The Jira project lets a requester **verify** it. That converts the collection's most contestable claim — *"we are full"* — from something people have to take on trust into something they can check, and it is what makes the slot-based hold rule from C1 credible in practice.

---

## How this round differs from the last two

The first review asked *what does the team actually do*. The second asked *can someone use these pages*. This one asks a narrower question, because it is the one that matters now:

> **When this is published, where does the argument start?**

So the bar is different. A statement can be true, clear, and agreed, and still be a bad sentence to publish — because it invites a conversation that costs more than the sentence is worth. Several findings below are of that kind. Nothing is wrong with them; they are just expensive.

Findings are in two groups: **defects**, which are contradictions between pages that a reader can catch, and **discussion generators**, which are correct statements that will reliably produce a conversation.

---

## Group 1 — Defects (C1–C7)

### C1 — The inflow ceiling counts arrivals, but capacity is measured in slots

> Pages 1, 3, 4: *"more than eight new tickets in a week means the ones above that number are automatically put on hold"*

The mechanism and the constraint do not match, and it misfires in both directions:

- **Quiet week, free slots.** Eight tickets arrive Monday, all get picked up, six are closed by Thursday. Ticket nine arrives Friday and is held — with slots free. The requester can see they are free.
- **Busy week, no slots.** Two long feature-testing tickets per engineer are still running from a fortnight ago. Three tickets arrive. None is held, because three is under eight. There is nowhere to put them.
- **Freeze week.** Throughput is zero and the rule still admits eight.

The rule is also the thing most likely to be gamed once people notice it: submitting on Monday beats submitting on Friday, for reasons that have nothing to do with the work.

**Recommendation.** Keep **eight per week as the published planning figure** — it is genuinely useful and it is what makes the capacity argument concrete. But make the *mechanism* slot-based: **a ticket is held when no WIP slot is free.** That is self-correcting, needs no counting, is right during freezes automatically, and cannot be gamed by submission timing. The eight becomes the explanation for why holds happen, rather than the trigger.

> ### ✅ Answered — 2026-09-22
>
> **Confirmed: the mechanism is slot-based.** A ticket is held when **no WIP slot is free**. Eight per week stays as the **published planning figure**, describing what the team can sustain, not as the rule that fires.
>
> This was the intent all along; the arrival-counting phrasing was mine.
>
> **What follows in the pages:**
>
> - Pages 1, 3 and 4 stop describing a weekly arrival count as the trigger. The trigger is a full queue.
> - It becomes **automatically correct in the cases the old rule got wrong** — freeze weeks, weeks when scheduled work has reduced the available slots, and weeks when long-running tickets are still occupying capacity from a fortnight ago. None of these needs a special case any more.
> - It is also **verifiable by the requester** against the Jira filter, which matters for D3: a hold explanation that someone can check is worth several that they cannot.
> - The eight moves to page 4 as capacity context and is referenced, not restated, elsewhere — which is also part of the E2 de-duplication.

---

### C2 — Page 1 promises a daily hold review that page 3 has already downgraded

> Page 1: *"every held ticket is looked at again every working day. A waiting ticket is never a forgotten one."*
> Page 3: *"Holds are reviewed daily today; this may move to twice weekly if ticket volume makes daily impractical."*

The requester-facing page makes an unqualified promise; the internal page pre-announces breaking it. Whichever a reader finds second undermines the other.

**Recommendation.** Delete the hedge from page 3. If the review moves to twice weekly, that is a change made at a retrospective and published, not a caveat carried from day one. A commitment with its own escape clause attached is not read as a commitment.

---

### C3 — A blocked ticket has no state on the requester-facing page

> Page 1: *"You will get a comment saying one of three things… There is no fourth state."*
> Page 3: *"A blocked ticket frees the slot. It returns to the queue keeping its priority."*

From the requester's side this is a fourth state and a visible one: the ticket was picked up, the assignee disappears, and page 1 has no explanation. Page 1's two hold reasons — cannot start yet, at capacity — do not cover it either.

There is also a gap underneath. *"More information needed"* covers a ticket blocked on **the requester**. Nothing covers a ticket blocked on **a third party** — waiting on Engineering for a fix, on DevOps for an environment, on a feature flag being switched on. That is a common case and it has no described behaviour.

**Recommendation.** Add blocked-on-someone-else as a hold reason on page 1, and say plainly that the ticket returns to the queue and may be picked up by a different engineer. The unassignment is the part that looks alarming if it is not explained, and trivial if it is.

---

### C4 — The RUM gate blocks, except when it does not, and nobody grants the exception

> Page 3: *"The gate blocks."* … *"A known regression may ship under a recorded waiver, with the escalation ticket left open."*

A gate with a waiver is a recommendation. That may well be the right design — but as written no one is named as able to grant the waiver, so the question gets settled in the release channel at the moment it is least settleable.

**Recommendation.** Name the grantor. Whoever owns the release decision does; QA records it. QA's line stays exactly where it is on everything else — QA reports against criteria owned by others and does not own the shipping decision.

> ### ✅ C4 and C5 answered together — 2026-09-22
>
> **There is no waiver. The team does not release with blockers, full stop.**
>
> The waiver was an edge case settled in round two; it is **overturned**. That removes the contradiction outright rather than resolving it — no grantor needs naming, because no one grants it.
>
> **What follows in the pages:**
>
> - Page 3 loses the *"known regression may ship under a recorded waiver"* line entirely. **The gate blocks, and that is the whole rule.**
> - The two statements collapse into **one consistent position** across pages 2 and 3: a below-threshold RUM result and a bug of severity ≥ Medium both stop the release, and neither has an exception path.
> - The *"not assessable"* case survives untouched and is now the only nuance left in the gate — a module with no defined threshold is recorded as not assessable, **never as a pass**.
> - **C5's absolute stays, and gets attributed as well as asserted.** The severity rules already exist and are owned elsewhere, so the page says both: the rules define what blocks a release, *and* a release does not go out with a blocker open, with the link. Attribution here does not soften the claim — it means QA is citing organisational policy rather than announcing its own, which is a far harder thing to argue with.

---

### C5 — "No bug of severity ≥ Medium is ever released" is an absolute that nothing else in the set is

> Page 2: *"No bug of severity ≥ Medium is ever released."*

Two problems. It is a stronger claim than the RUM gate next to it, which has a waiver — so the set says performance regressions can ship by exception but functional Medium bugs never can. And an absolute with no exception path is the kind of sentence Engineering or Product Management will contest on first reading, or quietly work around on first collision.

**Recommendation.** Either give it the same named exception path as C4, or attribute it rather than assert it: the severity rules already exist and are owned elsewhere, so *"the severity rules define what blocks a release"* with the link does the same job without QA staking a claim it does not own. The second is cheaper.

---

### C6 — Training and enablement is requestable and not requestable on the same page

> Page 2 lists it in **Requestable by anyone**, then: *"Training and enablement is agreed at quarter start and tracked in Jira outside the queue."*

Someone submits a training request in week six and finds out it was a quarter-start conversation. The table promised otherwise.

**Recommendation.** Keep it requestable any time, and say in the table row what actually happens: it is **scheduled rather than queued**, and normally agreed at quarter start, so mid-quarter requests are planned into the next cycle. One clause, and the surprise is gone.

---

### C7 — The release cost figures cannot be added up

> Page 3: *"Release testing ~2 days. Verification of fixes ~2 days. CI-related work ~1 FTE per release, spread across the four engineers."*

The first two read as elapsed days, the third as effort. A release week holds ten portal engineer-days in total. Two plus two plus one-FTE-of-CI does not resolve against that, and the reader cannot tell whether "2 days" means two days for one person or two days of the whole team.

This matters because "about a week per release" is load-bearing — it is what justifies half the quarter being unavailable.

**Recommendation.** State release cost once, in engineer-days per release, and derive the calendar week from it. Any consistent set of numbers is fine; the current ones cannot be checked, and a number that cannot be checked gets challenged.

> ### ✅ Answered — 2026-09-22 — and it is a scope change, not just an arithmetic fix
>
> **CI work is out of scope for the QA team.** The only CI activity QA performs is **triggering the software builds as part of a release**. No troubleshooting, and no CI-related requests.
>
> This **overturns the round-two figure** of *"the entire CI related work is 1 FTE per release"*. That line was the largest single component of the release cost, and it turns out not to be QA's work at all.
>
> **The arithmetic then resolves cleanly.** Release cost is release testing plus fix verification, with build triggering as a minor task inside it:
>
> | Per release | |
> |---|---|
> | Release testing | ~2 days |
> | Fix verification | ~2 days, **actively being reduced** |
> | Triggering builds on CI | minor, inside the above |
> | **Team capacity consumed** | **about 10 engineer-days — one week of the portal-and-release half** |
>
> Four elapsed days with the team working in parallel, at 2.5 portal days each, comes to roughly ten engineer-days. That reproduces *"about a week per release"* from the component parts instead of asserting it, so the claim that justifies half the quarter can now be checked. *(Stating the derivation explicitly — correct it if the days are per-engineer rather than elapsed.)*
>
> **One boundary has to be drawn or this creates the argument it removes.** QA still investigates its **own failing automated tests** — that is its test code and it sits in the automation half. What is out of scope is the **CI platform itself**: broken agents, pipeline configuration, build infrastructure. Without that sentence, "CI is out of scope" and "QA investigates failing automations" look like a contradiction on pages 2 and 5.
>
> **What follows in the pages:**
>
> - Page 2's out-of-scope list gains **CI troubleshooting and CI-related requests**, routed to DevOps, with the automated-test carve-out stated.
> - Page 3 drops the 1 FTE CI component and states release cost as above.
> - Page 5 marks CI platform work **Stopped**, keeps *investigating failing automations* as **Internal**, and adds the boundary between them.
> - Page 4's capacity section reproduces the same figures, since it is canonical for numbers under E2.

---

## Group 2 — Discussion generators (D1–D10)

Ranked by how often each will actually fire.

### D1 — "Estimate" is not defined as effort or elapsed time. This fires on every single ticket

> Page 1: *"When an engineer picks the ticket up, they estimate it and tell you."*

Page 1 offers the estimate as the replacement for a completion date, so the requester reads it as a date. The engineer almost certainly means effort.

The gap between those is not small, and the pages contain the arithmetic to prove it. Two tickets in progress, 2.5 portal days a week: each in-progress ticket receives about **1.25 engineer-days per week**. So a three-day piece of work is roughly **two and a half weeks elapsed** — more if a freeze lands in the middle.

"Three days" heard as Thursday, delivered a fortnight later. **This is the highest-frequency discussion trigger in the collection**, and it will fire on almost every ticket until it is fixed.

**Recommendation.** Commit to an **expected completion date**, not an effort figure — it is what the requester needs and the engineer can compute it. And state the WIP arithmetic openly on page 1: *two tickets at a time and half a week each means work in progress is not work being worked on continuously.* Surprising in the document is free. Surprising on the ticket is not.

> ### ✅ Answered — 2026-09-22
>
> **An estimate is a completion time in elapsed business days plus a delivery date** — for example, *"10 business days, delivered by 6 October"*. Not an effort figure. It comes **from the QA team**, not from the individual engineer.
>
> This closes the gap entirely: the requester is handed the thing they were going to infer anyway, and the conversion is done by the person who can see the WIP and the freeze calendar rather than by the person who cannot.
>
> **What follows in the pages:**
>
> - Page 1 replaces *"they estimate it and tell you"* with the two-part estimate, stating that it is **elapsed** time that already accounts for the engineer's other ticket and any release freeze in the window.
> - The **WIP arithmetic goes on page 1 openly** — two tickets at a time, about 1.25 engineer-days each per week. This is what makes a ten-day estimate on three days of work read as mechanics rather than padding.
> - The estimate coming **from the team** matches the rule already on page 3: QA never leaves an individual engineer to negotiate a date alone.
> - Page 4's *"no completion promise"* needs tightening rather than removing. QA publishes **no completion SLA up front**, but does commit to a **date per ticket once it is picked up**. Those are different claims and the page currently blurs them.

---

### D2 — The quarterly cycle reads as a gate, and nothing says mid-quarter work is welcome

Page 1 leads with it, page 3 makes it the spine, page 2 lists it first under what Product Management owes. Nowhere does the set say that work arriving mid-quarter is **normal, accepted, and triaged like anything else**.

Every Product Manager with genuinely emergent work will ask, and they will ask defensively, because the pages have implied they are already out of compliance.

**Recommendation.** One sentence on page 1: the quarterly cycle is about **preparation, not eligibility**; mid-quarter requests are accepted and ordered the same way, they just arrive without the preparation. Cheap, and it removes the single most predictable objection from the audience QA most needs on side.

> ### ✅ Answered — 2026-09-22
>
> **The quarter-start expectation is scoped to one kind of work: testing new features, initiatives and epics.** That is what the upfront delivery is for. Everything else — test design, migration testing, performance work, documentation testing — arrives mid-quarter as normal business and is triaged like anything else.
>
> **Within that scope there is a real pushback case**, and it should be stated rather than implied: **a large epic arriving mid-quarter with an ETA of about a week will be pushed back.** Not because it arrived late, but because the preparation it depends on — requirement review, test scenarios, automation placeholders — cannot be compressed into the lead time.
>
> **What follows in the pages:**
>
> - Page 1 scopes the quarterly ask explicitly to **feature, initiative and epic testing**, so the other categories stop looking non-compliant by default.
> - It states the pushback case plainly, as a **consequence of lead time rather than of lateness**. That distinction is what keeps it from reading as a punishment, and it is checkable.
> - **"Push back" is written as a conversation, not a refusal** — QA says what it can deliver and by when, and the discussion is about moving the date or reducing the scope. This reuses the rule already on page 3: QA raises it on the ticket, as a team. *(Flagging the interpretation — if pushback here does mean an outright decline for this one case, the page should say so instead.)*
> - This also strengthens D2's original point rather than replacing it: the pages can now be **more welcoming about ordinary mid-quarter work** precisely because they are specific about the one case that genuinely does not fit.

---

### D3 — Requesters cannot see the work they are competing with

BugCrowd findings and post-initiative regression consume the same eight slots. Both are QA-raised. Page 1 never mentions either.

A requester told *"on hold, at capacity"* who then looks at the queue and sees four requests will conclude the capacity claim is soft. They will be wrong, and they will say so.

**Recommendation.** Say on page 1 that QA-raised work — regression and security findings — occupies the same queue, and that BugCrowd volume is externally driven. The Jira filter should show it. A capacity claim that the requester can verify is worth several that they cannot.

---

### D4 — Holds have no expiry, so the hold list grows without a stated end

Page 1 describes holds as reviewed daily and never forgotten. True. But nothing says what happens to a ticket held at capacity for six weeks. It is reviewed daily and stays held daily.

The honest version is that some held work is never going to be done. The pages do not have a way to say so, which means it gets said in person, late, to someone who has been waiting.

**Recommendation.** Give holds a **review horizon** — at some stated point QA goes back to the requester and the ticket is either scheduled, reduced, or withdrawn by agreement. A "no" that arrives at four weeks costs far less than one that arrives at twelve, and it is the mechanism that keeps the hold list an honest number rather than a place things go.

> ### ✅ Answered — 2026-09-22
>
> **Four weeks.** Where there has been **no progress on the engineering side**, QA **contacts the requester and then closes the ticket**.
>
> **One distinction has to be written in, or this rule collides with the quarterly cycle.** Page 3 says the most common hold is now *"work cannot start yet"* — epics submitted at quarter start for features shipping in week eight. That hold list is the team's forward book, and a blanket four-week closure would destroy it, which is plainly not the intent.
>
> So the horizon is written as **two outcomes, not one**:
>
> | At four weeks | Outcome |
> |---|---|
> | The hold is a **planned wait with a known date** — the feature is progressing, it simply is not ready | The hold **continues**. This is the forward book working as designed |
> | There is **no progress on the engineering side** and no date to point at | QA **contacts the requester and closes the ticket** |
>
> **Closure here is not a refusal, and the pages say so.** The work can be resubmitted when the engineering side is actually ready — which is the honest description of what happened, and it keeps the request in step with the quarterly cycle rather than sitting in a queue pretending to be active.
>
> Note the interaction with the reopen rule: the one-week reopen window covers *"this does not answer my question"*. A ticket closed for lack of progress comes back as a **new request**, not a reopen, since by then the underlying work has changed.
>
> **What this buys.** The hold list stays an honest number and keeps working as evidence of real demand. And a "no" delivered at four weeks costs a fraction of one delivered at twelve — the scenario most likely to damage trust in the portal is the one where a requester waits months believing the queue is moving.

---

### D5 — "The team will not grow beyond four engineers" is stated as permanent policy

It appears on the README and pages 2, 3 and 4.

As an operating assumption it is exactly right and it makes the whole model coherent. As a published sentence it is a standing invitation for a Director to ask who decided it, on what horizon, and whether QA is entitled to declare it. That conversation has nothing to do with ways of working.

**Recommendation.** Same operational effect, much less surface: state it as the **planning basis** — the model is built for four engineers and does not assume growth — rather than as a permanent constraint. Everything downstream still holds, including "the lever is scope, not headcount", and QA is no longer making an organisational declaration in a process document.

---

### D6 — The reorganisation backstory does not belong in a company-wide document

> *"Following the team's reorganisation, four QA engineers remain with BigPicture"* — README, pages 2 and 3

It is true and it explains a lot. It also references a reorganisation in which people were let go, in a document being published to Product Management, Engineering and Support. Some readers will engage with that rather than with the process.

**Recommendation.** Keep the number, drop the history. *"The team is four engineers"* carries the entire operational weight of the sentence. The context belongs in `MEMORY.md`, where it already is.

> ### ✅ D5 and D6 answered together — 2026-09-22
>
> **Both framings go. The number stays.** The sentence becomes *"The team is four engineers, and the model is built for that size — it does not assume growth."*
>
> No reorganisation backstory, and no declaration that the team will never grow. Everything downstream survives, including **the lever is scope, not headcount**, which is the operationally important half and does not need either framing to stand up.
>
> **What follows in the pages:**
>
> - The sentence is corrected in all three places — README, page 2, page 3 — and page 4's capacity table row loses *"the team will not grow beyond this"*.
> - Page 2's out-of-scope framing keeps the **consequence** and drops the **history**: the list is what four engineers cannot cover. That is true without explaining why there are four, and it still reads as a cost rather than a preference.
> - The reorganisation context stays in `MEMORY.md` as the decision record.

---

### D7 — "Owes QA" reads as a demand, and the consequence column reads as a penalty

Page 2's *What QA needs from other functions* is the right section and the right content. The framing is the problem: a column headed **Owes QA**, paired with a column of consequences, is a list of debts with enforcement attached. *"Assets go unmaintained; QA does not pick them back up"* lands as a threat even though it is a plain statement of fact.

This is the section most likely to generate a discussion **about the document** rather than about the work — the worst kind, because it stalls everything else in it.

**Recommendation.** Reframe as **what QA depends on** and **what happens without it**. Identical information, stated as mechanics rather than obligation. Also drop the DoD sign-off row: the epic not closing is not a QA consequence, it is just the SDLC, and including it makes the table look padded.

> ### ✅ Answered — 2026-09-22
>
> **Reframe it.** The section keeps every dependency and loses the debt framing.
>
> - The heading becomes **what QA depends on**, and the columns become **what QA relies on** and **what happens without it** — mechanics rather than obligation and penalty.
> - The consequences stay factually identical. *"Assets go unmaintained; QA does not pick them back up"* becomes a statement of where ownership sits, not a warning shot.
> - **The Definition of Done sign-off row is cut.** The epic not closing is the SDLC working normally, not a consequence QA imposes, and its presence made the table look padded. A short table of real dependencies is much harder to dismiss than a long one with filler in it.
>
> The stake here is larger than one table. A reader who concludes QA is issuing demands re-reads the out-of-scope list in that light too — and then the discussion is about QA's posture rather than about capacity, which is the one argument these pages cannot afford to have.

---

### D8 — Escalation ends at the person who wrote the pages

Page 4 routes escalation to the ticket, then to Marek Wyszyński. There is no route past that. The ad-hoc manager session covers **requester versus requester**; nothing covers **requester versus QA**.

A Senior Manager reading a document that names its own author as the final authority on disputes about itself will notice.

**Recommendation.** Name the next step — whoever Marek escalates to, or the ad-hoc session extended to cover disputes with QA. It costs one line and it makes everything else in the document read as a team position rather than one person's.

> ### ✅ Answered — 2026-09-22
>
> **The path continues past QA, in two steps:** difficult or unresolvable requests reach the **Senior QA Manager**, and then the **SW Director for BigPicture**.
>
> Written as **roles rather than names**, so the page does not go stale when people move.
>
> The full path published on page 4 becomes: **the ticket → daily triage → Marek Wyszyński → Senior QA Manager → SW Director for BigPicture.** Most things stop at the first or second step; the point is that the last two exist in print.
>
> **This does more than close a gap.** It is what makes the absolute rules elsewhere defensible — *no work outside the portal*, *no exceptions regardless of size*, *QA does not argue the severity label*. A rule with no appeal reads as stubbornness; the same rule with a published route above the team reads as a team position that the organisation has agreed to. The escalation line is cheap and it underwrites several expensive sentences.

---

### D9 — The awkward arithmetic is better published by QA than discovered by a Director

Eight tickets a week against ten engineer-days implies **about 1.25 engineer-days per request**. Page 4 gets close to saying it and stops. But a feature test is plainly more than 1.25 days, so either the average request is much smaller than feature testing or the ceiling is too high.

Someone will do this division. Found by a reader it is a gotcha; stated by QA with *"measurement will confirm whether it holds"* it is a shared open question — and it makes the case for measuring intake far better than the measurement section does.

**Recommendation.** State the implied average and flag it as unverified. Consider also publishing the quarterly throughput it implies — roughly **seven non-freeze weeks at eight a week, so about 50 to 55 requests a quarter**. That is a throughput figure, not a completion promise, and it answers the planning question the absent SLA leaves hanging. It is the single most useful number the collection could contain, and QA currently has it and does not print it.

> ### ✅ Answered — 2026-09-22
>
> **The quarterly throughput figure is not published yet.** It rests on an assumed fixed ticket size, and that assumption has never been checked against a real quarter. It is revisited at **end of year**, once there is intake data behind it.
>
> **But the inference cannot be withheld, only left unstated.** Eight per week and 2.0 FTE are both on page 4 already, so **anyone can derive the ~1.25 engineer-days per ticket in one division** — and a feature test is obviously more than that. Staying silent does not remove the gotcha; it only removes QA's chance to frame it.
>
> **So the split is: acknowledge the assumption, withhold the total.**
>
> - Page 4 states that the eight-per-week figure **assumes an average ticket size that has not yet been measured**, and that the average is the thing intake measurement is for.
> - **No quarterly throughput number is published**, and the page says why — it would be read as a commitment, and the assumption underneath it is not yet tested.
> - **End of year is named as the checkpoint**, which turns an unverified number into a dated open question rather than a soft spot.
>
> This keeps the credibility benefit of stating the weakest number first, without putting a figure on a page that someone will quote back before it has been earned.

---

### D10 — There is no way for another team to propose a change

The pages are maintained by QA, reviewed at the QA retrospective, with QA as the contact. A Product Manager who thinks a rule is wrong has a person to talk to and no process.

**Recommendation.** One line: raise it with the contact or at the monthly review, and changes are published with the version. Minor, but it converts the set from something issued to something maintained — which matters for a document telling four other functions what to do.

---

## Group 3 — Editorial, being fixed without asking (E1–E7)

| # | Fix |
|---|-----|
| **E1** | Version markers disagree — README says *2.0 (draft for review)*, the pages say *2.0*. Align |
| **E2** | The response commitment, WIP limit, ceiling and release cadence are each restated on three or four pages. They will drift. Page 4 becomes canonical for capacity numbers; the others state the consequence and link |
| **E3** | *Absolutely Critical* is an incident condition, not the Jira severity field. Someone will file a severity-Critical bug and expect QA. One clarifying clause |
| **E4** | Page 6 warns that a *Needed by* date inside a freeze cannot be met; page 1 does not, and page 1 publishes first. Move it |
| **E5** | *"At least one test case per engineer per day"* alongside *"2 to 3 per week"* reads as a contradiction until you work out it means one per **automation** day. Say that |
| **E6** | The *holiday calendar* link is one I introduced while drafting and may not be a real artifact. Drop it to plain text unless it exists |
| **E7** | *"There is no fourth state"* is too absolute once C3 adds the blocked case |

---

## What this adds up to

Nothing here is a hole in the operating model — after two rounds, the model itself is sound and internally consistent. What is left is the difference between a document that is correct and one that is difficult to argue with.

The seven defects are cheap and mostly mechanical. **C1 is the only one with a design decision inside it.**

Of the discussion generators, four are worth the most:

- **D1**, because it fires on every ticket
- **D2**, because it alienates Product Management on page 1
- **D5 and D6**, because they invite arguments that have nothing to do with QA and cost the document its authority on everything else

**D9 is the opportunity rather than the risk.** Publishing the throughput number is the one addition that would meaningfully reduce the questions this collection receives, because it answers the planning question that the deliberate absence of a completion SLA leaves open.
