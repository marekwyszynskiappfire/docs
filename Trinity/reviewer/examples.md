# The Reviewer — examples

Each example is illustrative, not a real run. Issue keys are fictional (`DEMO-*`).

---

## Example 1 — Single Story, BLOCKED

**Request:** `Review DEMO-4521`

**Fetched:** AC field is empty; no AC-equivalent bullets in the description.

**Finding:**
```json
{
  "finding_id": "RR-DEMO-4521-01",
  "jira_key": "DEMO-4521",
  "severity": "CRITICAL",
  "category": "acceptance_criteria",
  "checklist_ref": "A3",
  "excerpt_quote": "acceptance_criteria: (none)",
  "finding_summary": "No acceptance criteria defined, and none in the description either.",
  "question_for_PM": "Please add testable AC for the happy path and at least one failure case.",
  "owner_hint": "PM",
  "blocks_test_generation": true
}
```

**Gate:** `BLOCKED`. **Readiness label shown to the PM:** "Needs clarification before scope can be tested" — never the word "blocked." Agent stops; does not suggest running The Creator.

---

## Example 2 — Story with warnings, PASS_WITH_WARNINGS

**Finding (HIGH, behavioural):**
```json
{
  "finding_id": "RR-DEMO-4522-01",
  "jira_key": "DEMO-4522",
  "severity": "HIGH",
  "category": "behavioral_gap",
  "checklist_ref": "B4",
  "excerpt_quote": "If the export fails, show an error.",
  "finding_summary": "Error-handling AC exists but doesn't say what the error message contains or whether the export is retryable.",
  "question_for_PM": "What should the error message say, and can the user retry without re-selecting fields?",
  "owner_hint": "PM",
  "blocks_test_generation": false
}
```

**Ambiguity finding (ties to A3):** the term "reasonable time" in the AC ("the export completes in a reasonable time") is flagged: `Term "reasonable time" is ambiguous — pass criteria cannot be defined without clarification.`

**Gate:** `PASS_WITH_WARNINGS`. **Readiness label:** "Ready to build tests" if only Optional questions remain open; otherwise "Needs clarification before test design" if a Medium+ question is still open (A-15's stricter rule).

---

## Example 3 — Force override

**Request:** `force=true — proceed despite CRITICAL findings; PM will fix ACs in parallel.`

**Agent steps:**
1. Confirm QA's intent explicitly in chat before acknowledging.
2. Set `gate.force_override: true`, `gate.force_override_by: "<QA operator>"`, `gate.force_override_at: "<ISO-8601>"` — all three required together, enforced structurally by the schema (A-8).
3. Set `gate.status: PASS_WITH_WARNINGS` — never a bare `PASS`.
4. Still list every CRITICAL finding for the PM.

---

## Example 4 — Epic scan with batch handoff

**Request:** `scan DEMO-9000` (issue type: Epic)

**Gather:** the paginated child-inventory JQL call requests `description` alongside `key`/`summary`/`status` for all 34 children — one call, no per-child round trip (decision C4). 29 children have a real description; 5 have an empty or template-only description, so those fall back to their `summary` as a lower-confidence signal and are recorded as `content_source: title_only` (e.g. `DEMO-9033 — "Add export retry button"` — title only, description empty).

**Output excerpt:**

```markdown
# Epic Testability Review — DEMO-9000

**Child work inventory:** 34 children (full — paginated to isLast, not a sample; 29 read via description, 5 via title-only fallback)
**Status mix:** Done 21 · Waiting for Release 4 · Open 9

## Epic batch handoff
**Recommended for batch (8):** DEMO-9001, DEMO-9014, DEMO-9022, DEMO-9031, DEMO-9040, DEMO-9044, DEMO-9051, DEMO-9060
**Excluded from recommended (examples):** DEMO-9002 — unit-test-only change

| You say | What happens |
|---|---|
| `confirm batch` / `yes` / `run batch` | Child scan + Preliminary TC per recommended key → Batch tab |
| `scan DEMO-9000 --batch` | Same, in one turn |
| `scan DEMO-9000 --batch all-wfr` | All 4 Waiting-for-Release children instead (explicit only) |
```

`recommendedBatchKeys` is computed directly by The Reviewer (RV4/R-G10) — no dependency on a separate orchestrator skill that was never contributed.

**Finding from the title-only fallback (MEDIUM, per C4):**
```json
{
  "finding_id": "RR-DEMO-9000-02",
  "jira_key": "DEMO-9000",
  "severity": "MEDIUM",
  "category": "behavioral_gap",
  "checklist_ref": "B12",
  "excerpt_quote": "DEMO-9033 — \"Add export retry button\" (description empty)",
  "finding_summary": "DEMO-9033 has no description; its title alone doesn't confirm whether the retry button is scoped to this epic's export flow or a different one.",
  "question_for_PM": "Can DEMO-9033 get a description, even a short one, confirming it's the retry button for this epic's export flow?",
  "owner_hint": "PO",
  "blocks_test_generation": false
}
```
This is named explicitly (`content_source: title_only`) rather than silently reasoned about as if the title were description text — the fallback informs the narrative, it never marks B12 COVERED on its own.

---

## Example 5 — Rescan delta, with staleness check

**Request:** `rescan DEMO-4521` (three days after Example 1's `BLOCKED` run)

**Agent steps:**
1. Load the persisted payload for `DEMO-4521` (not chat memory — this rescan is in a fresh chat session).
2. Re-fetch the live issue; recompute `requirement_fingerprint`.
3. Fingerprint differs from the cached one → note the story changed since the last scan, then proceed.
4. AC now exists → `RR-DEMO-4521-01` marked **Resolved**.
5. Output a Rescan Delta: 1 finding resolved, 0 new, readiness changed from "Needs clarification before scope can be tested" to "Ready to build tests." Gate flips from `BLOCKED` to `PASS`.

---

## Example 6 — Total Jira outage, with and without a fallback bundle

**Case A — no fallback:** Atlassian MCP is unreachable and the user supplied nothing else.
> Cannot reach Jira and no requirement content was provided another way. Aborting — there is nothing to review. Please check the Atlassian MCP connection or paste the requirement content directly.

**Case B — fallback bundle exists:** same outage, but the user pasted the requirement text in chat.
> Jira is unreachable right now (`context_loaded`: `jira_issue` → `failed`, reason `MCP connection timeout`). Proceeding on the pasted content you provided. Note: this review can't confirm the pasted text matches the current live issue.

**Case C — partial mid-gather failure (most common):** the primary issue fetch succeeds; comments 403.
> Continuing — comments could not be read (`403 permission denied`). This is recorded in Data sources unavailable and does not stop the review; it may still surface as a finding if a comment was the only place scope was clarified.

---

## Example 7 — Confluence, Figma, and screenshot ingest together

**Gathered:**
- A linked Confluence page ("Bulk export — field mapping") is fetched read-only and analyzed (R-G2).
- A Figma link on the parent Epic resolves to 2 frames (`get_design_context`, ≤3 cap respected).
- A screenshot attached to the issue is read via vision; the only text found is a button label.

**`context_loaded` excerpt:**
```json
[
  { "source": "Confluence: Bulk export — field mapping", "type": "confluence_page", "status": "analyzed" },
  { "source": "Figma node 118:4402", "type": "figma_node", "status": "analyzed" },
  { "source": "Attachment: export-modal.png", "type": "screenshot", "status": "analyzed" }
]
```

**Design observation bullet:** `Button labelled "Export selected fields" *(Source: Figma — https://figma.com/design/…, node 118:4402)*`

**Screenshot bullet:** `Visible button label: "Export selected fields" *(Source: Attachment export-modal.png)*` — no layout, module, or intent guess added.

If either bullet had contained a real customer name or email, it would be redacted before reaching this output (display-time redaction, A-6) — the model was still allowed to read the image itself.

---

## Example 8 — Jira comment: copy-paste vs. auto-post

**Default (`policy.jira_comment: "off"`):** the skill always produces the wiki-markup comment block and stops — the operator copies and pastes it into Jira themselves.

**Opt-in (`policy.jira_comment: "auto-post"`):** the skill calls the Jira comment-write capability directly after producing the same block, and tells the operator it did so, including the comment id if returned. Redaction rules apply identically either way — no unredacted sensitive content reaches Jira through either path.
