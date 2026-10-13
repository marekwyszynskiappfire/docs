# Cursor skills & Atlassian MCP

<!-- Confluence title: Trinity — Cursor skills & MCP setup -->

## Install skills

From repo root:

```bash
./Trinity/scripts/install-trinity-skills.sh
```

This links Trinity skill folders into Cursor’s skills path. You should see:

- **trinity-reviewer** — `Trinity/reviewer/SKILL.md`
- **trinity-creator** — `Trinity/creator/SKILL.md`
- **trinity-importer** — `Trinity/importer/SKILL.md`

## When to use which skill

| Skill | Trigger | Output |
|-------|---------|--------|
| Reviewer | Portfolio scan, rescan epic | `review-payload.json`, HTML report, Jira comment text files |
| Creator | After Studio approve + handoff prompt | `suite-payload.json` |
| Importer | After Studio import plan | Xray tests + import report JSON |

Studio generates **handoff prompts** (Reviewer config, Send to Creator, Importer plan) — operators paste into Cursor.

## Atlassian MCP (dual site)

Many programs use:

- Jira on `appfire.atlassian.net`
- Confluence on `appfireteam.atlassian.net`

Configure **one MCP connection per host**. Full checklist and JSON template:

`Trinity/reviewer/config/DUAL-ATLASSIAN-MCP.md`

Verification: run a small Reviewer gather and confirm **Data sources** in the payload show Confluence as **analyzed**, not *Unavailable*.

## Figma (optional)

If epics link Figma, enable Figma MCP per your org policy. Reviewer documents epic-mode Figma rules in `reviewer/SKILL.md`.

## Studio vs Cursor boundary

| Action | Where |
|--------|--------|
| Edit personas / run configs | Studio |
| Jira/Confluence gather | Cursor (Reviewer skill) |
| Test case generation | Cursor (Creator skill) |
| Human approve / metrics / import plan | Studio |
| Xray batch create | Studio execute **or** Importer skill in Cursor |
