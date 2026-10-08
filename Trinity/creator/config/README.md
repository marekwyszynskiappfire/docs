# Per-product config (Creator)

Resolution order: session `product` id → `config/<product>.json` → `config/default.json`.

## Keys (Phase 1)

| Key | Purpose |
|-----|---------|
| `product.id` | Config file name / batch `product_id` |
| `golden_root` | Product golden corpus (Xray extract folder or `golden/v1`) |
| `assets.golden_style` | Path to `style-rules.md` |
| `assets.golden_examples` | Optional v1 example folder |
| `assets.coverage_catalog` | Optional `coverage-catalog.md` path; **null** for Reviewer-driven Epic runs |
| `policy.suite_mode_default` | `release_slice_e2e` |
| `policy.release_slice_test_count_min` / `max` | Default **3** / **5** |
| `policy.allow_atomic` | Default **false** |
| `policy.max_steps_per_journey` | Default **15** |

## Examples

| Product | File | `golden_root` |
|---------|------|----------------|
| Default | `default.json` | `Trinity/creator/golden/v1` |
| BigPicture | `bigpicture.json` | `Trinity/creator/golden/v2/filter-17844-bigpicture-manual` |

Add new products by copying `default.json`, pointing `golden_root` at that product’s extract (or v1 until export exists).

Do not commit secrets or production tokens.
