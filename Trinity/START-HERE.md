# Trinity — start here (new operators)

**Share this link with your team:** [Trinity — Start here (Confluence)](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754590489/Trinity+Start+here)

**Pilot feedback window:** **15 Oct – 29 Oct 2026** — report friction via [Trinity pilot feedback](https://github.com/marekwyszynskiappfire/docs/issues/new?template=trinity-pilot-feedback.yml) (label `trinity-support`) or your program channel. Share pack for leads: [PILOT-SHARE.md](PILOT-SHARE.md).

**Version:** `Trinity/VERSION` (currently **0.2.x**). You can run **real work** on **onboarded product lines**; org-wide GA is [PATH-TO-1.0.md](PATH-TO-1.0.md).

---

## What you are installing

| Piece | Role |
|-------|------|
| **Cursor** + **trinity-*** skills | AI reads Jira/Confluence, writes reviews and tests, runs Xray import |
| **Trinity Studio** (local) | One workspace per portfolio: verdict, tests, and the Xray plan |

You stay in control: approve in Studio; type **PRODUCTION** before live Xray execute.

---

## Choose your path

| Goal | Document | Time |
|------|----------|------|
| **Questions first** | [FAQ](FAQ.md) | 5 min |
| **UI only (no Jira)** | [FIRST-RUN.md](FIRST-RUN.md) Phase 0–1 + `seed-demo.sh` | ~20 min |
| **One-time machine setup** | [OPERATOR-ONBOARDING.md](OPERATOR-ONBOARDING.md) + [CURSOR-MCP-SETUP.md](CURSOR-MCP-SETUP.md) | ~60 min |
| **Real Epic** | [FIRST-RUN.md](FIRST-RUN.md) Phase 2–3 | 1–3 h |
| **Checklist** | [OPERATOR-SETUP.md](OPERATOR-SETUP.md) | reference |
| **UAT with QA lead** | [UAT-SESSION.md](UAT-SESSION.md) + [OPERATOR-VALIDATION.md](OPERATOR-VALIDATION.md) | ~90 min |
| **Doc review (Sam)** | [NEWBIE-PERSONA-REVIEW.md](NEWBIE-PERSONA-REVIEW.md) | maintainers |
| **New operator, one document** | [MANUAL.md](MANUAL.md) — checkout, samples, credentials, the run, BigQuery | first day |

---

## Confluence documentation (wiki)

All pages below sync from git via `python3 Trinity/scripts/sync_confluence_from_git.py`.

| Wiki page | Git source |
|-----------|------------|
| [Start here](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754590489/Trinity+Start+here) | This file |
| [FAQ](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754164473/Trinity+FAQ) | `FAQ.md` |
| [Operator onboarding](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3755311111/Trinity+Operator+onboarding) | `OPERATOR-ONBOARDING.md` |
| [First run playbook](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3750592672/Trinity+First+run+playbook) | `FIRST-RUN.md` |
| [Cursor and MCP setup](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3753312561/Trinity+Cursor+and+MCP+setup) | `CURSOR-MCP-SETUP.md` |
| [Prompts and inputs](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3755442183/Trinity+Prompts+and+inputs) | `PROMPTS-AND-INPUTS.md` |
| [Setup checklist](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754459462/Trinity+Setup+checklist) | `OPERATOR-SETUP.md` |
| [Credentials and Importer](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3754492109/Trinity+Credentials+and+Importer) | `GUIDE.md` |
| [Architecture](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3750920216/Trinity+Architecture) | `ARCHITECTURE.md` |
| [Operator manual](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3750658179/Trinity+Operator+manual) | `MANUAL.md` |
| [BigQuery and Looker](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3779068614/Trinity+BigQuery+and+Looker) | `BIGQUERY.md` |
| [Newbie persona review](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3758587937/Trinity+Newbie+persona+review) | `NEWBIE-PERSONA-REVIEW.md` |

**Hub (parent):** [Trinity — AI-assisted QA pipeline](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3750559869/Trinity+AI-assisted+QA+pipeline+operator+guide)

---

## Clone and five commands (first-day order)

```bash
git clone https://github.com/marekwyszynskiappfire/docs.git DOCS && cd DOCS
./Trinity/studio/scripts/start.sh          # Phase 0 — leave running
./Trinity/studio/scripts/seed-demo.sh      # Phase 1 — demo, no Jira
./Trinity/scripts/install-trinity-skills.sh # Phase 2 — then MCP per CURSOR-MCP-SETUP
./Trinity/scripts/pilot-preflight.sh
./Trinity/studio/scripts/import-run.sh Trinity/reviewer/runs/<folder-with-epic-keys>
```

A finished Reviewer opens the workspace itself. `import-run.sh` is the fallback when that URL was not printed. Narrative: [FIRST-RUN.md](FIRST-RUN.md). Doc review (persona Sam): [NEWBIE-PERSONA-REVIEW.md](NEWBIE-PERSONA-REVIEW.md).

---

## Production use vs GA

| Question | Answer |
|----------|--------|
| Real Epics and Xray? | **Yes** on onboarded product lines (mapping + portfolio from QA lead). |
| Any product, zero setup? | **Not yet** — [PATH-TO-1.0.md](PATH-TO-1.0.md). |
| Need expert every run? | **No** if MCP, `.env`, and Studio prompts are used — see [FAQ](FAQ.md). |

---

## Stuck?

1. [FAQ](FAQ.md)  
2. [Operator onboarding — recovery](OPERATOR-ONBOARDING.md#6-failure-recovery)  
3. GitHub Issue with label `trinity-support` (portfolio id, Epic key, sandbox vs prod).
