# Checkout & 10-minute Studio demo

<!-- Confluence title: Trinity — Checkout & Studio demo (no Jira) -->

This page proves Trinity Studio works **without** Jira credentials or Cursor skills.

## Steps

### 1. Start Studio

```bash
./Trinity/studio/scripts/start.sh
```

Open http://127.0.0.1:5173

Health check:

```bash
curl -sf http://127.0.0.1:8765/api/health
```

Expect `features` to include `importer_plan`, `jira_epic_comments`, etc.

### 2. Seed demo Reviewer run

```bash
./Trinity/studio/scripts/seed-demo.sh
```

### 3. Click-through

| Step | Where | What |
|------|--------|------|
| Open run | Dashboard | Pipeline run from seed |
| Review unit | `DEMO-4500` | Fictional demo epic |
| Skim payload | Unit page | Questions, findings, gate |
| Creator | Creator tab | Import `Trinity/creator/samples/demo-story.suite.json` |
| Triage | Creator run | Approve/reject sample tests |
| Importer | Importer tab | **Preview plan only** (no `.env` required for read-only UI) |

### 4. Reset local state (optional)

```bash
rm Trinity/studio/data/qa-studio.db
./Trinity/studio/scripts/start.sh
./Trinity/studio/scripts/seed-demo.sh
```

## Important: DEMO-4500

- Folder `DEMO-4500` matches `scope.value` in the demo payload.
- **Not** a real production epic — do not use **Post to Jira** against production with this key.

## Next

- Live Jira: page **04** (MCP) then **05** (Reviewer).
- Full checklist: `Trinity/OPERATOR-SETUP.md` steps 1–6.
