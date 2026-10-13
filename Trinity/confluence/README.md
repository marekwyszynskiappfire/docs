# Trinity — Confluence publishing pack

Markdown in this folder is written to become **shareable Confluence pages** (customers, partners, or internal wiki with external visibility). Source of truth remains the git repo; update here when operator flows change.

## Page tree (create in this order)

| Order | File | Suggested Confluence title |
|-------|------|----------------------------|
| Parent | — | **Trinity — AI-assisted QA pipeline (operator guide)** |
| 1 | [`01-overview.md`](01-overview.md) | Overview & architecture |
| 2 | [`02-prerequisites.md`](02-prerequisites.md) | Prerequisites & preflight |
| 3 | [`03-checkout-and-studio-demo.md`](03-checkout-and-studio-demo.md) | Checkout & 10-minute Studio demo |
| 4 | [`04-cursor-skills-and-mcp.md`](04-cursor-skills-and-mcp.md) | Cursor skills & Atlassian MCP |
| 5 | [`05-reviewer-workflow.md`](05-reviewer-workflow.md) | Reviewer workflow |
| 6 | [`06-studio-review-and-jira-comments.md`](06-studio-review-and-jira-comments.md) | Studio review & Jira epic comments |
| 7 | [`07-creator-workflow.md`](07-creator-workflow.md) | Creator workflow |
| 8 | [`08-importer-workflow.md`](08-importer-workflow.md) | Importer & Xray |
| 9 | [`09-troubleshooting-and-glossary.md`](09-troubleshooting-and-glossary.md) | Troubleshooting & glossary |

**Diagram:** attach [`assets/trinity-operator-pipeline.svg`](assets/trinity-operator-pipeline.svg) to page 1 (or embed via Confluence image macro).

**Sample prompts:** link child page or attach files from [`samples/`](samples/).

## How to publish

### Option A — Manual (any Confluence)

1. Create the parent page in your space.
2. For each `0N-*.md` file: create a child page, paste body (Confluence Cloud: paste markdown or use *Insert* → *Markup* if available).
3. Upload the SVG to the overview page.
4. Add labels: `trinity`, `qa`, `cursor`, `xray` (adjust per your taxonomy).
5. Restrict the space or page tree per your external-sharing policy.

### Option B — Atlassian MCP / API

Use `createConfluenceContent` with your `spaceId`, parent page id, and markdown/HTML body. Convert relative links to absolute wiki links after publish.

**Published (QACoE, 2026-10-13):** parent under [QA Center of Excellence](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/1055719475/QA+Center+of+Excellence) → [Trinity — AI-assisted QA pipeline (operator guide)](https://appfire.atlassian.net/wiki/spaces/QACoE/pages/3750559869/Trinity+AI-assisted+QA+pipeline+operator+guide) (child pages 01–09, samples, OPERATOR-SETUP).

### Option C — Export from repo (readers with git access)

Point readers to [`OPERATOR-SETUP.md`](../OPERATOR-SETUP.md) for a single linear guide; Confluence pages are sectional copies of the same content.

## External-sharing checklist

Before marking pages **visible to customers**:

- [ ] Remove or redact internal hostnames, tokens, and personal emails in examples.
- [ ] Use **sandbox** Jira/Xray in screenshots; never production keys in samples.
- [ ] State that **DEMO-4500** and sample payloads are fictional.
- [ ] Link to your support channel for MCP credential setup (do not paste API tokens into Confluence).

## Maintainers

When you change Studio flows (new API, Jira comment behaviour, Importer gates):

1. Update the relevant `confluence/0N-*.md` and [`OPERATOR-SETUP.md`](../OPERATOR-SETUP.md).
2. Bump the *Last reviewed* date in [`01-overview.md`](01-overview.md).
3. Re-publish or diff Confluence children.

Linear setup index: [`OPERATOR-SETUP.md`](../OPERATOR-SETUP.md).
