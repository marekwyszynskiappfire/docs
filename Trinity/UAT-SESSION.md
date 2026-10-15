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

---

## Minute-by-minute script (operator)

| Min | Do | Pass if |
|-----|-----|---------|
| 0–15 | [START-HERE](START-HERE.md) → clone → `start.sh` → health check | Dashboard at :5173 |
| 15–25 | `seed-demo.sh` → DEMO-4500 → Creator import demo suite → Importer preview | Part B in validation |
| 25–35 | `install-trinity-skills.sh` → `pilot-preflight.sh` | All PASS |
| 35–55 | [CURSOR-MCP-SETUP](CURSOR-MCP-SETUP.md) single-site sandbox → verify resources in Agent | Gate 2 |
| 55–60 | Copy `studio/.env.example` → sandbox creds → restart Studio | Importer shows instance |
| 60–75 | FIRST-RUN Phase 3 with **one** sandbox Epic (Prompt 1 → import → approve → Prompt 2) | `review-payload.json` + Creator batch |
| 75–85 | Export for Importer → preview → sandbox execute **or** dry-run per policy | Part C |
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
