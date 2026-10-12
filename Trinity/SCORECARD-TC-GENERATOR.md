# Test case generator — scorecard

One-pager template for Mateusz §2 evidence. Copy **Template** for each pilot; see **Example** (ONE-228469).

Export live numbers: `curl -s http://127.0.0.1:8765/api/telemetry/export` (after Studio runs on that machine).

After Xray execute, use Importer → **Persist Xray keys** (or `POST /api/importer/record-results`) so `xray_test_key` appears on the Creator run.

---

## Template

| Field | Value |
|-------|--------|
| **Use case** | |
| **Product / solution** | Trinity (Reviewer + Creator + Studio + Importer); Cursor skills `trinity-reviewer`, `trinity-creator`, `trinity-importer` |
| **Who used it** | |
| **Input** | Jira key(s), review run path, requirement summary |
| **Output** | # tests generated, # approved, # rejected, Xray keys (if imported) |
| **Human review** | Who reviewed, Studio approve/reject, edits made |
| **Accepted** | List or count of approved / exported tests |
| **Rejected** | Count + top rejection reasons from [METRICS.md](METRICS.md) enum |
| **Impact** | Time saved/spent vs manual; quality notes; cost (if any) |

**Acceptance rate:** `approved / (approved + rejected)` after review (exclude pending).

**Date / environment:** PROD Jira / TC project / folder path.

---

## Example — ONE-228469 (production import)

| Field | Value |
|-------|--------|
| **Use case** | AI-assisted manual test cases for custom fields (part 2); import to Xray for execution |
| **Product / solution** | Trinity pipeline; production mapping `appfire-production.json`; Importer GraphQL create |
| **Who used it** | Marek Wyszyński (operator); QA review in Studio |
| **Input** | ONE-228469; Creator handoff from Reviewer-approved context |
| **Output** | 5 tests planned; 5 created in Xray: TC-6704, TC-6705, TC-6706, TC-6707, TC-6708 |
| **Human review** | Validation fixes (`coverage_catalog_id`, `Generic`→`Manual`, Automated field mapping) before successful import |
| **Accepted** | 5/5 imported after plan corrections |
| **Rejected** | N/A (pre-import validation caught issues, not post-review reject) |
| **Impact** | First prod E2E proved path; iteration on mapping/validation reduced repeat failures |

*Note:* Fill rejection-reason metrics from Studio for runs that use bulk reject after Creator import.

---

## Checklist before sharing scorecard

- [ ] Telemetry export saved (`trinity-telemetry-export.json`)
- [ ] Screenshot or link to Xray folder
- [ ] Reviewer readiness noted (if `review_ref` linked)
- [ ] Limitations from [POC-TC-GENERATOR.md §9](POC-TC-GENERATOR.md#9-known-limitations-honest-poc) acknowledged if presenting to leadership
