# The Reviewer — user manual

*Draft for Confluence publishing. Written for the QA engineer running the skill day to day, with a section aimed at PMs reading a report for the first time. Source of truth for the underlying rules is `SKILL.md` / `reference.md` / `checklist.md` in the same folder — this manual explains and illustrates, it doesn't redefine.*

---

## 1. What The Reviewer is

The Reviewer is an AI-assisted requirement quality check that runs **before** test cases get written. Point it at a Jira Story, Bug, Task, or Epic, and it comes back with:

- A list of concrete **findings** — gaps, ambiguities, and contradictions in the requirement, each graded CRITICAL / HIGH / MEDIUM / LOW.
- A short list of **clarification questions** you can hand to the PM, grouped by topic, ready to paste into a Jira comment.
- A plain-language **readiness label** — "Ready to build tests," "Needs clarification before test design," or "Needs clarification before scope can be tested."
- A **gate** that decides, mechanically, whether it's safe to move on to test-case generation.
- A shareable, self-contained **HTML report** — one file, opens by double-click, no login and no repo access required.

It is **read-only on Jira and Confluence**. It never edits a requirement, never writes a test case, and never touches Xray. The one write capability it has — posting a comment back to Jira — is off by default and always available as a copy-paste block either way (§9).

**It does not approve or reject anything.** It supports getting a requirement ready for testing; the decision to proceed is always a human's.

---

## 2. Quick start

| You want to… | You say | You get |
|---|---|---|
| Review a Story/Bug/Task | `Review DEMO-4522` or `scan DEMO-4522` | Full review: findings, questions, readiness |
| Review an Epic | `scan DEMO-9000` | Epic review + full child inventory + batch handoff |
| Get an HTML file to share | `export html` (after a scan) | Self-contained `.html`, opens anywhere |
| Get a Jira comment to paste | `format for Jira short` or `format for Jira full` | Wiki-markup block, copy-paste only by default |
| Re-check after the PM updates the story | `rescan DEMO-4522` | Delta: what's resolved, what's still open |
| Get a QA sign-off checklist | `export readiness checklist` | CSV-ready checklist, ≤ 50 rows |
| Override a block (rare, deliberate) | `force=true` + explain why in chat | Proceeds with every CRITICAL finding still listed |

**Works the same way on Cursor, Claude, and Hive.** On Hive, trigger it the same way you'd trigger any skill (`scan {KEY}` in the prompt); it always returns the full report in the same turn, never just "skill loaded."

---

## 3. Reading a report

Open [`sample-report.html`](sample-report.html) alongside this section — it's a worked example (fictional issue `DEMO-4522`) showing every part of the report populated. For what an Epic scan looks like instead, see [`sample-report-epic.html`](sample-report-epic.html) (§7).

The report is organized in three tiers, so you can stop reading as soon as you have what you need:

**Always visible (Tier 1) — the "can I proceed" summary:**
- Header: issue key, type, when it was scanned, a link back to Jira.
- One line of counts: how many findings, how many open questions.
- The **readiness strip** — the single most important line in the report. Full-width, colour-coded, states what's blocking in one sentence.
- Four KPI cards: Testability, Test scope confidence, Risk, Automation candidate.

**Expanded by default (Tier 2) — the "why":**
- The findings table.
- Clarification questions, grouped by topic (Behavior, Scope, Edge cases, Integrations, Permissions, Data, and for Epic-level concerns Definition of done, PRD authority, Design authority, Rollout), numbered Q1, Q2, Q3… in the order you read them.
- Known risks and suggested testing focus.

**Collapsed by default (Tier 3) — reference and audit detail, click to expand:**
- **Data sources** — every source The Reviewer tried to read and its status (Analyzed / Unavailable / Could not read / Not applicable, with a reason). Always present, even when nothing failed — this is the section to check first if a report looks thinner than expected.
- The raw facts the review was based on ("Information identified"), each with a source.
- Design observations pulled from Figma, if a design link was found.
- "Not stated in story" — the gaps, named plainly, with no guessed answer.
- Epic context (for a Story) or the full child inventory and status mix (for an Epic).
- The QA readiness checklist, if one was generated.

**Always visible at the bottom, outside the tiers:** a handoff block pointing at **The Creator** — the separate skill that actually drafts test cases. The Reviewer's report never contains test case tables itself.

The report has a light decision layer: you can mark a finding or question **Accept / Reject / Needs discussion** with an optional comment, and export those decisions as a small JSON file. This doesn't change the requirement or the findings — it's a sign-off record, and the requirement's real home stays Jira.

---

## 4. The gate vs. the readiness label — and why there are two

There are genuinely **two** things in every report, and they answer different questions:

| | Answers | Audience | Example values |
|---|---|---|---|
| **Gate** (technical) | "Is it safe to auto-run The Creator next?" | The tooling itself | `PASS`, `PASS_WITH_WARNINGS`, `BLOCKED` |
| **Readiness label** (human) | "What should I, a person, do next?" | Everyone reading the report | "Ready to build tests," "Needs clarification before test design," "Needs clarification before scope can be tested" |

They're computed from **different inputs** and can legitimately disagree. The gate counts findings by severity: any CRITICAL stops The Creator; any HIGH or MEDIUM gives `PASS_WITH_WARNINGS`; LOW findings alone (or none) give `PASS`. Readiness looks at how testable the requirement is and which questions are still open. So a requirement can have no CRITICAL findings, which lets The Creator run, and still read "Needs clarification before scope can be tested," which means any test cases drafted now will be thin or provisional. That's not a contradiction; it's two useful facts.

In the report, the coloured readiness strip always reflects readiness. The gate gets one plain sentence of its own right under the strip, for example "Test case drafting can start; the findings below should travel with it." Neither uses any of the phrases on the skill's blocked list: "gate," "blocker," "not ready," "story failed," and similar. The one exception is a direct quote: if the Epic itself says "undo is blocked with an error," the report quotes it as written rather than paraphrasing. A requirement review is a collaborative document, and the words that land as a verdict get treated as one whether that's intended or not.

**Epics never block.** On an Epic scan, nothing is rated CRITICAL. Problems that would be critical on a Story are rated HIGH instead, because The Creator never runs on an Epic directly. The real block, if any, happens when each child Story is scanned.

**A CRITICAL finding hard-blocks The Creator** unless a QA engineer explicitly overrides it in chat with `force=true` — and even then, the override is logged (who, when) and every CRITICAL finding is still listed. This is a deliberate, audited exception, not a bypass.

---

## 5. Findings — what the severities mean

| Severity | Roughly means | Blocks The Creator? |
|---|---|---|
| **CRITICAL** | No usable acceptance criteria, an unresolved must-answer question, a scope contradiction, or a live secret/credential in the text. Never used on an Epic (rated HIGH there instead) | Yes, unless overridden |
| **HIGH** | An acceptance criterion is vague or incomplete, or a behavioural gap (e.g. error handling undefined) blocks defining a clear test | No — but shown prominently |
| **MEDIUM** | A structural or template gap; a behavioural gap on edge/regression scope | No — but the gate shows warnings |
| **LOW** | A nice-to-have; low-impact clarity issue | No — and doesn't trigger warnings |

Every finding cites which checklist row it came from (see `checklist.md`) — either a **structural** row (is there a testable AC, is scope stated, is there a design link…) or a **behavioural** row (does the requirement address negative paths, boundaries, roles, error handling, NFRs…). Epic scans also use three **delivery** rows: is there a rollout or feature-flag plan, is there evidence of what was verified, and do the tracking fields (status, fix versions) agree. Both kinds matter; a beautifully-written story can still fail every behavioural check if it never mentions what happens on error.

---

## 6. Clarification questions — and what to do with them

Every open question is grouped by topic, and carries:
- **Context** — why it's being asked.
- **Source** — where the gap was found.
- **Priority** — High / Medium / Optional (a different scale from finding severity — this is about how urgently *you* need an answer, not how bad the gap is).
- **Unblocks** — which finding(s) get resolved once it's answered.

By default there are at most **8** questions, **5** of them High; a genuinely complex story can go up to 15 with a stated reason. A rescan adds at most **5 new** ones.

**The intended flow:** scan → review the questions → `format for Jira short` or `full` → paste into a Jira comment yourself (this is always a manual copy-paste step; see §9 for the one opt-in exception) → PM answers / updates the story → `rescan {KEY}` → questions marked Resolved fall away, new ones (if any) appear → repeat until readiness is "Ready to build tests" → hand off to The Creator.

---

## 7. Reviewing an Epic

Point The Reviewer at an Epic key and it switches modes automatically. See [`sample-report-epic.html`](sample-report-epic.html) for a full worked example. Instead of a single-issue review, you get:

- The **full child inventory** — every child issue, paginated to completion. Never a sample, never truncated silently.
- **Each child's actual content, not just its title.** The same fetch that builds the inventory also reads every child's description — this is the recursion into the Epic's children that the earlier v1 shipped without. If a child has no description (or only boilerplate), The Reviewer falls back to that child's **name/summary** as a weaker enrichment signal for the epic-level narrative, and marks that child `title_only` so the fallback is visible rather than silently treated as real content — a title alone still can never, by itself, resolve the child ↔ epic alignment check.
- A **status mix** across all children (Done / Waiting for Release / Open / …).
- Epic-scope findings — is there a testable definition of done, are most children still empty while the epic is active, does the epic describe a journey no child actually owns.
- An **Epic batch handoff** block listing **every child that isn't Canceled**, in the order they'll be scanned: children the findings and questions point at first, then Waiting for Release and In Progress before To Do, then Done. `confirm batch` scans them all, 8 at a time; `--batch keys ...` scans just the ones you name. Canceled children are never included; if one matters (say, the only test story was canceled), it shows up as a finding or question instead.

**Epics that have already shipped.** If the Epic is Done or Waiting for Release / Deploy, the report is labelled a **Post-delivery review**, and the readiness heading reads "Readiness for regression and sign-off" instead of "Readiness for test planning." A fixed sentence at the top says the findings are gaps to close for regression coverage and sign-off, not reasons to hold back the build. Everything else, including severities and readiness values, works exactly as for an Epic still in progress.

Clarification questions in Epic mode are routed to **PO / UX / EM** rather than assumed to always be for the PM (acceptance-criteria and scope questions on an Epic default to the PO) — things like "which PRD section is authoritative" or "which Figma node is canonical" aren't usually a PM's call alone.

The batch itself never runs automatically — you have to say `confirm batch`, `yes`, or pass `--batch` explicitly.

---

## 8. Rescanning

`rescan {KEY}` re-fetches the live requirement and compares it against the **last saved review**, not against anything remembered in the current chat — so it works even in a brand-new chat session, or when a different person runs it than the one who ran the original scan.

- If the requirement changed since the last review, you'll be told (this is a staleness check, not a guess).
- Each finding is marked **Resolved** or stays **Open**.
- Readiness and the gate update accordingly.
- If you re-run the exact same scan/rescan request with nothing changed, you'll be asked whether you actually want to re-gather everything — it won't silently do the same work twice.

---

## 9. The Jira comment — copy-paste, and the one opt-in exception

**By default, always:** every run writes `jira-comment-full.txt` and `jira-comment-short.txt` next to the report, in Jira's wiki markup, with each question tagged with who should answer it (PM, PO, EM, UX, Security). `format for Jira short` or `format for Jira full` just shows you one of them. You paste it yourself. Nothing is posted automatically.

**Opt-in, per product:** if your product's config sets `policy.jira_comment` to `"auto-post"`, The Reviewer will post the comment directly instead of stopping at the copy-paste step. This is off by default everywhere. Either way, the same redaction rules apply — no unredacted secret or PII ever reaches Jira through this path.

---

## 10. Configuration

The Reviewer is product-agnostic. Everything product-specific — which Jira field holds acceptance criteria, whether Confluence fetch is on, whether the Jira comment auto-posts, which Xray project a suggestion should eventually point at — lives in a per-product config file, not in the skill itself. If your product doesn't have one yet, The Reviewer falls back to sensible defaults and will ask (once) for anything it can't resolve, such as the AC field, offering to remember the answer for next time.

You don't need to touch the config to run a review. It matters when you're onboarding a new product, or when the auto-post behaviour in §9 needs turning on.

### Connecting to more than one Atlassian site

Requirements sometimes link to Confluence or Jira on a **second** Atlassian host (at Appfire: `appfire.atlassian.net` vs `appfireteam.atlassian.net`). The Reviewer needs one MCP connection per host; otherwise those sources appear as *Unavailable* in **Data sources**.

**Full setup (manual steps, JSON template, troubleshooting, and a paste-in Cursor prompt):** [`config/DUAL-ATLASSIAN-MCP.md`](config/DUAL-ATLASSIAN-MCP.md).

Nothing in `config/<product>.json` is required for site routing — the skill discovers connected sites each run.

---

## 11. Who does what (personas)

| Role | What they get from The Reviewer |
|---|---|
| **QA engineer** (primary operator) | Runs the scan, triages findings, drives the clarification loop, decides when to hand off to The Creator |
| **QA lead / manager** | Skims Tier 1 of *one* report at a time (readiness, testability, risk) without opening the detail. There's no multi-story rollup in v1 — checking several requirements still means opening each one's report in turn |
| **PM / BA** | Receives the clarification questions and the readiness label; never needs to open a findings table or a checklist to know what's being asked of them |
| **UX designer** | Findings and questions carrying `owner_hint: UX` (design/Figma disagreements, copy/labelling) are tagged as theirs directly, in both the HTML and Markdown reports — instead of everything defaulting to the PM |
| **Release / delivery manager** | Uses Epic mode's child inventory, status mix, and batch handoff block for release-readiness triage — see [`sample-report-epic.html`](sample-report-epic.html) |
| **Security / compliance reviewer** | Owns anything flagged `data_sensitivity` — a CRITICAL finding, always |
| **Skill maintainer** | Owns `checklist.md` (append-only, versioned) and the decision record in `DECISIONS.md`; extends the checklist or the payload schema without renumbering a shipped `checklist_ref` |
| **Platform / MCP administrator** | Reads the "Data sources" section of any report — every source's status (Analyzed / Unavailable / Could not read / Not applicable) with a reason, always rendered even when nothing failed |

*Not covered above: **Automation engineer** and **Test-data / environment steward**. Both are real personas for the Jira review ecosystem, but their needs (`test_pattern`, stability, parallel test-data isolation) belong to **The Creator**, not The Reviewer — this skill hands them a `automation_candidate`/`suggested_level` signal at most, nothing more.*

---

## 12. Known limitations (v1)

Said plainly, so nobody is surprised:

- **No code-grounding.** The Reviewer never looks at product source code — it only reasons from what's written in Jira, Confluence, Figma, screenshots, and pasted spreadsheets. If the real behaviour lives only in code, this review can't see it.
- **Confluence, yes; PDF, no.** A linked Confluence page is fetched and read. A linked PDF (or any other non-Confluence document) is reported as "linked but not fetched," not silently ignored — but it isn't read either.
- **No numeric scores in the report.** You'll see counts ("3 findings, 2 High") but never a percentage or a weighted score in the rendered text — that was a deliberate call to avoid false precision that gets quoted out of context.
- **English output only**, even if the trigger phrase or the requirement itself is in another language.
- **It's advisory in tone, mechanical in enforcement.** The report never sounds like a verdict; the gate behind it genuinely is one for CRITICAL findings.

---

## 13. Troubleshooting / FAQ

**"It says it can't reach Jira."**
If nothing else was provided, there's nothing to review, and it stops rather than guessing. If you paste the requirement text directly in chat, it will proceed on that instead.

**"One data source failed but I still got a report."**
That's expected — a single failed source (comments, a sibling lookup, Figma) never aborts the whole review. It's recorded under "Data sources unavailable" with the reason, and if that missing source was actually needed to judge something, it shows up as its own finding rather than being silently skipped.

**"Why didn't it read the screenshot / the linked PDF / the whole spreadsheet?"**
Screenshots: it does read them. It downloads each image attachment through the Atlassian connection to a temporary file, looks at it, and deletes it afterwards; it never opens Jira in a browser to do this. It only quotes text it can actually see, with no guessing at layout or intent. If a download fails, the report says so under "Could not read". Links to another Atlassian site are read through your connection to that site if you have one (see §10); if you don't, the report says which site the link is on and which sites you're connected to, instead of showing a generic error. Linked PDFs: not read in v1 (see §12). Spreadsheets: only if you paste the data or attach a file; it never fetches a Google Sheet on its own.

**"The readiness label and the gate seem to disagree."**
They can, and that's expected (§4). The gate only counts findings by severity; readiness asks how close the requirement is to a testable scope. "Test case drafting can start" next to an amber or red readiness strip means The Creator may run, but whatever it drafts now will be provisional.

**"Can I make it stop asking me which field holds the Acceptance Criteria?"**
Yes — once it asks and you answer, it offers to save that into your product's config so it won't ask again.

**"I re-ran the exact same scan and nothing happened."**
That's the duplicate-request guard (§8) — it noticed nothing changed and asked before re-doing the work. Say yes if you want it to check anyway.

---

## 14. Glossary

| Term | Meaning |
|---|---|
| **Finding (F#)** | A specific gap or problem in the requirement, with a severity |
| **Clarification question (Q#)** | An open question for a human, distinct from a finding |
| **Checklist ref** | Which row of `checklist.md` a finding came from (`A1`–`A8` structural, `B1`–`B12` behavioural) |
| **Gate** | The machine verdict controlling whether The Creator may run automatically |
| **Readiness label** | The human-facing headline — never uses a blocked phrase ("gate," "blocker," "not ready," …) |
| **Rescan** | Re-checking a requirement against its last saved review, not against chat memory |
| **The Creator** | The separate skill that drafts test cases, run only after The Reviewer stops |

---

## 15. Version

This manual describes The Reviewer v1 (`payload_version` / `schema_version` `1.1`), drafted 2026-09-28, updated 2026-09-29. From schema 1.1 on, every report is generated from `review-payload.json` by `scripts/render_report.py`, so two reports always share the same sections in the same order. A rescan whose previous payload used an older schema runs as a full scan rather than a comparison. The full rationale for every rule above is recorded in [`DECISIONS.md`](DECISIONS.md); this manual will be updated if a locked decision changes.
