import { describe, expect, it } from "vitest";
import type { ReviewerRunConfig } from "../api";
import { buildReviewerCursorPrompt } from "./reviewerPrompt";

const config: ReviewerRunConfig = {
  config_version: "1.0",
  portfolio_id: "q4-backlog",
  persona_id: "reviewer-expert-qa-automation.md",
  product_id: "default",
  scope: { kind: "epic_keys", value: "ONE-1" },
  pass_type: "full_sweep",
  child_scan: "epic_only_inventory",
  planning_dates: "jira_due_then_end",
  creator_handoff_exclude_not_fit: true,
};

describe("buildReviewerCursorPrompt", () => {
  it("requires unanswered, actionable questions and comments", () => {
    const text = buildReviewerCursorPrompt(config);
    expect(text).toContain("unanswered decisions");
    expect(text).toContain("Drop nits");
  });

  it("passes the open workspace and its Epics into the prompt", () => {
    const text = buildReviewerCursorPrompt(config, {
      workspaceUrl: "http://127.0.0.1:5173/workspace/pr-1",
      epicKeys: ["ONE-1", "ONE-2"],
    });
    expect(text).toContain("http://127.0.0.1:5173/workspace/pr-1");
    expect(text).toContain("ONE-1, ONE-2");
    expect(text).toContain("Do not start a second pipeline run");
  });
});
