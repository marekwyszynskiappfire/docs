# Trinity — GitHub backlog (post-release)

Create issues on **`marekwyszynskiappfire/docs`** so pilot evidence stays in scorecard/docs and engineering debt is tracked in the issue tracker ([`docs/agents/issue-tracker.md`](../docs/agents/issue-tracker.md)).

```bash
cd /path/to/DOCS
./Trinity/scripts/create_github_backlog.sh          # dry-run
./Trinity/scripts/create_github_backlog.sh --create # creates issues
```

Or create manually from the table below.

**Labels to add once:** `trinity`, `post-poc`, `studio`, `importer`, `telemetry`, `docs`

---

## Priority P0 — Production safety (post-release unless noted)

| Title | Body summary | Labels |
|-------|----------------|--------|
| **Trinity: BigQuery telemetry ingest + Looker Studio** | Wire `TRINITY_TELEMETRY_URL`; document dataset schema; dashboard for acceptance rate + rejection reasons. Blocked on GCP credentials. Ref: METRICS.md, ADR 0002. | `trinity`, `telemetry`, `post-poc` |
| ~~Trinity: Hard block redaction on Importer execute~~ | *Shipped* — `importer_execute_guard`; override `STUDIO_IMPORTER_ALLOW_REDACTION_EXECUTE=1`. | — |
| ~~Trinity: Idempotency block/skip duplicate Xray keys~~ | *Shipped* — block until `idempotency_acknowledged` on plan/execute + UI checkbox. | — |

---

## Priority P1 — Product gaps (REVIEW / grill)

| Title | Body summary | Labels |
|-------|----------------|--------|
| **Trinity Studio: QA readiness checklist panel** | Grill R5 deferred; Profile A HTML link covers pilot. parity-matrix.md | `trinity`, `studio` |
| **Trinity Studio: Jira epic comments — polish & ADF** | MVP shipped (preview/post/history). Remaining: Phase 0 ADF/wiki, duplicate-post warn, batch post, GUIDE update. Spec: [`studio/JIRA-EPIC-COMMENTS-OUTLINE.md`](studio/JIRA-EPIC-COMMENTS-OUTLINE.md). | `trinity`, `studio`, `post-poc` |
| **Trinity: Map automation_fit to Xray Automated field** | TQ-02 deferred at release; per-test Jira fields on execute. importer/reference.md | `trinity`, `importer` |
| **Trinity Creator: test_data_isolation config enforcement** | PQ-03: warn today; optional schema + Studio display. | `trinity`, `creator` |
| **Trinity: CQ-02 escalate warn → block** | Studio warns in coverage summary (shipped); optional block on approve/export. creator/reference.md | `trinity`, `creator` |
| **Trinity Reviewer export: environment/tenant metadata** | RQ-02 follow-up for multi-tenant analytics. | `trinity`, `reviewer` |

---

## Priority P2 — Polish and ops

| Title | Body summary | Labels |
|-------|----------------|--------|
| **Trinity Studio: Wall-clock timing metrics** | Time from batch import → review complete → Xray persist; derive from `metric_event` or explicit timers. | `trinity`, `telemetry` |
| **Trinity: Second product pilot scorecard** | Multi-project validation; mapping + acceptance comparison per [FAQ.md](FAQ.md). | `trinity`, `docs` |
| **Trinity Studio: deprecate duplicate static editor** | Single React UI on 5173/8765. NEXT-STEPS.md | `trinity`, `studio` |
| **Trinity: GitHub release v0.1.0 + internal announcement** | Tag + changelog after pilot sign-off. | `trinity`, `docs` |
| **Trinity: Sanitize demo Reviewer runs in repo** | Hub README + committed demo portfolio only. | `trinity`, `docs` |

---

## Done in repo (do not re-open)

IQ-01–IQ-17 (except post-release hardening above), IQ-10–15, grill R1–R5 (portfolio rollup, child inventory + status banner, classifications banner, plan test_type coercion, Reviewer HTML open, PQ-06 dashboard alerts, CQ-02 doc), run rename/delete, `pr-`/`cr-` IDs, production Importer default, Cursor cost hooks (optional telemetry), **Jira epic comments MVP** (Studio API + panel), **Studio API router split**, **demo fixture DEMO-4500** + import key guard, **operator Confluence pack** + [`OPERATOR-SETUP.md`](OPERATOR-SETUP.md).

Roadmap summary: [`ROADMAP.md`](ROADMAP.md).

**Open review-report.html** — done in repo (R4); do not re-open unless parity regresses.
