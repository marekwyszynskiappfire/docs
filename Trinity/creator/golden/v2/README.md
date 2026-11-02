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

## neutral-manual-journeys (IQ-12)

- **Purpose:** Product-agnostic manual journey references for teams that import to **non-TC** Jira projects (ONE, SPM, etc.).
- **Tests:** 5 synthetic references (`TC-99001`–`TC-99005`) — not live Xray issues.
- **Rebuild:** `python3 Trinity/creator/scripts/build_neutral_golden_corpus.py`
- **Registry:** [`registry.json`](../registry.json) · product config `requirements.json`

## filter-17844-bigpicture-manual

- **Source:** [Jira filter 17844](https://appfire.atlassian.net/issues/?filter=17844) — *BigPicture - Manual TestRun*
- **Base:** 245 tests · 2582 steps (2026-10-08)
- **Cloud enrichment:** `project = "Big Picture QA" AND "Automated Platform[Select List (multiple choices)]" = "Atlassian Cloud"`; its run metadata is recorded in `manifest.json`.
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

Committed artifacts (`extraction.json`, `rag/`) are written with presigned S3 query strings stripped automatically. Re-run `redact_presigned_s3_urls.py` only if you paste exports from elsewhere.

Refresh `issues.json` after filter changes: paginate `filter = 17844` in Jira, then `merge_jira_search_pages.py`.

### Refresh the Atlassian Cloud enrichment

The enrichment script uses Xray GraphQL directly, requires only `XRAY_CLIENT_ID`
and `XRAY_CLIENT_SECRET`, and fetches pages concurrently. It preserves the base
filter corpus, replaces selected tests with their current Xray definitions, and
does not modify the corpus unless every page succeeds.

```bash
python3 Trinity/creator/scripts/enrich_bigpicture_cloud_golden.py \
  --env-file Trinity/studio/.env.production \
  --workers 6 --page-size 25
```

Use `--dry-run` to validate authentication, JQL, and selected count without
writing files. Do not put credentials in a command line, committed config, or
the corpus.
