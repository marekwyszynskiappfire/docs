import type { ReviewerRunConfig } from "../api";

export type ReviewerPromptContext = {
  workspaceUrl?: string;
  epicKeys?: string[];
};

export function buildReviewerCursorPrompt(
  config: ReviewerRunConfig,
  context?: ReviewerPromptContext
): string {
  const runRoot = `${config.artifacts_dir ?? "Trinity/reviewer/runs"}/${config.portfolio_id}`;
  const epicKeys = context?.epicKeys?.filter(Boolean) ?? [];
  const runSection = context?.workspaceUrl
    ? `
### This Studio run

Workspace: ${context.workspaceUrl}
${epicKeys.length ? `Epics already in this run: ${epicKeys.join(", ")}\n` : ""}
Write the payloads into this portfolio's run folder and reopen that workspace. Do not start a second pipeline run.
`
    : "";
  return `## Trinity Reviewer run

Run the **trinity-reviewer** skill in Cursor for this portfolio program.

| Field | Value |
|-------|-------|
| **portfolio_id** | \`${config.portfolio_id}\` |
| **pass_type** | \`${config.pass_type}\` |
| **persona_id** | \`${config.persona_id}\` |
| **product_id** | \`${config.product_id}\` |
| **child_scan** | \`${config.child_scan}\` |
| **creator_handoff_exclude_not_fit** | ${config.creator_handoff_exclude_not_fit} |

### Scope (\`${config.scope.kind}\`)

\`\`\`
${config.scope.value.trim()}
\`\`\`

${
  config.scope.kind === "jql" || config.scope.kind === "filter_url"
    ? `**source_jql (handoff):** use \`scope.value\` above in portfolio Creator handoff when the Reviewer run completes.\n`
    : ""
}${
  config.resolved_epic_keys?.length
    ? `**resolved_epic_keys (${config.resolved_epic_keys.length}):** ${config.resolved_epic_keys.slice(0, 20).join(", ")}${config.resolved_epic_keys.length > 20 ? "…" : ""}\n`
    : ""
}

### Operator steps

1. Load run config from \`Trinity/reviewer/config/runs/${config.portfolio_id}.json\`.
2. **Return visit:** ask whether configuration changed; if **no**, confirm **same scope** as this portfolio_id.
3. Apply persona: \`Trinity/personas/${config.persona_id}\`.
4. Questions and Jira comments must be unanswered decisions. Each one names the missing fact, who answers it, and what test, scope boundary, or pass/fail criterion the answer changes. Drop nits, restatements, and anything the sources already answer.
5. For \`pass_type: new_epics_only\`, scan only epics without \`review-payload.json\` under the run folder (use Studio **List new epics** or \`python3 Trinity/reviewer/scripts/list_new_epics.py ${config.portfolio_id}\`).
${runSection}
### After the run — Trinity Studio

\`\`\`bash
./Trinity/studio/scripts/import-run.sh ${runRoot}
\`\`\`

Use the dated subfolder under \`${runRoot}/\` if the skill wrote a separate \`portfolio_run_id\`.
`;
}
