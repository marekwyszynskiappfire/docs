# Sample — start Reviewer portfolio (Cursor)

Paste after configuring `Trinity/reviewer/config/runs/<portfolio_id>.json` in Studio.  
Studio **Copy Cursor prompt** generates a richer, portfolio-specific version — use this as a template when explaining the flow externally.

---

Run the **trinity-reviewer** skill for portfolio **`{portfolio_id}`**.

**Config file:** `Trinity/reviewer/config/runs/{portfolio_id}.json`

**Scope:** `{scope_kind}` — `{scope_value}`

**Pass type:** `{pass_type}`

**Persona:** `Trinity/personas/{persona_filename}`

**Product:** `{product_id}`

**Artifacts directory:** `Trinity/reviewer/runs/`

### Instructions

1. Load the run config JSON and confirm scope with me if anything is ambiguous.
2. Run the portfolio interview only if config is missing required fields (otherwise skip interview).
3. Gather per skill checklist — Epic folder name must equal the Jira epic key.
4. Write `review-payload.json` and `review-report.html` under  
   `Trinity/reviewer/runs/{portfolio_run_folder}/{EPIC-KEY}/`.
5. Generate `jira-comment-full.txt` and `jira-comment-short.txt` per policy `generate_review_before_post` — do **not** auto-post to Jira.
6. When complete, tell me the import command:  
   `./Trinity/studio/scripts/import-run.sh Trinity/reviewer/runs/{portfolio_run_folder}`

### Redaction

Apply Reviewer redaction rules before any Jira-bound text is finalized.
