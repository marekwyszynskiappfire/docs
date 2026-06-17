# Xray extract — optional depth reference

When you pass an **existing Xray extract** into test-case-creation, use a structured export (JSON or Markdown) of current production tests for the same feature area.

**Purpose:** match step granularity and naming style; set `possible_duplicate_of` where intent overlaps. The skill does **not** require this file.

## Minimal shape (informal)

- List of tests with keys (e.g. `TC-6101`), titles, and steps (action + expected).
- Enough structure for the agent to compare journeys and atoms to the new draft.

## Sample format

Use any JSON/MD export from your Xray project that lists tests with keys, titles, and steps. **This package does not ship sample extracts** — add your own under `TestCaseCreator/artifacts/` or pass an absolute path via `existing_xray_extract`.

Copy structure from your team’s standard export; the agent compares journey depth and naming to the new draft.
