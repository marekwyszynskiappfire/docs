# Trinity pipeline (operator view)

End-to-end flow from portfolio planning through test-case prep.

**New operators:** [Start here](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754590489/Trinity+Start+here) · [`FAQ.md`](FAQ.md)  
**Checkout → operational:** [`OPERATOR-SETUP.md`](OPERATOR-SETUP.md) · **Wiki map:** [`confluence/README.md`](confluence/README.md) · **SVG:** [`confluence/assets/trinity-operator-pipeline.svg`](confluence/assets/trinity-operator-pipeline.svg)

**Manual:** [`MANUAL.md`](MANUAL.md) (full operator guide). Contracts: [`CONTRACTS.md`](CONTRACTS.md).

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

1. **Persona** — edit `Trinity/personas/reviewer-expert-qa-automation.md` (Studio → **Personas**) if needed; audience map: [`personas/P1-P10.md`](personas/P1-P10.md).
2. **Portfolio run config** — **More → Reviewer configs** (or interview in Cursor). Saves `Trinity/reviewer/config/runs/{portfolio_id}.json`.
3. **Copy Cursor prompt** from Studio → paste into Cursor → run **trinity-reviewer**.

Outputs land under `Trinity/reviewer/runs/{portfolio_run_id}/` (per-epic payloads + optional `portfolio/index.html`).

## 2. Import into Studio

```bash
./Trinity/studio/scripts/import-run.sh Trinity/reviewer/runs/<folder-that-directly-contains-EPIC-KEY>
```

A finished Reviewer opens the workspace. `import-run.sh` is the fallback, then **Open workspace** on that run. For portfolio metrics, use top nav **Statistics** ([`METRICS.md`](METRICS.md)).

## 3. Human QA on reviews

The workspace is the normal path: read the verdict, approve the review, copy the Creator prompt.

- **Run page** — toggle **In Creator** per epic; bulk exclude `not_fit`; copy **Creator JQL** and handoff JSON.
- **Unit page** — edit `review-payload.json` fields, QA workflow, Jira epic comment. **Save draft** before a comment preview.
- **Export** — approved `review-payload.json` under `Trinity/studio/data/exports/`.

## 4. Creator (test cases)

1. On the workspace, approve the review, then **Copy Creator prompt** (prompt includes `review_ref` + three Creator personas). Several Epics: **Prepare Creator prompts**, then copy them together.
2. Run **trinity-creator** in Cursor — **3–5 e2e journey** scenarios per Epic (CR-EPIC-01); golden style from `Trinity/creator/config/<product>.json` → `golden_root`.
3. The workspace imports `suite-payload.json` (**one file per Epic** — no merged portfolio file). Multi-epic programs write under `Trinity/creator/artifacts/{portfolio_id}/{EPIC_KEY}/suite-payload.json`; see [`creator/artifacts/README.md`](creator/artifacts/README.md). **More → Creator** is the fallback.
4. Operator: edit → approve or reject; mark **Send to Xray**. **Approve selected** covers the tests you ticked. **More → Creator → Export for Importer** still writes `studio/data/exports/creator/{run}/importer-payload.json`.
5. On the workspace: instance, mapping, **[project key override](GUIDE.md#6-importer-studio--xray)** (default TC), folder → **Preview import plan** → **Write to Xray**. Several Epics can be previewed together; the write stays one Epic. The full Importer page remains for a Cursor prompt ([`GUIDE.md` §6](GUIDE.md#6-importer-studio--xray)).

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

**Evidence:** per-run export via Statistics → **Download export JSON**; acceptance telemetry via [`export-telemetry.sh`](scripts/export-telemetry.sh) ([`SCORECARD.md`](SCORECARD.md)).
