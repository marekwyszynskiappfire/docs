# Trinity Creator

Test suite generation skill for the Trinity pipeline: **Reviewer** → **Creator** → **Studio** (human QA) → **Importer** (Xray).

## Status

| Item | State |
|------|--------|
| [`SKILL.md`](SKILL.md) | v1 — 3–5 e2e journeys, Reviewer-driven coverage, three personas — install via [`../scripts/install-trinity-skills.sh`](../scripts/install-trinity-skills.sh) |
| Personas | [`../personas/creator-*.md`](../personas/README.md) |
| Product config | [`config/default.json`](config/default.json), [`config/bigpicture.json`](config/bigpicture.json) |
| Schema | [`schemas/TestCaseDraft.schema.json`](schemas/TestCaseDraft.schema.json) |
| Studio import | [`samples/demo-story.suite.json`](samples/demo-story.suite.json) |
| Roadmap | [`../PATH-TO-1.0.md`](../PATH-TO-1.0.md) |

## Quick demo (Studio)

```bash
./Trinity/studio/scripts/start.sh
```

Open **Creator** → import path:

`Trinity/creator/samples/demo-story.suite.json`

## Layout

```
creator/
  SKILL.md, reference.md
  schemas/          TestCaseDraft (+ future suite-payload)
  golden/v1/        Style rules and pattern examples
  golden/v2/        Per-product Xray extracts (see config golden_root)
  samples/          Committed demo batches
  templates/        Review gate and external-context samples
  config/           Per-product JSON (start from default.json)
  artifacts/        Gitignored agent runs → {run_id}/suite-payload.json
  runs/             Optional committed pilots (see runs/README.md)
  scripts/          Render/import helpers (roadmap)
```

## Reference run (Profile B, optional local)

If present under `runs/TC-6504/`, see `runs/TC-6504/report/README.md` — combinable facet filters for test↔bug triage (not required for operators).
