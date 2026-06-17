# Coverage catalog — comprehensive test generation

**Version:** 1.0  
**Used by:** `test-case-creation` skill when the feature matches this catalog (optional elsewhere — use a run-scoped `CAT-*` checklist instead).  
**Purpose:** Optional domain checklist so generated suites can match **production QA depth** when this catalog applies **plus** full Epic traceability. Attach your own Xray-style extract for depth comparison (not bundled in TestCaseCreator). Every applicable catalog item must map to ≥1 test or an explicit `UNCOVERED` + warning.

---

## How to use this catalog

1. After parsing requirements, instantiate applicable **catalog items** for the feature.
2. For each item, generate the prescribed **test pattern** (journey or atomic).
3. Assign **execution tier** (P0–P3), **customer impact** text, and **test data prerequisites** (`test_data_required`, `test_data_prerequisites`).
4. In `coverage_report.catalog_coverage[]`, record item id → test title(s) → status.
5. **Do not mark generation complete** while any **P0 or P1** item is `UNCOVERED` without a documented blocker (TBD spec).

Skip items only when requirements explicitly exclude them (note `N/A` with quote).

---

## Execution tiers

| Tier | Label | Run when | Customer harm if skipped |
|------|-------|----------|---------------------------|
| **P0** | Critical | Every release gate, smoke + regression | Data loss, security, core feature unusable, wrong data shown at scale |
| **P1** | Mandatory | Full regression each sprint | Major workflow broken; admin or user cannot complete primary tasks |
| **P2** | Medium | Standard regression when time allows | Degraded UX, workaround exists, secondary surfaces |
| **P3** | Deferrable | Time-boxed releases only | Analytics, promo, cosmetic, low-traffic edge cases |

**Priority mapping (Xray/Jira):**

| execution_tier | Default `priority` field |
|----------------|--------------------------|
| P0 | Highest or High |
| P1 | High |
| P2 | Medium |
| P3 | Low or Lowest |

---

## Roles (perspectives)

Generate tests from each applicable role:

| Role id | Description | Typical tests |
|---------|-------------|---------------|
| `OKR_ADMIN` | Manage custom fields + edit OKR data | Config, create journeys, settings admin |
| `STANDARD_USER` | Edit OKR field values, no config access | Inline edit, creation modal, blocked from settings |
| `NO_PERMISSION` | Lacks Manage custom fields | Negative access to settings |
| `API_CLIENT` | API/integration caller | API read/write, 403 |
| `SYSTEM` | Feature flag, background | Flag off hides UI |

---

## Test patterns

### Journey test (`test_pattern: journey`)

One test proves a **coherent end-to-end path** with shared test data (dedicated box/workspace).

**Use for:** create-by-type, update-by-type, settings flows with data dependencies.

| Rule | Detail |
|------|--------|
| Max steps | **15** (split only if logically impossible) |
| Test box | Name preconditions with `boxName: {draft-id} {summary}` pattern |
| Hierarchy | When OKR module: create **Strategic Theme → Objective → Key Result** when field applies to all types |
| Surfaces per journey | Settings, creation modal, tree/right panel, Overview table, side panel (grey row), detail Info — **as applicable to Used-in** |
| Negative in journey | Embed validation in update journeys (invalid URL, non-numeric, clear value) where catalog specifies |

### Atomic test (`test_pattern: atomic`)

One test = one concern. Max **15** steps (same cap as journeys).

**Use for:** Overview filter/sort/columns, create-form validation negatives, permissions, feature flag, API, CSV, promo, Amplitude, regression spot-checks.

---

## Catalog — OKR custom fields (reference implementation)

Use as template for similar admin+multi-surface features. Adapt ids when generating for other Epics.

### A. Create journeys — one per field type (7)

| Catalog id | Title pattern | Tier | Pattern | Role |
|------------|---------------|------|---------|------|
| `CAT-CREATE-TEXT` | SPM - OKR - Creating Text type custom field | P0 | journey | OKR_ADMIN |
| `CAT-CREATE-NUMBER` | SPM - OKR - Creating Number type custom field | P0 | journey | OKR_ADMIN |
| `CAT-CREATE-HYPERLINK` | SPM - OKR - Creating Hyperlink type custom field | P0 | journey | OKR_ADMIN |
| `CAT-CREATE-SELECT` | SPM - OKR - Creating Select type custom field | P0 | journey | OKR_ADMIN |
| `CAT-CREATE-MULTISELECT` | SPM - OKR - Creating Multi-Select type custom field | P0 | journey | OKR_ADMIN |
| `CAT-CREATE-USER` | SPM - OKR - Creating User type custom field | P0 | journey | OKR_ADMIN |
| `CAT-CREATE-DATE` | SPM - OKR - Creating Date type custom field | P0 | journey | OKR_ADMIN |

**Each journey must include:**

1. Navigate to Settings → Fields (verify table columns, Create new button).
2. Open Create modal — verify type-specific controls (Values for Select/Multi-Select, Max length for Text, etc.).
3. Create field with valid data; verify list entry.
4. Create ST / O / KR (skip types excluded by Used-in — **assert field absent** on excluded types).
5. Verify Overview table column/value.
6. Verify side panel per goal type (grey row click).
7. Verify detail page Info section per goal type.

**Used-in scoping:** At least one type journey (e.g. Number) must use **partial Used-in** (ST+O only) and assert KR exclusion in modal, tree, Overview, side panel, detail.

### B. Update value journeys — one per field type (7)

| Catalog id | Tier | Pattern | Preconditions in step 1 |
|------------|------|---------|-------------------------|
| `CAT-UPDATE-TEXT` | P1 | journey | Field exists; ST/O/KR have preset values |
| `CAT-UPDATE-NUMBER` | P1 | journey | Same + **invalid non-numeric rejected** + **stepper** |
| `CAT-UPDATE-HYPERLINK` | P1 | journey | Same + **delete value** + **invalid URL blocked** + label |
| `CAT-UPDATE-SELECT` | P1 | journey | Same + **clear** + dropdown values |
| `CAT-UPDATE-MULTISELECT` | P1 | journey | Same + **clear individual** + **clear all** |
| `CAT-UPDATE-USER` | P1 | journey | Same + **clear individual user** + multi-user if applicable |
| `CAT-UPDATE-DATE` | P1 | journey | Same + **date picker** + **clear** |

Surfaces: Overview inline edit → side panel → detail (at minimum for one goal type; expand per Xray depth).

### C. Settings admin (4)

| Catalog id | Scenario | Tier | Pattern |
|------------|----------|------|---------|
| `CAT-SETTINGS-RENAME` | Update field name and description; name >40 chars rejected | P1 | journey |
| `CAT-SETTINGS-SELECT-OPTIONS` | Rename option values; delete option with **usage warning** | P0 | journey |
| `CAT-SETTINGS-DELETE-FIELD` | Delete field — confirm dialog, data erasure, absent everywhere | P0 | journey |
| `CAT-SETTINGS-HIDE` | Hide field; absent from Overview/column layout/tree | P1 | journey |
| `CAT-SETTINGS-RESHOW` | Re-show hidden field; data preserved | P2 | atomic |

### D. Permissions (2)

| Catalog id | Scenario | Tier | Pattern | Role |
|------------|----------|------|---------|------|
| `CAT-PERM-NO-ADMIN` | User without Manage custom fields cannot access Fields settings | P0 | atomic | NO_PERMISSION |
| `CAT-PERM-STANDARD-EDIT` | Standard user can edit values inline but cannot open config | P1 | atomic | STANDARD_USER |

### E. Config validation — create form (5)

| Catalog id | Scenario | Tier | Pattern |
|------------|----------|------|---------|
| `CAT-VAL-NO-NAME` | Cannot save without Name | P1 | atomic |
| `CAT-VAL-NO-TYPE` | Cannot save without Type | P2 | atomic |
| `CAT-VAL-NO-GOAL-TYPE` | Cannot save without Applicable goal type | P1 | atomic |
| `CAT-VAL-NO-VALUES` | Select/Multi-Select cannot save without Values | P1 | atomic |
| `CAT-VAL-DUPLICATE-NAME` | Duplicate field name rejected | P2 | atomic |

### F. Overview table — Epic GOAL-02 extras (6)

| Catalog id | Scenario | Tier | Pattern |
|------------|----------|------|---------|
| `CAT-OVERVIEW-COLUMNS` | Custom field columns in column picker | P1 | atomic |
| `CAT-OVERVIEW-FILTER-SELECT` | Filter by Select value | P1 | atomic |
| `CAT-OVERVIEW-SORT-NUMBER` | Sort by Number column | P2 | atomic |
| `CAT-OVERVIEW-FILTER-MULTI` | Multi-Select filter (any match) | P2 | atomic |
| `CAT-OVERVIEW-COLUMNS-PERSIST` | Column layout persists after reload | P2 | atomic |
| `CAT-OVERVIEW-CANCEL-EDIT` | Cancel/escape discards unsaved inline edit | P2 | atomic |
| `CAT-OVERVIEW-EMPTY` | Unset value empty state in cell | P3 | atomic |

### G. Field-type validation — atomic supplements (5)

| Catalog id | Scenario | Tier |
|------------|----------|------|
| `CAT-VAL-URL-OVERVIEW` | Invalid Hyperlink URL rejected on inline edit | P1 |
| `CAT-VAL-URL-MODAL` | Invalid Hyperlink URL rejected in creation modal | P2 |
| `CAT-VAL-NUMBER` | Non-numeric rejected on inline edit | P1 |
| `CAT-VAL-DATE` | Invalid date rejected in side panel | P2 |
| `CAT-VAL-TEXT-MAX` | Text at max length saves; max+1 rejected (when limit known) | P2 |

If max length unknown → generate test with `generation_notes: BLOCKED pending MAX_TEXT_LENGTH` and tier P2, warn.

### H. Feature flag (2)

| Catalog id | Scenario | Tier |
|------------|----------|------|
| `CAT-FLAG-OFF` | Custom fields UI hidden when flag disabled | P0 |
| `CAT-FLAG-ON` | Custom fields UI visible when flag enabled | P1 |

If flag name unknown → still generate with placeholder `{FLAG_KEY}` and **warn**; tier remains P0.

### I. API (3) — only when contract documented

| Catalog id | Scenario | Tier |
|------------|----------|------|
| `CAT-API-DEFINITIONS` | API returns custom field definitions | P1 |
| `CAT-API-VALUES` | API returns values on OKR fetch | P1 |
| `CAT-API-403` | 403 when caller lacks permission | P2 |

If GOAL-03 TBD → status `UNCOVERED`, warning, **do not fabricate endpoints**.

### J. CSV (4) — only when schema documented

| Catalog id | Scenario | Tier |
|------------|----------|------|
| `CAT-CSV-EXPORT` | Export definitions to CSV | P2 |
| `CAT-CSV-IMPORT-OK` | Valid import creates fields | P2 |
| `CAT-CSV-IMPORT-NO-NAME` | Import missing Name column rejected | P2 |
| `CAT-CSV-IMPORT-NO-VALUES` | Import Select without Values rejected | P3 |

### K. Promo & analytics (4)

| Catalog id | Scenario | Tier |
|------------|----------|------|
| `CAT-PROMO-SHOW` | Promo message displayed when campaign active | P3 |
| `CAT-PROMO-DISMISS` | Dismiss promo; no reappear same session | P3 |
| `CAT-AMP-CREATE` | Amplitude event on field create | P3 |
| `CAT-AMP-EDIT` | Amplitude event on inline edit save | P3 |

### L. Regression (1)

| Catalog id | Scenario | Tier |
|------------|----------|------|
| `CAT-REG-PART1` | Part 1 / prior Epic fields still work after deployment | P1 |

---

## Generic catalog (non-OKR features)

When feature is not OKR custom fields, derive catalog items from:

1. **Requirement AC / goals** — one happy path minimum per must-have AC.
2. **CRUD lifecycle** — create, read, update, delete (if in scope).
3. **Roles** — admin vs standard vs denied.
4. **Surfaces** — each UI/API surface listed in requirements.
5. **Validation** — each constraint named in PRD (type, length, required fields).
6. **Integration points** — API, export, flags, analytics (tier P2–P3 unless security/data).

Use ids: `CAT-{AREA}-{VERB}-{NOUN}`.

---

## Minimum suite size (OKR custom fields class)

| Tier | Approx. tests |
|------|---------------|
| P0 | 12–15 |
| P1 | 15–20 |
| P2 | 10–15 |
| P3 | 4–8 |
| **Total** | **~35–50** (journey + atomic, minimal overlap) |

This subsumes the 19 Xray journeys **and** Epic gaps (filter, sort, flag, permissions breadth).

---

## QA review minimization

Generated batch must include:

1. **`execution_plan` table** in markdown — tier, count, estimated hours, deferrable flag.
2. **`catalog_coverage`** — 100% of applicable items addressed.
3. **Per-test `customer_impact`** — one sentence why tier was assigned.
4. **Per-test `deferrable_rationale`** when tier is P3 (or P2 with deferrable=true).
5. **No duplicate journey + atomic** for same assertion unless atomic isolates a defect class (note in `generation_notes`).

QA triage becomes: confirm TBD placeholders, adjust tiers, drop P3 — not rewrite coverage from scratch.
