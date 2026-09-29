# The Reviewer

Product-agnostic Jira requirement quality review (Stories, Bugs, Tasks, Epics). Produces a schema-valid `ReviewPayload`, Markdown/HTML reports, and optional Jira comment drafts.

## Quick start

1. **Install the skill** — symlink or copy this folder into your agent skills path, for example:
   - Cursor: `.cursor/skills/reviewer/` → this directory (the folder must contain `SKILL.md`).
   - Claude / Hive: follow your host’s skill install docs; point `skill_root` at this directory.
2. **Connect Atlassian MCP** (Jira read, optional Confluence read) and Figma MCP if design links appear on issues.
3. **Run:** `scan ONE-12345` or `Review ONE-12345` in chat.

Operator guide: [`MANUAL.md`](MANUAL.md). Rules and workflow: [`SKILL.md`](SKILL.md).

## Layout

| Path | Purpose |
|------|---------|
| `SKILL.md` | Agent workflow (source of truth for behaviour) |
| `checklist.md` | Unified A/B/C checklist |
| `reference.md` | Severity, limits, templates, decision trees |
| `schemas/review-payload.schema.json` | Payload contract |
| `scripts/render_report.py` | Payload → reports (stdlib; optional `jsonschema`) |
| `config/default.json` | Default product config |
| `artifacts/` | Per-run output (`{run_id}/review-payload.json`, reports) — gitignored |
| `samples/` | Demo payloads for local renderer checks |
| `DECISIONS.md` | Rationale archive (shared history with The Creator) |

## Render a payload locally

```bash
python3 scripts/render_report.py samples/demo-story.payload.json --strict
```

## Config

Per-product overrides: `config/<product>.json` (see `config/default.json`). Resolution order is documented in `SKILL.md`.
