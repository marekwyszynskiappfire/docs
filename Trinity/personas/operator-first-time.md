# Persona — first-time Trinity operator (P11)

**Use for:** doc reviews, UAT scripts, and “would Sam get stuck here?” checks.  
**Not a Cursor runtime prompt** — skills still load [`reviewer-expert-qa-automation.md`](reviewer-expert-qa-automation.md) etc.

---

## Sam — profile

| Field | Value |
|-------|--------|
| **Role** | QA engineer (P1), ~3 years on one product |
| **Strong** | Jira Epics, Xray Test Repository, manual test design, sandbox projects |
| **Weak** | Git beyond clone/pull, terminal, Cursor Agent, MCP, local `.env`, JSON schemas |
| **Has** | Laptop (macOS or Windows), Appfire Jira + sandbox access, API token, Xray keys after asking P2 |
| **Does not have** | Pre-made portfolio config, Importer mapping, or a buddy in the room |
| **Goal** | One sandbox Epic: review → approve → Creator batch → Xray import without breaking production |
| **Fear** | Wrong folder path, posting DEMO data to prod, “inventing” prompts and voiding checks |

---

## Success criteria (first week)

1. Complete [FIRST-RUN.md](../FIRST-RUN.md) Phases 0–1 **without** Jira (demo only).
2. Pass [OPERATOR-VALIDATION.md](../OPERATOR-VALIDATION.md) Parts A–C on **sandbox** with ≤2 support pings (MCP auth, mapping path).
3. Can explain: **three Studio prompts**, **approve vs In Creator** ([MANUAL.md](../MANUAL.md) §7.5.1), **sandbox vs PRODUCTION** gate.
4. Does **not** need to edit `SKILL.md`, portfolio JSON by hand, or mapping JSON without P2.

---

## Reading order (do not skip)

1. [START-HERE.md](../START-HERE.md) — pick path  
2. [FIRST-RUN.md](../FIRST-RUN.md) Phases 0 → 1 → 2 → 3 (canonical **time** order)  
3. [OPERATOR-ONBOARDING.md](../OPERATOR-ONBOARDING.md) — same steps as **gates** for sign-off  
4. [FAQ.md](../FAQ.md) — when stuck  
5. [MANUAL.md](../MANUAL.md) — only after first epic import attempt  

Avoid until Phase 2 done: [`reviewer/SKILL.md`](../reviewer/SKILL.md), [`PIPELINE.md`](../PIPELINE.md), [`PATH-TO-1.0.md`](../PATH-TO-1.0.md).

---

## Review checklist (for doc authors)

When reviewing a page as Sam, ask:

| # | Question |
|---|----------|
| 1 | Is the **next click** obvious (Studio nav label matches UI)? |
| 2 | Are **placeholders** replaced (`<docs-repo-url>`, `YOUR-EPIC-KEY`)? |
| 3 | Is **order** Studio-before-MCP for day one? |
| 4 | Does import path say “folder that **contains** `EPIC-KEY/`”? |
| 5 | Are **Approve**, **export path**, and **Send to Creator** distinguished? |
| 6 | Is there a **picture or ASCII map** where the UI has 6+ tabs? |
| 7 | Does sandbox vs prod appear **before** first execute? |

Full friction log: [NEWBIE-PERSONA-REVIEW.md](../NEWBIE-PERSONA-REVIEW.md).

---

## Mapping to P1–P10

| P# | Sam interaction |
|----|-----------------|
| **P1** | Primary — triage, approve, Creator, Importer preview |
| **P2** | Provides epic key, portfolio id, mapping file, sandbox project |
| **P10** | Escalation for MCP / dual-site only |
