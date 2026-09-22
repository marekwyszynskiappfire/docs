# Open questions — BP QA Way of Working

Working file for the grilling session that turns `WoW.md` into publishable Confluence pages. Questions are grouped into **rounds**: each round contains every question whose prerequisites are already settled. Answering a round pushes the frontier outward and unlocks the next one.

**Delivery mode: one question at a time.** At the user's request (2026-09-21), questions are put one by one rather than a whole round at once. The round grouping below still governs *order* and *dependencies*; it no longer governs how many are asked per message.

**How to use this file:** answer in the chat, or write answers directly under each question. Settled answers move to the *Settled decisions* table and are mirrored into `MEMORY.md` so nothing is lost between sessions.

**Legend:** ⬜ open · ✅ settled · 🔁 revisited

---

## Settled decisions

| # | Decision | Answer | Date |
|---|----------|--------|------|
| Q1 | Confluence page structure | Five pages, one audience each | 2026-09-21 |
| Q2 | Language | English only, all five pages, glossary for acronyms | 2026-09-21 |
| Q3 | Scope principle | Single principle, lists demoted to examples. Release blockers **in**, BugCrowd **in**, Kibana/DataStudio/dashboards **out** | 2026-09-21 |
| Q3b | Observability exit | Full exit, all assets inherited by engineering. RUM retained as a **pre-release performance regression review** | 2026-09-21 |
| Q3c | RUM review modelling | Part of the **release process**, not a portal request. Engineering owns the RUM Events portal; QA reviews the data only. Thresholds are set by **Product Management and Engineering** | 2026-09-21 |
| Q3d | RUM gate outcome | Pass → release proceeds. Fail → **ticket to Engineering** naming module and events; Engineering fixes; **QA re-reviews**. A blocking loop | 2026-09-21 |
| Q3e | RUM edge cases | As recommended, and already current practice: missing threshold recorded as **not assessable**; known regressions shipped only on a **recorded waiver**. **RUM branch closed** | 2026-09-21 |
| Q4 | Bug boundary | QA files bugs **it finds**, never **on behalf of** Engineering, PM or Support. Release blocker = **severity ≥ Medium**, per existing rules to be linked. QA **does** create BugCrowd issues | 2026-09-21 |
| Q4b | Blocker context | A release blocker is a bug raised **during Release Testing**. **No bug of severity ≥ Medium is ever released.** Severity rules already exist; link, do not restate | 2026-09-21 |
| Q5 | Urgency handling | **Deadline-aware prioritisation.** A **"Needed by…"** field already exists in the portal. Some requests are **not feasible at short notice** regardless of the date. Portal mechanics move to a **sixth page** | 2026-09-21 |
| Q6 | Assignment model | **Pull.** No assignment by Engineering or anyone else. Tickets are **triaged daily**; whoever has capacity picks one up | 2026-09-21 |
| Q6b | Pull mechanics | **Ordered by priority**, set at the **daily triage meeting**. **4 QA Engineers, WIP limit 2 each.** Unclaimed tickets with tight deadlines get a **comment and a discussion** | 2026-09-21 |
| Q7 | Triage clock | **24 business hours**, not 24 hours flat. Triage meeting runs **daily at 10:00 CET** | 2026-09-21 |
| Q7b | Returned tickets | **The clock stops** while the ticket sits with the requester. Stale-return closure rule **still open** | 2026-09-21 |
| Q8 | Ownership | Maintained by the **QA Team**. Reviewed **monthly at Team Retrospective Sessions**. First point of contact: **Marek Wyszyński** | 2026-09-21 |
| Q9 | Capacity | **50/50** portal work and test automation, shifting toward automation over time. Intake **not yet measured**, believed modest. **The WIP ceiling is never exceeded**; at the ceiling the team negotiates the deadline or parks other work. Requesters are asked to **submit early** | 2026-09-21 |
| Q10 | SLA form | **Two-tier.** A firm **response** commitment (triage in 24 business hours) plus **typical completion ranges** that are not guarantees. At the ceiling the date is **negotiated at triage** | 2026-09-21 |
| Q11 | Category sorting | Three kinds of work, not two. Most categories **requestable**; initiative regression is a **QA-raised portal ticket**; release blockers, RUM, TR and Sanity are **release-process**; BugCrowd is **standing intake** | 2026-09-21 |
| Q11b | Release periods | **Release work pre-empts everything.** No other work is submitted or tackled. **One Release ticket** in the portal; the detail lives in **linked Jira tickets visible to all** | 2026-09-21 |
| Q11c | Release visibility | **Slack `#bp-status-release-feature`** carries release communication. A **Jira filter showing all QA tickets** is to be created. **Daily meetings run during releases**; tickets get comments — never silence | 2026-09-21 |
| Q12 | Environments | QA **creates instances for its own work** — release process, testing and verifying features. QA does **not offer instance creation as a service** to external parties | 2026-09-21 |
| Q13 | Priority | **Standard Jira scale.** Everything arrives as **Medium** by default. QA assesses and re-assesses at triage, **taking "Needed by…" into consideration** | 2026-09-21 |
| Q13b | Priority triggers | **"Needed by…" is the main determinant.** **High/Highest**: release-related work and Critical production issues needing QA assistance. **Lowered** when QA learns from Engineering or PM that the feature is not shipping soon, or documentation is massively incomplete | 2026-09-21 |
| Q14 | Production issues | QA does **not handle production issues**, with one exception: **absolutely Critical** issues where **QA verification is needed**. Verification is the *only* help provided | 2026-09-21 |
| Q14b | Closure | QA **closes the ticket as Done**, adds a **fitting comment**, and provides **links to any artifacts** created while working the ticket | 2026-09-21 |
| Q15 | Out-of-band work | **No work arriving outside the portal will be tackled.** The requester is **always redirected to the portal**. No exceptions | 2026-09-21 |
| Q16 | Shift-left | **Asynchronous review**, produced with **AI-assisted tooling**, with **QA reviewing the tool output** before returning **additional questions** to the requester. Not meeting attendance | 2026-09-21 |
| Q18 | Completion times | **No published completion ranges.** Effort is **estimated by the QA engineer who picks the ticket up**, and communicated only then | 2026-09-21 |
| Q19 | Product depth | **Generalist by design** — the team is too small to specialise. Depth is replaced by **knowledge sharing, AI tooling, documented test cases, and a required clear feature description**, so that the **need for in-depth knowledge is minimised** | 2026-09-21 |
| Q18b | Triage feedback | Triage **always comments**: that the issue has been **picked up**, that it **needs more information**, or that it is **on hold until a stated point**, **with the reason given** | 2026-09-21 |
| Q17 | DoR / DoD | **Epic-level, shared with Engineering — not QA portal rules.** DoR: clear functionality description, clearly defined acceptance criteria, stated implementation out-of-scope, relevant Figma designs. DoD: Engineering and QA work complete **and PM sign-off** — the sign-off is **outside QA scope**. **QA provides the testing results, and that is it** | 2026-09-21 |
| Q10 | SLA shape | **Firm triage commitment + typical completion ranges**, with the capacity assumption stated and the date negotiated at the ceiling. Numbers are **not guarantees** | 2026-09-21 |

---

## Round 1 — foundations

These eight have no unanswered prerequisites. Everything else in the tree hangs off them.

### ✅ Q1 — Page structure and audience split

**Answer: the five-page split, as recommended.** The page set is fixed as:

1. **Requesting QA work** — requesters
2. **QA Portal scope** — requesters and managers
3. **How the QA team works** — QA team and managers
4. **Service levels and measures** — managers
5. **Appendix: QA activity inventory** — QA internal

Everything settled from here on is filed against one of these five pages.

<details><summary>Original question</summary>

`WoW.md` currently serves QA, requesters and management in one document, and serves none of them well (finding C8). The proposal is five Confluence pages, each with one audience: *Requesting QA work* (requesters), *QA Portal scope* (requesters and managers), *How the QA team works* (QA and managers), *Service levels and measures* (managers), and *Appendix: activity inventory* (QA internal).

Alternatives: a single long page with anchors; or two pages only, external and internal.

➡️ **Recommended:** the five-page split. The requester page is the one that must be skimmable in two minutes, and it cannot be if it carries the capacity model.

</details>

---

### ✅ Q2 — Language of the published pages

**Answer: English only, across all five pages including the internal appendix.** The company is international, so Polish is not carried into any published page. Polish terms currently in `WoW.md` §8 (*analiza wymagań*, *weryfikacja fixów*, *projektowanie scenariuszy testowych*, *wrzutki* and others) are translated rather than kept alongside the English.

A **glossary** is still required, because the acronym problem is separate from the language problem: `TR`, `BP`, `BG`, `BT`, `AAN`, `JCMA`, `FF`, `RUM`, `UT` are expanded on first use and collected in one place. `TR` additionally needs disambiguating — it is currently used for two different things.

<details><summary>Original question</summary>

`WoW.md` mixes English with Polish terms (*analiza wymagań*, *weryfikacja fixów*, *wrzutki*) and uses acronyms with no expansion (findings N1, N2).

➡️ **Recommended:** English only for all published pages, with a short glossary section covering both the Polish concepts and the internal acronyms (`TR`, `BP`, `BG`, `BT`, `AAN`, `JCMA`, `FF`, `RUM`). Keep Polish only inside the internal appendix if the team prefers it there.

</details>

---

### ✅ Q3 — The scope principle

**Answer: adopt a single principle with the lists as worked examples, and three specific scope calls.**

| Area | Call |
|------|------|
| Release blocker testing | **In scope** |
| BugCrowd | **In scope** — stays with the QA team, despite being reactive work |
| Kibana, DataStudio, dashboards | **Out of scope** — the team will not work with these tools any more |

The "planned versus reactive" rule proposed in the question **does not survive these answers**: release blockers and BugCrowd are both reactive and both in scope. The dividing line is therefore not the timing of the work but its subject. Revised principle:

> The QA Portal covers **testing the product and maintaining the assets used to test it**. It does not cover infrastructure and tooling operations, customer support, or decisions about how the product should behave. Reactive work enters the portal only when it is **release-critical** or **security-related**; routine defect verification stays with the feature team.

Consequences to carry into the rewrite:

- `WoW.md` §2 currently lists observability ("Kibana and DataStudio features; dashboard updates") as in scope. It moves to the out-of-scope page.
- `WoW.md` §8.4 (Observability and data) is largely work the team is exiting. What remains of it, if anything, is open — see Q3b.
- `WoW.md` §4.1 asks requesters "what we want to measure — dashboards?" as required request information. That field is removed.
- Two new contradictions are created by these answers and are tracked as Q4 (reframed) and Q3b below.

<details><summary>Original question</summary>

Scope is currently three overlapping lists that must be maintained by hand and already diverge (finding M9). A single rule lets requesters classify their own edge cases.

Candidate rule: *the portal accepts planned QA effort with a defined deliverable and a named requirement; it does not accept reactive verification of individual defects, infrastructure requests, or questions about intended behaviour.*

Alternatives: keep enumeration only; or split by effort size (anything over N days goes to the portal).

➡️ **Recommended:** adopt a single principle of that shape, then keep the existing lists underneath it as worked examples rather than as the definition.

</details>

---

### ✅ Q3b — How far does the observability exit reach, and who takes the work?

**Answer: a full exit, with one retained activity.**

- **All dashboard and reporting assets are inherited by engineering.** No phased handover was considered necessary.
- **Rationale, recorded because it is the defence for the decision:** apart from RUM, these dashboards no longer have an audience — nobody is acting on their results. The exit removes maintenance cost from work that had stopped producing value, rather than shifting a live obligation onto another team.
- **RUM is retained, but in a changed role.** QA no longer maintains RUM dashboards as an observability asset; QA **reviews RUM event dashboards before a release** to establish whether performance has regressed across modules. This is a release quality gate that consumes a dashboard, not dashboard maintenance.

This is consistent with the Q3 principle: reviewing RUM before release is testing the product; building and maintaining reporting tooling is not.

Two consequences are unresolved and tracked as Q3c below: how the pre-release RUM review is modelled, and the fact that QA now depends for a release gate on an asset owned by another team.

<details><summary>Original question</summary>

*Raised by the answer to Q3.* Dropping Kibana, DataStudio and dashboards is a clean scope call, but `WoW.md` §8.4 contains neighbouring work that the answer does not obviously cover: **BigQuery maintenance**, **Grafana**, **RUM event requirements and rollout**, and **error analysis across tools (Anomaly detector)**. §8.3 also lists **monitoring active user counts on image instances**.

Two things need settling: which of those neighbours are also being exited, and **who owns the dashboards and data assets that exist today** once QA stops maintaining them. A tooling exit with no named successor tends to come back as ad-hoc requests within a quarter, which is precisely the side-channel risk in §7.

➡️ **Recommended:** exit the full reporting-and-dashboard stack (Kibana, Grafana, DataStudio, BigQuery) with a named receiving team and a handover date; **keep** RUM event requirements, since that is requirement authoring rather than tooling operation; treat log verification during testing as part of testing, not observability work.

</details>

---

### ✅ Q3c — How is the pre-release RUM review modelled, and who owns the dashboard it depends on?

**Answer, on both parts:**

- **Modelling:** reviewing RUM dashboards is **part of the release process**. It does not require a request through the QA Portal and is not a portal request type. It is documented on the "How the QA team works" page under release activities.
- **Ownership:** the **Engineering team owns the RUM Events portal**. QA does not maintain it. QA's role is to **review the data displayed there** and assess whether a regression has occurred. The recommended carve-out was not taken; engineering ownership stands.
- **Criteria:** a regression is a drop in performance below **thresholds defined by Product Management and Engineering**. QA does not set thresholds. QA reviews the data, dashboards and graphs against them.

This keeps the portal queue free of recurring, unrequested work and keeps QA out of tooling ownership, consistent with Q3 and Q3b. It leaves QA as an assessor working to criteria owned elsewhere, which is a deliberate and defensible position — and which raises the authority question tracked as Q3d.

<details><summary>Original question</summary>

*Raised by the answer to Q3b.* Two linked parts.

**Part one — is it a portal request or a standing release step?** The RUM performance review happens for every release, triggered by the release itself rather than by a requester. Modelling it as a portal ticket puts recurring, predictable work into a queue designed for requested work, and it would consume SLA capacity for something nobody actually requests. Modelling it as a release-process step keeps the queue clean, but then it must be documented somewhere other than the portal pages, and it becomes invisible in portal throughput figures.

**Part two — ownership of the asset.** Engineering now owns all dashboard assets, including RUM. QA depends on the RUM dashboard for a release gate. If it breaks, changes shape, or loses an event, the gate silently stops working and QA finds out at release time. The agreed Q3 principle says QA maintains "the assets used to test the product", which argues for RUM dashboards being the exception that stays with QA.

Also unresolved, and deferred to a later round: what counts as a **regression**. "No regression across modules" is a judgement call until a threshold exists.

➡️ **Recommended:** model it as a **standing step in the release process**, listed on the "How the QA team works" page under release activities rather than as a portal request type; and carve RUM dashboards out of the handover so the asset QA gates on stays with QA. If engineering must own them, state the dependency explicitly and name who QA notifies when the dashboard is wrong.

</details>

---

### ✅ Q3d — What does QA do when the RUM review fails, and what if no threshold exists?

**Answer: the gate blocks, and the fix belongs to Engineering.**

| Outcome | Action |
|---------|--------|
| Data within thresholds | The release proceeds |
| Performance below threshold | QA **escalates to Engineering via a ticket**, identifying **which module** is regressing and **on which events**. Engineering owns the fix. When it is done, **QA reviews the dashboards again** |

This is a **blocking gate with a re-review loop**, not the advisory report that was recommended. QA does not diagnose or fix; QA identifies the affected module and events with enough precision for Engineering to act, and re-checks afterwards.

The division of labour across the gate is now complete: **Engineering** owns the RUM Events portal and the fix, **Product Management and Engineering** own the thresholds, and **QA** owns the assessment and the escalation.

**Not settled by this answer**, carried into Q3e: the behaviour when a module has no threshold defined, and whether a known regression can ever be released without a fix.

<details><summary>Original question</summary>

*Raised by the answer to Q3c, and the last open item in the RUM branch.*

QA now reviews data against criteria owned by Product Management and Engineering. That is a clear division, but it leaves the **decision right** unassigned. Three things need settling, and they are one decision:

**What QA's output is.** Does QA record a finding ("module X is 18% below threshold") and hand it on, or does QA hold a stop on the release until someone clears it? A review with no stated consequence is a report, not a gate, and the release page should say which one this is.

**Who acts on it.** If QA does not own the threshold, QA arguably should not own the go/no-go decision either. But someone must, by name or role, and the release cannot wait for that to be worked out in the moment.

**What happens when there is no threshold.** Thresholds are owned by PM and Engineering, and it is unlikely every module has one defined today. If a module has no threshold, QA cannot assess it, and the release process currently has no defined behaviour for that state — the gate silently passes.

➡️ **Recommended:** QA **reports** against thresholds and does not hold the stop; the release manager makes the go/no-go call using QA's finding. Where a module has no defined threshold, QA records "not assessable — no threshold defined" rather than passing it silently, which makes the gap visible to PM and Engineering and creates pressure to close it. Modules without thresholds are listed on the release page so the coverage gap is known rather than discovered.

</details>

---

### ✅ Q3e — The two cases the gate loop does not cover

**Answer: both as recommended — and both already reflect how the team works today.** The gap was in the document, not in the practice, so this is a matter of writing down what already happens:

- A module with **no defined threshold** is recorded as **not assessable**, never as a pass, and those modules are visible on the release page.
- A **known regression can be released under a recorded waiver**, rather than the fix being the only exit from the loop. The escalation ticket stays open.

**The RUM branch is closed.** No further questions in this area.

<details><summary>Original question</summary>

*Last open item in the RUM branch.* The pass and fail paths are settled; two states fall between them.

**A module with no threshold.** Thresholds belong to PM and Engineering, and it is unlikely every module has one today. "If the data is OK we proceed" cannot be evaluated where nothing defines OK. The dangerous part is that an unassessable module currently looks exactly like a passing one.

**A regression nobody intends to fix before shipping.** The loop as described has no exit other than a fix: escalate, fix, re-review. Real releases eventually meet a small regression that is understood and accepted, or one discovered too late to fix. With no waiver path, that decision will be made informally, off the page, by whoever is in the room — which is precisely the outcome the document exists to prevent.

➡️ **Recommended:** record a missing threshold as **"not assessable — no threshold defined"** rather than a pass, and list those modules on the release page so the coverage gap is visible to the people who own it. For the second, add a narrow **waiver**: the release proceeds with a known regression only on a recorded decision by a named role — release manager with PM agreement — with the ticket staying open. Both keep the exception visible instead of silent.

</details>

---

### ✅ Q4 — The bug boundary: what QA files, and what separates a blocker from a regular bug

**Answer on all three parts.**

**1. The distinction is *on whose behalf*, not *whether QA files bugs*.** QA does **not** create bugs on behalf of someone else — not for Engineering, not for Product Management, not for Support. QA **does** create bugs for issues **QA itself has found**. This replaces the current §3 wording, which reads as though QA does not file bugs at all.

**2. A release blocker is an issue of severity ≥ Medium.** The severity rules already exist and are written down; the published pages **link** to them rather than restating them, so the two cannot drift apart. *(Checked: no severity rubric exists in this repository — it lives in Confluence or Jira, so the link is an external dependency for the rewrite.)*

**3. QA also creates BugCrowd issues.** BugCrowd findings originate with external security researchers, so this is a deliberate carve-out from rule 1 rather than a contradiction of it: the "not on behalf of others" rule covers **internal colleagues**, while externally-sourced security findings are QA's to raise.

**A consequence worth stating plainly on the scope page.** If severity ≥ Medium is in scope, then the out-of-scope line for "regular / simple bug testing" covers **Low severity only**. As currently written, §3 reads as "QA does not test bugs", when the real rule is far narrower. Leaving it as is would decline work the team actually accepts.

**Not settled**, carried to Q4b: who assigns the severity that now determines scope.

<details><summary>Original question</summary>

*Reframed after Q3.* Two problems now sit together.

**First**, as written the document says QA does not create bug reports, which contradicts its own activity inventory (finding C2). Either **(a)** requesters cannot ask the portal to test or file an individual bug, while QA still raises bugs found during portal work as a normal part of it, or **(b)** bug work is genuinely outside the team's remit.

**Second**, and new: release blocker testing is now **in** scope while "regular / simple bug testing" stays **out**. Both are bug testing, so the boundary is severity, not activity — and the document defines neither the threshold nor who applies it. Without that, every requester has an incentive to label their bug a blocker, and the distinction collapses on first contact. Related: BugCrowd is in scope while "bug reporting" is out, so BugCrowd needs stating as its own intake class rather than as an exception nobody can explain.

➡️ **Recommended:** (a) for the first part. For the second, define a release blocker by a testable condition rather than by judgement — a defect on a release candidate that would prevent the release from shipping — and give the classification to a named role (release manager or QA lead), not the requester. State BugCrowd separately as an externally-sourced security intake with its own handling.

</details>

---

### ✅ Q4b — Who assigns severity, and does blocker status depend on release context?

**Answer: release context is required, and the bar is absolute.**

- A release blocker is a bug **raised during the Release Testing activity**. Severity alone does not make a defect a blocker; it must arise in that context.
- **No bug of severity ≥ Medium is ever released.** This is a hard rule, not a judgement.
- Severity assignment is governed by the **existing written rules**. The published pages link them; they are not restated here and the question is not reopened.

**The important structural consequence.** Because blockers arise from **QA's own Release Testing** rather than from a request, release blocker testing does not enter the QA Portal as an intake category at all. It is a **release-process activity**, exactly like the RUM review settled in Q3c. Listing it among portal request types in §2 would tell requesters they can submit something that is not submittable.

This also corrects the concern raised under Q4 that the out-of-scope bug line would collapse to Low severity only. It does not: **requester-submitted bug testing stays out of scope at every severity**, because the in-scope blocker work is not requester-submitted.

<details><summary>Original question</summary>

*Raised by the answer to Q4.* Severity now decides what the portal accepts, which moves the original problem rather than removing it: instead of requesters labelling their bug a blocker, they set the severity field.

**Who sets severity.** If the reporter sets it, the incentive to inflate is obvious and the boundary erodes the same way. If QA sets or confirms it, the team controls its own intake but adds a step to every request. If it is governed by the existing written rules with a named arbiter for disputes, the rules do the work.

**Whether release context matters.** Read literally, "severity ≥ Medium" makes any Medium defect a release blocker regardless of when or where it is found — including one raised mid-sprint with no release in sight. If the existing rules already bind severity to a release candidate, that answers it and the page simply links them. If they do not, the portal scope line needs the extra condition, or QA inherits every Medium bug in the product.

➡️ **Recommended:** severity is assigned per the existing written rules, with **QA confirming it at triage** and a named arbiter — QA lead with the release manager — for disagreements; and blocker status requires **both** severity ≥ Medium **and** a link to a release candidate, unless the existing rules already say so. Please point me at the severity document and I will check rather than assume.

</details>

---

### ✅ Q5 — Is there an expedite path for urgent portal requests?

**Answer: mostly (c), deadline-aware prioritisation, with one hard qualification and one structural change.**

- **The mechanism already exists.** The portal form has a **"Needed by…"** field, so the required-by date is captured today. The rewrite documents how that date is *used*, rather than introducing anything new.
- **A deadline does not create capacity.** Some requests are simply not feasible at short notice — testing an entire feature as a last-minute request being the clear example. Deadline-aware ordering decides *what comes first among things that can be done*; it does not make an impossible request possible.
- **Portal mechanics become a sixth page.** How the portal itself is operated — the form, the fields, screenshots, the walkthrough — is a **dedicated document**, separate from the ways of working. It was agreed as its own discussion.

**Revises Q1:** the page set grows from five to six. See the updated structure in `MEMORY.md`.

**Folded into Round 2:** what QA does when a "Needed by" date cannot be met is really the capacity question (finding C5), and is answered there rather than as a separate branch.

<details><summary>Original question</summary>

*Reframed after Q4b.* The original question asked about a fast lane for release blockers. That premise is gone: blockers arise during QA's own Release Testing and never pass through portal intake, so they cannot be delayed by triage or by the queue. Effectively answer **(b)** — no lane needed, because they are not portal work.

The underlying question survives in a different form. Portal requests will sometimes be genuinely urgent for reasons unrelated to a release: a customer commitment, a deadline outside the team's control, a demo. The current process offers one speed, and a requester with a real deadline has no route other than finding a QA engineer directly — which is the side-channel problem §7 already names.

- **(a)** A named expedite path, rationed (for example one in flight at a time) and approved by a named role rather than claimed by the requester.
- **(b)** No expedite path. Urgency is expressed only through queue priority, and the honest answer to a requester is that the queue is the queue.
- **(c)** Deadline-aware prioritisation: requests carry a required-by date, and the queue orders by deadline risk rather than by an urgency flag.

➡️ **Recommended:** (c), with (a) as a narrow exception. Option (b) is clean but tends to produce exactly the informal bypass the document is trying to eliminate, and a deadline field is information the team needs at triage anyway — §4.1 already asks for it.

</details>

---

### ✅ Q6 — Assignment model: pull or assign

**Answer: pull, without qualification.** Option (a), not the recommended hybrid.

- **Nobody assigns QA work** — not Engineering, not Product Management, not the QA lead.
- Tickets are **triaged daily**.
- **Whoever has capacity picks one up.**

This settles finding C1 and also answers the open question left in §5.5: queue items carry **no assignee until someone pulls them**. The assignment language currently in §5.3 ("the team estimates and checks who has open capacity") is removed rather than reconciled.

Two consequences that must be carried, not forgotten:

- **The area-ownership risk in §7 is now live.** The recommended hybrid existed to protect work that needs a specific person's product knowledge. Choosing pure pull means the team is operating as generalists by policy, and "lack of knowledge about areas" and "lower product familiarity, weaker tests" move from open questions to accepted risks that need a mitigation.
- **"Triaged daily" gives Q7 part of its answer** — the cadence is daily, which delivers the 24-hour triage commitment. Ownership of triage and the clock rules are still open.

<details><summary>Original question</summary>

§5.3 asserts both models at once (finding C1). Options:

- **(a)** Pull: the queue is prioritised, engineers take the top item they can work on, WIP limit of two.
- **(b)** Assign: during daily planning the team estimates and allocates to whoever has capacity.
- **(c)** Hybrid: pull by default, assignment only for expedites and for work needing specific domain knowledge.

➡️ **Recommended:** (c). Pure pull breaks when a ticket needs a specific person's product knowledge — a risk the document already names in §7.

</details>

---

### ✅ Q6b — What constrains the pull, and what happens to a ticket nobody takes?

**Answer: the pull is ordered by priority, and unclaimed work is surfaced by conversation rather than by rule.**

- **The team is 4 QA Engineers.**
- **WIP limit: no more than two tickets** held and worked on by any engineer at a time. The reason matters and belongs in the document: engineers also **automate test cases as part of their daily work**, so portal tickets never occupy their whole capacity.
- **Tickets are pulled by priority**, and priority is **assessed at the daily triage meeting**. This is ordered pull, as recommended — the queue is not a menu.
- **An unclaimed ticket with a tight deadline** gets a **comment in the ticket**, and a discussion is started if needed. The daily triage meeting is what surfaces it.

**Capacity arithmetic now available for Round 2.** Four engineers at a WIP of two gives a ceiling of **eight portal tickets in progress at once**, and that ceiling assumes no automation time, which the WIP limit exists precisely to protect. The remaining unknown is how the working week divides between portal tickets and automation.

**Vocabulary note for the rewrite.** "No more than two tickets can be *assigned*" describes tickets held in progress, not assignment in the Q6 sense. With a pull model the published pages should say **claimed** or **in progress**, or the two ideas will read as a contradiction. This is finding N4.

<details><summary>Original question</summary>

*Raised by the answer to Q6.* Pure pull is a clean model, and it has two well-known failure modes. Both need an answer on the page, because both will otherwise be settled informally.

**Is the pull ordered or free choice?** "Whoever has capacity picks them up" does not say *which* ticket they pick. If engineers take the top of the prioritised queue, priority means something and the model is disciplined. If they choose freely, the queue is a menu: quick and familiar work is taken first, and awkward, unfamiliar or tedious tickets are passed over repeatedly. That second outcome is not a failure of good faith — it is what free-choice pull does under time pressure.

**What happens to a ticket nobody picks?** With no assignment, no ticket has an owner by default. A request needing knowledge only one person has, or one everybody finds unattractive, can sit in the queue while its "Needed by" date passes and still be nobody's problem. The model has no mechanism to notice this, and the requester experiences it as silence.

➡️ **Recommended:** make the pull **ordered** — engineers take the highest-priority ticket they are able to work on, and skipping one is visible rather than silent. Add a single safety rule: if a ticket is still unclaimed after an agreed age, or its "Needed by" date comes within reach, it is raised at the daily triage and the team decides deliberately — which is a decision, not an assignment, and so does not break the pull model.

</details>

---

### ✅ Q7 — Triage ownership and the definition of the clock

**Answer:**

- The window is **24 business hours**, explicitly not 24 hours flat.
- Triage is a **daily meeting at 10:00 CET**, owned by the team rather than by a rotating individual.

This resolves finding M1 and fixes the §5.1 wording, which currently promises an unqualified "24 hours". It also makes the commitment concrete for a requester: anything submitted before 10:00 CET is looked at that morning; anything after waits for the next meeting.

**Still open**, carried to Q7b: what the clock does when a ticket is returned for missing information.

<details><summary>Original question</summary>

Nobody owns triage, and "24 hours" is unqualified (findings C4, M1). This needs three answers: **who** triages, **what 24 hours means** (business hours, and which time zone), and **what happens to the clock** when a ticket is returned for missing information.

➡️ **Recommended:** a weekly rotating triage duty; 24 **business** hours in the team's working time zone; the clock **stops** when a ticket is returned and **restarts** when the requester responds, with the ticket closed after two unanswered returns.

</details>

---

### 🔁 Q7b — What happens to the clock when a ticket is returned? *(partly answered)*

**Answer: the clock stops.** When a ticket is returned for missing information it stops consuming the triage window, and resumes when the requester responds. QA is not held to a window while waiting on someone else.

This settles the §4 versus §5.1 contradiction in favour of **return**, not block: §4's wording that missing information "blocks the 24h triage window" is replaced.

**Still unanswered, deliberately not assumed:** whether an unanswered return is ever **closed**. Without a rule, an incomplete ticket can sit indefinitely with the clock stopped, invisible in SLA figures but still occupying the queue and the daily meeting's attention. The proposal on the table is closure after two unanswered attempts, with the requester free to resubmit. Parked rather than decided.

<details><summary>Original question</summary>

*The remaining half of Q7, and a contradiction inside the current draft.* §4 says missing information "blocks the 24h triage window"; §5.1 says the ticket is **returned** to the requester. Those describe different behaviour, and only one can be published.

Two sub-answers are needed. **Does the clock stop** while the ticket sits with the requester, or keep running? And **is there a limit** on unanswered returns, or do incomplete tickets stay in the queue indefinitely?

➡️ **Recommended:** the clock **stops** on return and **restarts** when the requester responds — QA cannot be held to a window while waiting on someone else — and an unanswered return is **closed after two attempts**, with the requester free to resubmit. Without the second rule the queue slowly fills with tickets nobody intends to complete, and the daily triage spends its time re-reading them.

</details>

---

### ✅ Q8 — Document ownership and review cadence

**Answer:**

- **Maintained by the QA Team**, collectively rather than by an individual editor.
- **Reviewed monthly**, as part of the existing **Team Retrospective Sessions** — no new meeting is created for it.
- **First point of contact: Marek Wyszyński.**

This resolves finding C7 and gives the pages the thing they most needed for external credibility: a name to go to and a date that proves the content is current. Attaching the review to the retrospective is better than a standalone cycle, because the retrospective is where the team already notices that practice and documentation have drifted apart.

**Two details left for the rewrite rather than asked as questions**, since neither is contentious: each page carries a **version and last-reviewed date**, and the review has a standing agenda item so it is not skipped when the retrospective is busy.

**This completes Round 1.**

<details><summary>Original question</summary>

No owner, version or review cycle (finding C7).

➡️ **Recommended:** a named owner for the page set, a version and last-reviewed date on every page, review monthly for the first quarter after publication and quarterly after that. Changes to scope or SLAs require the owner's approval; anything else can be edited in place.

</details>

---

### ✅ Q9 — The capacity model

**Answer:**

- **The split is 50/50** between portal work and test automation. This is the **company's expectation**, not an internal preference, and it is expected to **shift further toward automation** over time.
- **Intake is not yet measured.** It is believed to be modest, but no figure exists.
- **The WIP ceiling is never exceeded.** At the ceiling, each case is assessed individually at the daily triage meeting, and the team either **negotiates the deadline** or **parks other work**.
- **Requesters are asked to submit as early as possible**, ideally at the start of the quarter, so there is time to react, prepare test cases and do the automation.

**What this gives the service levels page:** four engineers at a 50% split is **2.0 FTE of portal capacity**. That is the real number behind every commitment, and it should be published rather than implied.

**Two consequences that need handling in the rewrite, not hidden:**

- The split **will change**. Publishing SLAs derived from a 50/50 split without saying the split is moving toward automation sets up a future broken promise. The service levels page should state the split it assumes and tie SLA review to the monthly retrospective.
- **Intake is unknown**, which means the SLA numbers are currently estimates. That is acceptable if stated. The honest form is to publish them as provisional, measure intake for a defined period, then confirm or revise — which the monthly review cycle already supports.

**Raised by this answer and asked next:** the SLA arithmetic does not work (see Q10), and "parking other work" needs rules (see Round 2 list).

---

### ✅ Q10 — Do the SLA numbers survive the capacity model, and are they elapsed time or effort?

**Answer: the recommended two-tier form.** The single blended "SLA" is replaced by two different kinds of commitment, because only one of them can actually be guaranteed.

| Tier | Commitment | Strength |
|------|-----------|----------|
| **Response** | Triage within **24 business hours**, at the daily 10:00 CET meeting | **Firm.** The team controls it and it does not depend on queue depth |
| **Completion** | A **typical range** per category, stated as elapsed business days | **Indicative.** Holds when the queue is below the ceiling |
| **At the ceiling** | The date is **negotiated at triage** — the deadline moves, or other work is parked | The published behaviour, not an exception |

**Why the original table could not stand.** It never said whether its numbers were elapsed time or effort. Read as elapsed time, which is how every requester reads them, they are unachievable at full WIP: 2.0 FTE spread across up to 8 in-progress tickets gives each ticket about a quarter of one engineer's time, so three days of hands-on work takes roughly twelve business days.

**What the service levels page must state alongside the numbers:** that completion ranges assume the queue is below the ceiling, that they derive from a **50/50 split which is expected to move toward automation**, and that **intake has not yet been measured** — so the figures are provisional and reviewed monthly at the retrospective.

This resolves C13. Completing the ranges for every category (C4) depends on first sorting which categories are requestable at all, which is Q11.

---

### ✅ Q11 — Which §2 categories are actually requestable?

**Answer: the proposed sorting, with one important correction — there are three kinds of work, not two.**

| Category | Kind | Raised by |
|----------|------|-----------|
| Feature testing | Requestable | Anyone |
| Test automation for a feature | Requestable | Anyone |
| Performance tests | Requestable | Anyone |
| New test cases after a feature | Requestable | Anyone |
| JCMA / migration testing | Requestable | Anyone |
| Azure DevOps testing | Requestable | Anyone |
| Shift-left requirement review | Requestable | Anyone |
| Testing documentation | Requestable | Anyone |
| **Training and courses** | Requestable | **Others, for the most part** |
| **Event Manager sanity and regression** | Requestable | **Per occasion** |
| **Regression after initiative delivery on `develop`** | **QA-raised portal ticket** | **QA.** The team knows when it is due and raises the ticket itself; much of the work is still manual |
| Release blocker testing | Release process | Triggered by Release Testing |
| RUM performance review | Release process | Triggered by the release |
| Full TR and Sanity cycles | Release process | Triggered by the release |
| BugCrowd | Standing intake | The BugCrowd platform |
| Kibana / DataStudio / dashboards | Out of scope | — |

**The correction that matters.** The portal is **not only an external intake**. QA raises tickets in it for planned work that nobody requests, initiative regression being the example. So §1's framing — "the single entry point for structured QA work" — is right, but the requester page must not imply that everything in the portal came from a requester, and the scope page must not imply that everything QA does is requestable.

This resolves C12 and unblocks the completion ranges (C4), which now only need to cover the ten requestable categories plus the QA-raised one.

**Raised by this answer:** whether release-process work is tracked in the portal too — see Q11b.

---

### ✅ Q11b — Is release-process work tracked in the portal, and does it consume the WIP limit?

**Answer: release work pre-empts everything else, and is represented by a single ticket.**

- **During a release, no other work is submitted and none is tackled.** This is long-standing practice and is not changing.
- **One Release ticket** is created in the portal to represent the release effort.
- **Everything else is created as corresponding Jira tickets, visible to everyone, linked to the original request.**

So the WIP question does not arise in the form it was asked: during a release the team is not holding eight portal tickets alongside release work, it is doing the release. The recommendation to track release work as several portal tickets counting against WIP was **not** adopted, and does not need to be — one ticket plus linked Jira issues already gives the visibility, without duplicating a structure that works.

**What this obliges the published pages to say**, because it is the strongest example yet of something the team treats as common knowledge:

- **Completion ranges exclude release periods.** A range that quietly assumes no release is running is a range that will be missed.
- **Requests submitted during a release wait.** Including urgent ones. The "Needed by" date does not override a release.
- **Requesters must be able to tell when a release is running.** "Everyone knows" is true inside the team and false for the wider company these pages are written for — see Q11c.

**Partly addresses M6** (quarter-end demand spike): release periods are handled by pre-emption, and the early-submission guidance from Q9 covers some of the rest.

---

### ✅ Q11c — How does someone outside QA know a release is running?

**Answer: two visibility mechanisms and a service commitment.**

| Mechanism | Status | Purpose |
|-----------|--------|---------|
| Slack **`#bp-status-release-feature`** | **Exists** | Release-related communication. Linked from the requester page as the place to check |
| **Jira filter showing all QA tickets** | **To be created** | Self-service view of the queue and of any individual ticket's state |
| **Daily meetings continue during a release** | Existing practice | Even when the only outcome is adding comments to tickets |

**"There will never be silence on our end."** This is the strongest commitment made in the whole session and it should be published as one, not buried in the process description. The failure mode C14 described — submit, hear nothing, conclude the portal is broken, go back to messaging an engineer — is closed by it: the daily meeting runs regardless, and a waiting ticket receives a comment saying so.

**Action, not a fact:** the Jira filter does not exist yet. It is a prerequisite for the requester page, which will link to it.

This resolves C14 for release visibility. The broader pattern it named — practices the team treats as common knowledge and therefore never wrote down — remains a checklist item for the rewrite rather than an open question.

---

### ✅ Q12 — Who prepares environments for portal work?

**Answer: the split is by beneficiary, not by activity.**

QA creates instances **for its own work** — the release process, and testing or verifying features. QA does **not run an instance-creation service** for external parties.

This dissolves the apparent contradiction between §3 and §8.3. Both are correct, and they were never describing the same thing:

| Reading | Correct statement |
|---------|-------------------|
| §3 "creating QA instances" is out of scope | **"We will not create an instance for you."** Self-service instructions in Confluence |
| §8.3 lists environment creation, preparation and tuning as QA work | **Internal enablement.** QA builds what QA needs in order to test |

**Consequence for capacity.** Environment work is not a requestable category, but it is real effort inside the 2.0 FTE. It is therefore **absorbed into the completion range** of whatever category it serves, not tracked or quoted separately. Performance testing that needs a tuned instance takes as long as the tuning plus the testing.

**Default carried into the rewrite, to be corrected if wrong:** §5 asks the requester for "names and numbers of environments to test". Read against this rule, that field applies when the request targets an **existing shared environment** such as AAN, develop or preprod. Where testing needs a purpose-built instance, QA provisions it and the field does not apply.

---

### ✅ Q13 — What is the priority scale, and who sets it?

**Answer: the standard Jira scale, defaulted to Medium, owned by QA at triage.**

| Aspect | Decision |
|--------|----------|
| Scale | **Standard Jira**: Highest / High / Medium / Low / Lowest |
| On submission | Everything is **reported as Medium automatically** |
| Who changes it | **QA, at the daily triage meeting** — assessed and re-assessed as the queue changes |
| Role of "Needed by…" | An **input to that assessment**, not a determinant |

The default-to-Medium design is the right one and worth stating as deliberate on the requester page. It removes the priority field as a lever, which is what prevents the arms race where every request arrives as High. A requester influences urgency through **"Needed by…"** and through the discussion at triage — not by setting a number.

Priority is also **re-assessed**, not set once. A ticket that sat at Medium while its date was distant can move up as the date approaches, without anyone needing to resubmit or escalate.

**Still open — see Q13b:** what actually moves a ticket off Medium.

---

### ✅ Q13b — What moves a ticket off the Medium default?

**Answer: the date drives ordering; two named conditions escalate; new information can demote.**

| Level | Trigger |
|-------|---------|
| **High / Highest** | Anything **release-related**; **Critical production issues** where QA assistance is needed |
| **Medium** (default) | Everything else, ordered by **"Needed by…"** — the main determinant |
| **Lowered** | QA learns from **Engineering or Product Management** that the feature is not shipping any time soon, or that **documentation is massively incomplete** |

**This sharpens Q13 rather than contradicting it.** "Needed by…" is the main determinant *of ordering within the default band*; the two escalation conditions sit above it, and they are narrow by design. Release work pre-empts everything regardless (Q11b), so the High/Highest band is in practice reserved for production incidents.

**The demotion path is the important half, and the pages should say so plainly.** A date on a form is a claim, not a fact. QA checks it against what Engineering and Product Management actually expect to ship, and lowers the priority when the claim does not hold up. That is what keeps "the date is the main determinant" from becoming "whoever types the earliest date wins" — and it belongs on the requester page as a stated behaviour, not a surprise: *an unrealistic date will be checked, and an early date on a feature that is not close to shipping will be lowered.*

**Incomplete documentation as a demotion trigger, not a rejection**, is worth stating too. It gives triage a third option between accepting and refusing, and it creates a visible incentive to submit complete requests — reinforcing §5's required-information list with a consequence.

**New scope consequence — see finding C15.** "Critical production issues in which our assistance might be needed" is reactive work that the Q3 scope principle does not currently cover. It needs adding as a third carve-out alongside release-critical testing and BugCrowd.

---

### ✅ Q14 — The production-issue boundary

**Answer: verification only, and only when the issue is absolutely Critical.**

> "We will not be handling production issues, unless it is absolutely Critical and our verification is needed — this is the only help we will provide in such cases."

This closes **C15** with a tighter boundary than the finding asked for, and it is worth publishing in close to these words. Two limits are doing the work:

- **Severity limit** — *absolutely Critical*, not "urgent", not "production".
- **Activity limit** — **verification only**. QA does not investigate, reproduce on request, triage, or own resolution.

The activity limit is the more valuable of the two, because severity labels drift upward under pressure while "we verify, we do not investigate" holds regardless of what the incident is called.

**Scope rule gains a third carve-out**, alongside release-critical testing and BugCrowd, stated as an exception with both limits attached.

---

### ✅ Q14b — What the requester gets at closure

**Answer: Done, a comment, and links to artifacts.**

| Step | Detail |
|------|--------|
| **QA closes** the ticket as **Done** | No requester acceptance step; QA closes when the request is complete |
| **A fitting comment** in the request | The result, written for the requester |
| **Links to any artifacts** created while working the ticket | Test cases, runs, recordings, reports — whatever the work produced |

**This resolves both §5.4 TBDs by dissolving them.** The "standardised QA delivery report" and the "single template for testing reports (screenshot / comment / recording)" are replaced by something lighter: a comment plus artifact links. That is the right call for a four-person team — a report template nobody has time to fill in becomes a template nobody fills in — and it keeps the evidence where the requester already is.

**Default carried into the rewrite, to be corrected if wrong:** a ticket is **Done when the testing is complete, whatever the outcome**. If QA finds bugs, those are raised as separate linked issues (consistent with Q4) and the portal ticket still closes. The alternative — holding the ticket open until someone else's fixes land — would fill the WIP ceiling with work QA does not control, which the Q10 model cannot absorb.

**Left for the rewrite, not a blocker:** whether a requester can reopen a closed ticket if the comment does not answer their question, and within what window. Logged as a minor point rather than an open question.

---

### ✅ Q15 — What happens when work arrives outside the portal?

**Answer: nothing. It is redirected, every time.**

> "No work arriving outside the portal will be tackled, the requestor will always be re-directed to the portal."

No carve-out for quick favours. The recommendation to allow a trivial-question exception was **declined**, and the rewrite should not reintroduce one — a rule with a size threshold requires every engineer to estimate the work before refusing it, which is the negotiation the rule exists to prevent.

**"Always" is what makes it survivable.** A rule with no exceptions is easier for an individual engineer to apply than one requiring judgement, because redirecting stops being a personal decision and becomes what the team does. The pages carry the refusal, not the person. This is the same mechanism Q8 established when it named a document owner — something to point at.

**Rewrite note — say what counts as "work".** Read literally, the rule can be mistaken for "do not talk to QA", which will not survive contact with normal collaboration and will discredit the rest of the page. The default carried forward: **answering a question is not work; doing testing is.** Anything that requires an environment, a test run, or produces a result someone will act on goes through the portal, however small it looks.

This also protects every number the pages publish. Out-of-band work consumes the same 2.0 FTE while being invisible to triage, which would make the completion ranges wrong and leave Anna arguing for capacity from a queue showing a fraction of real demand.

---

### ✅ Q16 — Is shift-left a document review or meeting attendance?

**Answer: asynchronous review, AI-assisted, with a human in the loop.**

| Step | Who |
|------|-----|
| Requirement is reviewed against the standard | **AI-assisted tooling** |
| Tool output is reviewed | **QA** — before anything goes back |
| Additional questions returned to the requester | **QA** |

**Meeting attendance is not the model.** That settles the conflict between §2/§6 and §7 in favour of the queued, asynchronous reading — which is the version that fits the pull model, consumes a WIP slot, and is already costed in the two-business-day service level. It also substantially defuses the §7 *meeting overload* risk, which the rewrite should downgrade rather than repeat unchanged.

**The human-in-the-loop step is the part to publish, not the AI.** "QA reviews the tool output before returning questions" is what makes the deliverable QA's work rather than a tool's, and pre-empts the obvious objection from a requester who receives a list of questions they think are naive. Stated the other way round — "AI reviews your requirements" — the same process reads as QA outsourcing the judgement.

**The deliverable is questions, not a verdict.** Requirement review returns *additional questions* to the requester. It is not a pass/fail gate, and the pages should not imply one.

**Two cross-references for the rewrite:**
- The tooling is the **`requirements-review` skill** already built in this repository under `AI in QA/Skills/requirements-review/`, along with `templates/requirement_standard.md`. The pages should link it rather than describe a hypothetical capability — and this partly answers finding **N7**.
- Once questions go back to the requester, the **clock stops** under the Q7b pause rule, exactly as for any other incomplete request.

---

### ✅ Q17 — What do DoR, DoD and acceptance criteria contain?

**Answer: they are epic-level delivery standards shared with Engineering — they are not QA portal rules.**

The suggestion to collapse DoR into §5's required-information list and DoD into the Q14b closure rule was **wrong, and is withdrawn.** These operate at a different level and belong to a different process.

**Definition of Ready** — when work by **Engineering and QA** can start on an epic:

- a clear description of the functionality
- **very clearly defined acceptance criteria**
- a statement of what is **out of scope of the implementation**
- relevant **Figma designs**

**Definition of Done** — Engineering and QA work is complete **and the issue has been officially signed off by Product Management**. The sign-off is **outside QA scope**: *"we provide the results of testing the implementation and that is it."*

**Two pairs of concepts that must not be conflated in the rewrite.** This is the real risk here, because both pairs use the same words:

| Epic level (shared standard) | Portal level (QA's own rule) |
|------------------------------|------------------------------|
| **DoR** — description, acceptance criteria, out-of-scope, Figma | **Request completeness** — §5 required information, checked at 24h triage |
| **DoD** — Eng + QA complete, **PM signs off** | **Closure** — QA closes as Done with a comment and artifact links (Q14b) |

They need distinct names on the pages. Reusing "Ready" and "Done" for both guarantees the confusion that made M3 a finding in the first place.

**Acceptance criteria are an input QA consumes, not an output QA writes.** They sit inside DoR, authored by whoever writes the epic. A ticket lacking them is not a QA problem to solve by writing them.

**DoD ends before sign-off, and that boundary is worth stating plainly.** QA supplies test results; it does not approve, accept, or gate the epic. This is the same distinction as Q14 (verify, do not own) and the RUM decision (review the data, do not set the thresholds) — a consistent pattern across the whole process and worth naming as such in the rewrite.

**Ownership question for the rewrite — see finding M17.** DoR and DoD span Engineering, QA and Product Management, so the QA pages should **reference** them, not define them.

**Link to Q16:** requirement review effectively checks an epic against DoR — description, acceptance criteria, scope boundaries, designs. The `requirements-review` skill and `templates/requirement_standard.md` should be aligned with this list so the two describe the same standard.

---

### ✅ Q18 — Completion ranges per category

**Answer: there are none. Effort is estimated by the engineer who picks the ticket up, and communicated only then.**

The banded proposal — small / medium / large with day ranges — is **declined**. No per-category completion times are published.

**This is defensible, and it is also a real trade.** Publishing invented ranges for nine categories with no intake data would have produced numbers the team missed and requesters quoted back. Estimating at pickup, by the person doing the work, is the honest version.

The cost is that **C4 is not so much resolved as answered by removing the promise**. The two-tier service model settled earlier — a firm response time plus indicative completion ranges — loses its second tier. What remains is the 24-hour triage response, and after that a queue with no published expectation.

That is workable, but only if the pages are explicit that this is deliberate: **QA commits to a response, not to a completion date, until an engineer has the ticket.** Left unstated, it reads as an omission and requesters will assume the old §6 numbers still apply to everything.

---

### ✅ Q18b — What does the requester learn at triage?

**Answer: a comment, in every case. One of three.**

| Triage outcome | What the requester is told |
|----------------|----------------------------|
| **Picked up** | The ticket is in progress |
| **Incomplete** | What additional information is needed |
| **On hold** | That it is parked **until a stated point**, **with the reason clearly given** |

This closes the gap Q18 opened. There is no state in which a triaged ticket sits silent, which makes good on the Q11c commitment and removes the incentive to chase a QA engineer directly — the behaviour Q15 now forbids.

**The hold comment is the most valuable of the three,** because it is the one a requester can act on. A reason and a date let them re-plan, escalate through their own manager, or reduce the scope of the ask. Silence offers none of those, and a bare "parked" offers only the first.

**This also supplies the parking rule** that was outstanding from the WIP-ceiling discussion: when the team cannot take work on, the ticket is put on hold explicitly, with a reason and a point in time — not left in the queue to age.

**Default carried into the rewrite, to be corrected if wrong:** §6's four figures — requirement review 2 days, automation 3–5, full regression 4–7, performance 3–5 — are **no longer commitments** under Q18. They are either dropped or kept under a heading such as *typical past durations, not commitments*. They cannot stay unlabelled beside "the engineer who picks it up estimates it".

<details>
<summary>Original question</summary>

### Q18b — What does the requester learn at triage?

Q18 leaves a gap between two points both already settled. Triage sees every ticket **within 24 hours** (§5.1). But the estimate does not exist until an engineer **pulls** the ticket, which under a WIP limit of 2 may be days later. Between those points the requester has a ticket that has been read, prioritised, ordered against a "Needed by" date — and told nothing.

That is the failure mode C14 described, arriving through a different door. Silence is what sends people back to messaging engineers directly, which Q15 has just ruled out. And Q11c committed to the opposite: *"there will never be silence on our end."*

The gap is cheap to close without inventing estimates. Triage already knows the queue, so it can say **when the ticket is likely to be picked up** — this week, after the release, not before date X — without saying how long the work will take. That is a schedule signal, not an estimate, and it is the thing a requester actually needs in order to plan.

**Second half: what happens to §6's four existing numbers?** Requirement review at 2 business days, automation at 3–5, full regression at 4–7, performance at 3–5. Under Q18 these are no longer commitments. Either they go, or they stay labelled as **typical past durations, not commitments**. Leaving them on the page unlabelled next to "we estimate at pickup" is the one option that cannot work — requesters will read the numbers and ignore the caveat.

**Recommendation:** commit to a **pickup signal at triage** rather than a completion estimate, delivered as a ticket comment; keep the four §6 figures only if they are relabelled as indicative history; and state plainly that the estimate arrives when an engineer takes the ticket.

</details>

---

### ✅ Q19 — What mitigates the loss of product depth under pure pull?

**Answer: reduce the depth the work requires, rather than try to hold more of it.**

> "With such a little team we cannot fully allow for specialization — we need to share the knowledge so that everyone will be able to tackle the testing requests. Also, that is why we use AI tools, document test cases, require a clear description of the features, so that the need for in-depth knowledge is minimized."

Generalist working is a **deliberate design choice**, not a side effect of the pull model, and the mitigation is not "learn more" — it is to lower the knowledge threshold the work sits behind:

| Mechanism | Already settled in |
|-----------|--------------------|
| Knowledge sharing across the team | Q10 (pull), Q8 (monthly retrospective review) |
| **AI tooling** | Q16 (AI-assisted requirement review) and the `AI in QA` work in this repository |
| **Documented test cases** | Q14b (artifacts linked on every ticket); the Xray test-case library |
| **A required clear feature description** | Q17 (DoR: description, acceptance criteria, scope boundaries, Figma) |

**This is the organising principle of the whole model, and the pages should say it once, explicitly.** Four engineers cannot cover the product in silos, so the process is built so that a well-documented request can be tested by whoever has capacity. Everything else follows from it — why requirements must be complete, why test cases get documented, why AI tooling is used, why any engineer can take any ticket.

**It also explains a rule that otherwise looks arbitrary.** Q13b lowers the priority of requests with massively incomplete documentation. Under this principle that is not bureaucracy: incomplete documentation is precisely what breaks a generalist team, because it is the one thing no amount of shared knowledge compensates for. The system is internally consistent — the input the model depends on is the input it protects.

**Residual risk, stated honestly rather than mitigated away:** the model holds while requirements are good. When they are not, the demotion rule is the release valve, and depth is genuinely traded for flow. That is the right trade at four engineers, and it is worth writing as a trade rather than a claim that nothing is lost.

---

## Round 2 — now live

**Round 1 is complete.** All eight foundation questions are settled, along with seven follow-ups that branched off them (Q3b–Q3e, Q4b, Q6b, Q7b). The frontier below is now open.

**Suggested order.** The capacity model comes first, because the SLA table, the shift-left modality and the quarter-end spike all depend on it and cannot be answered before it.

| Question | Waits on |
|----------|----------|
| ✅ *Capacity model* — **settled as Q9** | — |
| ✅ *SLA form* — **settled as Q10** | — |
| ✅ *Category sorting* — **settled as Q11** | — |
| ✅ *Release periods* — **settled as Q11b** | — |
| ✅ *Release visibility* — **settled as Q11c** | — |
| ✅ *Environments* — **settled as Q12** | — |
| ✅ *Priority scale and owner* — **settled as Q13** | — |
| ✅ *Priority triggers* — **settled as Q13b** | — |
| ✅ *Production-issue boundary and closure* — **settled as Q14 / Q14b** | — |
| ✅ *Out-of-band work* — **settled as Q15** | — |
| ✅ *Shift-left* — **settled as Q16** | — |
| ✅ *DoR / DoD / acceptance criteria* — **settled as Q17** | — |
| ✅ *Completion times* — **settled as Q18** | — |
| ✅ *Triage feedback* — **settled as Q18b** | — |
| ✅ *Product depth under pure pull* — **settled as Q19** | — |
| **Nothing substantive remains open.** What is left is writing: C8, M9, M17, N5, N6, N7 | — |
| Completion ranges for the ten requestable categories plus the QA-raised one (finding C4) | Q10, Q11 |
| Rules for **parking** work when the WIP ceiling is reached: what may be parked, who decides, when it resumes, and whether a parked ticket still counts against WIP (findings N6, M2) | Q9 |
| Which §2 entries are requestable work and which are release-process activities (finding C12) | Q1, Q3 |
| The **priority scale** itself, and how "Needed by" interacts with it (finding M2) | Q6 |
| Measuring intake, so the provisional SLAs can be confirmed or revised | Q9 |
| Who prepares environments for portal work, and does an unprepared environment make a request incomplete? | Q3 |
| Is shift-left an asynchronous document review or meeting attendance? | capacity |
| What DoR, DoD and acceptance criteria actually contain, and who authors them | Q3 |
| Closure: the deliverable, the report format, and who accepts it | Q1 |
| Enforcement when work arrives outside the portal, and who agrees to it | Q3, Q8 |
| Handling the end-of-quarter demand spike | capacity |
| Whether portal tickets link to Xray test cases and executions | Q1, Q3 |
| What is measured, and where SLA attainment is reported | Q8, and the SLA answer |
| Whether blocked items count against the WIP limit | Q6 |

---

## Round 3 and beyond

Expected to surface once Round 2 is settled: the request form fields per type, the escalation path and its approver, the redirect targets for each out-of-scope category, the glossary contents, and the migration plan from `WoW.md` to the live Confluence pages.
