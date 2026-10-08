const base = "";

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${base}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json() as Promise<T>;
}

export type PipelineRun = {
  id: string;
  label: string;
  trigger_type: string;
  trigger_value: string;
  source_path: string | null;
  unit_count?: number;
  updated_at: string;
};

export type ReviewUnit = {
  id: string;
  pipeline_run_id: string;
  jira_key: string;
  summary: string | null;
  gate_status: string | null;
  qa_planning_fit: string | null;
  include_in_creator: number;
  approved_revision_id: number | null;
};

export type ReviewerRunConfig = {
  config_version: "1.0";
  portfolio_id: string;
  label?: string;
  created_at?: string;
  updated_at?: string;
  persona_id: string;
  product_id: string;
  scope: {
    kind: "filter_url" | "jql" | "epic_keys" | "epic_url";
    value: string;
  };
  pass_type: "full_sweep" | "rescan_delta" | "new_epics_only";
  child_scan: "epic_only_inventory" | "include_child_checklists";
  planning_dates: "jira_due_then_end";
  artifacts_dir?: string;
  creator_handoff_exclude_not_fit: boolean;
  jira_comment_policy?: "generate_review_before_post";
  notes?: string;
  resolved_epic_keys?: string[];
  resolved_at?: string;
  resolved_source?: "paste" | "scope_inline" | "jira_rest";
};

export type Stats = {
  pipeline_runs: number;
  review_units: number;
  review_units_approved: number;
  open_findings_latest: number;
  open_questions_latest: number;
  creator_runs: number;
  test_cases: number;
  test_cases_approved: number;
  test_cases_automation_candidate: number;
  test_cases_imported_xray: number;
};

export const api = {
  stats: () => json<Stats>("/api/stats"),
  runs: () => json<PipelineRun[]>("/api/runs"),
  run: (id: string) =>
    json<{ units: ReviewUnit[]; creator_handoff?: unknown } & PipelineRun>(
      `/api/runs/${id}`
    ),
  importRun: (path: string) =>
    json<{ pipeline_run_id: string; units_imported: number }>(
      "/api/import/reviewer-run",
      { method: "POST", body: JSON.stringify({ path }) }
    ),
  unit: (id: string) =>
    json<{
      unit: ReviewUnit;
      payload: Record<string, unknown>;
      revision: number | null;
      approved_revision: number | null;
    }>(`/api/units/${id}`),
  savePayload: (unitId: string, payload: Record<string, unknown>) =>
    json<{ revision: number }>(`/api/units/${unitId}/payload`, {
      method: "PUT",
      body: JSON.stringify({ payload }),
    }),
  patchUnit: (
    unitId: string,
    body: { include_in_creator?: boolean; qa_planning_fit?: string }
  ) =>
    json(`/api/units/${unitId}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  approve: (unitId: string) =>
    json(`/api/units/${unitId}/approve`, { method: "POST" }),
  exportUnit: (unitId: string) =>
    json<{ path: string; review_ref?: string; jira_key: string }>(
      `/api/units/${unitId}/export`,
      { method: "POST" }
    ),
  sendToCreator: (unitId: string) =>
    json<{
      review_ref: string;
      creator_run_id: string;
      prompt: string;
      suite_payload_hint: string;
      creator_studio_path: string;
    }>(`/api/units/${unitId}/send-to-creator`, { method: "POST" }),
  creatorHandoff: (runId: string) =>
    json<Record<string, unknown>>(`/api/runs/${runId}/creator-handoff`),
  creatorRuns: () =>
    json<
      { id: string; label: string; test_count?: number; status: string }[]
    >("/api/creator-runs"),
  creatorRun: (id: string) =>
    json<{
      run: { id: string; label: string };
      tests: { id: string; draft_id: string; title: string; human_review_status: string }[];
    }>(`/api/creator-runs/${id}`),
  test: (id: string) =>
    json<{ test: { id: string }; case: Record<string, unknown> }>(
      `/api/tests/${id}`
    ),
  saveTest: (id: string, caseObj: Record<string, unknown>, status?: string) =>
    json(`/api/tests/${id}`, {
      method: "PUT",
      body: JSON.stringify({ case: caseObj, human_review_status: status }),
    }),
  importBatch: (path: string) =>
    json("/api/import/test-case-batch", {
      method: "POST",
      body: JSON.stringify({ path }),
    }),
  personas: () => json<{ id: string; label: string }[]>("/api/personas"),
  persona: (filename: string) =>
    json<{ id: string; content: string }>(
      `/api/personas/${encodeURIComponent(filename)}`
    ),
  savePersona: (filename: string, content: string) =>
    json<{ id: string; saved: boolean }>(
      `/api/personas/${encodeURIComponent(filename)}`,
      { method: "PUT", body: JSON.stringify({ content }) }
    ),
  reviewerRunConfigs: () =>
    json<{ portfolio_id: string; label: string; updated_at?: string }[]>(
      "/api/reviewer-run-configs"
    ),
  reviewerRunConfig: (portfolioId: string) =>
    json<ReviewerRunConfig>(
      `/api/reviewer-run-configs/${encodeURIComponent(portfolioId)}`
    ),
  saveReviewerRunConfig: (portfolioId: string, config: ReviewerRunConfig) =>
    json<ReviewerRunConfig>(
      `/api/reviewer-run-configs/${encodeURIComponent(portfolioId)}`,
      { method: "PUT", body: JSON.stringify(config) }
    ),
  resolveReviewerScope: (portfolioId: string) =>
    json<{
      status: "resolved" | "cursor";
      config?: ReviewerRunConfig;
      prompt?: string;
      message?: string;
      warning?: string;
    }>(
      `/api/reviewer-run-configs/${encodeURIComponent(portfolioId)}/resolve-scope`,
      { method: "POST" }
    ),
  resolveScopePrompt: (portfolioId: string) =>
    json<{ prompt: string }>(
      `/api/reviewer-run-configs/${encodeURIComponent(portfolioId)}/resolve-scope-prompt`
    ),
  pasteResolvedKeys: (portfolioId: string, keysText: string) =>
    json<{ config: ReviewerRunConfig; resolved_count: number; warning?: string }>(
      `/api/reviewer-run-configs/${encodeURIComponent(portfolioId)}/resolved-keys`,
      { method: "POST", body: JSON.stringify({ keys_text: keysText }) }
    ),
  clearResolvedKeys: (portfolioId: string) =>
    json<ReviewerRunConfig>(
      `/api/reviewer-run-configs/${encodeURIComponent(portfolioId)}/resolved-keys`,
      { method: "DELETE" }
    ),
  reviewerNewEpics: (portfolioId: string) =>
    json<{
      portfolio_id: string;
      run_folder: string;
      epics_in_scope: string[];
      new_epics: string[];
      already_scanned: string[];
      scope_resolution_note?: string | null;
      error?: string | null;
    }>(`/api/reviewer-run-configs/${encodeURIComponent(portfolioId)}/new-epics`),
};
