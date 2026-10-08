# Per-product config (Creator)

Resolution order (same as The Reviewer): session `product` id → `config/<product>.json` → `config/default.json` → built-in defaults.

**Phase 1:** copy [`The Reviewer/config/default.json`](../../../../The%20Reviewer/config/default.json) as a starting point and extend:

- `assets.golden`, `assets.coverage_catalog`, `assets.requirement_standard`
- `xray.*` (environment, test project, folder, draft label, allowlist)
- `policy.require_approval_before_write`, `policy.code_grounding`, `policy.generate_api_tests`
- `policy.test_data_isolation` (hook for Kacper-style parallel date bands — T-G6)

Do not commit secrets or production tokens.
