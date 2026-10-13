# Trinity — Cursor cost attribution

Track **how much Cursor usage costs** for each Trinity pipeline step when agents run in **Cursor IDE**. Studio stores per-stage sessions, models, tokens (when available), and USD cost (when backfilled from Cursor’s Team Admin API).

Related: [FAQ.md](FAQ.md) · [METRICS.md](METRICS.md) · [PREFLIGHT.md](PREFLIGHT.md)

---

## What you get

| Stage ID | Pipeline step |
|----------|----------------|
| `reviewer_analyze` | Gather Jira/Confluence context, analyze epic, build review payload |
| `reviewer_mcp` | Post questions / comments via Atlassian MCP |
| `creator` | Generate test cases (`trinity-creator`) |
| `importer` | Importer plan / execute assisted by agent |
| `unscoped` | Fallback when stage was not armed |

For each **Agent session** (one Cursor `conversation_id`):

- **Model** (`model` / `model_id` from Cursor hooks)
- **Duration** (`duration_ms` on session end)
- **Tokens** (after Admin API backfill)
- **Cost** (`chargedCents` summed per conversation, after backfill)

**Pipeline rollup** on the Reviewer run page: stage breakdown + **total USD** + **models used** across the e2e path (Reviewer + linked Creator runs).

---

## What Cursor does *not* expose in hooks

Hooks (`sessionStart` / `sessionEnd`) do **not** include token counts or dollars. Trinity records:

1. **Immediately** — conversation id, model, stage, run ids (from Studio session file + hook env).
2. **Async** — cost and tokens via **Cursor Team Admin API** (`CURSOR_ADMIN_API_KEY` in `Trinity/studio/.env`).

Billing data is typically **aggregated on an hourly cadence**; use **Backfill cost from Cursor API** in Studio after sessions complete (or wait and click again).

Enterprise teams can additionally export **OpenTelemetry** with per-request tokens and estimated cost; that is not wired in Studio yet (track via GitHub Issues).

---

## Setup (one time per machine)

### 1. Project hooks (this repo)

Hooks live at [`.cursor/hooks.json`](../.cursor/hooks.json) and [`.cursor/hooks/trinity-cursor-usage.py`](../.cursor/hooks/trinity-cursor-usage.py). Open the **DOCS** repo root in Cursor so they load (check **Settings → Hooks**).

### 2. Studio running

```bash
./Trinity/studio/scripts/start.sh
```

Hooks POST to `http://127.0.0.1:8765/api/cursor-usage`.

### 3. Optional — dollar amounts

In `Trinity/studio/.env`:

```bash
# Team Admin API key (Cursor dashboard → team settings → API)
CURSOR_ADMIN_API_KEY=
```

Create a key with access to usage events. Backfill calls `POST https://api.cursor.com/teams/filtered-usage-events` and matches `conversationId` to stored sessions.

---

## Operator workflow (per epic / pipeline)

Use **one new Agent chat per stage** so costs split cleanly (same chat spans multiple stages otherwise).

1. In Studio, open the **Reviewer run** (or Creator run).
2. Under **Cursor cost**, choose the stage (e.g. **Reviewer — gather & analyze epic**) → **Arm Cursor session**.
3. In Cursor, start **Agent** and run the skill (`trinity-reviewer`, etc.).
4. When the session ends, Studio records the hook event.
5. Repeat for **reviewer_mcp**, **creator**, **importer** as you progress.
6. Click **Backfill cost from Cursor API** to pull `chargedCents` (after Cursor has aggregated usage).

View rollup on the same panel; export full telemetry still via `GET /api/telemetry/export` (QA metrics) — cursor rows are in `GET /api/cursor-usage/summary?pipeline_run_id=…`.

---

## API reference

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/cursor-session` | Arm stage + run ids (`Trinity/studio/data/.cursor-session.json`) |
| `GET` | `/api/cursor-session` | Read active session context |
| `POST` | `/api/cursor-usage` | Record session (hooks or manual) |
| `GET` | `/api/cursor-usage/summary` | Rollup by `pipeline_run_id` or `creator_run_id` |
| `POST` | `/api/cursor-usage/backfill` | Pull costs from Admin API |
| `GET` | `/api/cursor-usage/stages` | Stage labels for UI |

Manual record example:

```bash
curl -s -X POST http://127.0.0.1:8765/api/cursor-usage \
  -H 'Content-Type: application/json' \
  -d '{
    "stage": "creator",
    "conversation_id": "from-cursor-ui-if-needed",
    "pipeline_run_id": "pr-…",
    "creator_run_id": "cr-…",
    "model": "claude-…",
    "cost_cents": 42,
    "source": "manual"
  }'
```

---

## Limitations

- **Subagents** may use separate `conversation_id`s; arm stage before each subagent-heavy step or accept partial attribution.
- **Importer execute** itself is mostly Xray/Jira HTTP; only tag **importer** when an Agent session drives plan/execute.
- **Non-Cursor** runs (CLI-only Creator) have no automatic Cursor cost — use manual `POST /api/cursor-usage` or scorecard **Impact**.
- Admin API response shape may evolve; backfill logs errors in the API response if parsing fails.

---

## Scorecard / leadership

For pilot evidence, copy from Studio:

- **Total** and **by stage** table
- **Models used**
- Link to the same `pipeline_run_id` in QA telemetry export

Compare Cursor cost to manual test-design time in your program’s pilot notes or GitHub Issue.
