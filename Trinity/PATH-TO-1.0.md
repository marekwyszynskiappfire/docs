# Trinity — path to v1.0

**Current:** `0.3.0` — one-click **Run in Cursor**, BigQuery release gate, and the Mateusz pilot closed at `0.2.0`. Multi-product pilots are planned.  
**Versioning rules:** [`VERSIONING.md`](VERSIONING.md)

**v1.0** means: *any trained QA operator can run Reviewer → Creator → Studio → Importer on a supported product line with evidence, without ad-hoc Marek intervention, and leadership can read acceptance metrics from a standard export or org dashboard.*

---

## Anything left from Mateusz (optional polish)

| Item | Required for “closed”? |
|------|------------------------|
| Walkthrough with Mateusz using reveal.js deck | Yes — human step |
| Xray folder link/screenshot on scorecard | Nice-to-have |
| M4–M5 BigQuery / Looker | **No** for pilot sign-off (deferred in ADR 0002) |
| M2 pilots (BP, TT, Core Apps, RF) | **No** for pilot 1 closure; **yes** before v1.0 |

---

## Release ladder (semver)

```mermaid
flowchart LR
  v02["0.2.0 POC"]
  v03["0.3.x Pilots"]
  v04["0.4.x Hardening"]
  v10["1.0.0 GA"]
  v02 --> v03 --> v04 --> v10
```

### 0.3.x — Multi-product pilots (4–8 weeks)

**Goal:** Mateusz §5 + scorecard row 2+ with comparable metrics.

| Work | Done when |
|------|-----------|
| Pilot per product line (start: **BigPicture**, **TimeTracker**, **Core Apps**, **Rich Filters**) | Filled [`SCORECARD.md`](SCORECARD.md) row + telemetry export each |
| `creator/config` + **IQ-09** mapping per line | Import succeeds on PROD test project without custom hacks |
| ≥1 additional **named operator** (not only Marek) | “Who used it” on scorecard |
| Rejection mix in real runs | `rejection_reasons` non-empty in at least one pilot export |

**Tag:** `trinity-v0.3.0` when **two** product lines have scorecard rows and shared deck updated.

---

### 0.4.x — Operator hardening (4–6 weeks)

**Goal:** Reduce Cursor-only steps; tighten safety and observability.

| Work | Done when |
|------|-----------|
| **Importer** execute path reliable in Studio (guards, idempotency, keys persisted) | [`TESTING.md`](TESTING.md) green without hand-holding |
| **IQ-01–04, IQ-16** implemented or explicitly waived in ADR | No “documented but missing” Importer gaps |
| Telemetry **BigQuery ingest** live (M4) + optional Looker (M5) | `TRINITY_TELEMETRY_URL` documented; one successful org-wide flush |
| Phase **timings** on scorecard (manual or derived from events) | METRICS “not yet automated” shrunk |
| CI always green on `main`; no duplicate static Studio UI | Single React dist on 8765 |
| Confluence wiki synced with FIRST-RUN / MANUAL after material changes | QACoE tree matches git |

**Tag:** `trinity-v0.4.0` when TESTING + Importer E2E is repeatable by a second operator on two products.

---

### 1.0.0 — General availability (internal)

**Goal:** Trinity is the **default** AI-assisted manual TC path for onboarded product lines.

| Gate | Criterion |
|------|-----------|
| **Coverage** | ≥3 product lines with completed scorecards and acceptance-rate trend |
| **Operators** | ≥3 people have completed [`FIRST-RUN.md`](FIRST-RUN.md) on real epics |
| **Evidence** | Org dashboard **or** standardized monthly telemetry export process |
| **Docs** | FIRST-RUN + MANUAL + ARCHITECTURE; no critical doc drift vs Studio |
| **Support** | Known limitations published; mapping owners named per product |
| **Version** | `CHANGELOG.md` (or release notes) for `0.2.0` → `1.0.0` |
| **Sign-off** | QA lead + stakeholder (e.g. Mateusz) — “recommend scaling” on record |

**Tag:** `trinity-v1.0.0` + short internal announcement (Confluence + release notes).

**Out of scope for 1.0 (later 1.x):** full automation to regression suites, sandbox Xray write, multi-tenant SaaS Studio.

---

## Suggested order (next 30 days)

1. Mateusz walkthrough + optional Xray screenshot on scorecard.  
2. Pick **one** pilot 2 product (recommend **BigPicture**) — one epic end-to-end, second scorecard row.  
3. Parallel: BQ ingest URL when creds arrive (unblocks M4–M5 without blocking 0.3).  
4. Bump `VERSION` → `0.3.0` only when second scorecard row is **shared**, not merely started.

---

## How this ties to files

| Artifact | Role |
|----------|------|
| [`MATEUSZ-CRITERIA.md`](MATEUSZ-CRITERIA.md) | POC traceability; update as pilots complete |
| [`SCORECARD.md`](SCORECARD.md) | Per-pilot evidence |
| [`PATH-TO-1.0.md`](PATH-TO-1.0.md) | This roadmap |
| [`VERSION`](VERSION) | Bump on tagged releases only |

**Last updated:** 2026-10-13
