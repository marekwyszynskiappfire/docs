# Source provenance — Kacper's contribution

| Field | Value |
|---|---|
| Repository | `7pace/7pace.Timetracker` (private) |
| Path | `qa-coe/E2E/.cursor/skills/TestCaseWriting/` |
| Branch | `main` |
| Commit at checkout | `374230db457df3e8ee678c47eeb04ced7272e86e` (2026-09-28 08:51 +0200) |
| Retrieved | 2026-09-28 |
| Method | `git` sparse checkout (cone mode, blobless clone) |

## What was copied

The complete `qa-coe/E2E/.cursor/skills/` directory:

| File here | Source | Notes |
|---|---|---|
| `TestCaseWriting/SKILL.md` | `TestCaseWriting/SKILL.md` | Skill `name` is `timetracker-test-case-writing`. The primary contribution. |
| `AutomatingTestCases/SKILL.md` | `AutomatingTestCases/SKILL.md` | Automation hand-off target; 443 lines. TestCaseWriting passes it the test summary plus Jira work-item key, summary, and id, and it refuses to start without them. |
| `skills-hub-README.md` | `README.md` | Skills hub. Documents the intended order: TestCaseWriting → Jira import → AutomatingTestCases. |
| `skills-overview.html` | `skills-overview.html` | See prior-art note below. |

### `skills-overview.html` is directly relevant prior art

A 23 KB **self-contained** HTML guide — inline `<style>` and `<script>`, zero external `src`/`href` references, navigation via in-page anchors only. Titled "Timetracker E2E Skills — Quick Guide", with sections for overview, authority, pipeline, data, rules, mapping, and invocation, plus a scroll-spy nav built on `IntersectionObserver`.

This independently arrives at the same conclusion as decision D1: a single self-contained HTML file that opens in any browser. Worth reading before building `shared/render_report.py`, both for the pattern and because Kacper already has a house style for this kind of artifact that our reports could stay consistent with.

## Related material in the source repo, NOT copied

| Path | Relationship |
|---|---|
| `qa-coe/E2E/Timetracker/specs/TS-*/TTQA-*.case.ts` | ~143 Playwright cases the skill greps as pattern examples. Not a rule source. |
| `qa-coe/E2E/Timetracker/fixtures/jiraIssueIds.json` | Jira issue-id fixtures the skill reads for a given `TTQA-*`. |
| `qa-coe/E2E/Timetracker/api/e2eRequiredJiraUserEmails.ts` | Canonical E2E user list the skill requires in step Data. |
| `qa-coe/E2E/Timetracker/config/parallelTestDateIsolation.ts` | Date-isolation bands underpinning the strict relative date labels. |

These are product-specific and live in a different repo, so they are deliberately out of scope as consolidation inputs. They matter to the Phase 1 inventory only as evidence of **what kind of product-specific grounding a skill may require** — see the note below.

## Notes for the Phase 1 inventory

This skill is materially different in shape from Marek's two, and the differences are the interesting part of the consolidation:

- **Output format is Xray CSV** with exactly three columns (`Action`, `Data`, `Expected Result`), plus a separate plain-text Jira Description block. Marek's skills produce a `TestCaseDraft` JSON batch. These are incompatible test representations and the merged payload must cover both.
- **Explicitly does not create anything in Jira/Xray** — import is manual. That conflicts with the agreed decision D4 (The Creator submits after approval).
- **Interrogative by design:** a nine-item "ask before drafting" gate that blocks on missing Summary, `TTQA-*`, Jira work-item key/summary/id. Marek's skills gate on requirement quality instead.
- **Draft status model** is binary (`Final draft` vs `Preliminary draft`) based on whether behaviour was verified against current code, rather than P0–P3 execution tiers.
- **Code grounding as authority:** authority order is approved Jira steps → current product code and live UI → repo examples. Marek's skills ground in requirements plus external context, with no code-reading step at all.
- **Hard anti-invention rules** around identifiers (never invent or borrow `TTQA-*`, `KAN-*`, `SUG-*`; never invent users) that are stricter and more specific than anything in Marek's skills.
- **Coverage strategy is risk-layered** (access → platform shell → domain happy path → domain edges → regression) with a 5–15 manual cases per feature slice heuristic, versus Marek's `CAT-*` catalog-coverage model.
- Contains its own **comparison note** against a platform `story-ui-test-cases` skill, which implies at least one more skill exists in the wider organisation that we have not seen.
