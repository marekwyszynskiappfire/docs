# Per-product config (Creator)

Resolution order: session `product` id → `config/<product>.json` → `config/default.json`.

## Keys (Phase 1)

| Key | Purpose |
|-----|---------|
| `product.id` | Config file name / batch `product_id` |
| `golden_corpus_id` | Optional id in [`golden/registry.json`](../golden/registry.json) |
| `golden_root` | Product golden corpus (v2 Xray extract or neutral journeys) |
| `assets.golden_style` | Path to `style-rules.md` |
| `assets.golden_examples` | Optional v1 example folder |
| `assets.coverage_catalog` | Optional `coverage-catalog.md` path; **null** for Reviewer-driven Epic runs |
| `policy.suite_mode_default` | `release_slice_e2e` |
| `policy.release_slice_test_count_min` / `max` | Default **3** / **5** |
| `policy.allow_atomic` | Default **false** |
| `policy.max_steps_per_journey` | Default **15** |
| `importer.default_jira_project_key` | Studio Importer project key hint (RQ-01) |
| `importer.default_folder_template` | Folder template; `{requirement_key}` from first linked Jira key |
| `importer.default_mapping_id` | Hint for mapping file id (e.g. `appfire-production`) |

## Examples

| Product | File | Golden corpus | Importer default project |
|---------|------|-----------------|--------------------------|
| Default | `default.json` | `neutral-manual-journeys` | TC |
| BigPicture | `bigpicture.json` | `bigpicture-manual-17844` (245 TC tests) | TC |
| Requirements / SPM | `requirements.json` | `neutral-manual-journeys` | **ONE** |

Studio: `GET /api/creator/products` and `GET /api/creator/golden-corpora`.

Add new products by copying `requirements.json` or `default.json`, set `golden_corpus_id` + `importer.default_jira_project_key`. Export a dedicated v2 corpus when neutral depth is not enough ([`GUIDE.md` §7](../../GUIDE.md)).

Do not commit secrets or production tokens.
