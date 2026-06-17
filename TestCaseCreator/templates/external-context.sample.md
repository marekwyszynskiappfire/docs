# External context — optional user-supplied inputs

You can pass **extra** material beyond Jira or the requirement bundle so test design matches PRDs, PDFs, mockups, and links you care about.

## How to specify (in chat)

Either use the `external_context` parameter in YAML form (see [`../README.md`](../README.md) prompts) or a clear bullet list in natural language:

```yaml
external_context:
  paths:
    - path/inside/workspace/spec.pdf
    - /absolute/path/if-allowed/notes.md
  urls:
    - https://confluence.example.com/pages/viewpage.action?pageId=12345
    - https://www.figma.com/design/...
```

## Supported ideas (agent capability–dependent)

| Kind | Typical use |
|------|----------------|
| **PDF** | PRD, legal/security annex, exported Word |
| **Markdown / HTML / text** | Local spec drafts, RFCs |
| **Images** | Mockups, flowcharts, UI screenshots (expectations in steps) |
| **Spreadsheets** | CSV / Excel when the agent can read them |
| **URLs** | Confluence, public docs, Figma, other Jira issues — same as skill “linked context” but **you** name them explicitly here |

## Rules

1. Paths must be readable from the **current workspace** (or absolute paths your environment allows).  
2. If a file or URL **cannot** be loaded, the agent should **tell you** and record the outcome in the output under **User-supplied external context**.  
3. User-supplied content **must not** override a contradictory primary requirement without calling it out (e.g. `generation_notes`: conflict between PDF and Jira AC-3).

## Primary requirement key

The output file is still named `{JIRA-KEY} - testcase-draft.md`. You need a real Jira key on the Epic/Story (or in the bundle’s `work_item.jira_key`) even when most detail comes from PDFs.
