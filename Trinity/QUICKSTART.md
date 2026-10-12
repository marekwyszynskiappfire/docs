# Trinity — 10-minute operator quickstart

**Goal:** Studio running with demo Reviewer + Creator data — **no Jira, no Cursor skills required**.

Full guide: [`GUIDE.md`](GUIDE.md) · Checklist: [`TESTING.md`](TESTING.md)

## Before you start (one-time per machine)

| Requirement | Check |
|-------------|--------|
| Python **3.11+** | `python3 --version` |
| Node **18+** | `node --version` |
| Repo cloned | `cd` to repo root (folder that contains `Trinity/`) |

**Time note:** The first `./Trinity/studio/scripts/start.sh` installs Python + npm packages (often **3–8 minutes** on a fresh laptop). The steps below are **~10 minutes of hands-on time after that**.

## Steps (repo root)

### 1. Start Studio (~1 min after deps exist)

```bash
./Trinity/studio/scripts/start.sh
```

Leave this terminal open. Confirm:

```bash
curl -sf http://127.0.0.1:8765/api/health | head -c 200
```

Open **http://127.0.0.1:5173**

Port busy? `STUDIO_FORCE=1 ./Trinity/studio/scripts/start.sh`

### 2. Load demo Reviewer run (~30 s)

In a **second terminal** (repo root):

```bash
./Trinity/studio/scripts/seed-demo.sh
```

Or use the Dashboard **Import Reviewer run** field (pre-filled path):

`Trinity/studio/fixtures/demo-reviewer-run`

### 3. Click through Studio (~5 min)

| Step | Where | What |
|------|--------|------|
| Open run | Dashboard → pipeline run | See `ONE-90001` unit |
| Review unit | Click epic | Skim payload, optional edit |
| Creator batch | **Creator** tab → Import | Path: `Trinity/creator/samples/demo-story.suite.json` |
| Triage tests | Open creator run | Approve / reject; mark for Xray |
| Importer dry-run | **Importer** tab | Preview plan only (no `.env` needed for read-only UI) |

### 4. Optional next (~same day)

```bash
./Trinity/scripts/install-trinity-skills.sh   # Cursor: Reviewer / Creator / Importer
```

Copy `Trinity/studio/.env.example` → `.env` for Jira project list and Importer execute — [`GUIDE.md` §3](GUIDE.md#3-credentials-setup).

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| API health missing `importer_plan` | Wrong process on :8765 — `STUDIO_FORCE=1` restart |
| Import fails “No epic folders” | Use `Trinity/studio/fixtures/demo-reviewer-run`, not `reviewer/runs/` (empty until you scan) |
| Empty Dashboard after import | Refresh; check second terminal for import errors |
| Reset local DB | Delete `Trinity/studio/data/qa-studio.db`, restart `start.sh`, re-run `seed-demo.sh` |

## What this does *not* cover in 10 minutes

- Live Reviewer gather (needs Cursor + Atlassian MCP) — [`PREFLIGHT.md`](PREFLIGHT.md)
- Xray **execute** (needs `XRAY_*` in `.env` / `.env.production`)
- Pilot sign-off scorecard — [`SCORECARD-TC-GENERATOR.md`](SCORECARD-TC-GENERATOR.md)

Maintainer backlog: [`studio/CODE-HEALTH.md`](studio/CODE-HEALTH.md)
