# Newbie persona review — Trinity solution & docs

**Date:** 2026-10-15  
**Persona:** [Sam (P11)](personas/operator-first-time.md) — Jira/Xray QA, first Cursor/git setup  
**Method:** Walk docs in Sam’s reading order; run `./Trinity/scripts/pilot-preflight.sh`; smoke Studio API (`/api/health`); cross-check UI labels vs FIRST-RUN / MANUAL. **Not** a live human UAT (see [OPERATOR-VALIDATION.md](OPERATOR-VALIDATION.md)).

**Wider pilot (15–29 Oct 2026):** track human feedback in GitHub `trinity-support` + [PILOT-SHARE.md](PILOT-SHARE.md). Re-score this doc after the wave closes.

---

## Executive summary

| Area | Verdict | Score (1–5) |
|------|---------|-------------|
| **Can Sam finish demo without Jira?** | Yes — `seed-demo.sh` + FIRST-RUN Phase 1 paths are consistent | 4 |
| **Can Sam finish one sandbox Epic alone?** | Possible after MCP + P2 config; high friction on portfolio/import paths | 3 |
| **Documentation completeness** | Strong spine (START-HERE → FIRST-RUN → FAQ → PROMPTS); gaps: screenshots, clone URL, section order | 3.5 |
| **Solution shareability** | Internal pilot + buddy/P2 for mapping; not unattended GA | 3 |

**Bottom line:** Documentation is **good enough for guided pilot**; **not** yet proof that a stranger completes OPERATOR-VALIDATION with zero coaching. Close the loop with one recorded UAT using this file + validation checklist.

---

## Journey walkthrough (simulated)

### Day 0 — “What is this?”

| Step | Sam experience | Result |
|------|----------------|--------|
| Open START-HERE | Clear table of paths; wiki links work | OK |
| Read PATH-TO-1.0 early via link | May feel “not ready” despite START-HERE “production use” table | Mixed — START-HERE mitigates |
| Clone repo | Placeholder `<docs-repo-url>` in several files | **Friction** — use [clone command](#fixes-applied-in-git) |

### Day 1 morning — Studio only (FIRST-RUN 0–1)

| Step | Sam experience | Result |
|------|----------------|--------|
| `start.sh` | 3–8 min wait documented | OK |
| Two URLs 5173 vs 8765 | Explained in FIRST-RUN | OK |
| `seed-demo.sh` | Works; Creator default path matches UI | OK |
| Importer Phase 1 “preview optional” | May think pipeline is broken if form empty | OK if FAQ read |
| Screenshots | None in repo; text-only nav map | **Gap** |

**Mechanical check:** `pilot-preflight.sh` — 7/7 PASS (skills, renderer, Studio health).

### Day 1 afternoon — Cursor (FIRST-RUN 2)

| Step | Sam experience | Result |
|------|----------------|--------|
| `install-trinity-skills.sh` | Clear | OK |
| MCP setup | Long; dual-site easy to miss until thin gather | **Risk** — CURSOR-MCP-SETUP helps |
| `.env` | Many vars; restart Studio repeated | OK in GUIDE/FIRST-RUN |

**Historical doc issue:** [OPERATOR-ONBOARDING.md](OPERATOR-ONBOARDING.md) used to put MCP **before** demo; learning order now aligned with FIRST-RUN (see that file intro).

### Day 2 — Real Epic (FIRST-RUN 3)

| Step | Sam experience | Result |
|------|----------------|--------|
| Reviewer configs in Studio | Needs product line from P2 | Expected |
| Prompt 1 | Must paste Studio prompt, not hand-write | OK in golden rules |
| Output paths | `portfolio_run_id` may be dated subfolder under `runs/` | **Friction** — import folder = parent of `EPIC-KEY/` |
| Approve → Send to Creator | Approve vs export vs run-folder JSON | OK after MANUAL §7.5.1 + FAQ |
| Multi-epic Creator | One import per epic — easy to miss | OK in FIRST-RUN 3.5 + artifacts README |
| Importer mapping + project key | #1 support topic | OK in FAQ/GUIDE; still hard |

---

## Documentation map (Sam lens)

| Doc | Fit for P11 | Notes |
|-----|-------------|-------|
| [START-HERE.md](START-HERE.md) | Entry | Add canonical clone; command order |
| [FIRST-RUN.md](FIRST-RUN.md) | **Primary tutorial** | Best phased narrative |
| [OPERATOR-ONBOARDING.md](OPERATOR-ONBOARDING.md) | Gate checklist | Must match FIRST-RUN order |
| [FAQ.md](FAQ.md) | Safety net | Strong troubleshooting |
| [PROMPTS-AND-INPUTS.md](PROMPTS-AND-INPUTS.md) | Pre-flight for Agent | Does not replace portfolio interview in SKILL |
| [MANUAL.md](MANUAL.md) | Reference | Long; not day-one |
| [OPERATOR-VALIDATION.md](OPERATOR-VALIDATION.md) | Sign-off | Empty until human runs it |
| [reviewer/SKILL.md](reviewer/SKILL.md) | Agent | Too deep for Sam |

**Overlapping entry points:** FIRST-RUN vs OPERATOR-SETUP vs OPERATOR-ONBOARDING — intentional; START-HERE table reduces confusion if read first.

---

## Solution (product) findings

| Topic | Finding |
|-------|---------|
| **Studio** | Demo path solid; Statistics/approve flows documented; favicon/Jira links help orientation |
| **Reviewer** | Full fidelity = long runs; newbie must trust “wait until agent finishes” |
| **Creator** | `suite-payload.json` per epic clear for portfolios; `not_fit` blocks Send to Creator — documented |
| **Importer** | Execute vs Cursor prompt split remains cognitive load |
| **Confluence** | Source in git; wiki rendering may differ — git wins |
| **Assets** | No PNG set under `docs/screenshots/` — tutorial feels “enterprise text” |

---

## Gaps (prioritized)

### P0 — before next external share

1. **Human UAT** — one operator fills [OPERATOR-VALIDATION.md](OPERATOR-VALIDATION.md); use [UAT-SESSION.md](UAT-SESSION.md) + [issue template](../.github/ISSUE_TEMPLATE/trinity-pilot-feedback.yml). **Still open.**
2. **Canonical clone URL** — done (START-HERE, FIRST-RUN, GUIDE, OPERATOR-SETUP).
3. **Import folder rule** — done (FAQ, MANUAL, PROMPTS, PIPELINE, runs README, etc.).

### P1 — quality

4. **Screenshots** — done in [`docs/screenshots/`](docs/screenshots/) (2026-10-15); wiki attachments manual.
5. Short Loom or deck clip: Phase 1 click-through (5 min). **Still open.**
6. **Portfolio interview** pointer — done in [PROMPTS-AND-INPUTS.md](PROMPTS-AND-INPUTS.md) § Prompt 1.

### Wiki

7. **Newbie persona review** — [Confluence page](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3758587937/Trinity+Newbie+persona+review) + `page-map.json` (sync from git).

### P2 — GA

7. Second product mapping (PATH-TO-1.0).
8. Studio CI / operator regression tests in TESTING.md automation.

---

## Doc changes from this review

- Persona [operator-first-time.md](personas/operator-first-time.md) (P11).
- This review document.
- [OPERATOR-ONBOARDING.md](OPERATOR-ONBOARDING.md) — learning order + section reorder (Studio → demo → Cursor).
- [START-HERE.md](START-HERE.md) — clone URL, command order, link to review.
- [FIRST-RUN.md](FIRST-RUN.md) — import-folder clarification.
- [P1-P10.md](personas/P1-P10.md) — P11 row.

**Canonical clone:**

```bash
git clone https://github.com/marekwyszynskiappfire/docs.git DOCS
```

---

## Re-run this review

1. Read as Sam: [personas/operator-first-time.md](personas/operator-first-time.md) checklist §7.  
2. `./Trinity/scripts/pilot-preflight.sh`  
3. FIRST-RUN Phase 1 on a clean machine (or `cleanup-local-runs.sh` dry-run).  
4. Update **Score** table and **Gaps** when OPERATOR-VALIDATION is filled.
