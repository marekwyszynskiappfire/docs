# Test case creation — how to run it

This folder defines the **test-case-creation** Agent Skill. The normative procedure lives in [`SKILL.md`](SKILL.md). This README is the **operator guide**: what to prepare, how to invoke the agent, and copy-paste **prompts**.

## What you get

- **One output file:** `AI in QA/Skills/artifacts/{JIRA-KEY} - testcase-draft.md`  
  Full suite, requirement ↔ test traceability, coverage tables, and a **JSON appendix** for tooling.
- **Rules:** assessment-first suite size, **≤15 steps** per test, P0–P3 tiers, optional domain catalog or run-scoped `CAT-*` checklist.

## Inputs (mandatory vs optional)

| Input | Required? | Notes |
|-------|-------------|--------|
| **Requirement source** | **Yes** | Jira Epic/Story key (or JQL scope), **or** a normalized bundle file per [`AI in QA/requirements-template.md`](../requirements-template.md). The `{JIRA-KEY}` in the output filename comes from the primary work item. |
| **Requirements review JSON** | No — **strongly recommended** | Optional gate file; generation still allowed without it. Sample: [`templates/requirements-review.sample.json`](templates/requirements-review.sample.json). |
| **External context** | No | **You may add** workspace paths and/or URLs (PDFs, Confluence, images, exports, etc.). See [`templates/external-context.sample.md`](templates/external-context.sample.md). |
| **Xray extract** | No | Depth / dedupe reference. See [`templates/xray-extract.sample.md`](templates/xray-extract.sample.md). |
| **Domain coverage catalog** | No | Only if the feature matches that domain: [`coverage-catalog.md`](coverage-catalog.md). |

The agent also loads repo **style/schema assets** (you do not pass these): `golden/v1/`, `schemas/TestCaseDraft.schema.json`.

---

## Step-by-step (full run)

### Step 1 — Open the right workspace

Open the repository that contains this skill (e.g. your **DOCS** repo with `AI in QA/Skills/`). The agent needs read access to any **local paths** you list under `external_context`.

### Step 2 — Gather the requirement anchor

- **Jira path:** have the Epic or Story key (e.g. `PROJ-12345`) and ensure MCP or your process can fetch it.  
- **Bundle path:** if you use a file instead, ensure `work_item.jira_key` is set in the bundle so `{JIRA-KEY}` and schema traceability stay valid.

### Step 3 — (Recommended) Run requirements review

Run the `requirements-review` skill first, or produce equivalent `requirements-review.json`. This improves AC quality; it is **not** mandatory to start test generation.

### Step 4 — Collect optional external files and links

Decide what should **drive or enrich** test design beyond Jira:

- Downloaded **PDFs** (PRD, security review), **Word** exports saved as PDF or `.md`, **markdown/HTML** specs.
- **Images** (mockups, flow diagrams, screenshots) — attach paths; the agent will use them for UI expectations where possible.
- **URLs** you want read explicitly (internal Confluence, public docs, design files) — paste them in the prompt list.

Put files somewhere the workspace can read (e.g. under your repo or an absolute path the agent is allowed to access).

### Step 5 — (Optional) Prepare Xray extract or domain catalog

Only if you use them: paths to extract JSON/MD, and confirm whether [`coverage-catalog.md`](coverage-catalog.md) applies to your feature.

### Step 6 — Invoke the agent with the master prompt

In Cursor chat, paste a prompt from **Prompts** below. Adjust:

- `PROJ-12345` → your Jira key  
- Paths → your real files (workspace-relative or absolute)  
- URLs → your real links  
- Remove sections you do not use.

### Step 7 — Let the agent follow the skill

The agent should:

1. Load requirements (Jira/bundle).  
2. Load **user-supplied** `external_context` (files + URLs).  
3. Resolve **Jira-embedded** links (Confluence, linked issues, Figma, attachments) when tools allow.  
4. Run the gate **only if** you supplied a review JSON.  
5. Publish the assessment plan in chat, then generate tests.  
6. Write **`AI in QA/Skills/artifacts/{JIRA-KEY} - testcase-draft.md`**.

### Step 8 — Read the output

Open the Markdown file. Check:

- **Linked external context** and **User-supplied external context** tables (what was loaded vs skipped).  
- **Requirement → test traceability**.  
- **Appendix JSON** if you need `xray_graphql_import.py` or another consumer (save the fenced JSON to a temp file if the script requires a path).

### Step 9 — Triage and import

Edit tiers/placeholders in the draft if needed; then run your Xray import flow when ready (the skill itself does **not** import).

---

## Prompts (copy-paste)

### A — Minimal (Jira only)

Use when the Story/Epic is self-contained and you have no extra files.

```text
Follow the test-case-creation skill at AI in QA/Skills/test-case-creation/SKILL.md.

Parameters:
- scope: PROJ-12345
- golden_version: golden/v1
- comprehensive: true

Generate the testcase draft. Write the single output file under AI in QA/Skills/artifacts/ using the required filename pattern.
```

### B — Full (Jira + external files, URLs, optional review and Xray extract)

Use when you have PDFs, images, Confluence/design links, or exports the agent must read **in addition** to Jira.

```text
Follow the test-case-creation skill at AI in QA/Skills/test-case-creation/SKILL.md.

Parameters:
- scope: PROJ-12345
- jira_primary_key: PROJ-12345
- golden_version: golden/v1
- comprehensive: true
- force: false

external_context (user-supplied — load all before generating tests; notify me if any cannot be accessed):
  paths:
    - /Users/me/repo/DOCS/AI in QA/SPM-PRD - Feature overview.pdf
    - AI in QA/local-specs/PROJ-12345-acceptance-notes.md
    - AI in QA/mockups/checkout-empty-state.png
  urls:
    - https://confluence.example.com/display/PROJ/Checkout+redesign
    - https://www.figma.com/design/FILEKEY/Page-name

Optional session files (use if present):
- requirements_review_json: AI in QA/Skills/artifacts/my-run/requirements-review.json
- existing_xray_extract: AI in QA/Skills/artifacts/6113-extraction.json

Instructions:
1. Treat external_context paths and urls as first-class inputs alongside Jira; cite them in source_quotes or generation_notes where they drive a test.
2. After loading user files, still follow Jira remote links (Confluence, Figma, linked issues) per the skill; tell me clearly if any link or file fails.
3. Write exactly one output: AI in QA/Skills/artifacts/PROJ-12345 - testcase-draft.md (include JSON appendix). Do not run xray-import.
```

### C — Bundle on disk + external PDF

Use when requirements are normalized to a file, plus a PDF PRD.

```text
Follow the test-case-creation skill at AI in QA/Skills/test-case-creation/SKILL.md.

Parameters:
- scope: /Users/me/repo/DOCS/requirements/bundles/PROJ-12345.bundle.yaml
- golden_version: golden/v1
- comprehensive: true

external_context:
  paths:
    - /Users/me/repo/DOCS/requirements/refs/PROJ-12345-prd.pdf

Write AI in QA/Skills/artifacts/PROJ-12345 - testcase-draft.md per the skill (single file, full traceability, appendix JSON).
```

Replace paths and keys with your own. If a path contains spaces, keep quoting as shown or use your shell/workspace conventions; the agent should resolve paths inside the workspace root when relative.

---

## Troubleshooting

| Issue | What to do |
|--------|------------|
| Output filename wrong | Ensure `jira_primary_key` or bundle `work_item.jira_key` matches the Story/Epic you want on the file. |
| PDF/image not used | Check the **User-supplied external context** table in the output; fix path or permissions and rerun. |
| Gate BLOCKED | Supply `force: true` only after QA explicitly accepts risk; or fix CRITICAL findings and rerun review. |
| Import script needs `.json` | Copy the appendix `json` block from the Markdown into a temporary `.json` file and pass it to `xray_graphql_import.py --batch`. |

---

## Related files

| File | Purpose |
|------|---------|
| [`SKILL.md`](SKILL.md) | Full workflow (authoritative) |
| [`reference.md`](reference.md) | Tiers, roles, gate, markdown shape |
| [`examples.md`](examples.md) | Scenario examples |
| [`templates/README.md`](templates/README.md) | Input templates index |
| [`../README.md`](../README.md) | Skills hub for this repo |
