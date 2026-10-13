# Trinity — Confluence publishing

**Wiki tree (QACoE):** [Trinity — AI-assisted QA pipeline](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3750559869/Trinity+AI-assisted+QA+pipeline+operator+guide)

Only **three** child pages are maintained on Confluence (sync from git):

| Order | Git source | Confluence page |
|-------|------------|-----------------|
| 1 | [`FIRST-RUN.md`](../FIRST-RUN.md) | [First run playbook](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3750592672/Trinity+First+run+playbook) |
| 2 | [`ARCHITECTURE.md`](../ARCHITECTURE.md) | [Architecture](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3750920216/Trinity+Architecture) — attach [`assets/trinity-operator-pipeline.svg`](assets/trinity-operator-pipeline.svg) on the page if needed |
| 3 | [`MANUAL.md`](../MANUAL.md) | [Operator manual](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3750658179/Trinity+Operator+manual) |

Older sectional files (`01-overview.md` … `09-*.md`, `samples/`) remain in git as **optional excerpts**; they are **not** published to Confluence anymore.

## Republish after edits

1. Update the three git files above (and `OPERATOR-SETUP.md` if the checklist changed — content is folded into FIRST-RUN).
2. Use Atlassian MCP `updateConfluenceContent` with `body.format: markdown` and the page `contentId` from the table.
3. Bump *Last reviewed* dates in the markdown sources.

## External-sharing checklist

- [ ] Sandbox keys in examples; no production tokens in wiki
- [ ] State that **DEMO-4500** is fictional
- [ ] Restrict space per your external-sharing policy
