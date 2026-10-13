# Creator workflow

<!-- Confluence title: Trinity — Creator workflow -->

## Entry conditions

- Review unit **approved** in Studio.
- `qa_planning_fit` is not **`not_fit`**.
- Operator completed Reviewer triage (open questions understood).

## Steps

1. Unit page → **Send to Creator** → paste prompt in Cursor.
2. Run **trinity-creator** skill (loads three Creator personas from `Trinity/personas/creator-*.md`).
3. Skill writes **`suite-payload.json`** (path in prompt, typically under `Trinity/creator/artifacts/<epic-key>/`).
4. Studio → **Creator** → import batch JSON.
5. Open creator run → edit tests → **approve** / **reject**.
6. For approved tests, check **Fit for Xray import**.
7. **Export for Importer** → `studio/data/exports/creator/<run>/importer-payload.json`.
8. Optional: **Export suite report** (Profile B HTML).

## Coverage matrix

Creator run page shows linkage coverage vs approved review (IQ-11). Use with QA lead for gap review.

## Sample prompt

See `Trinity/confluence/samples/creator-handoff-prompt.md` (shape matches Studio **Send to Creator**).

## Golden corpora

Product config points to `golden_root` for style depth:

`Trinity/creator/config/<product>.json`

Studio lists corpora: **Creator** UI / `GET /api/creator/products`.
