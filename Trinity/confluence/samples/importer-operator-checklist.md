# Sample — Importer operator checklist (after plan preview)

Use with Studio **Importer** tab after **Preview import plan** succeeds.

---

## Pre-execute

- [ ] Instance = **sandbox** (first time) or production with `PRODUCTION` typed
- [ ] Mapping file matches product (`Trinity/importer/config/mappings/...`)
- [ ] Project key override intentional (default TC)
- [ ] Folder path exists or **create folder** allowed
- [ ] Reviewer gate acknowledged if plan shows `requires_acknowledgement`
- [ ] `export_preflight_warnings` reviewed (redaction / deferrable tests)

## Execute

- [ ] **Copy Cursor prompt** → trinity-importer in Cursor, **or**
- [ ] **Execute import batch** in Studio (sandbox)

## Post-execute

- [ ] Open `xray-import-report.json` (or report folder from result)
- [ ] Studio → **Persist Xray keys** with Creator run id
- [ ] Spot-check 1–2 tests in Xray UI

## Cursor prompt source

The full prompt is **not** duplicated here — Studio builds it from the plan (`cursor_prompt` field). Always copy from the latest **Preview import plan** so folder mutations and validation match.
