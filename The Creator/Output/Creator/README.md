# Staging: The Creator skill package

This directory is the **build area** for The Creator (test suite generation, triage report, gated Xray submit). It mirrors how [`Output/Reviewer/`](../Reviewer/) was used before [`The Reviewer/`](../../../The%20Reviewer/) shipped at the repo root.

**Plan:** [`../../ACTION-PLAN.md`](../../ACTION-PLAN.md)  
**Ship target (CR0):** repo-root [`Creator/`](../../../Creator/). **Do not install from this staging folder after promotion** — symlink `Creator/` as the skill.

## While staging

- Agent runs write under `artifacts/{run_id}/` (gitignored; see `.gitignore`).
- Schemas, scripts, and `SKILL.md` will appear here during Phases 1–3, then move to the final ship path.
