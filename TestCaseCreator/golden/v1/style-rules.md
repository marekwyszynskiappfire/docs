# Golden test style rules — v1

**Version:** golden/v1 (comprehensive mode)  
**Owner:** QA lead (update after pilot)  
**Used by:** test-case-creation skill  
**Coverage catalog:** `coverage-catalog.md` (package root, optional domain checklist)

These rules define how generated tests should read before QA triage. Golden **examples** live in `golden/v1/examples/` (atomic + journey).

---

## 1. Naming

| Rule | Example |
|------|---------|
| Title starts with action or outcome context | `OKR Admin creates Text custom field on config page` |
| Include role when permission matters | `User without Manage custom fields permission cannot access config page` |
| Negative tests prefix with role + restriction | `Non-admin user cannot edit custom field values inline` |
| Max title length ~120 chars | Truncate with clear ellipsis only if needed |
| No ticket keys in title | Use tags for `ONE-232514` instead |

---

## 2. Step structure

| Rule | Detail |
|------|--------|
| One action per step | Do not combine unrelated actions |
| Step uses imperative mood | "Click **Save**", "Open OKR Overview table" |
| Expected result is observable | UI state, message text, API response code, data persisted |
| Avoid vague results | Not: "Works correctly". Yes: "Custom field appears in Overview table columns list" |
| Max steps — **any** test (journey or atomic) | **15** — split into additional tests if a flow needs more |
| Include test data in step or `test_data` field | "Enter `Budget Q2` in Name field" |
| Journey tests use dedicated **boxName** | `boxName: QA-JOURNEY-CREATE-TEXT TC-001` |
| Preconditions separate from steps | Login, feature flag on, test box setup |
| **Pre-test data fields** | Every test: `test_data_required` + `test_data_prerequisites` — setup checklist before step 1 |
| Step 1 preconditions in update journeys | Embed "field exists with preset values" as step 1 when catalog requires; also set `test_data_required: true` |

---

## 3. Execution tiers and priority

Every test requires `execution_tier` (P0–P3) — see [reference.md](../../reference.md).

| execution_tier | Name | Default `priority` | Deferrable under time pressure? |
|----------------|------|-------------------|--------------------------------|
| **P0** | Critical | Highest / High | **Never** — data loss, security, core unusable |
| **P1** | Mandatory | High | **No** — primary workflows |
| **P2** | Medium | Medium | Optional — workaround exists |
| **P3** | Deferrable | Low / Lowest | **Yes** — analytics, promo, cosmetic |

Also set `customer_impact` (one sentence) on every test.

---

## 4. Test type

| Type | When |
|------|------|
| **Manual** | Default for UI flows in SPM/OKR |
| **Generic** | API-only verification without UI |
| **Cucumber** | Only when org explicitly uses BDD export |
| **Other** | Rare; note in `generation_notes` |

---

## 5. Traceability

- Every test **must** have ≥1 entry in `linked_requirement_keys`.
- When AC ids exist (`AC-01`), populate `linked_ac_ids`.
- When Epic has goal bullets only (no formal AC), use `linked_ac_ids: ["GOAL-01"]` and map in coverage matrix; cite source in `source_quotes`.
- Add `source_quotes` for non-obvious expected results.

---

## 6. Negative and corner case policy (comprehensive)

Follow [coverage-catalog.md](../../coverage-catalog.md) when that catalog applies. Generate catalog validation items **even when not explicit in AC** if PRD implies behaviour.

| Category | Tier | Pattern | Example |
|----------|------|---------|---------|
| **Permissions** | P0–P1 | atomic | Admin blocked; standard user can edit |
| **Create form validation** | P1–P2 | atomic | Missing Name, Values, duplicate name |
| **Inline validation** | P1 | journey + atomic | Invalid URL, non-numeric, invalid date |
| **Settings data loss** | P0 | journey | Select option delete with usage warning |
| **Delete field** | P0 | journey | Confirm dialog; data erased everywhere |
| **Feature flag off** | P0 | atomic | UI hidden (placeholder flag name + warn) |
| **Overview filter/sort** | P1–P2 | atomic | Filter Select, sort Number |
| **Empty / cancel edit** | P2–P3 | atomic | Empty cell; escape discards changes |
| **Amplitude / promo** | P3 | atomic | Event fired; promo dismiss |

Embed validation in **update journeys** (e.g. non-numeric in CAT-UPDATE-NUMBER) **and** add atomic supplements when catalog lists both.

If requirement says **TBD**: catalog item `UNCOVERED` + warning — **do not fabricate endpoints or event names**.

---

## 7. Design references

- Set `covers_design: true` when steps reference specific UI screens from Figma/UX.
- Populate `design_references` with Figma URLs from requirement bundle.
- Step should name the screen: "On **Custom fields config page** (Figma: …)"

---

## 8. Tags (recommended)

Use lowercase kebab or area tags:

- `okr`, `custom-fields`, `permissions`, `api`, `csv-import`, `smoke`, `regression`
- Jira key as tag: `one-232514`

---

## 9. Forbidden patterns

| Avoid | Why |
|-------|-----|
| "Verify it works" | Not observable |
| "Check UI" without specifics | Not reproducible |
| Production URLs/credentials | Use staging placeholders |
| Testing Part 3 / out-of-scope items | Scope creep |
| Atomic-only suite when catalog requires journeys | Misses cross-surface consistency |
| Splitting create journey across 5 atomic tests | QA must reassemble; use one journey |
| Missing `execution_tier` or `customer_impact` | QA cannot prioritize under time pressure |
| Missing `test_data_required` or `test_data_prerequisites` | QA cannot plan setup before execution |
| P0 tests marked deferrable | Contradicts release gate policy |

---

## 10. Language

- **English** for steps and expected results unless requirement specifies otherwise.
- Use product terms from requirement (OKR, Key Result, Overview table, Side panel).
- Preserve field type names exactly: Text, Number, Hyperlink, Select, Multi-Select, User Picker, Date.
