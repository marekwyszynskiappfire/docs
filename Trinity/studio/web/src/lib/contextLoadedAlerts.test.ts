import { describe, expect, it } from "vitest";
import {
  groupContextLoadedAlertsByRun,
  sortContextLoadedAlerts,
  type ContextLoadedAlert,
} from "./contextLoadedAlerts";

const sample: ContextLoadedAlert[] = [
  {
    pipeline_run_id: "run-a",
    run_label: "Alpha",
    unit_id: "u1",
    jira_key: "ONE-2",
    source: "confluence",
    status: "failed",
  },
  {
    pipeline_run_id: "run-a",
    run_label: "Alpha",
    unit_id: "u1",
    jira_key: "ONE-1",
    source: "jira",
    status: "unavailable",
  },
  {
    pipeline_run_id: "run-b",
    run_label: "Beta",
    unit_id: "u2",
    jira_key: "ONE-9",
    source: "figma",
    status: "failed",
  },
];

describe("sortContextLoadedAlerts", () => {
  it("sorts epic keys ascending", () => {
    const sorted = sortContextLoadedAlerts(sample, "jira_key", "asc");
    expect(sorted.map((a) => a.jira_key)).toEqual(["ONE-1", "ONE-2", "ONE-9"]);
  });

  it("sorts epic keys descending", () => {
    const sorted = sortContextLoadedAlerts(sample, "jira_key", "desc");
    expect(sorted.map((a) => a.jira_key)).toEqual(["ONE-9", "ONE-2", "ONE-1"]);
  });
});

describe("groupContextLoadedAlertsByRun", () => {
  it("groups by pipeline run and orders by alert count", () => {
    const groups = groupContextLoadedAlertsByRun(sample);
    expect(groups.map((g) => g.pipeline_run_id)).toEqual(["run-a", "run-b"]);
    expect(groups[0].alerts).toHaveLength(2);
    expect(groups[0].epicKeys).toEqual(["ONE-2", "ONE-1"]);
  });
});
