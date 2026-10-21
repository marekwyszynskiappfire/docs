# Trinity — Confluence publishing

**Share with new operators:** [Trinity — Start here](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754590489/Trinity+Start+here)

**Wiki tree (QACoE parent):** [Trinity — AI-assisted QA pipeline](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3750559869/Trinity+AI-assisted+QA+pipeline+operator+guide)

Git source of truth: `marekwyszynskiappfire/docs` · Page IDs: [`page-map.json`](page-map.json)

---

## Maintained wiki pages (sync from git)

| Order | Git source | Confluence |
|-------|------------|------------|
| 0 | [`START-HERE.md`](../START-HERE.md) | [Start here](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754590489/Trinity+Start+here) |
| 1 | [`FAQ.md`](../FAQ.md) | [FAQ](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754164473/Trinity+FAQ) |
| 2 | [`OPERATOR-ONBOARDING.md`](../OPERATOR-ONBOARDING.md) | [Operator onboarding](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3755311111/Trinity+Operator+onboarding) |
| 3 | [`FIRST-RUN.md`](../FIRST-RUN.md) | [First run playbook](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3750592672/Trinity+First+run+playbook) |
| 4 | [`CURSOR-MCP-SETUP.md`](../CURSOR-MCP-SETUP.md) | [Cursor and MCP setup](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3753312561/Trinity+Cursor+and+MCP+setup) |
| 5 | [`PROMPTS-AND-INPUTS.md`](../PROMPTS-AND-INPUTS.md) | [Prompts and inputs](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3755442183/Trinity+Prompts+and+inputs) |
| 6 | [`OPERATOR-SETUP.md`](../OPERATOR-SETUP.md) | [Setup checklist](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754459462/Trinity+Setup+checklist) |
| 7 | [`GUIDE.md`](../GUIDE.md) | [Credentials and Importer](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754492109/Trinity+Credentials+and+Importer) |
| 8 | [`ARCHITECTURE.md`](../ARCHITECTURE.md) | [Architecture](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3750920216/Trinity+Architecture) |
| 9 | [`MANUAL.md`](../MANUAL.md) | [Operator manual](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3750658179/Trinity+Operator+manual) |
| 10 | [`BIGQUERY.md`](../BIGQUERY.md) | [BigQuery and Looker](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3779068614/Trinity+BigQuery+and+Looker) |
| 11 | [`NEWBIE-PERSONA-REVIEW.md`](../NEWBIE-PERSONA-REVIEW.md) | [Newbie persona review](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3758587937/Trinity+Newbie+persona+review) |

**Git-only (not synced):** [`PATH-TO-1.0.md`](../PATH-TO-1.0.md), [`TESTING.md`](../TESTING.md), [`PIPELINE.md`](../PIPELINE.md), [`OPERATOR-VALIDATION.md`](../OPERATOR-VALIDATION.md), [`UAT-SESSION.md`](../UAT-SESSION.md), scorecard/Mateusz artifacts. Screenshots: [`docs/screenshots/`](../docs/screenshots/) — attach to wiki manually.

---

## Republish after edits

```bash
export ATLASSIAN_EMAIL='you@appfire.com'
export ATLASSIAN_API_TOKEN='...'
python3 Trinity/scripts/sync_confluence_from_git.py
```

Options: `--dry-run` · `--page FAQ` (title substring).

Relative `.md` links in git are rewritten to wiki URLs during sync.

---

## Parent index page

Page `3750559869` embeds child links — **full markdown replace is blocked**. After adding pages:

1. Open parent in Confluence edit mode.
2. Add a **Children display** macro or bullet list pointing to **Start here** and **FAQ** at the top.
3. Paste snippet from [`HUB-SNIPPET.md`](HUB-SNIPPET.md) if helpful.

**Last sync note (2026-10-14):** Expanded wiki tree (Start here, FAQ, onboarding, MCP, prompts, checklist, GUIDE) + newbie FAQ + operator onboarding rename.

---

## External sharing

- Sandbox examples only; no production tokens in wiki.
- State **DEMO-4500** is fictional.
- Follow QACoE space policy for external audiences.
