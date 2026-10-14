# Trinity — Confluence publishing

**Wiki tree (QACoE):** [Trinity — AI-assisted QA pipeline](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3750559869/Trinity+AI-assisted+QA+pipeline+operator+guide)

Only **three** child pages are maintained on Confluence (sync from git):

| Order | Git source | Confluence page |
|-------|------------|-----------------|
| 1 | [`FIRST-RUN.md`](../FIRST-RUN.md) | [First run playbook](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3750592672/Trinity+First+run+playbook) |
| 2 | [`ARCHITECTURE.md`](../ARCHITECTURE.md) | [Architecture](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3750920216/Trinity+Architecture) — attach [`assets/trinity-operator-pipeline.svg`](assets/trinity-operator-pipeline.svg) on the page if needed |
| 3 | [`MANUAL.md`](../MANUAL.md) | [Operator manual](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3750658179/Trinity+Operator+manual) |

Superseded sectional markdown (`confluence/0*.md`, `samples/`) is **gitignored** — do not re-add; wiki content is the three pages above only.

**Mateusz POC closure** stays in git ([`SCORECARD.md`](../SCORECARD.md), [`MATEUSZ-CRITERIA.md`](../MATEUSZ-CRITERIA.md)); paste or link from Slides when the pilot log is ready — not a fourth maintained wiki page unless leadership asks.

## Republish after edits

1. Update the three git files above (and `OPERATOR-SETUP.md` when the checklist changes — content is folded into FIRST-RUN for wiki, but Step 16 statistics is in git only until manual sync).
2. **Preferred:** Atlassian MCP `updateConfluenceContent` on cloud **`appfire`** (`8e83c2b4-97ae-4335-8a8f-bbdff09d62dd`) with `body.format: markdown`, page `contentId`, and fresh `snapshotToken` from `getConfluenceContent`.
3. **Alternative:** `python3 Trinity/scripts/sync_confluence_from_git.py` (needs `JIRA_EMAIL` / `JIRA_API_TOKEN` with Confluence write on appfire.atlassian.net; uses `certifi` when installed).
4. **Parent index** (`3750559869`) embeds child page links — full markdown replace is blocked; add a footer comment or edit *Last published* in the UI.
5. Bump *Last reviewed* dates in the markdown sources.

**2026-10-14 sync topics:** Studio **Statistics** nav (single + compare with baseline dropdowns), TC readiness from `report.qa_planning_fit`, sortable tables, [`METRICS.md`](../METRICS.md) API rows.

## External-sharing checklist

- [ ] Sandbox keys in examples; no production tokens in wiki
- [ ] State that **DEMO-4500** is fictional
- [ ] Restrict space per your external-sharing policy
