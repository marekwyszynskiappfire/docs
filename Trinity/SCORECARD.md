# Test case generator — scorecard

Pilot evidence template: acceptance, rejection reasons, and Xray traceability for leadership readouts.

**Related:** [`METRICS.md`](METRICS.md) (definitions) · program criteria live with **QA CoE** (Confluence / internal program docs — not in this git tree).

---

## Interim system of record (Google Sheet)

**BigQuery / Looker are deferred for pilot evidence.** Until we turn BQ back on, record each completed Trinity run in the shared scorecard:

**[Trinity Usage Scorecard](https://docs.google.com/spreadsheets/d/123L4BTTTrgghlLHni-vqCAEiJperj-pu1tDKuEyg6oo/edit?gid=0#gid=0)**

| Tab | Use |
|-----|-----|
| **BigPicture** | One **row per BigPicture run** (canonical columns below) |
| **Dashboard** | Rollups and Run A vs Run B comparison (driven by product tabs + `_Config`; do not hand-edit formulas unless you know the sheet) |
| **Example** | Extra fields worth capturing in notes or a future column (input JQL/keys, epic rejections, comment/question counts) |

**Run ID:** use the next free id on the product tab (e.g. `BP-106`). Keep ids stable once shared.

### BigPicture row — what to enter

| Sheet column | Store (per run) | Studio / local source |
|--------------|-----------------|------------------------|
| Run ID | `run_id` | Assign on sheet (e.g. `BP-106`) |
| QA User | Operator display name | `TRINITY_OPERATOR_NAME` or pipeline run owner |
| Product | `BigPicture` | Portfolio / handoff product |
| Use Case | `create` \| `review` \| `modify` | How the run was executed (Reviewer-only vs full Creator path) |
| Epics Rev. | Count | Statistics → epics reviewed |
| Epics Appr. | Approved for Creator / generation | Statistics → epics selected / approved |
| Epic Appr. % | Ratio | Sheet formula or `approved / reviewed` |
| TC Gen. | Generated | Creator batch + Studio rows |
| TC Appr. | Approved in Studio | `test_cases_approved` / statistics summary |
| TC Rej. | Rejected | `test_cases_rejected` |
| TC Appr. % | Ratio | `approved / (approved + rejected)` among decided |
| Sent XRay | Imported count | After Importer + **Record Xray keys** |
| TC Time (m) | Review phase minutes | Statistics phase timing (Creator review) |
| Total Time (m) | End-to-end minutes | Statistics overall duration |
| Coverage Depth | e.g. Comprehensive | Creator `suite_mode` / policy label |

### How rows get onto the sheet (for now)

**Default:** copy the **[Cursor prompt](pilot-scorecard-cursor-prompt.md)** into a new chat after each run. Studio supplies the numbers; Cursor (Google Drive) writes the sheet row.

1. Studio → **Statistics** → **Download export JSON** (or copy summary from the page).
2. Open [`pilot-scorecard-cursor-prompt.md`](pilot-scorecard-cursor-prompt.md), copy the fenced block, fill in `pipeline run` + **RUN DATA**, paste into Cursor.
3. Agent appends one row on the product tab (usually **BigPicture**). Dashboard rollups update from the tab.

Optional later: Studio **Push to scorecard** when `TRINITY_SCORECARD_CREDENTIALS` is configured — not part of the default workflow.

BigQuery setup remains documented in [`BIGQUERY.md`](BIGQUERY.md) for later; it is **not** required to fill the scorecard today.

---

Copy the **Template** table below for Confluence one-offs or git notes. Attach telemetry JSON when you share evidence (not committed — see below).

---

## Live numbers from Studio

```bash
curl -s http://127.0.0.1:8765/api/telemetry/summary | jq .
./Trinity/scripts/export-telemetry.sh trinity-telemetry-export.json
# Per pipeline run (readiness, phases, compare): Statistics → Download export JSON
# or: curl -s "http://127.0.0.1:8765/api/runs/<pipeline_run_id>/statistics/export"
```

Include **`trinity_version`** from `/api/health` or `Trinity/VERSION` on each filled scorecard.

After Xray execute: workspace → **Record Xray keys** (or `POST /api/importer/record-results`) so `xray_test_key` appears on the Creator run.

---

## Template (copy per pilot)

| Field | Value |
|-------|--------|
| **Trinity version** | e.g. `0.3.0` |
| **Use case** | |
| **Product / solution** | Trinity (Reviewer + Creator + Studio + Importer); skills `trinity-reviewer`, `trinity-creator`, `trinity-importer` |
| **Who used it** | Operator + reviewers (names) |
| **Input** | Jira key(s), review run id, requirement summary |
| **Output** | # generated, # approved, # rejected, Xray keys (if imported) |
| **Human review** | Who reviewed, Studio approve/reject, material edits |
| **Accepted** | Count or list exported to Importer |
| **Rejected** | Count + top reasons from [`METRICS.md`](METRICS.md) enum |
| **Impact** | Time vs manual; quality notes; optional [`CURSOR-COST.md`](CURSOR-COST.md) |
| **Decision** | `Scale`, `Adjust`, or `Stop`. Do not infer it from volume |

**Acceptance rate:** `approved / (approved + rejected)` after review (exclude pending).

**Date / environment:** PROD Jira · project key · Xray folder path.

---

## Example — ONE-228469 (production import)

| Field | Value |
|-------|--------|
| **Trinity version** | **0.2.0** (`trinity-v0.2.0`) |
| **Use case** | AI-assisted manual test cases for custom fields (part 2); import to Xray |
| **Product / solution** | Trinity; mapping `appfire-production.json`; Importer GraphQL create |
| **Who used it** | Pilot operator; QA review in Studio |
| **Input** | ONE-228469; Creator handoff from Reviewer-approved context |
| **Output** | 5 tests → **TC-6704, TC-6705, TC-6706, TC-6707, TC-6708** |
| **Human review** | Validation fixes (`coverage_catalog_id`, `Generic`→`Manual`, field mapping) before import |
| **Accepted** | 5/5 after plan corrections |
| **Rejected** | N/A (validation caught issues before post-review reject) |
| **Impact** | **Time:** ~4–8h manual test design → ~2–4h with Trinity (estimate). **Quality:** Reviewer findings + human approve in Studio before Xray. **Cost:** Cursor trackable in Studio; no formal baseline study in POC. |
| **Decision** | **Adjust.** One accepted production import. A second product, a second operator, and a measured baseline are still open. |

For runs that use Studio **bulk reject**, copy `rejection_reasons` from telemetry summary into **Rejected**.

---

## Pilot log (fill in)

| Pilot | Jira key / scope | Date | Acceptance rate | Telemetry export file | Shared |
|-------|------------------|------|-----------------|----------------------|--------|
| 1 | **ONE-228469** → TC-6704–6708 | **2026-10-13** | **5/5** Xray import; Studio **14 approved / 0 rejected** (25 rows incl. 11 pending) → **100%** among decided | `scorecard-exports/2026-10-13-pilot1-telemetry.json` | ☑ reveal.js [`presentations/mateusz-pilot1-2026-10-13.html`](presentations/mateusz-pilot1-2026-10-13.html) |
| 2 | **Planned:** BigPicture, TimeTracker, Core Apps, Rich Filters; *stretch:* CMJ | — | — | — | ☐ |
| 3 | | | | | ☐ |

---

## Checklist before sharing

- [x] `./Trinity/scripts/export-telemetry.sh` → `scorecard-exports/2026-10-13-pilot1-telemetry.json` (2026-10-13)
- [ ] Screenshot or link to Xray folder (add URL in chat / Confluence when ready)
- [ ] Reviewer readiness noted if `review_ref` linked
- [x] Presentation: [`presentations/mateusz-pilot1-2026-10-13.html`](presentations/mateusz-pilot1-2026-10-13.html)
- [x] Honest limits documented — [`FAQ.md`](FAQ.md), [`MANUAL.md`](MANUAL.md)

---

## Where files live

| What | In git? |
|------|---------|
| This template + ONE-228469 example | **Yes** — `Trinity/SCORECARD.md` |
| Per-pilot telemetry JSON exports | **No** — local or Confluence attachment (may contain operator email in summary) |
| Filled scorecard copies for pilots 2+ | **Your choice** — edit tables above in git, or duplicate to Confluence/Slides |

Older filename `SCORECARD-TC-GENERATOR.md` was removed during the runtime-only repo trim; use this file instead.
