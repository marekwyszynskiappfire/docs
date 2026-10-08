# Trinity personas

Editable **role prompts** for Reviewer, Creator, and Importer. The agent loads the file named in the portfolio **run config** (`Trinity/reviewer/config/runs/{portfolio_id}.json` → `persona_id`).

| File | Used by |
|------|---------|
| [`reviewer-expert-qa-automation.md`](reviewer-expert-qa-automation.md) | The Reviewer (default) |

**Trinity Studio:** open **Personas** in the UI (`./Trinity/studio/scripts/start.sh`) — edits write back to this folder.

Change tone, automation bias, and question style here — not in `SKILL.md` bodies.
