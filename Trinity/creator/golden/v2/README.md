# Golden corpus v2 (Xray extracts)

Production test exports for Creator **depth / style** reference (`existing_xray_extract` in [SKILL.md](../../SKILL.md)).

## Layout per export

| Path | Use |
|------|-----|
| `manifest.json` | Run metadata, counts, filter link |
| `extraction.json` | Full structured export (same shape as `AI in QA/Skills/artifacts/6113-extraction.json`) |
| `extraction.md` | Human index |
| `rag/chunks.jsonl` | One JSON object per test: `id`, `text`, `metadata` — primary RAG / embedding feed |
| `rag/by-key/TC-*.json` | Per-test slice (`test` + `rag` document) |
| `raw-batches/` | Resumable GraphQL responses (**gitignored** — may contain presigned URLs) |
| `issues.json` | Jira keys + ids used for the run |

## filter-17844-bigpicture-manual

- **Source:** [Jira filter 17844](https://appfire.atlassian.net/issues/?filter=17844) — *BigPicture - Manual TestRun*
- **Tests:** 245 · **Steps:** 2582 (2026-10-08)
- **Point Creator at:** `filter-17844-bigpicture-manual/extraction.json` or `rag/chunks.jsonl`

## Re-export

```bash
export XRAY_CLIENT_ID=... XRAY_CLIENT_SECRET=...
# Corporate TLS intercept may require:
export XRAY_INSECURE_SSL=1

python3 Trinity/creator/scripts/xray_graphql_export.py \
  --issues-json Trinity/creator/golden/v2/filter-17844-bigpicture-manual/issues.json \
  --out-dir Trinity/creator/golden/v2/filter-17844-bigpicture-manual \
  --filter-id 17844 --filter-name "BigPicture - Manual TestRun" \
  --workers 6 --batch-size 8 --resume
```

Refresh `issues.json` after filter changes: paginate `filter = 17844` in Jira, then `merge_jira_search_pages.py`.
