# Trinity — sandbox UAT session (90 min)

**For:** First-time operator ([Sam / P11](personas/operator-first-time.md))  
**QA lead:** Runs Parts A–D in [OPERATOR-VALIDATION.md](OPERATOR-VALIDATION.md)  
**Pilot wave feedback deadline:** **2026-10-29** (see [PILOT-SHARE.md](PILOT-SHARE.md))  
**Before start:** P2 provides sandbox Epic key, portfolio id (or empty for operator-created), Importer mapping path, Xray project key + folder.

---

## Session setup (QA lead, 10 min)

| Item | Value |
|------|--------|
| Date / operator | |
| Machine | macOS / Windows |
| Trinity version | `cat Trinity/VERSION` |
| Sandbox site | `appfire-sandbox-774.atlassian.net` (or org default) |
| Epic key for Part C | |
| Support channel | GitHub Issues `trinity-support` |

**Rules for the operator:** No live coaching during Parts B–C except MCP OAuth and mapping file path. Note every stall >3 minutes.

**QA lead pre-UAT BigQuery gate:** restart Studio with the configured key, call
`POST /api/telemetry/sync`, and record `failed: 0`, `pending: 0`, and
`report_errors: []`. Confirm the run appears in
`qa-coe.trinity.v_run_summary`. BigQuery failure must not prevent any pipeline
stage; see [BIGQUERY.md](BIGQUERY.md). If no key is available, record live GCP
verification as the outstanding environment precondition.

---

## Minute-by-minute script (operator)

| Min | Do | Pass if |
|-----|-----|---------|
| 0–15 | [START-HERE](START-HERE.md) → clone → `start.sh` → health check | Studio at :5173. Top bar is Workspace, Personas, Statistics |
| 15–25 | `seed-demo.sh` → **Open workspace** on DEMO-4500 | Verdict and Next step visible. Creator and Importer are under More |
| 25–35 | `install-trinity-skills.sh` → `pilot-preflight.sh` | All PASS |
| 35–55 | [CURSOR-MCP-SETUP](CURSOR-MCP-SETUP.md) single-site sandbox → verify resources in Agent | Gate 2 |
| 55–60 | Copy `studio/.env.example` → sandbox creds + `CURSOR_API_KEY` → restart Studio | Workspace import panel lists sandbox; Cursor agent status is configured |
| 60–75 | FIRST-RUN Phase 3 with **one** sandbox Epic (**Run Reviewer in Cursor** → workspace URL → approve → **Run Creator in Cursor**) | `review-payload.json` and a suite on the workspace |
| 75–85 | **Plan Xray import** on the workspace → preview → sandbox write or **Run Importer in Cursor** per policy | Part C |
| 85–90 | Knowledge check (validation Part D) | Operator can answer 4 questions |

**Doc reference:** [OPERATOR-ONBOARDING.md](OPERATOR-ONBOARDING.md) gates match this order.

---

## Friction log (fill during session)

| Time | Step | What happened | Severity | GitHub # |
|------|------|---------------|----------|----------|
| | | | blocker / major / minor | |

**Severity:** **blocker** = could not finish without expert; **major** = >10 min lost; **minor** = confusion only.

---

## After session

1. Complete sign-off table in [OPERATOR-VALIDATION.md](OPERATOR-VALIDATION.md).  
2. File issues: [New pilot feedback](../../.github/ISSUE_TEMPLATE/trinity-pilot-feedback.yml) (label `trinity-support`).  
3. Update scores in [NEWBIE-PERSONA-REVIEW.md](NEWBIE-PERSONA-REVIEW.md) if verdict changes.

**Approved outcomes:** Solo sandbox · Production epics (after remediation) · Remediation required.
