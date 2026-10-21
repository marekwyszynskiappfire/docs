"""Server-owned Reviewer prompts used by one-click Cursor agents."""

from __future__ import annotations

from typing import Any

from cursor_handoff import studio_base_url


def build_reviewer_agent_prompt(
    config: dict[str, Any],
    *,
    pipeline_run_id: str | None = None,
    epic_keys: list[str] | None = None,
) -> str:
    portfolio_id = config["portfolio_id"]
    artifacts_dir = config.get("artifacts_dir") or "Trinity/reviewer/runs"
    scope = config.get("scope") or {}
    resolved = config.get("resolved_epic_keys") or []
    lines = [
        "## Trinity Reviewer run",
        "",
        "Run the **trinity-reviewer** skill in Cursor for this portfolio program.",
        "",
        f"- portfolio_id: `{portfolio_id}`",
        f"- pass_type: `{config.get('pass_type', 'full_sweep')}`",
        f"- persona_id: `{config.get('persona_id', 'reviewer-expert-qa-automation.md')}`",
        f"- product_id: `{config.get('product_id', 'default')}`",
        f"- child_scan: `{config.get('child_scan', 'epic_only_inventory')}`",
        f"- scope kind: `{scope.get('kind', 'epic_keys')}`",
        "",
        "### Scope",
        "",
        "```",
        str(scope.get("value") or "").strip(),
        "```",
        "",
    ]
    if resolved:
        shown = ", ".join(str(key) for key in resolved[:20])
        lines.append(f"Resolved Epic keys ({len(resolved)}): {shown}")
        lines.append("")
    lines.extend(
        [
            f"Load `Trinity/reviewer/config/runs/{portfolio_id}.json`.",
            f"Apply `Trinity/personas/{config.get('persona_id', 'reviewer-expert-qa-automation.md')}`.",
            "Questions and Jira comments must be unanswered decisions. Each names the missing fact, "
            "who answers it, and what test, scope boundary, or pass/fail criterion the answer changes. "
            "Drop nits, restatements, and anything the sources already answer.",
        ]
    )
    if pipeline_run_id:
        workspace = f"{studio_base_url()}/workspace/{pipeline_run_id}"
        lines.extend(
            [
                "",
                "### This Studio run",
                "",
                f"Pipeline run: `{pipeline_run_id}`",
                f"Workspace: {workspace}",
                f"Epics already in this run: {', '.join(epic_keys or []) or 'none'}",
                "Write into this portfolio's run folder and reopen that workspace. "
                "Do not create a second pipeline run.",
            ]
        )
    run_root = f"{artifacts_dir}/{portfolio_id}"
    lines.extend(
        [
            "",
            "### After the run",
            "",
            f"Write the run under `{run_root}` and run:",
            "",
            "```bash",
            f"./Trinity/studio/scripts/import-run.sh {run_root}",
            "```",
            "",
            "Use the dated subfolder if the skill creates a separate portfolio_run_id.",
        ]
    )
    return "\n".join(lines)
