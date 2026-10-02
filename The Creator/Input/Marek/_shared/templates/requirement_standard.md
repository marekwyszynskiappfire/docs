# Requirement standard — review checklist

Use this checklist when running the **requirements-review** skill. Each criterion maps to finding categories in [reference.md](../requirements-review/reference.md).

**Version:** 1.0

---

## 1. Identity and metadata

| # | Criterion | Severity if failed |
|---|-----------|-------------------|
| 1.1 | `work_item.jira_key` is present and resolves to a real issue | CRITICAL |
| 1.2 | `work_item.summary` is present and describes user-visible outcome | HIGH if missing |
| 1.3 | `work_item.issue_type` is appropriate (Story/Epic for test generation) | MEDIUM |
| 1.4 | `document.schema_version` and extraction metadata present when bundle is file-based | MEDIUM |

---

## 2. Description

| # | Criterion | Severity if failed |
|---|-----------|-------------------|
| 2.1 | `description` or `summary` paragraph explains context, actors, and desired outcome | CRITICAL if both empty |
| 2.2 | Description does not contradict acceptance criteria | CRITICAL |
| 2.3 | Explicit **out of scope** noted when feature touches shared systems | HIGH |

---

## 3. Acceptance criteria (primary test source)

| # | Criterion | Severity if failed |
|---|-----------|-------------------|
| 3.1 | At least one acceptance criterion item exists | CRITICAL |
| 3.2 | Each AC is **atomic** (one verifiable behaviour per item) | HIGH |
| 3.3 | Each AC is **testable** — observable pass/fail without inventing behaviour | CRITICAL if untestable |
| 3.4 | AC uses concrete actors, states, inputs, and outcomes (not vague “works correctly”) | HIGH |
| 3.5 | AC ids are stable (`AC-01`, …) when multiple items exist | MEDIUM |
| 3.6 | No duplicate AC items stating the same behaviour | MEDIUM |

**Testability test:** Could a QA engineer write step + expected result from this AC alone, without guessing product behaviour?

---

## 4. Scope

| # | Criterion | Severity if failed |
|---|-----------|-------------------|
| 4.1 | `scope.in_scope` lists what this work item delivers | HIGH if missing for complex features |
| 4.2 | `scope.out_of_scope` lists exclusions when ambiguity is likely | HIGH |
| 4.3 | In-scope and out-of-scope do not contradict each other or ACs | CRITICAL |

---

## 5. Testability

| # | Criterion | Severity if failed |
|---|-----------|-------------------|
| 5.1 | Target **environment** named (staging, sandbox, etc.) when behaviour is environment-specific | HIGH |
| 5.2 | **Test data** or fixtures identified when AC references specific data states | HIGH |
| 5.3 | **API** paths/methods named when AC covers API behaviour | HIGH |
| 5.4 | **UI screens** or routes named when AC covers UI behaviour | HIGH |
| 5.5 | Enumerations (status codes, error codes) listed when AC references them | HIGH |
| 5.6 | Mark `N/A` with reason when section truly does not apply (API-only, UI-only) | MEDIUM if blank without reason |

---

## 6. Traceability

| # | Criterion | Severity if failed |
|---|-----------|-------------------|
| 6.1 | Parent Epic linked when work item is a Story | HIGH |
| 6.2 | Design reference (Figma, spec link) present when AC implies UI validation | HIGH |
| 6.3 | Related Jira keys noted for dependencies that affect test setup | MEDIUM |

---

## 7. Open questions and assumptions

| # | Criterion | Severity if failed |
|---|-----------|-------------------|
| 7.1 | No `open_questions` with `blocking: true` remain unanswered | CRITICAL |
| 7.2 | Non-blocking open questions are listed with owner | MEDIUM |
| 7.3 | Material assumptions are explicit; flagged if they affect test validity | HIGH |

---

## 8. Data sensitivity

| # | Criterion | Severity if failed |
|---|-----------|-------------------|
| 8.1 | No live secrets, API keys, or production credentials in requirement text | CRITICAL |
| 8.2 | PII in examples flagged; `document.redaction_applied: true` when redacted | HIGH |
| 8.3 | Attachment index lists names only if binaries are excluded from LLM | MEDIUM |

---

## 9. Template compliance

| # | Criterion | Severity if failed |
|---|-----------|-------------------|
| 9.1 | Required sections from [requirements-template.md](../../requirements-template.md) are present or explicitly `N/A` | MEDIUM |
| 9.2 | Empty required fields are marked, not silently omitted | HIGH |

---

## Gate rules (summary)

- **CRITICAL** finding → `blocks_test_generation: true` → gate **BLOCKED** unless QA sets `force=true`.
- **HIGH** → report and warn; does not block by default.
- **MEDIUM / LOW** → report only.
