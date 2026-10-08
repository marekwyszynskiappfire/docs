# Trinity preflight

Run once on a new machine before a portfolio review.

1. **Clone** the docs repo and `cd` to repo root.
2. **MCP** — Atlassian (and Figma if needed): [`reviewer/config/DUAL-ATLASSIAN-MCP.md`](reviewer/config/DUAL-ATLASSIAN-MCP.md).
3. **Skills** — `./Trinity/scripts/install-trinity-skills.sh` (or symlink `Trinity/reviewer` into `.cursor/skills/`).
4. **Reviewer renderer** —  
   `python3 Trinity/reviewer/scripts/render_report.py Trinity/reviewer/samples/demo-epic.payload.json --strict`
5. **Trinity Studio** —  
   `./Trinity/studio/scripts/start.sh` (installs Python deps from `Trinity/studio/requirements.txt`, including **jsonschema**).  
   UI http://127.0.0.1:5173 · `curl -sf http://127.0.0.1:8765/api/health`  
   Smoke: open **Personas** and **Reviewer configs**; save should write under `Trinity/personas/` and `Trinity/reviewer/config/runs/`.
6. **Import** —  
   `./Trinity/studio/scripts/import-run.sh Trinity/reviewer/runs/<your-local-run>` after a Reviewer portfolio scan (runs are gitignored).
7. **Pipeline** — skim [`PIPELINE.md`](PIPELINE.md) for the Reviewer → Studio → Creator sequence.
8. **Optional Jira REST** (Studio scope resolve) — copy `Trinity/studio/.env.example` → `.env` with API token; otherwise use **Copy JQL resolve prompt** in Reviewer configs.
