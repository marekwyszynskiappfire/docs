# Review personas — BP QA Ways of Working

Seven personas used as review lenses for the pages in `Ways of Working/`. Each one represents a group that must be able to act on the pages without asking a person first.

**How to use them.** Read a page *as* the persona and ask their questions out loud. A page that cannot answer a persona's questions is not ready for that audience. Where two personas want incompatible things, the answer is usually a different page rather than a compromise sentence — see the disagreement map at the end.

**Continuity note.** Anna Kowalska appears throughout `review-report.md` as the manager lens from the first review round. She is retained here as **Senior QA Manager**, so existing findings marked *Lens: Anna* still read correctly.

| # | Persona | Role | The question they exist to ask |
|---|---------|------|-------------------------------|
| 1 | Tomasz Nowak | Software Engineer | Can I get what I need without asking anyone? |
| 2 | Priya Raman | QA Engineer | Can I actually apply this on a Tuesday? |
| 3 | Daniel Okonkwo | Software Engineering Manager | Can I plan my team's work around this? |
| 4 | Elena Rossi | QA Manager | Is every rule here decidable at triage? |
| 5 | Anna Kowalska | Senior QA Manager | Is this defensible, measurable and scalable? |
| 6 | Sarah Whitfield | Director of Software Engineering | What is this costing us and what risk are we accepting? |
| 7 | Inês Duarte | Product Manager | What is this document making me responsible for? |

---

## 1 — Tomasz Nowak, Software Engineer

| Attribute | Value |
|-----------|-------|
| Role | Senior Software Engineer, product feature team |
| Tenure | 3 years, deep in one product area |
| Relationship to QA | Occasional requester — a few requests a quarter, plus ad-hoc questions |
| How he reads | Once, in a hurry, because he needs something tested this week |

**What he is trying to do.** Ship a feature behind a flag and get it validated before it is switched on. He does not care about QA's internal model; he wants a predictable answer to "will this be tested, and by when?"

**Goals**

- Work out in under two minutes whether his request belongs in the portal
- Submit once, correctly, with no round-trip for missing information
- Know what happens next without asking a person
- Know where to go for the things QA will not do

**Frustrations**

- Being bounced between the portal, DevOps and the PM with nobody owning the handoff
- Rules written from QA's point of view — "we do not want X" — that never say what to do instead
- Prerequisites discovered only after submitting
- Jargon he is expected to already know
- Being told there is a response time, then finding the clock never started

**Questions he asks of every page**

1. Does this apply to me, or is it internal QA housekeeping?
2. What exactly do I fill in, and where?
3. What happens if I leave something out?
4. When will I hear back, and from whom?
5. This is urgent — is there a faster path, and who approves it?
6. It says "not in the portal", so where *does* it go?
7. What do I get at the end, and how do I know it is finished?

**Good looks like:** one skimmable page, a decision table, and a stated response time with a named owner.

---

## 2 — Priya Raman, QA Engineer

| Attribute | Value |
|-----------|-------|
| Role | QA Engineer, one of four |
| Tenure | 2 years, generalist across the product by necessity |
| Relationship to the pages | She is the one who has to *enforce* them, usually to someone she likes |
| How she reads | Looking for the sentence she can point at when she says no |

**What she is trying to do.** Get through a day where she has two tickets in progress, automation to write, a release approaching, and a developer at her desk asking for "just a quick look".

**Goals**

- Apply the rules without having to make a personal judgement call each time
- Have the document, not her, be the thing that declines work
- Protect the automation half of her week from being eaten
- Know what to do when a ticket turns out to be far bigger than it looked

**Frustrations**

- Rules with thresholds that require her to estimate work before refusing it
- Being the only thing standing between the team and unbounded demand
- Policies written by managers that assume every case is clean
- Being told to "use judgement" and then being second-guessed
- Documentation that describes the happy path and goes quiet on the awkward cases

**Questions she asks of every page**

1. If someone asks me for this in Slack, what exactly do I say?
2. Does this rule need me to decide something, or does it decide for me?
3. What do I do when the answer is "it depends"?
4. My ticket is blocked — can I pull another, or do I sit on it?
5. I estimated this at three weeks and the deadline is Friday. Now what?
6. Am I allowed to say no to this, and who backs me up?
7. Does this protect my automation time or quietly spend it?

**Good looks like:** rules that are absolute rather than judgement-based, a written path for every awkward case, and an explicit statement of what she is allowed to refuse.

---

## 3 — Daniel Okonkwo, Software Engineering Manager

| Attribute | Value |
|-----------|-------|
| Role | Engineering Manager, two feature teams |
| Relationship to QA | Dependent — his teams' delivery dates assume QA capacity he does not control |
| How he reads | Looking for the parts that constrain his plan |

**What he is trying to do.** Commit to delivery dates for his teams and hit them. QA sits in the critical path of every one of those commitments and reports to someone else.

**Goals**

- Know far enough ahead whether QA can support a delivery
- Understand what his teams must produce so QA is not blocked by them
- Have a route to raise a genuine conflict without it becoming a political fight
- Avoid discovering a QA constraint in the week it matters

**Frustrations**

- A dependency that will not give him a date
- Being deprioritised without being told why, or being told after the fact
- Quality bars applied to his team's documentation that are never written down
- Escalation paths that terminate in "talk to the team"
- Discovering during a release that nothing of his will be looked at for two weeks

**Questions he asks of every page**

1. How far ahead do I need to tell QA about this?
2. What is my team accountable for producing, precisely?
3. If my request is deprioritised, how do I find out and how do I contest it?
4. Another manager and I both need QA the same week — how is that settled, and can I be in the room?
5. What does a release do to my plans, and how much notice do I get?
6. If QA cannot do it, what is my alternative — and is that alternative sanctioned?
7. Who do I talk to when this is not working?

**Good looks like:** lead times he can plan against, a clear statement of his own team's obligations, and a named forum where conflicts get settled.

---

## 4 — Elena Rossi, QA Manager

| Attribute | Value |
|-----------|-------|
| Role | QA Manager, runs the daily triage and owns day-to-day operation |
| Relationship to the pages | Operates them, every working day |
| How she reads | Testing whether each rule can be applied in a ten-minute meeting |

**What she is trying to do.** Run a triage meeting that reaches decisions quickly, consistently, and the same way whoever is in the room.

**Goals**

- Make every rule decidable without a debate
- Keep the queue honest — no silent backlog, no hidden holds
- Keep the team's commitments and its capacity in the same relationship
- Hand over the meeting to someone else without the process degrading

**Frustrations**

- Criteria that are adjectives — "absolutely Critical", "substantially incomplete" — with nobody named to decide
- Ticket states that exist in practice but not on paper
- Rules that assume everyone is present and nobody is on holiday
- Growing lists of parked work that nobody ever revisits
- Time zones: commitments expressed in working hours without saying whose

**Questions she asks of every page**

1. Who decides this, when the room disagrees?
2. Can this decision be made in the meeting, or does it need research first?
3. What happens when the person who normally decides is away?
4. Where does this ticket state appear in Jira, and who reviews it?
5. Whose business hours are these?
6. What is the rule when the answer is genuinely borderline?
7. If I hand this meeting to someone else tomorrow, what breaks?

**Good looks like:** every criterion has a decider, every state has a review cadence, and every commitment names the working hours it runs in.

---

## 5 — Anna Kowalska, Senior QA Manager

| Attribute | Value |
|-----------|-------|
| Role | Senior QA Manager, accountable for the QA function across the organisation |
| Relationship to QA | Owns capacity, prioritisation and headcount arguments |
| How she reads | Carefully, twice, then defends it to peers and to her director |

**What she is trying to do.** Turn QA from an interrupt-driven service into a function with visible demand, defensible capacity and evidence of value — and survive contact with a peer manager whose work was deprioritised.

**Goals**

- Make all QA demand visible in one place, so capacity arguments rest on data
- Decline out-of-scope work without a political fight
- Show attainment and throughput well enough to justify headcount
- Protect the team from interrupt-driven work and burnout
- Publish something other teams follow, rather than a wishlist

**Frustrations**

- Commitments made without a capacity model behind them
- Boundaries stated as preferences rather than enforceable policy with a redirect
- Processes with no owner, no cadence and no metric
- Work arriving through side channels, invisible to the queue
- Documents that describe the happy path and omit escalation and exceptions
- Measurement that is listed as a good idea but never assigned to anyone

**Questions she asks of every page**

1. Who owns this by name or role, and what happens when they are away?
2. What measure tells me it is working, where is it reported, and who produces it?
3. When two requesters both claim urgency, who decides?
4. Is this commitment backed by capacity, or is it aspirational?
5. What enforces this when someone bypasses it?
6. How does this scale from four engineers, and what breaks first?
7. Can I defend this sentence to a peer whose request was declined?

**Good looks like:** every commitment has an owner, a measure and an exception path; scope is a rule others can apply themselves; and the document names what it has not solved.

---

## 6 — Sarah Whitfield, Director of Software Engineering

| Attribute | Value |
|-----------|-------|
| Role | Director, owns the engineering organisation that QA serves |
| Relationship to QA | Funds it, and answers for delivery predictability above it |
| How she reads | The index and one page. Ten minutes, looking for cost, risk and the decision she is being asked to endorse |

**What she is trying to do.** Understand what the organisation gets from QA, what it gives up, and which risks she is now implicitly accepting by letting this be published.

**Goals**

- Know the trade being made, stated as a trade
- See where the model breaks before it breaks
- Avoid a shared-service bottleneck silently becoming everyone's critical path
- Understand key-person risk and succession
- Be able to answer "why does QA not commit to dates?" in one sentence

**Frustrations**

- Documents that describe process without stating cost
- Risks listed without an owner or a trigger point
- Single points of contact presented as a strength
- Being asked to endorse an operating model that was never framed as a choice
- Finding out about a capability exit — a tool, an activity — after another team has inherited it

**Questions she asks of every page**

1. What is the trade here, in one sentence?
2. What does this cost other teams — buffer, delay, rework?
3. At what size or demand level does this stop working?
4. Who else has agreed to what this document assumes of them?
5. What is the key-person risk, and what is the succession plan?
6. Which risks are we accepting rather than mitigating, and who signed that off?
7. What would I see, and when, if this were failing?

**Good looks like:** an explicit trade, named scaling limits, evidence that dependent teams have agreed to their obligations, and risks that are accepted deliberately rather than by omission.

---

## 7 — Inês Duarte, Product Manager

| Attribute | Value |
|-----------|-------|
| Role | Product Manager for two product areas |
| Relationship to QA | Named in the pages as an owner of things she has not been asked about |
| How she reads | Defensively, once she realises the document assigns her work |

**What she is trying to do.** Get features specified, built and shipped. She is a source of the requirements QA depends on, and the pages make her accountable for several inputs and one decision.

**What the pages currently ask of her**

- authoring clear acceptance criteria, as part of Definition of Ready
- defining performance thresholds, jointly with Engineering, for the RUM release gate
- signing off Definition of Done
- being a source of truth on whether a feature is really shipping soon — which changes a request's priority

**Goals**

- Know precisely what QA needs from her, and when
- Not have her features delayed by a documentation bar she did not know existed
- Understand what QA's "Done" does and does not mean for her sign-off
- Keep the performance gate from blocking a release on a threshold nobody ever set

**Frustrations**

- Being assigned responsibilities by another team's document
- Quality bars on her specifications that are judged but never published
- Learning that a release was gated on criteria she was supposed to have defined
- QA closing a ticket as Done when the feature is plainly not done
- Informal conversations changing a queue position with no record

**Questions she asks of every page**

1. What am I accountable for here, and did anyone ask me?
2. What does "very clearly defined acceptance criteria" actually mean — who judges it?
3. If I have not set a performance threshold, what happens at the release gate?
4. QA says Done, but bugs are open — what am I signing off?
5. Someone told QA my feature is not shipping soon and my request was deprioritised. Where is that recorded and how do I correct it?
6. What is the difference between QA finishing and the epic being finished?
7. Where is the page written for me?

**Good looks like:** her obligations stated in one place, agreed rather than assumed, with the bar made concrete and every priority decision recorded on the ticket.

---

## Where the personas disagree

The tensions worth recording, because several findings sit exactly on them.

| Topic | Pulling one way | Pulling the other |
|-------|-----------------|-------------------|
| Intake detail | **Tomasz**: few fields, submit fast | **Elena**: complete fields, so triage is not research |
| Urgency | **Tomasz, Daniel**: a fast lane we can use | **Anna, Priya**: a lane that is rationed, or it stops meaning anything |
| Dates | **Daniel, Sarah**: give me something to plan against | **Priya, Elena**: do not promise what the queue cannot deliver |
| Rules | **Priya**: absolute, so I never have to judge | **Daniel, Inês**: flexible, because my case is genuinely different |
| Documentation bar | **Priya, Elena**: strict, it is what makes generalist testing work | **Inês**: published and objective, or it is arbitrary |
| Scope | **Anna**: a boundary that holds under pressure | **Sarah**: a boundary that does not push cost onto other teams invisibly |
| Detail | **Tomasz**: one short page | **Anna, Elena**: enough precision to settle a dispute |
| Ownership | **Sarah**: no single point of failure | **Anna**: a named contact, or nobody owns it |

Two of these are unresolved in the current pages rather than traded off deliberately: **dates** and the **documentation bar**. Both appear in the question list.
