---
name: testcase-cleanup
description: >-
  Inventory and clean up Xray Test issues in the Jira TC project on
  appfire.atlassian.net. Classify duplicates, orphans, obsolete tests, and
  Trinity imports. Dry-run before any Jira or Xray write. Prefer archive or
  labels over delete. Use when the user asks to clean up TC tests, Xray Test
  Repository, or the TC project.
---

# Test case cleanup (TC / Xray)

Clean up **Test** issues in project **TC** on **Appfire production** (`appfire.atlassian.net`).

Read [`reference.md`](reference.md) and [`config/project.json`](config/project.json) before querying.

## Required inputs

Obtain or infer:

1. Jira site — default production `https://appfire.atlassian.net`. Never assume production from `.env`; confirm the host before writes.
2. Scope — whole TC project, a JQL filter, an Xray Test Repository folder, labels (e.g. `trinity-import`), or an explicit list of keys.
3. Cleanup policy — inventory only (default), label, transition/archive, folder move, or delete.
4. Execution-history rule — by default, Tests with Xray test runs are **out of delete scope**.

If scope is missing, inventory first and stop with a classification summary.

## Safety

- Default is **read-only inventory**.
- Dry-run plan before any `POST`/`PUT`/`DELETE` to Jira or Xray.
- Execute only when the user names the site, the action, and the keys (or an approved plan file under `artifacts/`).
- Prefer **labels + status/archive + folder moves** over issue delete.
- Do not bulk-delete. Caps: propose batches; wait for confirmation between batches.
- Do not change Trinity Importer mappings, golden corpora, or Studio code from this skill.
- Never commit credentials, tokens, or raw Xray dumps that include secrets.

## Workflow

### 1. Inventory

Search Jira for Tests in `project = TC`. Pull comments, links, labels, status, and reporter when classifying.

For Xray detail (folder path, test type, test runs), authenticate to Xray Cloud and query `getTests` as in [`reference.md`](reference.md).

Write results under `TestCase_Cleanup/artifacts/` (gitignored). Do not dump the full TC project into git.

### 2. Classify

Assign each Test one or more buckets from [`reference.md`](reference.md#classification). Typical buckets:

- orphan (no requirement / Test link)
- duplicate (near-identical summary or steps)
- never executed (no Xray runs)
- trinity-import (`trinity-import` label or `/Trinity imports` folder)
- obsolete product / archived feature
- keep (in active folders, linked, or recently executed)

Do not treat Jira status `Done` as proof of execution.

### 3. Plan (dry-run)

Produce a plan file listing keys, proposed action, and rationale. Actions:

| Action | When |
|--------|------|
| keep | Active coverage |
| label | Needs triage (`cleanup-candidate`, `cleanup-orphan`, …) |
| archive / transition | Confirmed obsolete, keep history |
| move folder | Wrong Test Repository location |
| delete | User explicitly requested **and** no execution history (or they listed keys to force-delete) |

If the work creates Jira filters, create **saved filters** and record `id` + `https://appfire.atlassian.net/issues/?filter={id}`. Do not stop at JQL in a markdown file.

### 4. Execute (only when asked)

Confirm:

1. Host is `appfire.atlassian.net`.
2. Project is `TC`.
3. Exact keys and action.
4. User said to execute (not “plan” or “inventory”).

Then apply the approved batch. Re-inventory those keys and report before/after counts.

## Outputs

- `artifacts/<run-id>-inventory.json` — keys and classification (local).
- `artifacts/<run-id>-plan.json` — proposed actions.
- Saved filter URLs when filters are part of the deliverable.
- Short operator summary: counts by bucket, next batch, what was **not** touched.
