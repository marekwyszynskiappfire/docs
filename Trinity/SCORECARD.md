# Test case generator — scorecard

Mateusz §2 one-pager: pilot evidence for leadership (acceptance, rejection reasons, Xray traceability).

**Traceability:** [`MATEUSZ-CRITERIA.md`](MATEUSZ-CRITERIA.md) · **Requirements (PL):** [`Mateusz.MD`](Mateusz.MD)

Copy the **Template** table for each new pilot. Keep **Example** as the reference prod run. Attach telemetry JSON when you share the scorecard (not committed — see below).

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

**Acceptance rate:** `approved / (approved + rejected)` after review (exclude pending).

**Date / environment:** PROD Jira · project key · Xray folder path.

---

## Example — ONE-228469 (production import)

| Field | Value |
|-------|--------|
| **Trinity version** | **0.2.0** (`trinity-v0.2.0`) |
| **Use case** | AI-assisted manual test cases for custom fields (part 2); import to Xray |
| **Product / solution** | Trinity; mapping `appfire-production.json`; Importer GraphQL create |
| **Who used it** | Marek Wyszyński (operator); QA review in Studio |
| **Input** | ONE-228469; Creator handoff from Reviewer-approved context |
| **Output** | 5 tests → **TC-6704, TC-6705, TC-6706, TC-6707, TC-6708** |
| **Human review** | Validation fixes (`coverage_catalog_id`, `Generic`→`Manual`, field mapping) before import |
| **Accepted** | 5/5 after plan corrections |
| **Rejected** | N/A (validation caught issues before post-review reject) |
| **Impact** | **Time:** ~4–8h manual test design → ~2–4h with Trinity (estimate). **Quality:** Reviewer findings + human approve in Studio before Xray. **Cost:** Cursor trackable in Studio; no formal baseline study in POC. |

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
