# Trinity Studio — code health backlog

Last reviewed: 2026-10-13 (Jira ADF, duplicate guard, export refactor, telemetry rename).

## Bugbot

**Bugbot found no bugs** in reviewed Studio changes on `main`. (Omitted untracked artifacts outside `Trinity/studio`.)

## Done (this pass)

| Item | Notes |
|------|--------|
| FastAPI **lifespan** | Replaced deprecated `@app.on_event("startup")`. |
| **API routers** | `server/routers/` — review runs/units, stats, creator, importer, telemetry, cursor, reviewer insights, Jira epic comments, personas/config. |
| Shared **api_models**, **studio_paths**, **studio_env** | `app.py` ~100 lines (health + static UI only). |
| **Jira epic comments** | Preview/post API + `JiraEpicCommentPanel`; wiki→ADF subset; 24h duplicate guard; mock HTTP tests. |
| **Export handoff** | `review_unit_export.py`; single DB txn for send-to-creator. |
| **Telemetry** | `operator_review_summary` (alias `mateusz_summary`). |
| **Vitest** | `web/src/lib/contextLoadedAlerts.test.ts` for sort/group helpers. |
| **Importer execute guards** | `importer_execute_guard.py` — redaction block + Xray idempotency ack; React Importer panel. |
| **Stats / alerts scale** | Open Q/F scan cap (`studio_stats`); context-loaded unit scan limit. |
| **Single UI path** | `app.py` prefers `web/dist`; `server/static/DEPRECATED.md`. |

## Prioritized follow-ups

| P | Item | Rationale |
|---|------|-----------|
| P2 | Split any oversized router modules further (creator/importer ~300+ lines each) | `app.py` split done. |
| P2 | Index or SQL-filter `context_loaded` alerts | Full unit scan on dashboard load at scale. |
| P3 | Document `operator_review_summary` rename in ADR | Alias kept for internal callers. |
| P3 | ESLint + Prettier for `web/` | TS strict only today. |
| P3 | Component tests (RTL) for critical flows | Importer plan, bulk approve. |
| P3 | Auth + path allowlist if Studio leaves localhost | Operator tool assumption today. |
| P2 | Jira comment batch post wizard + full wiki parity | ADF subset in `jira_wiki_adf.py`; Phase 3 in outline |

## CI

```bash
cd Trinity/studio && pytest tests -q
cd Trinity/studio/web && npm test && npm run build
```
