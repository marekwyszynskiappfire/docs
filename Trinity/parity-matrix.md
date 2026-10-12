# Trinity Studio vs Reviewer HTML (parity matrix)

**Status:** Phase 1 — Reviewer epic view + Creator run; track gaps for **P2 leads** (see [GRILL-SESSION-2026-10-12.md](GRILL-SESSION-2026-10-12.md) G6).

| Reviewer HTML section | Trinity Studio epic view | Notes |
|----------------------|---------------------------|--------|
| Data sources (`context_loaded`) | Yes — Data sources panel | |
| Information identified / Not stated / Risks / Testing focus | Yes — report detail panels | |
| Gate / readiness | Yes — summary + gate/fit chips on epic table (UI round 2) | |
| Clarification questions + Why / Source | Yes | |
| Findings + testing impact / quote | Yes | |
| QA review (valid / do not ask / discuss) | Yes — `studio_qa` | |
| Child inventory & status mix | **Gap** | RQ-02 |
| Classifications banner | **Gap** | RQ-02 |
| QA readiness checklist | **Gap** | |
| Link to per-epic `review-report.html` | **Gap** | Open static report alongside Studio |
| Portfolio index link | **Gap** (run-level) | PQ-01 related |

| Creator / Importer capability | Studio | Offline HTML / CLI |
|------------------------------|--------|---------------------|
| Coverage matrix (architect) | Yes — Creator run (`IQ-11`) | Batch JSON only |
| Profile B suite report | Export API + template (`IQ-13`) | `build_suite_report.py` |
| Importer plan + execute | Yes (`IQ-10`) | `xray_graphql_import.py` |
| Idempotency when `xray_test_key` set | Warn in plan (`importer_idempotency`) | Post-POC: block/skip |

HTML source of truth: [`reviewer/scripts/render_report.py`](reviewer/scripts/render_report.py).
