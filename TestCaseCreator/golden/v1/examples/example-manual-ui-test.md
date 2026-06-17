# Golden example — manual UI test (reference)

**Purpose:** Style reference for test-case-creation. Not a live Xray export.

---

## Title

OKR Admin creates Select custom field with applicable goal type Objective

## Metadata

| Field | Value |
|-------|-------|
| test_type | Manual |
| priority | High |
| linked_requirement_keys | ONE-EXAMPLE-001 |
| linked_ac_ids | AC-01 |
| tags | okr, custom-fields, smoke |

## Preconditions

- User is logged in as OKR Administrator with "Manage custom fields" permission
- Feature flag `okr.custom-fields.enabled` is on (staging)
- At least one OKR workspace exists

## Steps

| # | Step | Expected result | Test data |
|---|------|-----------------|-----------|
| 1 | Navigate to **Settings → OKR → Custom fields** | Custom fields configuration page opens; existing fields list or empty state is displayed | — |
| 2 | Click **Add custom field** | Create custom field form/modal opens | — |
| 3 | Enter a user-facing name in **Name** | Name field accepts input | Name: `Work Area` |
| 4 | Select **Select** as field **Type** | Values section becomes required/enabled | — |
| 5 | Add at least one option in **Values** | Option is listed in values editor | `Innovation`, `Core` |
| 6 | Set **Applicable goal type** to **Objective** only | Objective is selected; other levels deselected per design | — |
| 7 | Click **Save** | Custom field is created; success feedback shown; field appears in admin list with Type=Select, Goal type=Objective | — |

## Notes

- Expected result names UI labels as shown in Figma — adjust if UX copy differs.
- One AC → one primary happy-path test; edge cases belong in separate tests.
