# Golden example — journey test (create Text custom field)

**Pattern:** `journey` · **Tier:** P0 · **Reference:** TC-6117

## SPM - OKR - Creating Text type custom field

**Priority:** High | **Type:** Manual | **Execution tier:** P0 — Critical  
**Role:** OKR Admin | **Tags:** journey, create, field-type-text, smoke

**Linked:** ONE-232514 · **Catalog:** CAT-CREATE-TEXT  
**Customer impact:** If this fails, customers cannot create or use Text custom fields across OKR views — core Part 2 deliverable.

**Preconditions:** OKR Admin logged in; staging tenant; feature flag enabled (`{FLAG_KEY}`)

**Pre-test data required:** No  
**Pre-test data setup:** Environment only — OKR Admin account, feature flag on, staging tenant. No custom field or OKR data required beforehand; create empty dedicated test box in step 1.

| Step | Action | Expected result | Test data |
|------|--------|-----------------|----------|
| 1 | Navigate to OKR Settings → Fields for boxName | Fields settings page displays table (Field name, Type, Used in, Description, Visibility) and **Create new** button | boxName: QA-JOURNEY-CREATE-TEXT |
| 2 | Click **Create new** | Create custom field modal opens with Type default Text, Max length (optional), Used-in options, Create disabled until valid | — |
| 3 | Enter name and description; click **Create** | Field appears in Your custom fields list with correct name, type, description, Used-in | fieldName: Text field QA; description: Journey test field |
| 4 | Overview → Add → Create strategic theme | Creation modal shows Text field default **Not set** | — |
| 5 | Enter ST name, period, Text value; click **Create** | ST visible in tree; Text field shows value in right panel | stName: Strategic theme 1; period: Y2026; value: Sample1234 |
| 6 | Add Objective under ST | Creation modal shows Text field **Not set** | — |
| 7 | Enter Objective name, period, Text value; click **Create** | Objective in tree; Text field in right panel | objectiveName: Objective 1; value: Sample5678 |
| 8 | Add Key Result under Objective | Creation modal shows Text field **Not set** | — |
| 9 | Enter KR name, period, Text value; click **Create** | KR in tree; Text field in right panel | krName: KR 1; value: Sample999 |
| 10 | Open Overview; locate Text column | Text field visible for ST, Objective, KR with correct values | — |
| 11 | Click grey area on ST row | Side panel opens; Text field name and value correct | — |
| 12 | Click grey area on Objective row | Side panel opens; Text field name and value correct | — |
| 13 | Click grey area on KR row | Side panel opens; Text field name and value correct | — |
| 14 | Open ST detail → Info section | Text field name and value correct | — |
| 15 | Open Objective detail → Info section | Text field name and value correct | — |
| 16 | Open KR detail → Info section | Text field name and value correct | — |

**Deferrable:** No — P0 Critical
