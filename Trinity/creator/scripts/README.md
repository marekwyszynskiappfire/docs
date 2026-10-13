# Scripts

| Script | Purpose |
|--------|---------|
| `render_report.py` | Extend Reviewer renderer for `suite` and `import` kinds (or split only if merge is unmaintainable) |
| `xray_graphql_import.py` | Fallback submit path (from `Input/Marek/_shared/scripts/`) |
| `xray_graphql_export.py` | Batched multi-worker Xray `getTests` export for golden / RAG corpora |
| `merge_jira_search_pages.py` | Merge Jira search page JSON into `issues.json` for export |
| `sample_golden_references.py` | **CR-GOLDEN-01** — rank golden TCs by Epic theme; take up to 10 similar; random fill if &lt;5 |

Copy and adapt from [`The Reviewer/scripts/render_report.py`](../../../../The%20Reviewer/scripts/render_report.py) when starting Phase 2.
