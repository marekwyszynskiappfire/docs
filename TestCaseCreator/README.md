# TestCaseCreator

Self-contained **Agent Skill** package for generating structured manual test drafts from Jira (or requirement bundles), optional review gates, external PDFs/images/URLs, and optional Xray depth references.

**Normative workflow:** [`SKILL.md`](SKILL.md) (Cursor / Composer: “Follow `TestCaseCreator/SKILL.md`” from the repo root, or point to this file if `TestCaseCreator` is the project root).

---

## Repository layout (this folder)

| Path | Purpose |
|------|---------|
| [`SKILL.md`](SKILL.md) | Skill definition (authoritative) |
| [`reference.md`](reference.md) | Tiers, roles, gate, markdown output shape |
| [`examples.md`](examples.md) | Scenario examples |
| [`coverage-catalog.md`](coverage-catalog.md) | Optional domain checklist (use only when applicable) |
| [`requirements-template.md`](requirements-template.md) | Requirement bundle shape + YAML example |
| [`schemas/TestCaseDraft.schema.json`](schemas/TestCaseDraft.schema.json) | JSON schema for the appendix batch |
| [`golden/v1/style-rules.md`](golden/v1/style-rules.md) | Writing style rules |
| [`golden/v1/examples/`](golden/v1/examples/) | Golden journey + atomic pattern examples |
| [`templates/`](templates/) | Sample inputs (`requirements-review`, `external_context`, Xray extract notes) |
| [`artifacts/`](artifacts/) | **Output directory** — drafts are written here (only `.{JIRA-KEY} - testcase-draft.md` + your own extracts if you add them) |

Paths like `TestCaseCreator/artifacts/...` in `SKILL.md` assume this directory lives at **`TestCaseCreator/` under your git repository root** (e.g. `DOCS/TestCaseCreator/`). If you lift these files to become the **root** of a new repo, replace the prefix `TestCaseCreator/` with `./` (or your chosen subfolder) in `SKILL.md` and in the prompts below.

---

## Cursor / Composer setup

1. Clone or copy this repo so `TestCaseCreator/` is available on disk.
2. In Cursor, open the **parent** repository as the workspace (so paths `TestCaseCreator/...` resolve), **or** open only this folder and adjust paths as above.
3. Optional: copy `SKILL.md` (or the whole folder) into `.cursor/skills/test-case-creation/` per your team’s convention.

---

## What you get

- **One output file:** `TestCaseCreator/artifacts/{JIRA-KEY} - testcase-draft.md`  
  Full suite, requirement ↔ test traceability, coverage tables, and a **JSON appendix** for tooling.
- **Rules:** assessment-first suite size, **≤15 steps** per test, P0–P3 tiers, optional domain catalog or run-scoped `CAT-*` checklist.

## Inputs (mandatory vs optional)

| Input | Required? | Notes |
|-------|-------------|--------|
| **Requirement source** | **Yes** | Jira Epic/Story key (or JQL scope), **or** a normalized bundle file per [`requirements-template.md`](requirements-template.md). The `{JIRA-KEY}` in the output filename comes from the primary work item. |
| **Requirements review JSON** | No — **strongly recommended** | Optional gate file; generation still allowed without it. Sample: [`templates/requirements-review.sample.json`](templates/requirements-review.sample.json). |
| **External context** | No | Workspace paths and/or URLs (PDFs, Confluence, images, exports). See [`templates/external-context.sample.md`](templates/external-context.sample.md). |
| **Xray extract** | No | Depth / dedupe reference. See [`templates/xray-extract.sample.md`](templates/xray-extract.sample.md). |
| **Domain coverage catalog** | No | Only if the feature matches that domain: [`coverage-catalog.md`](coverage-catalog.md). |

The agent also loads **style/schema assets** from this folder (`golden/v1/`, `schemas/`) — you do not pass those as session parameters.

---

## Step-by-step (full run)

### Step 1 — Open the workspace

Open the git repository that contains **`TestCaseCreator/`** (or this folder alone, after path adjustments). The agent needs read access to every **local path** you list under `external_context`.

### Step 2 — Gather the requirement anchor

- **Jira:** Epic or Story key (e.g. `PROJ-12345`) and MCP / API access as needed.  
- **Bundle:** YAML/MD file on disk with `work_item.jira_key` set for filename + schema traceability.

### Step 3 — (Recommended) Requirements review

Run your `requirements-review` flow first, or attach `requirements-review.json`. Improves AC quality; **not** mandatory to start test generation.

### Step 4 — Optional external files and URLs

Place PDFs, images, extra markdown, etc. where the agent can read them; list paths and URLs in the prompt (see **Prompts**).

### Step 5 — Optional Xray extract / domain catalog

Attach paths only if you use them.

### Step 6 — Paste a prompt from below

Adjust keys and paths.

### Step 7 — Agent execution

The agent follows `SKILL.md`: load requirements → `external_context` → Jira-embedded links → optional gate → plan → tests → write **`TestCaseCreator/artifacts/{JIRA-KEY} - testcase-draft.md`**.

### Step 8 — Review output

Check traceability tables, linked-context tables, and the JSON appendix.

### Step 9 — Triage / import

Edit if needed; use your Xray import pipeline (skill does **not** import).

---

## Prompts (copy-paste)

### A — Minimal (Jira only)

```text
Follow the skill in TestCaseCreator/SKILL.md (repo root: path …/TestCaseCreator/SKILL.md).

Parameters:
- scope: PROJ-12345
- golden_version: golden/v1
- comprehensive: true

Generate the testcase draft. Write the single output file under TestCaseCreator/artifacts/ using the required filename pattern.
```

### B — Full (Jira + external files + optional review / Xray)

```text
Follow the skill in TestCaseCreator/SKILL.md.

Parameters:
- scope: PROJ-12345
- jira_primary_key: PROJ-12345
- golden_version: golden/v1
- comprehensive: true
- force: false

external_context (load all before tests; notify me if anything fails):
  paths:
    - TestCaseCreator/specs/PROJ-12345-prd.pdf
    - TestCaseCreator/mockups/error-state.png
  urls:
    - https://confluence.example.com/display/PROJ/Checkout+redesign
    - https://www.figma.com/design/FILEKEY/Page-name

Optional:
- requirements_review_json: path/to/requirements-review.json
- existing_xray_extract: path/to/xray-extract.json

Write exactly one file: TestCaseCreator/artifacts/PROJ-12345 - testcase-draft.md (include JSON appendix). Do not run xray-import.
```

### C — Bundle + PDF

```text
Follow the skill in TestCaseCreator/SKILL.md.

Parameters:
- scope: /absolute/path/to/PROJ-12345.bundle.yaml
- golden_version: golden/v1
- comprehensive: true

external_context:
  paths:
    - TestCaseCreator/specs/PROJ-12345-prd.pdf

Write TestCaseCreator/artifacts/PROJ-12345 - testcase-draft.md per the skill.
```

---

## Troubleshooting

| Issue | What to do |
|--------|------------|
| Wrong output name | Set `jira_primary_key` or bundle `work_item.jira_key` to the intended issue. |
| Asset not found | Paths in `SKILL.md` use `TestCaseCreator/` from the **repo root**; fix prefix if your layout differs. |
| Gate BLOCKED | Use `force: true` only with explicit QA acceptance, or fix CRITICAL review items. |
| Need raw JSON | Copy the appendix `json` block from the `.md` into a `.json` file for import scripts. |

---

## Related

| File | Purpose |
|------|---------|
| [`SKILL.md`](SKILL.md) | Full workflow |
| [`reference.md`](reference.md) | Reference tables |
| [`examples.md`](examples.md) | Examples |
| [`templates/README.md`](templates/README.md) | Template index |

If this package still lives inside the original **DOCS** monorepo, the upstream skills hub is `AI in QA/Skills/README.md` (optional).
