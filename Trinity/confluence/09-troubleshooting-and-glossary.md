# Troubleshooting & glossary

<!-- Confluence title: Trinity — Troubleshooting & glossary -->

## Common issues

| Symptom | Likely cause | Fix |
|---------|----------------|-----|
| Import fails “folder does not match payload epic key” | `ONE-90001` folder but payload says `DEMO-4500` | Rename folder to match `scope.value` |
| Jira preview empty after triage | Unsaved draft | **Save draft** → refresh preview |
| Post to Jira 503 | Missing `.env` | Copy `.env.example`, set `JIRA_*` |
| Post blocked with redaction | Secret-like text in comment | Edit payload or unlock wording after fix |
| Creator disabled | `not_fit` or not approved | Fix planning fit or approve unit |
| Wrong process on :8765 | Stale API | `STUDIO_FORCE=1` restart |
| Confluence *Unavailable* | Single-site MCP | Dual MCP setup doc |
| Demo unit still `ONE-90001` | Old SQLite | Reset DB + `seed-demo.sh` |

## Glossary

| Term | Meaning |
|------|---------|
| **Pipeline run** | One imported Reviewer folder in Studio |
| **Review unit** | One epic’s payload + revisions |
| **studio_qa** | Operator overlay on `review-payload.json` |
| **send_to_epic** | Include item in epic feedback / studio Jira variant |
| **review_ref** | Relative path to exported `review-payload.json` |
| **Profile A / B** | HTML report layouts (`shared/html-report-guidelines.md`) |
| **not_fit** | Epic not suitable for test design this quarter |
| **pass_type** | full_sweep / rescan_delta / new_epics_only |

## Support evidence

For pilot scorecard: `Trinity/SCORECARD-TC-GENERATOR.md`, `Trinity/METRICS.md`, Studio telemetry export.

## Doc index (git)

| Doc | Role |
|-----|------|
| `OPERATOR-SETUP.md` | Linear setup |
| `QUICKSTART.md` | Short demo |
| `TESTING.md` | Validation checklist |
| `MANUAL.md` | Operator hub |
| `confluence/README.md` | Wiki publish instructions |
