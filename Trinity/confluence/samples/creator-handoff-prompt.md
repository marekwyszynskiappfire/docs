# Sample — Creator handoff (from Studio Send to Creator)

Studio generates the live prompt with real `review_ref`, gate, and paths. Example after approving epic **`ONE-228469`**:

---

## Trinity Creator run

Run the **trinity-creator** skill in Cursor.

| Field | Value |
|-------|-------|
| **review_ref** | `Trinity/studio/data/exports/<pipeline-id>/ONE-228469/review-payload.json` |
| **scope (Epic)** | `ONE-228469` |
| **creator_run_id** | `ONE-228469` |
| **Reviewer gate** | needs_clarification |
| **Readiness** | *(from payload classifications)* |
| **Test design fit** | fit |
| **suite_mode** | `release_slice_e2e` (3–5 journey tests) |

### Personas (load all)

- `Trinity/personas/creator-expert-qa-engineer.md`
- `Trinity/personas/creator-test-architect.md`
- `Trinity/personas/creator-expert-test-automation-engineer.md`

### Scope rule (CR-EPIC-01)

Run Creator **once on this Epic key**. Child stories are traceability only.

### After generation

1. Write `suite-payload.json` under `Trinity/creator/artifacts/ONE-228469/suite-payload.json`.
2. Trinity Studio → **Creator** → import that batch.
3. Operator approves tests and marks **Fit for Xray import**.

Replace keys and paths with values from your Studio handoff.
