# Prerequisites & preflight

<!-- Confluence title: Trinity — Prerequisites & preflight -->

## Machine requirements

- **Python 3.11+** — Studio API, Reviewer `render_report.py`, Importer scripts.
- **Node.js 18+** — Studio React UI (Vite).
- **Cursor** — Agent skills + Atlassian MCP for live Reviewer/Creator/Importer.
- **Disk** — Reviewer runs and Studio SQLite under `Trinity/studio/data/` (gitignored).

## Repository layout

After clone, repo root contains `Trinity/`. All commands below assume `cd` to repo root.

## Preflight commands

```bash
# Reviewer renderer smoke
python3 Trinity/reviewer/scripts/render_report.py \
  Trinity/reviewer/samples/demo-epic.payload.json --strict

# Install Cursor skills (optional for Studio-only demo)
./Trinity/scripts/install-trinity-skills.sh
```

Full list: `Trinity/PREFLIGHT.md`.

## Credentials (when needed)

| Capability | Env file | Variables |
|------------|----------|-----------|
| Jira read/write from Studio | `Trinity/studio/.env` | `JIRA_*` |
| Xray import execute | same | `XRAY_*` |
| Optional telemetry | same | `TRINITY_TELEMETRY_*` |
| Optional Cursor cost backfill | same | `CURSOR_ADMIN_API_KEY` |

Copy `Trinity/studio/.env.example` → `.env`. **Never commit `.env`.**

## MCP

For Appfire-style split Jira/Confluence hosts, configure **two** Atlassian MCP connections:

`Trinity/reviewer/config/DUAL-ATLASSIAN-MCP.md`

Without MCP, you can still run the **Studio demo** (step 03).

## CI parity (maintainers)

```bash
cd Trinity/studio && pip install -r requirements.txt && pytest tests -q
cd Trinity/studio/web && npm ci && npm test && npm run build
```
