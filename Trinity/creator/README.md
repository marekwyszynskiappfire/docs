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
| Rule port | [`PORT-CHECKLIST.md`](PORT-CHECKLIST.md) (fill during Phase 1) |
| Planning hub | [`../../The Creator/ACTION-PLAN.md`](../../The%20Creator/ACTION-PLAN.md) |
| Decisions | [`../reviewer/DECISIONS.md`](../reviewer/DECISIONS.md) § Creator Part 2 |

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
  runs/             Committed pilots (e.g. TC-6504 Profile B report)
  scripts/          Render/import helpers (roadmap)
```

## Reference run (Profile B)

[runs/TC-6504/report/](runs/TC-6504/report/) — combinable facet filters for test↔bug triage; build with `runs/TC-6504/build_bug_report.py`.

## Legacy paths

- Root [`Creator/README.md`](../../Creator/README.md) — pointer after CR0 cutover.
- Input skills and persona review: [`../../The Creator/`](../../The%20Creator/).
