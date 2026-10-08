"""Cursor handoff prompt after Importer dry-run plan."""

from __future__ import annotations

from typing import Any


def build_importer_cursor_prompt(
    plan: dict[str, Any],
    *,
    payload_path: str | None,
    creator_run_id: str | None,
    mapping_path: str | None,
    skip_requirement_link: bool,
) -> str:
    inst = plan.get("jira_instance") or {}
    target = plan.get("target") or {}
    mapping = plan.get("mapping") or {}
    summary = plan.get("summary") or {}
    handoff = plan.get("handoff") or {}
    creds = plan.get("credentials") or {}

    payload_line = payload_path or (
        f"Trinity/studio/data/exports/creator/{creator_run_id}/importer-payload.json"
        if creator_run_id
        else "(set payload_path or creator_run_id)"
    )
    map_path = mapping_path or mapping.get("path", "")

    tests = plan.get("tests") or []
    test_lines = "\n".join(
        f"- `{t.get('draft_id')}` — {t.get('title', '')[:80]} ({t.get('action')})"
        for t in tests[:25]
    )
    if len(tests) > 25:
        test_lines += f"\n- … and {len(tests) - 25} more"

    cred_note = []
    if inst.get("id") == "appfire-production":
        cred_note.append(
            "Production Xray: Studio overlays `Trinity/studio/.env.production` for `XRAY_*` on this instance."
        )
    else:
        cred_note.append("Sandbox Xray: set `XRAY_CLIENT_ID` / `XRAY_CLIENT_SECRET` in `Trinity/studio/.env`.")
    if creds.get("execute_ready"):
        cred_note.append("Credential check: **ready** for execute.")
    else:
        cred_note.append("Credential check: **not ready** — fix env before execute.")

    folder_action = (
        "Call Xray `createFolder` then `createTest` per test."
        if target.get("create_folder_if_missing")
        else "Folder must exist; `createTest` with `folderPath` only."
    )

    return f"""## Trinity Importer — execute handoff

Run the **trinity-importer** skill in Cursor. Studio dry-run plan is **validated**; your job is **execute** (or single-test CLI dry-run first if you want extra safety).

### Operator target

| Field | Value |
|-------|-------|
| **jira_instance_id** | `{inst.get("id")}` ({inst.get("jira_site")}) |
| **risk_tier** | {inst.get("risk_tier")} |
| **mapping_path** | `{map_path}` |
| **project_key** | `{plan.get("project_key")}` |
| **folder_path** | `{target.get("folder_path")}` |
| **create_folder_if_missing** | {str(bool(target.get("create_folder_if_missing"))).lower()} |
| **payload** | `{payload_line}` |
| **creator_run_id** | `{creator_run_id or handoff.get("creator_run_id") or "—"}` |
| **skip_requirement_link** | {str(skip_requirement_link).lower()} |
| **tests in plan** | {summary.get("valid", 0)}/{summary.get("total", 0)} valid |

### Credentials

{chr(10).join("- " + line for line in cred_note)}

- `XRAY_INSECURE_SSL=1` if corporate TLS blocks Xray Cloud on this Mac.

### Folder rule

{folder_action}

### Tests in this batch

{test_lines or "- (none)"}

### Execute (agent)

1. Confirm operator selected **{inst.get("label")}** intentionally ({inst.get("risk_tier")}).
2. Load mapping `{map_path}`; ensure `project.id` is set if `create_folder_if_missing` is true.
3. For each valid `draft_id`, run import (when Studio Execute ships) or CLI:

```bash
export XRAY_INSECURE_SSL=1   # if needed
python3 Trinity/importer/scripts/xray_graphql_import.py \\
  --config {map_path} \\
  --batch {payload_line} \\
  --draft-id TC-001 \\
  --folder "{target.get("folder_path")}" \\
  --execute
```

4. Link requirements via Jira unless `skip_requirement_link` is true.
5. Write `xray-import-report.json` per test under the batch folder; summarize keys created.

### Studio reference

- Plan API: `POST /api/importer/plan` (already run — do not regenerate tests).
- Skill: `Trinity/importer/SKILL.md`
"""

