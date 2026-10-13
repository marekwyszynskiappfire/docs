# Trinity Studio — code health backlog

Last reviewed: 2026-10-12 (Bugbot on `Trinity/studio` + structural pass).

## Bugbot

**Bugbot found no bugs** in reviewed Studio changes on `main`. (Omitted untracked artifacts outside `Trinity/studio`.)

## Done (this pass)

| Item | Notes |
|------|--------|
| FastAPI **lifespan** | Replaced deprecated `@app.on_event("startup")`. |
| **API routers** | `server/routers/` — review runs/units, stats, creator, importer, telemetry, cursor, reviewer insights, Jira epic comments, personas/config. |
| Shared **api_models**, **studio_paths**, **studio_env** | `app.py` ~100 lines (health + static UI only). |
| **Jira epic comments** | Preview/post API + `JiraEpicCommentPanel`; demo unit `DEMO-4500`; import folder/key guard. |
| **Vitest** | `web/src/lib/contextLoadedAlerts.test.ts` for sort/group helpers. |

## Prioritized follow-ups

| P | Item | Rationale |
|---|------|-----------|
| P2 | Split any oversized router modules further (creator/importer ~300+ lines each) | `app.py` split done. |
| P2 | Index or SQL-filter `context_loaded` alerts | Full unit scan on dashboard load at scale. |
| P2 | Rename `mateusz_summary` → neutral telemetry name | API compatibility note in ADR. |
| P3 | ESLint + Prettier for `web/` | TS strict only today. |
| P3 | Component tests (RTL) for critical flows | Importer plan, bulk approve. |
| P3 | Auth + path allowlist if Studio leaves localhost | Operator tool assumption today. |
| P2 | Jira comment ADF/wiki parity + batch post wizard | [`JIRA-EPIC-COMMENTS-OUTLINE.md`](JIRA-EPIC-COMMENTS-OUTLINE.md) Phase 3 |

## CI

```bash
cd Trinity/studio && pytest tests -q
cd Trinity/studio/web && npm test && npm run build
```
