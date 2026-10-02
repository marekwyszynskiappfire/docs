# Karolina & Agata's contribution — inventory notes

| Field | Value |
|---|---|
| File | `TestabilityScanner.MD` (1,442 lines) |
| Skill `name` | `story-testability` |
| Added | 2026-09-28, by Marek |
| Provenance | Not recorded — source repo/path unknown. Worth capturing. |

## What it is

A single-file skill for **Jira story and epic testability analysis**: read-only gather, gap heuristics across 12 dimensions, findings (`F#`) and clarification questions (`Q#`), readiness classification, rescan delta mode, Jira comment formatting, and an **HTML report export**.

This is the most directly relevant contribution to **The Reviewer** — it is essentially a mature implementation of it, and its report design is well ahead of anything in the working plan.

## Adopt from this skill

1. **Three-tier information architecture for the HTML report.** Tier 1 always visible (header, one-line counts, readiness strip, KPI cards); Tier 2 in `<details open>` (findings, questions, risks and testing focus); Tier 3 in collapsed `<details>` (raw facts, Figma observations, epic context, flows, checklist). Tier assignment is **fixed per section**, so a section with no content renders an empty-state line rather than moving tier or disappearing. This is better specified than the working plan's "summary band plus list" and should replace it.
2. **`<details>`/`<summary>` for progressive disclosure** — no JavaScript, survives printing to PDF, keyboard and screen-reader accessible. Item counts in every `<summary>` so the collapsed state still conveys scale.
3. **Report integrity rules.** Every fact bullet carries `*(Source: …)*`; anything absent is rendered as "Not stated in story" rather than an inferred default; no `*(Assumption)*` or `*(typical behavior)*` in the report body. Hypotheses live in questions, never in facts.
4. **Blocked phrases.** "Story failed", "Not ready", "Blocked by QA", "gate", "blocker" as judgment, "PM did not provide AC", "story is invalid". A tone and politics layer the working plan lacks entirely, and it matters because the PM persona is the audience.
5. **Data sources analyzed vs unavailable** in the report header, with per-step failure reasons (e.g. `Comments (403 permission denied)`) and a rule never to abort the whole run for one failed source. Stronger than the plan's `context_loaded[]`.
6. **Graceful MCP degradation**, including looking for a semantically equivalent connected tool before declaring a source unavailable.
7. **A canonical limits table** that every other section refers back to instead of restating numbers.
8. **Rescan delta mode** — marks each `F#` Resolved or Open when the story changes. The working plan has no re-run-after-fix concept at all.

## Conflicts with agreed decisions

See `../../DECISIONS.md` C3 for the full record. In summary:

| # | Conflict | Against |
|---|---|---|
| 1 | Readiness is **advisory**; the words "gate" and "Blocked by QA" are explicitly forbidden | D8 — CRITICAL findings hard-block The Creator |
| 2 | **Zero** numeric scores, percentages, or weighted totals in any output | Plan's coverage percentage and execution-hour estimates |
| 3 | HTML may use **Tailwind CDN** (a network dependency) | D1 — self-contained single file |
| 4 | Runs on **Hive MCP** (`hive-mcp__run_skill` / `load_skill`) with an execution contract for it | D2 — Cursor and Claude |
| 5 | Report is **no-JS by design** for print and accessibility | D3 — in-report editing and JSON export need JavaScript |
| 6 | **Epic batch mode** produces a two-tab report covering up to 8 child stories | Plan assumes single-issue scope throughout |
| 7 | Severity model is `F#` High/Medium/Low plus `Q#` High/Medium/Optional and a 3-value readiness | Marek's CRITICAL/HIGH/MEDIUM/LOW plus PASS/BLOCKED gate |

## Missing dependencies

| Referenced | Status |
|---|---|
| `@story-ui-test-cases` skill | **Missing and important.** This skill hands off to it, and Kacper's `TestCaseWriting` contains a comparison table against it. Two independent contributions point at it, so it belongs in `Input/`. |
| `html-report-template.html` | Referenced once in the TC handoff snippet (`Inner HTML for {{TC_HANDOFF_HTML}} in html-report-template.html`) while the Platform note states the file is self-contained with no companion files. Minor internal inconsistency; confirm whether such a template exists. |
| Figma MCP, Atlassian MCP | Optional and handled by graceful degradation. |

## Other observations

- Handles **Story, Bug, Task, and Epic** with explicit instructions not to silently treat non-Story types as Stories — the working plan only contemplates Story and Epic.
- Ingests **Figma designs (≤3 frames), spreadsheets, and screenshots** as gather inputs.
- Has a **Validation (before output)** section and tone-calibration **Examples**, both patterns worth carrying into the merged skills.
- Trigger parsing accepts Polish (`przeskanuj ONE-123`) but mandates **English output with no exceptions**.
- Explicitly never publishes to Jira or Xray — copy-paste only. Same stance as Kacper's skill, i.e. **two of three contributions forbid automated writes**.
