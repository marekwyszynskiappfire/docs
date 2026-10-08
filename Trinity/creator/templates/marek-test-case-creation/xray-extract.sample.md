# Xray extract — optional depth reference

When you pass an **existing Xray extract** into test-case-creation, use a structured export (JSON or Markdown) of current production tests for the same feature area.

**Purpose:** match step granularity and naming style; set `possible_duplicate_of` where intent overlaps. The skill does **not** require this file.

## Minimal shape (informal)

- List of tests with keys (e.g. `TC-6101`), titles, and steps (action + expected).
- Enough structure for the agent to compare journeys and atoms to the new draft.

## Sample in this repo

- JSON: `AI in QA/Skills/artifacts/6113-extraction.json`
- Markdown companion: `AI in QA/Skills/artifacts/6113-extraction.md`

Copy one of these as a starting point for another Epic only if the export format is comparable; otherwise attach your own extract using the same logical fields (test key, title, steps).
