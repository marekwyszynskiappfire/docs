# Trinity Studio — code health backlog

Last reviewed: 2026-10-12 (Bugbot on `Trinity/studio` + structural pass).

## Bugbot

**Bugbot found no bugs** in reviewed Studio changes on `main`. (Omitted untracked artifacts outside `Trinity/studio`.)

## Done (this pass)

| Item | Notes |
|------|--------|
| FastAPI **lifespan** | Replaced deprecated `@app.on_event("startup")`. |
| **API routers** | `server/routers/` — telemetry, cursor usage, reviewer insights (PQ-06, HTML reports, rollup). |
| Shared **api_models**, **studio_paths**, **studio_env** | Thinner `app.py`; importer still in `app.py` (next split). |
| **Vitest** | `web/src/lib/contextLoadedAlerts.test.ts` for sort/group helpers. |

## Prioritized follow-ups

| P | Item | Rationale |
|---|------|-----------|
| P1 | Split remaining `app.py` routes into routers (runs/units, creator, importer, personas/config) | `app.py` still ~1.3k lines. |
| P2 | Index or SQL-filter `context_loaded` alerts | Full unit scan on dashboard load at scale. |
| P2 | Rename `mateusz_summary` → neutral telemetry name | API compatibility note in ADR. |
| P3 | ESLint + Prettier for `web/` | TS strict only today. |
| P3 | Component tests (RTL) for critical flows | Importer plan, bulk approve. |
| P3 | Auth + path allowlist if Studio leaves localhost | Operator tool assumption today. |
| P1 | **Jira epic comment post from Studio** | [`JIRA-EPIC-COMMENTS-OUTLINE.md`](JIRA-EPIC-COMMENTS-OUTLINE.md) |

## CI

```bash
cd Trinity/studio && pytest tests -q
cd Trinity/studio/web && npm test && npm run build
```
