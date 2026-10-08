# Trinity pipeline (operator view)

End-to-end flow from portfolio planning through test-case prep. Details: [`MANUAL.md`](MANUAL.md), [`CONTRACTS.md`](CONTRACTS.md).

```mermaid
flowchart LR
  config[Reviewer config JSON]
  cursor[Cursor trinity-reviewer]
  runs[reviewer/runs folder]
  studio[Trinity Studio]
  creator[trinity-creator]
  importer[Importer dry-run + execute roadmap]

  config --> cursor
  cursor --> runs
  runs --> studio
  studio --> creator
  creator --> importer
```

## 1. Configure the program

1. **Persona** — edit `Trinity/personas/reviewer-expert-qa-automation.md` (Studio → **Personas**) if needed.
2. **Portfolio run config** — Studio → **Reviewer configs** (or interview in Cursor). Saves `Trinity/reviewer/config/runs/{portfolio_id}.json`.
3. **Copy Cursor prompt** from Studio → paste into Cursor → run **trinity-reviewer**.

Outputs land under `Trinity/reviewer/runs/{portfolio_run_id}/` (per-epic payloads + optional `portfolio/index.html`).

## 2. Import into Studio

```bash
./Trinity/studio/scripts/import-run.sh Trinity/reviewer/runs/<portfolio-run-folder>
```

Dashboard lists the pipeline run. Open the run to review epics.

## 3. Human QA on reviews

- **Run page** — toggle **In Creator** per epic; bulk exclude `not_fit`; copy **Creator JQL** and handoff JSON.
- **Unit page** — edit `review-payload.json` fields, QA workflow, approve revision.
- **Export** — approved `review-payload.json` under `Trinity/studio/data/exports/`.

## 4. Creator (test cases)

1. In Studio, open the epic unit → **Approve & export** → **Send to Creator** (prompt includes `review_ref` + three Creator personas).
2. Run **trinity-creator** in Cursor — **3–5 e2e journey** scenarios per Epic (CR-EPIC-01); golden style from `Trinity/creator/config/<product>.json` → `golden_root`.
3. Import `suite-payload.json` in Studio → **Creator**.
4. Operator: edit → approve or reject; mark **fit for Xray import**; **Export for Importer** → `studio/data/exports/creator/{run}/importer-payload.json`.
5. **Importer** (Studio): choose **production vs sandbox** Jira, mapping config, Test Repository **folder** (+ optional **create folder**); **Preview import plan**; Execute to Xray (batch submit next).

Each draft includes `automation_fit`, `automation_blockers`, and `persona_notes` (QA / architect / automation).

Blocked in Studio when `qa_planning_fit` is **not_fit**.

## 5. Pass types and deltas

| `pass_type` | Meaning |
|-------------|---------|
| `full_sweep` | Full gather + checklist |
| `rescan_delta` | Compare to prior payload when fingerprint matches |
| `new_epics_only` | Only epics without `review-payload.json` (uses `resolved_epic_keys` or inline `epic_keys`) |

For **JQL** scopes: resolve epics in Cursor → paste keys in Studio → then run Reviewer with `source_jql` = `scope.value`.

---

**Scope resolve:** JQL/filter → **Copy JQL resolve prompt** (Cursor MCP) or optional `JIRA_*` in `Trinity/studio/.env` for **Resolve from scope**.

**Next (round 10):** git commit / PR for Trinity changes; then Creator suite HTML or demo portfolio polish.
