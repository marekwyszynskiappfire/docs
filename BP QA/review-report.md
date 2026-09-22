# Review report — BP QA Way of Working

**Subject:** `BP QA/WoW.md` (269 lines, derived from the Process Vision whiteboard)
**Reviewers:** Tomasz Nowak (Software Engineer) and Anna Kowalska (Senior Manager, Engineering and QA) — see `personas.md`
**Date of review:** 2026-09-21
**Status of subject:** work in progress, not yet publishable to Confluence

---

## Summary

The document is a good inventory of what the team discussed, but it is currently a **record of a workshop rather than a set of ways of working**. It captures positions without resolving the conflicts between them, and it is written almost entirely from the QA team's point of view, which is the audience least in need of it.

Three themes run through the findings:

1. **Unresolved contradictions carried over from the whiteboard.** Two competing models (pull versus assign) and two competing bug policies sit in the document side by side, each stated as if settled.
2. **Commitments without machinery.** SLAs, a triage window and a WIP limit are promised, but there is no owner, no clock definition, no capacity model and no escalation path behind any of them.
3. **Wrong audience.** A requester cannot use this document to make a request. Everything they need — where the portal is, what the form asks, what they get back — is missing.

**Publishability:** not yet. Blockers are the Critical findings below — eight from the original review, plus two more (C9, C10) created by the scope decisions of 2026-09-21. The Major findings should be resolved before the pages are shared beyond the QA team; Minor findings can be fixed during the Confluence rewrite.

**Finding counts:** 15 Critical (14 resolved or answered, 1 withdrawn) · 17 Major (13 resolved, 4 open) · 9 Minor.

**The grilling session is complete: nineteen questions settled, and no substantive decision remains open.** Everything still listed is a writing task for the rewrite rather than a question for the team — C8 (the requester page must let someone actually submit), M9 (recast §9 as a rule, not a list), M17 (reference the shared DoR/DoD standard rather than defining it), N5 (mitigations in the risk table), N6 (whether a held ticket consumes a WIP slot) and N7 (cross-reference the Xray and `AI in QA` work). Findings added after the initial review are grouped in *Findings arising from settled decisions*; resolved findings are struck through and keep their resolution note rather than being deleted.

---

## Findings by severity

Each finding names the persona that surfaces it most sharply, though most are visible to both.

### Critical — blocks publication

#### ~~C1. Two contradictory assignment models are both stated as policy~~ — **resolved**
**Where:** §5.3 · **Lens:** Anna · **Resolved by:** Q6, 2026-09-21

The model is **pull**, with no assignment by Engineering, Product Management or the QA lead. Tickets are triaged daily and whoever has capacity picks one up. The assignment language in §5.3 is deleted rather than reconciled, and the §5.5 open question is answered: queue items have **no assignee until pulled**.

Two things follow and are tracked elsewhere: the operating rules of the pull (ordered or free choice, and the unclaimed-ticket case) as Q6b, and the area-ownership risk as M16.

#### ~~C2. "Creating bugs" is out of scope, but QA files bugs as core work~~ — **resolved**
**Where:** §3 against §8.1, §8.6 · **Lens:** Tomasz · **Resolved by:** Q4, 2026-09-21

The intended rule turned out to be about **on whose behalf**, not about whether QA files bugs: QA raises bugs it finds itself, and does not raise them on behalf of Engineering, Product Management or Support. The current §3 wording states neither half of that and must be replaced outright.

#### ~~C3. Release blockers are in scope but have no path that fits their urgency~~ — **resolved**
**Where:** §2 against §5.1 and §5.3 · **Lens:** both · **Resolved by:** Q4b, 2026-09-21

The premise does not hold. Release blockers are raised during QA's own Release Testing and never pass through portal intake, so neither the 24-hour triage window nor the queue can delay them. No expedite lane is needed for them. The residual question — whether *other* urgent portal requests need a faster path — is tracked separately as Q5.

#### C4. SLAs cover four of thirteen in-scope categories, with no clock definition — **answered by removing the promise**
**Where:** §6 against §2
**Lens:** Anna · **Answered by:** Q18, 2026-09-21

**No completion times are published at all.** Effort is estimated by the QA engineer who picks the ticket up, and communicated only then. The banded proposal was declined.

This is honest — inventing ranges for nine categories with no intake data would have produced numbers the team missed and requesters quoted back — but it resolves the finding by withdrawing the commitment rather than meeting it. The two-tier service model loses its second tier: what remains is a 24-hour triage response and then a queue with no published expectation. The pages must present that as a deliberate choice, since an unexplained absence reads as an oversight.

The clock-definition half of this finding was settled earlier: the clock stops when a ticket is returned for missing information (Q7b).

**The silence this would otherwise create is closed by Q18b**: triage always comments, saying either that the ticket is picked up, that information is missing, or that it is on hold until a stated point with the reason given. So the requester never has to infer state from silence, even though no completion date is promised. §6's four surviving figures are, by default, dropped or relabelled as typical past durations rather than commitments.

<details>
<summary>Original finding</summary>

§2 lists thirteen categories of in-scope work. §6 commits to SLAs for four: requirement review, automation, full regression and performance. Feature testing, Event Manager, JCMA, documentation, training, observability and BugCrowd have none. Separately, nothing defines **when the clock starts** (submission, triage completion, or information-complete), whether days are business or calendar, or what happens to the clock when a ticket is returned for missing information. §4 says missing information "blocks the 24h triage window"; §5.1 says the ticket is returned. These are different behaviours.

</details>

#### ~~C5. No capacity model stands behind the commitments~~ — **resolved, and it exposed C13**
**Where:** §6, §5.3 · **Lens:** Anna · **Resolved by:** Q6b and Q9, 2026-09-21

The model now exists: **4 QA Engineers**, **WIP 2 each**, a ceiling of **8 tickets that is never exceeded**, and a **50/50 split** between portal work and test automation — giving **2.0 FTE of portal capacity**. At the ceiling, the team assesses case by case at daily triage and either negotiates the deadline or parks other work. Requesters are asked to submit early.

Two qualifications belong on the published page rather than in a footnote: the split is a **company expectation that is expected to move toward automation**, so any SLA derived from it is dated; and **intake has not been measured**, so the SLA figures are estimates until it has been.

Applying this model to the existing SLA table is what produces C13.

#### ~~C13. The published SLA numbers do not survive the capacity model~~ — **resolved**
**Severity:** Critical · **Lens:** Anna
**Arising from:** Q9

With the numbers now known, the §6 SLA table can be checked for the first time, and it does not hold up.

Four engineers at a 50% split is **2.0 FTE** of portal capacity. The WIP ceiling allows **8 tickets in progress at once**. An engineer holding two tickets while spending half their week on automation gives each ticket roughly **a quarter of one person's time**. Work needing three days of hands-on effort therefore takes around **twelve business days** to clear — against a published SLA of **3–5 business days** for automation tasks and **4–7** for full regression.

Underneath the arithmetic is an ambiguity that has to be resolved first: **the SLA table never says whether its numbers are elapsed time or effort**. Read as effort they may be accurate but they are useless to a requester, who cannot convert effort into a date. Read as elapsed time — which is how every requester will read them — they are not achievable at full WIP.

**Resolved by Q10**, 2026-09-21: the single blended SLA is replaced by a **two-tier** commitment — a firm **response** time (triage within 24 business hours) and **typical completion ranges** that are indicative rather than guaranteed, valid while the queue is below the ceiling, with the date negotiated at triage once it is not. The page states its assumptions: the 50/50 split it derives from, that the split is moving toward automation, and that intake is unmeasured so the figures are provisional.

#### N9. "Assigned" is used for held work under a pull model
**Severity:** Minor · **Lens:** Tomasz
**Arising from:** Q6b

A WIP limit described as "no more than two tickets *assigned*" sits directly against a model where nothing is assigned. The published pages need **claimed** or **in progress** for work an engineer has pulled, reserving "assign" for the thing the team has decided does not happen. A close relative of N4.

#### ~~C6. Environment creation is out of scope, yet it is a prerequisite for in-scope work~~ — **resolved**
**Where:** §3 ("Creating QA instances — instructions should live in Confluence") against §4.1 ("Entry set-up if needed before tests") and §8.3
**Lens:** Tomasz · **Resolved by:** Q12, 2026-09-21

The two sections were never in conflict; they were describing different things, and the document simply never said so. The split is by **beneficiary, not activity**: QA creates instances **for its own work** — the release process, testing and verifying features — and does **not offer instance creation as a service** to external parties. So §3 means "we will not build one for you" and points at self-service instructions, while §8.3 describes internal enablement.

Environment effort is real cost inside the 2.0 FTE, but it is **absorbed into the completion range** of the category it serves rather than quoted separately. §5's "environments to test" field applies where a request targets an **existing shared environment**; where a purpose-built instance is needed, QA provisions it.

<details>
<summary>Original finding</summary>

Creating QA instances is pushed to self-service, but §8.3 lists environment creation and preparation as substantial current QA work, and several in-scope categories (performance, JCMA, Event Manager) cannot start without a prepared environment. The document never says who prepares the environment for a portal ticket, or whether an unprepared environment makes a request incomplete.

</details>

#### ~~C7. The document has no owner, version or review cadence~~ — **resolved**
**Where:** document-wide · **Lens:** Anna · **Resolved by:** Q8, 2026-09-21

The pages are maintained by the **QA Team**, reviewed **monthly at Team Retrospective Sessions**, with **Marek Wyszyński** as first point of contact. That supplies what the pages needed to be citable when declining work: a name and a review date. Each page carries a version and last-reviewed date in the rewrite.

#### C8. A requester cannot actually make a request from this document
**Where:** document-wide
**Lens:** Tomasz

There is no link to the portal, no description of the request form, no worked example of a good request, no statement of what the requester receives at the end, and no way to check status or escalate. §4 lists required information but never says where it is entered.

---

### Major — resolve before sharing outside the QA team

#### ~~M1. No owner for triage, and no definition of the 24-hour window~~ — **resolved**
**Where:** §5.1 · **Resolved by:** Q7, 2026-09-21

Triage is a **daily team meeting at 10:00 CET**, and the window is **24 business hours**. That gives the commitment an owner, a cadence and a concrete meaning for a requester: submit before 10:00 CET and it is looked at that morning. The unqualified "within 24 hours" in §5.1 is replaced.

#### ~~M2. Prioritisation has no owner and no scale~~ — **resolved**
**Where:** §5.3 · **Resolved by:** Q6b, Q13 and Q13b, 2026-09-21

Priority is assessed and re-assessed by the team at **daily triage**, on the **standard Jira scale**, with everything arriving as **Medium** by default. Within that default band, **"Needed by…" is the main determinant** of ordering. **High and Highest** are reserved for release-related work and Critical production issues where QA assistance is needed. Priority is **lowered** when Engineering or Product Management indicate the feature is not shipping soon, or documentation is massively incomplete.

That last rule answers Anna's original question — who wins when two requesters both claim urgency — better than a rubric would. The date is treated as a claim QA verifies against what Engineering and PM actually expect to ship, so the queue cannot be gamed by typing an early date. The pages should publish the demotion behaviour explicitly rather than leaving requesters to discover it.

<details>
<summary>Earlier state of this finding</summary>

**Partly resolved by:** Q6b and Q13, 2026-09-21

The **owner** is settled: priority is assessed and re-assessed at the **daily triage meeting**, and tickets are pulled in priority order. The **scale** is settled too: the standard Jira levels, with every request arriving as **Medium** by default and the **"Needed by…"** field feeding into QA's assessment rather than dictating it. Defaulting to Medium is what keeps the priority field from becoming a requester lever.

What remains is the **trigger** — what actually moves a ticket above Medium. Without it, Anna's question (who wins when two requesters both claim urgency) has a forum and a vocabulary but still no rule, and the Q6b commitment to argue the case for an unclaimed deadline ticket has no shared standard behind it. Tracked as Q13b.

</details>

#### ~~M3. Definition of Ready and Definition of Done are named but never defined~~ — **resolved**
**Where:** §5.2 · **Resolved by:** Q17, 2026-09-21

Both are **epic-level standards shared with Engineering**, not QA portal rules — which is why §5.2 sat awkwardly among sections describing the portal. **DoR**: a clear description of the functionality, very clearly defined acceptance criteria, a statement of what is out of scope of the implementation, and relevant Figma designs. **DoD**: Engineering and QA work complete *and* official sign-off by Product Management — with the sign-off explicitly outside QA scope. QA supplies the test results and nothing beyond them.

Acceptance criteria are therefore an **input QA consumes**, authored in the epic, not something QA writes when they are missing.

The rewrite's main job here is to stop two pairs of concepts colliding: epic **DoR** versus portal **request completeness** (§5 required information, checked at triage), and epic **DoD** versus portal **closure** (Q14b). They need different names on the page, since reusing "Ready" and "Done" is what produced this finding.

#### ~~M4. Shift-left is both a ticket type and an embedded practice, and the conflict is unresolved~~ — **resolved**
**Where:** §2 and §6 (requirement review, 2 business days) against §7 (meeting overload risk) · **Resolved by:** Q16, 2026-09-21

Shift-left is an **asynchronous review**, produced with **AI-assisted tooling** and **reviewed by QA** before additional questions go back to the requester. Meeting attendance is not the model, so the §2/§6 reading wins: the work stays queued, consumes a WIP slot, and is already costed at two business days. The §7 *meeting overload* risk should be downgraded in the rewrite rather than repeated.

Two things the pages should be careful about. The **human-in-the-loop step is the headline**, not the tooling — "QA reviews the output before returning questions" keeps the deliverable QA's judgement, where "AI reviews your requirements" invites a requester to dismiss it. And the deliverable is **questions, not a verdict**; requirement review is not a pass/fail gate.

The tooling is not hypothetical — it is the `requirements-review` skill in this repository under `AI in QA/Skills/`, which the pages should link. That also partly answers N7.

#### ~~M5. No enforcement mechanism for work arriving outside the portal~~ — **resolved**
**Where:** §7 lists side-channel requests as a risk, with no mitigation · **Resolved by:** Q15, 2026-09-21

**No work arriving outside the portal is tackled; the requester is always redirected.** The suggested carve-out for trivial asks was declined, and rightly — a size threshold would force each engineer to estimate the work before refusing it, which is precisely the negotiation the rule prevents. An absolute rule also moves the refusal from the individual to the team, which is what makes it applyable by someone sitting next to the person asking.

The rewrite must define what counts as "work", so the rule is not read as a ban on talking to QA: answering a question is not work; anything needing an environment, a test run, or producing a result someone will act on is.

#### M6. Batched, end-of-quarter feature testing conflicts with the service levels — **largely addressed**
**Where:** §2 · **Addressed by:** Q9 and Q11b, 2026-09-21

Three answers now cover most of this. Completion times are **indicative rather than guaranteed** and assume the queue is below the ceiling (Q10); requesters are asked to **submit early, ideally at the start of the quarter** (Q9); and during a release **nothing else is tackled at all** (Q11b), which is the sharpest form of the seasonality. What remains is simply to say all of this on the service levels page instead of leaving requesters to discover it.

#### C14. The pages depend on knowledge only the QA team has — **release visibility resolved, pattern still open**
**Severity:** Critical · **Lens:** Tomasz
**Arising from:** Q11b

"Everyone knows no other work should be submitted" is accurate inside a team of four and untrue for the company-wide audience these pages are written for. A requester who cannot tell that a release is in progress will submit anyway, hear nothing, and conclude the portal does not work — the precise experience that drives people back to messaging a QA engineer directly.

**Resolved for release visibility by Q11c**, 2026-09-21: Slack **`#bp-status-release-feature`** carries release communication and is linked from the requester page, a **Jira filter showing all QA tickets** gives a self-service view of any ticket's state, and the **daily meeting runs even during a release** so that waiting tickets receive comments. The commitment behind it — *"there will never be silence on our end"* — should be published as a service promise in its own right, since it closes the failure mode this finding described.

**The pattern remains open as a rewrite checklist item.** The release freeze was the clearest example of practice the team treats as common knowledge and never wrote down; the same test needs applying to every "as everyone knows" in the source material before publication.

#### ~~C15. Production-incident support is in scope but appears in no scope list~~ — **resolved**
**Severity:** Critical · **Lens:** Anna
**Arising from:** Q13b · **Resolved by:** Q14, 2026-09-21

QA does **not handle production issues**, with a single exception: **absolutely Critical** issues where **QA verification is needed**, and verification is the only help provided. Two limits bound it — severity and activity — and the activity limit is the one that will hold, since severity labels drift upward under pressure while "we verify, we do not investigate" does not. This becomes the third carve-out in the scope rule, alongside release-critical testing and BugCrowd.

<details>
<summary>Original finding</summary>

Q13b puts **Critical production issues where QA assistance is needed** in the High/Highest priority band — which means the team has committed to doing this work, at the top of the queue, ahead of everything except a release. But the scope principle settled in Q3 covers testing the product and its assets, with carve-outs for release-critical testing and BugCrowd. Production-incident support is neither, and it is not listed in §2 or §3.

This is the most expensive kind of gap: unbounded reactive work that outranks the committed queue and is invisible in the capacity model. If it is not named, nobody can see why the completion ranges slipped in the month it happened. The team's own expectation is that such incidents are rare — which is exactly the argument for writing it down now, while it costs nothing, rather than during one.

The pages need it as a **third carve-out** in the scope rule, with the boundary stated: QA assists, QA does not own incident resolution, and the trigger is a Critical severity production issue rather than any production question.

</details>

#### ~~M7. Closure is undefined: no deliverable, no report format, no acceptance~~ — **resolved**
**Where:** §5.4, with two TBDs · **Resolved by:** Q14b, 2026-09-21

At completion QA **closes the ticket as Done**, adds a **fitting comment**, and **links any artifacts** created while working it. Both TBDs are dissolved rather than filled: there is no delivery-report template and no testing-report template, because a comment plus artifact links does the same job at a fraction of the cost for a four-person team.

**QA closes; there is no requester acceptance step.** The rewrite carries one default forward for correction — a ticket is Done when testing completes whatever the outcome, with bugs raised as separate linked issues, so that WIP is never held open waiting on another team's fixes.

#### M8. Section 9 mixes two different dispositions in one column
**Where:** §9 (Portal vs team work)
The right-hand column combines "goes to another team" (support tickets, DevOps) with "do it yourself" (QA instance creation) and "not a QA matter" (business questions). These need different handling and different redirects, and merging them hides the redirect target.

#### M9. Scope is a list, not a rule
**Where:** §2, §3, §9
Scope is expressed as three overlapping enumerations. Anything not enumerated has no answer, and the three lists must be kept consistent by hand — §9 already diverges from §2 on bug-related work. A single stated principle, with the lists as examples, would let requesters classify their own edge cases.

---

### Minor — fix during the Confluence rewrite

#### N1. Undefined acronyms and internal shorthand
`TR` (used for both "full test regression" and a release activity), `BP`, `BG`, `BT`, `AAN`, `JCMA`, `FF`, `DoR`, `DoD`, `RUM`, `UT`. A company-wide page needs a glossary; several of these will be opaque outside the immediate team.

#### N2. Mixed Polish and English
§8 carries Polish terms (*analiza wymagań*, *weryfikacja fixów*, *wrzutki*) and the risk table leaves *wrzutki* untranslated. A decision is needed on language before publication.

#### N3. Transient notes embedded as process content
"team member out from 16.09" (§8.7), "currently handled by Robson" (§8.1), and three "(soon)" markers (§8.1, §8.6) will be stale within a quarter and do not belong in a standing process document.

#### N4. Inconsistent vocabulary for the unit of work
"Ticket", "request" and "task" are used interchangeably throughout. Pick one term and define it.

#### N5. Section 7 is titled "Risks and mitigations" but contains no mitigations
The second column holds restatements and open questions, not mitigations. Either add owners and mitigations or retitle the section.

#### N6. Whether a blocked item counts against the WIP limit is unstated
**Where:** §5.3. In practice this decides whether the limit of two is a real constraint.

#### N7. No cross-reference to the Xray and AI-in-QA work in this repository
The repository contains substantial material on Xray test management and AI-assisted test creation. Whether portal tickets produce Xray test cases or executions is never addressed, and the two bodies of process will drift apart if the link is not made.

---

## Findings arising from settled decisions

Added 2026-09-21 after Q1–Q3 were answered. Decisions resolve findings, but they also create new ones; these are tracked here so the published pages do not inherit a fresh contradiction in place of an old one.

#### ~~C9. "Release blocker" is in scope while "simple bug testing" is out~~ — **resolved**
**Severity:** Critical · **Lens:** both
**Arising from:** Q3 · **Resolved by:** Q4 and Q4b, 2026-09-21

Fully settled. A release blocker is a defect of **severity ≥ Medium raised during Release Testing**, under severity rules that already exist and will be linked rather than restated, and **no bug at that severity is released**. The classification-gaming risk disappears with the context condition: requesters cannot reach this category at all, so there is nothing to inflate.

#### ~~C10. BugCrowd is in scope while "bug reporting" is out, with no stated distinction~~ — **resolved**
**Severity:** Critical · **Lens:** Tomasz
**Arising from:** Q3 · **Resolved by:** Q4, 2026-09-21

QA creates BugCrowd issues. The apparent contradiction dissolves once the real rule is stated: QA does not file bugs **on behalf of internal colleagues**, and externally-sourced security findings are a separate intake that QA raises itself. The scope page needs that sentence explicitly, since the distinction is invisible otherwise.

#### ~~C11. The out-of-scope line on bug testing is far broader than the actual rule~~ — **withdrawn, analysis was wrong**
**Severity:** Critical · **Lens:** Tomasz
**Arising from:** Q4 · **Withdrawn after:** Q4b, 2026-09-21

The finding assumed that "release blocker in scope" meant requesters could submit Medium-and-above bugs, leaving only Low severity excluded. Q4b shows that is not the case: a blocker is a bug raised **during QA's own Release Testing**, so none of this work is requester-submitted. **Requester-submitted bug testing stays out of scope at every severity**, and the §3 line is accurate as a boundary — it needs rewording for clarity, not correction for substance.

Replaced by C12, which is the real issue underneath it.

#### M17. The QA pages should reference DoR and DoD, not define them
**Severity:** Major · **Lens:** Anna
**Arising from:** Q17

DoR and DoD span Engineering, QA and Product Management — PM sign-off is part of DoD and explicitly outside QA scope. A definition published on a QA page is therefore a definition QA cannot maintain or enforce, and the first disagreement about it will be settled somewhere else.

The pages should state QA's part (we supply test results; we do not sign off) and **link** the shared standard wherever it lives. If it does not yet live anywhere, that is a gap to raise with Engineering and Product Management rather than one for QA to close unilaterally — and the rewrite should say the standard is shared rather than implying QA owns it.

A related alignment task: the `requirements-review` skill and `templates/requirement_standard.md` in this repository should check an epic against exactly the DoR list from Q17, so the tooling and the page describe the same standard.

#### ~~M16. Choosing pure pull turns the area-ownership risk into an accepted risk with no mitigation~~ — **resolved**
**Severity:** Major · **Lens:** Anna
**Arising from:** Q6 · **Resolved by:** Q19, 2026-09-21

The team is **generalist by design**, and the mitigation is not to hold more knowledge but to need less of it: knowledge sharing, AI tooling, documented test cases, and a required clear description of the feature, so that a well-documented request can be tested by whoever has capacity.

This turns out to be the organising principle behind most of the model, and the pages should state it once and derive the rest from it. It also explains why Q13b lowers the priority of poorly documented requests — incomplete documentation is the single input that shared knowledge cannot compensate for, so the model protects the thing it depends on.

The residual risk should be written as a trade rather than argued away: the approach holds while requirements are good, and depth is genuinely being exchanged for flow. At four engineers that is the right exchange, but it is one.

<details>
<summary>Original finding</summary>

§7 lists "does everyone test everything, or do we own specific areas?" as an open question, and lists uneven product knowledge and "lower product familiarity, weaker tests" as risks. Pure pull answers the open question by implication: the team is **generalist by policy**, because any engineer with capacity may take any ticket. That is a legitimate choice, but it converts three entries in the risk table from "to be decided" into "accepted", and accepted risks need a mitigation — pairing, a knowledge base, rotation, or an explicit statement that depth is being traded for flow.

</details>

#### ~~C12. Release-process activities are listed as portal intake categories~~ — **resolved**
**Severity:** Critical · **Lens:** Tomasz
**Arising from:** Q3c and Q4b · **Resolved by:** Q11, 2026-09-21

Sorted into three kinds. Ten categories are requestable by anyone; **initiative regression is a portal ticket QA raises itself**; release blocker testing, the RUM review, TR and Sanity are release-process work; BugCrowd is standing intake from the platform; observability is out of scope.

The answer also corrected the model behind the finding. The portal is **not purely an external intake** — QA raises tickets in it for planned work nobody requests. So the requester page must not imply every portal ticket came from a requester, and the scope page must not imply everything QA does can be requested.

Two activities settled so far — the **RUM performance review** and **release blocker testing** — are triggered by the release, not by a requester, and cannot be submitted through the portal. Both are currently presented in §2 as in-scope portal categories, alongside things a requester genuinely can ask for. A requester reading that list will try to raise a ticket for work that has no intake path.

The category list conflates **what QA does** with **what you can ask QA for**. Those are different lists with different audiences, and the five-page structure agreed in Q1 already separates them: requestable work belongs on *Requesting QA work*, release-triggered work on *How the QA team works*. Every remaining §2 entry needs sorting into one or the other during the rewrite.

#### ~~M10. The observability exit has no successor and no handover date~~ — **resolved**
**Severity:** Major · **Lens:** Anna
**Arising from:** Q3 · **Resolved by:** Q3b, 2026-09-21

Original concern: dropping a tool is a decision, dropping the assets built with it is a transition, and without a named successor the work returns as side-channel requests.

Resolution: all assets are inherited by engineering, and the underlying premise turned out to be weaker than assumed — apart from RUM, these dashboards no longer have an audience acting on their results. The published page should carry that rationale, since "nobody consumes them" is what makes the exit defensible to a peer manager, and "engineering owns them now" is what makes it actionable.

#### ~~M12. The pre-release RUM review is in scope but appears in no category list~~ — **resolved**
**Severity:** Major · **Lens:** Anna
**Arising from:** Q3b · **Resolved by:** Q3c, 2026-09-21

The review is a step in the **release process**, not a portal request type, so it belongs on the "How the QA team works" page under release activities and is deliberately absent from the portal category list and the SLA table. The pass/fail criterion is ownership-resolved too: thresholds are set by Product Management and Engineering, and QA assesses against them. What remains of this finding is carried by M14.

#### M13. QA gates a release on an asset and criteria another team owns — **accepted, must be documented**
**Severity:** Major · **Lens:** Anna
**Arising from:** Q3b · **Decided in:** Q3c

Engineering owns the RUM Events portal and QA only reads it; PM and Engineering own the thresholds. This is a deliberate choice rather than an oversight, and it is defensible — QA stays out of tooling ownership. The residual risk is unchanged, though: if the dashboard breaks, changes shape, or loses an event, the gate fails silently and QA finds out at release time. The recommended carve-out was declined, so the release page must instead **state the dependency and name the engineering contact** QA raises it with. Without that, the fallback is an ad-hoc scramble during a release.

#### M14. The RUM gate has no stated consequence, no decision-maker, and no behaviour when a threshold is missing — **mostly resolved**
**Severity:** Major · **Lens:** both
**Arising from:** Q3c · **Largely resolved by:** Q3d, 2026-09-21

Two of the three gaps are closed. QA's **output** is a ticket to Engineering naming the affected module and events, and the gate **blocks**: the release waits for the fix and a QA re-review. The **decision right** follows from that — QA's assessment holds the release, Engineering owns the remedy — so no separate go/no-go role is needed on the pass and fail paths.

**Fully resolved by Q3e**, 2026-09-21: a module with no threshold is recorded as **not assessable** rather than as a pass, and appears on the release page. This already matched practice; only the documentation was missing.

#### ~~M15. The blocking RUM gate has no waiver path~~ — **resolved**
**Severity:** Major · **Lens:** Anna
**Arising from:** Q3d · **Resolved by:** Q3e, 2026-09-21

A known regression may be released under a **recorded waiver**, with the escalation ticket left open. As with the missing-threshold case, the waiver already existed in practice and was simply absent from the document. Both need writing into the release page so the exception stays visible rather than becoming a corridor decision.

**The RUM branch is closed.** Findings M10 and M12–M15 are all resolved; M13 remains open only as a documentation task — naming the engineering contact for when the RUM portal itself is wrong.

#### M11. Request fields and inventory sections are now stale in a way that contradicts the new scope
**Severity:** Major · **Lens:** Tomasz
**Arising from:** Q3

Three places still assume observability is QA work: §2 lists it as an in-scope category, §4.1 asks requesters "what we want to measure — dashboards?" as required request information, and §8.4 documents it as current activity. If any of these reach Confluence unchanged, the scope page and the request form will contradict each other on the first page a requester reads.

#### N8. The scope principle must be stated as subject, not timing
**Severity:** Minor · **Lens:** Anna
**Arising from:** Q3

Worth recording because it is easy to regress to: the intuitive "planned work in, reactive work out" framing was tested against the answers and fails, since release blockers and BugCrowd are both reactive and both in scope. The principle is about *what the work is about*, not *when it arrives*. Anyone editing the scope page later needs that stated, or the simpler-sounding version will creep back in.

---

## What is working well

Worth preserving through the rewrite:

- **§4 (required information)** is the strongest part of the document: concrete, per-request-type, and directly usable as the basis for a portal form.
- **§8 (activity inventory)** is valuable raw material. It belongs in an internal appendix rather than the shared page, but it is the evidence base for the capacity conversation Anna needs.
- **The out-of-scope response template** (§3) is exactly the kind of reusable artefact that makes a boundary hold in practice.
- **Naming the risks at all** (§7) is more honest than most process documents manage.

---

## Recommended page structure for Confluence

Derived from the audience split in `personas.md`. Proposed for confirmation, not yet decided — see Q1 in `open-questions.md`.

| Page | Audience | Contains |
|------|----------|----------|
| 1. Requesting QA work | Requesters (Tomasz) | What the portal is for, decision table for in/out of scope, request templates per type, what happens next, response times, escalation |
| 2. QA Portal scope | Requesters and managers | The scope principle, in/out examples, redirect targets, the out-of-scope response template |
| 3. How the QA team works | QA team and managers (Anna) | Triage, prioritisation, assignment model, WIP, capacity, expedite lane, closure and reporting |
| 4. Service levels and measures | Managers (Anna) | SLA table with clock definitions, what is measured, where it is reported, review cadence, document ownership |
| 5. Appendix: QA activity inventory | QA team | §8 content, kept internal as the capacity evidence base |

---

## Next step

The findings above are observations, not decisions. Resolving them is the purpose of the grilling session tracked in `open-questions.md`, which works through the decision tree in rounds. Answers are recorded there and in `MEMORY.md` as they are settled.
