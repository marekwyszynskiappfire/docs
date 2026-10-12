# Trinity personas

Editable **role prompts** for Reviewer and Creator agents. The Reviewer loads one file from the portfolio **run config** (`persona_id`); Creator loads **all three** creator personas each run.

**Design-time persona matrix (P1–P10)** — start here for operators and leads:

- **[`P1-P10.md`](P1-P10.md)** — roles, Trinity touchpoints, lead ownership, Studio entry points
- [`MANUAL.md`](../MANUAL.md) §11 — whole-pipeline “who does what”
- [`reviewer/MANUAL.md`](../reviewer/MANUAL.md) §11 — Reviewer HTML audiences (maps to P1–P10)
- [`The Creator/CREATOR-SKILLS-PERSONA-REVIEW.md`](../../The%20Creator/CREATOR-SKILLS-PERSONA-REVIEW.md) — historical consolidation (C-01–C-15)

Product/doc review using all layers: [`REVIEW-PRODUCT-AND-DOCS.md`](../REVIEW-PRODUCT-AND-DOCS.md).

| File | Used by |
|------|---------|
| [`reviewer-expert-qa-automation.md`](reviewer-expert-qa-automation.md) | The Reviewer (default) |
| [`creator-expert-qa-engineer.md`](creator-expert-qa-engineer.md) | The Creator |
| [`creator-test-architect.md`](creator-test-architect.md) | The Creator |
| [`creator-expert-test-automation-engineer.md`](creator-expert-test-automation-engineer.md) | The Creator |
| [`importer-xray-operator.md`](importer-xray-operator.md) | Importer operator (optional Cursor prompt) |

**Trinity Studio:** open **Personas** in the UI (`./Trinity/studio/scripts/start.sh`) — edits write back to this folder.

Change tone, automation bias, and question style here — not in `SKILL.md` bodies.
