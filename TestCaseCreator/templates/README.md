# test-case-creation — input templates and samples

Session inputs for [SKILL.md](../SKILL.md) are intentionally few. Each **optional** row below has a **template or sample** in this folder or elsewhere in the repo (paths are from the workspace root unless noted).

| Input | Mandatory? | Template or sample |
|-------|------------|-------------------|
| Requirement source (Jira key, JQL, or bundle file) | **Yes** | Bundle shape: [`requirements-template.md`](../requirements-template.md) (normative YAML example inside) |
| Requirements review (gate) | No — **highly encouraged** before generation | [`requirements-review.sample.json`](requirements-review.sample.json) |
| External context (paths + URLs) | No | [`external-context.sample.md`](external-context.sample.md) |
| Xray extract (depth / dedupe) | No | [`xray-extract.sample.md`](xray-extract.sample.md) |
| Domain coverage catalog | No | [`../coverage-catalog.md`](../coverage-catalog.md) (reference catalog for one domain only) |

**Operator guide:** [../README.md](../README.md) (step-by-step + copy-paste prompts).

**Repository assets (not session files):** the agent also loads style and shape from `TestCaseCreator/golden/v1/style-rules.md`, `TestCaseCreator/golden/v1/examples/`, and `TestCaseCreator/schemas/TestCaseDraft.schema.json` — you do not supply these as inputs.

**Output (single file):** `TestCaseCreator/artifacts/{JIRA-KEY} - testcase-draft.md` — see SKILL.md §9.
