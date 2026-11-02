# Scorecard — copy-paste Cursor prompt

After a Trinity run, open Statistics in Studio (or download **Download export JSON**). Copy the block below into a **new Cursor chat** (Google Drive MCP connected). Replace the placeholders, paste your export JSON or summary under `RUN DATA`.

---

```markdown
Update the Trinity Usage Scorecard Google Sheet for one completed pipeline run.

**Spreadsheet:** https://docs.google.com/spreadsheets/d/123L4BTTTrgghlLHni-vqCAEiJperj-pu1tDKuEyg6oo/edit

**Rules:**
- Read the product tab (default **BigPicture** unless RUN DATA says otherwise).
- Assign the next free Run ID on that tab (e.g. BP-106 after BP-105). Do not reuse IDs.
- Append **one new row** with these columns in order (match the tab header row):
  Run ID | QA User | Product | Use Case | Epics Rev. | Epics Appr. | Epic Appr. % | TC Gen. | TC Appr. | TC Rej. | TC Appr. % | Sent XRay | TC Time (m) | Total Time (m) | Coverage Depth
- Use case: `create`, `review`, or `modify` (infer from RUN DATA).
- Coverage depth labels on the sheet: Comprehensive, Standard, or Exploratory (map from Studio coverage profile if present).
- Percent columns: one decimal + `%` (e.g. 87.5%) or leave as sheet formulas if you only write counts.
- Do **not** edit the Dashboard or `_Config` tabs except to confirm the new row appears in rollups.
- Confirm when done: Run ID, tab name, and link to the spreadsheet.

**Pipeline run (Studio):** `PASTE_pr-uuid_OR_LABEL_HERE`

**RUN DATA** (paste Statistics export JSON, or bullet list of counts/timings):

PASTE_EXPORT_JSON_OR_SUMMARY_HERE
```

---

Column hints: [`SCORECARD.md`](SCORECARD.md#bigpicture-row--what-to-enter).
