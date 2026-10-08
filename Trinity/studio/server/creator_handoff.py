"""Build Creator handoff prompt from approved Reviewer export."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from personas import docs_repo_root


def review_ref_relative(absolute_path: str) -> str:
    p = Path(absolute_path)
    root = docs_repo_root()
    try:
        return str(p.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(p)


def build_creator_prompt(
    *,
    review_ref: str,
    jira_key: str,
    creator_run_id: str,
    gate_status: str | None,
    readiness_label: str | None,
    qa_planning_fit: str | None,
    pipeline_run_id: str | None,
) -> str:
    gate = gate_status or "unknown"
    readiness = readiness_label or "—"
    fit = qa_planning_fit or "—"
    suite_hint = f"Trinity/creator/artifacts/{creator_run_id}/suite-payload.json"
    personas = (
        "Trinity/personas/creator-expert-qa-engineer.md",
        "Trinity/personas/creator-test-architect.md",
        "Trinity/personas/creator-expert-test-automation-engineer.md",
    )
    persona_lines = "\n".join(f"- `{p}`" for p in personas)
    return f"""## Trinity Creator run

Run the **trinity-creator** skill in Cursor.

| Field | Value |
|-------|-------|
| **review_ref** | `{review_ref}` |
| **scope (Epic)** | `{jira_key}` |
| **creator_run_id** | `{creator_run_id}` |
| **Reviewer gate** | {gate} |
| **Readiness** | {readiness} |
| **Test design fit** | {fit} |
| **Studio pipeline run** | {pipeline_run_id or "—"} |
| **suite_mode** | `release_slice_e2e` (3–5 journey tests) |
| **product** | Resolve from pipeline/product config (e.g. `bigpicture` → `Trinity/creator/config/bigpicture.json`) |

### Personas (load all)

{persona_lines}

### Scope rule (CR-EPIC-01)

Run Creator **once on this Epic key**. Child stories supply traceability only — no per-child Creator batches.

### Style

- **E2E journeys only** — no atomic/button-level tests.
- Use **`golden_root`** from product config for depth (BigPicture: `golden/v2/filter-17844-bigpicture-manual`).
- Coverage matrix from **this review_ref**, not the legacy product catalog unless config enables it.
- Tag each test: `automation_fit`, `automation_blockers`, `persona_notes`.

### After generation

1. Write `suite-payload.json` under `{suite_hint}` (or path announced by the skill).
2. Trinity Studio → **Creator** → import batch path above.
3. Operator: edit → **approve** or **reject** each test; mark **fit for Xray import** when approved (Importer later).

### Parameters

- `review_ref`: path above (required).
- `jira_primary_key`: `{jira_key}`.
- `comprehensive`: **false** (default).
- `suite_mode`: `release_slice_e2e`.
"""


def payload_readiness(payload: dict[str, Any]) -> str | None:
    cls = payload.get("classifications") or {}
    readiness = cls.get("readiness") or {}
    return readiness.get("human_label") or readiness.get("value")
