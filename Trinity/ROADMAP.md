# Trinity — roadmap (what’s left)

**Last updated:** 2026-10-13  
**Audience:** QA lead, engineering, pilot stakeholders  
**Tracking:** GitHub Issues on `marekwyszynskiappfire/docs` ([`docs/agents/issue-tracker.md`](../docs/agents/issue-tracker.md)) · issue templates in [`GITHUB-BACKLOG.md`](GITHUB-BACKLOG.md)

This document is the **single “yet to be done” view**. Operator how-to is [`OPERATOR-SETUP.md`](OPERATOR-SETUP.md); post-P2 sequencing is [`NEXT-STEPS.md`](NEXT-STEPS.md).

---

## Recently shipped (baseline for “remaining”)

| Area | Delivered (on `main`) |
|------|------------------------|
| **Studio core** | Reviewer import, unit QA (`studio_qa`), Creator triage, Importer plan/execute, telemetry, cursor cost, portfolio rollup |
| **Studio structure** | FastAPI routers; thin `app.py`; pytest + Vitest smoke |
| **Jira epic comments (MVP)** | Preview/post/history API, unit page panel, production gate, redaction blockers, `metric_event` hooks |
| **Demo / safety** | `DEMO-4500` fixture; epic folder ↔ payload key validation on import |
| **CQ-02 (Studio)** | Coverage summary warns when `coverage_catalog_id` ∉ `linked_ac_ids` |
| **Operator docs** | [`OPERATOR-SETUP.md`](OPERATOR-SETUP.md), [`confluence/`](confluence/) page pack + SVG |

Treat everything below as **not done** unless marked *partial*.

---

## Now — pilot blockers & production hardening (P0)

| # | Work | Why it matters | Ref |
|---|------|----------------|-----|
| P0-1 | **Human pilot sign-off** | Scorecard, slides, one documented real run (staging/prod) | [`SCORECARD-TC-GENERATOR.md`](SCORECARD-TC-GENERATOR.md), [`NEXT-STEPS.md`](NEXT-STEPS.md) §4 |
| P0-2 | **BigQuery telemetry ingest + dashboard** | Central evidence for acceptance rate, reject reasons, Jira post events | `METRICS.md`, ADR 0002; blocked on GCP creds |
| P0-3 | **Importer: hard-block redaction on execute** | *Shipped in Studio* — `importer_execute_guard`; override `STUDIO_IMPORTER_ALLOW_REDACTION_EXECUTE=1` | [`GITHUB-BACKLOG.md`](GITHUB-BACKLOG.md) P0 |
| P0-4 | **Importer: idempotency on duplicate Xray keys** | *Shipped in Studio* — block until `idempotency_acknowledged` on plan/execute | Grill Q4 |

---

## Next — product gaps (P1)

| # | Work | Status | Notes |
|---|------|--------|-------|
| P1-1 | **Jira epic comments — Phase 0/2 polish** | *MVP done* | ADF/wiki spike on Appfire Cloud; 24h duplicate-post warn; `preview_edited` on preview telemetry; mock Jira pytest; update [`GUIDE.md`](GUIDE.md) “send back to epic” |
| P1-2 | **Jira epic comments — Phase 3** | Open | Batch post per run; MCP “post this comment” export; store Jira comment id in `studio_qa` |
| P1-3 | **QA readiness checklist panel (R5)** | Open | In-Studio checklist vs Profile A HTML link only |
| P1-4 | **`automation_fit` → Xray Automated field** | Open | TQ-02 on Importer execute |
| P1-5 | **`test_data_isolation` enforcement** | *Warn today* | Schema + Studio display; block or gate Creator handoff |
| P1-6 | **Reviewer export: environment/tenant metadata** | Open | RQ-02 multi-tenant analytics |
| P1-7 | **Parity matrix + ADR** | Open | Studio vs Reviewer HTML; gap issues per row [`parity-matrix.md`](parity-matrix.md) |

---

## Soon — engineering & ops (P2)

| # | Work | Notes |
|---|------|-------|
| P2-1 | **GitHub Actions CI** | Wire [`.github/workflows/trinity-studio-ci.yml`](../.github/workflows/trinity-studio-ci.yml) on every PR touching `Trinity/studio/` |
| P2-2 | **Confluence publish** | Markdown pack exists — create space pages, attach SVG, external-sharing review [`confluence/README.md`](confluence/README.md) |
| P2-3 | **Wall-clock timing metrics** | Import → approve → Xray persist durations |
| P2-4 | **Context-loaded alerts at scale** | SQL filter / index vs full scan on dashboard |
| P2-5 | **Single Studio UI** | Deprecate duplicate static editor; React on 5173/8765 only |
| P2-6 | **Repo hygiene for external readers** | Sanitized demo portfolio only; root hub README; gitignore/security pass |
| P2-7 | **Release v0.1.0** | Tag + changelog after pilot sign-off |
| P2-8 | **Second product pilot** | Mapping + scorecard comparison [`FAQ.md`](FAQ.md) |

---

## Later — quality of life (P3)

| # | Work |
|---|------|
| P3-1 | ESLint + Prettier for `studio/web` |
| P3-2 | RTL component tests (Importer plan, bulk approve, Jira panel) |
| P3-3 | Studio auth + path allowlist if exposed beyond localhost |
| P3-4 | Further router module splits (creator/importer ~300+ lines) |
| P3-5 | Neutral rename `mateusz_summary` telemetry field (ADR for compat) |
| P3-6 | Studio UI polish (empty states, risk badges, optional motion) — [`NEXT-STEPS.md`](NEXT-STEPS.md) §3 |

---

## Documentation debt (cross-cutting)

| Task | Status |
|------|--------|
| Linear operator setup + Confluence pack | **Done in git** — wiki publish **not done** |
| Deduplicate Importer steps across TESTING / PIPELINE / MANUAL | Partial — prefer links to [`GUIDE.md`](GUIDE.md) §6 |
| `parity-matrix.md` populated + linked from scorecard | Open |
| `install-trinity-skills.sh` + preflight one-liner in AGENTS / AI-in-QA docs | Open |
| Chaptered operator video + link from README | Open |
| Refresh [`GITHUB-BACKLOG.md`](GITHUB-BACKLOG.md) “Done” row for Jira epic comments MVP | Maintainer |

---

## Suggested sequencing (quarters)

```text
Pilot quarter
  ├── P0-1 sign-off artifacts (human)
  ├── P1-1 Jira comment ADF/wiki + sandbox Epic post proof
  ├── P2-2 Confluence external pack
  └── P2-1 CI on Studio

Hardening quarter
  ├── P0-2 telemetry dashboard
  ├── P0-3 / P0-4 Importer safety
  └── P1-4 / P1-5 Creator–Importer field enforcement

Scale quarter
  ├── P1-7 parity matrix closed or accepted
  ├── P2-5 single UI
  └── P2-8 second product pilot
```

---

## How to update this roadmap

1. When a item ships on `main`, move it to **Recently shipped** and strike from tables (or mark *done*).
2. Create or close GitHub Issues via [`GITHUB-BACKLOG.md`](GITHUB-BACKLOG.md) / `create_github_backlog.sh`.
3. Jira comment detail: [`studio/JIRA-EPIC-COMMENTS-OUTLINE.md`](studio/JIRA-EPIC-COMMENTS-OUTLINE.md) phases 0–3.
4. Studio-only debt: [`studio/CODE-HEALTH.md`](studio/CODE-HEALTH.md).

---

## Related

| Doc | Role |
|-----|------|
| [`NEXT-STEPS.md`](NEXT-STEPS.md) | Post-P2 pilot focus (no new product unless bug) |
| [`GITHUB-BACKLOG.md`](GITHUB-BACKLOG.md) | Issue titles for `gh issue create` |
| [`REVIEW-PRODUCT-AND-DOCS.md`](REVIEW-PRODUCT-AND-DOCS.md) | Open RQ/CQ/TQ product questions |
