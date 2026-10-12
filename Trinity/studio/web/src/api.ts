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
  test_cases_ready_for_import: number;
};

export type CreatorTestRow = {
  id: string;
  draft_id: string;
  title: string;
  human_review_status: string;
  automation_fit?: string | null;
  automation_candidate?: number | null;
  marked_for_xray_import?: number | null;
  creator_run_id?: string;
  xray_test_key?: string | null;
  import_status?: string | null;
};

export type CoverageMatrixRow = {
  ac_id: string;
  jira_key?: string | null;
  batch_status: string;
  batch_covered_by: string[];
  approved_covered_by: string[];
  draft_covered_by: string[];
  review_gap: boolean;
  gap_reason?: string | null;
};

export type CatalogCoverageRow = {
  catalog_id: string;
  tier: string;
  status: string;
  covered_by?: string[];
  blocker?: string;
};

export type CreatorCoverage = {
  available: boolean;
  batch_revision?: number | null;
  message?: string;
  gap_count?: number;
  uncovered_ac_ids?: string[];
  uncovered_goals?: string[];
  warnings?: string[];
  catalog_coverage_pct?: number;
  catalog_coverage?: CatalogCoverageRow[];
  matrix?: CoverageMatrixRow[];
  source_requirement_keys?: string[];
  approved_ac_ids?: string[];
};

export const api = {
  stats: () => json<Stats>("/api/stats"),
  runs: () => json<PipelineRun[]>("/api/runs"),
  run: (id: string) =>
    json<{ units: ReviewUnit[]; creator_handoff?: unknown } & PipelineRun>(
      `/api/runs/${id}`
    ),
  importRun: (path: string) =>
    json<{
      pipeline_run_id: string;
      units_imported: number;
      import_kind: "new" | "updated";
      pipeline_is_new: boolean;
      source_path?: string;
    }>("/api/import/reviewer-run", {
      method: "POST",
      body: JSON.stringify({ path }),
    }),
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
  creatorProducts: () =>
    json<{
      products: {
        product_id: string;
        name: string;
        config_file: string;
        golden_root: string;
        golden_corpus_id?: string;
        golden_title?: string;
        golden_test_count?: number;
        importer_default_project_key?: string;
        importer_default_folder_template?: string;
      }[];
    }>("/api/creator/products"),
  creatorGoldenCorpora: () =>
    json<{
      corpora: {
        id: string;
        title: string;
        path: string;
        resolved_path?: string;
        path_exists?: boolean;
        product_lines?: string[];
        test_count?: number;
        reference_jira_project?: string | null;
        notes?: string;
      }[];
    }>("/api/creator/golden-corpora"),
  creatorRuns: () =>
    json<
      {
        id: string;
        label: string;
        test_count?: number;
        batch_revision?: number;
        status: string;
      }[]
    >("/api/creator-runs"),
  creatorRun: (id: string) =>
    json<{
      run: { id: string; label: string };
      tests: CreatorTestRow[];
      summary: {
        total: number;
        approved: number;
        rejected: number;
        ready_for_import: number;
      };
      coverage?: CreatorCoverage;
    }>(`/api/creator-runs/${id}`),
  test: (id: string) =>
    json<{
      test: CreatorTestRow & { creator_run_id?: string };
      case: Record<string, unknown>;
    }>(`/api/tests/${id}`),
  saveTest: (
    id: string,
    caseObj: Record<string, unknown>,
    status?: string,
    markedForXrayImport?: boolean
  ) =>
    json<{
      revision: number;
      human_review_status: string;
      marked_for_xray_import: boolean;
    }>(`/api/tests/${id}`, {
      method: "PUT",
      body: JSON.stringify({
        case: caseObj,
        human_review_status: status,
        marked_for_xray_import: markedForXrayImport,
      }),
    }),
  patchTest: (
    id: string,
    body: { human_review_status?: string; marked_for_xray_import?: boolean }
  ) =>
    json(`/api/tests/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  bulkTestReview: (
    runId: string,
    testIds: string[],
    body: {
      human_review_status?: string;
      marked_for_xray_import?: boolean;
      rejection_reason?: string;
    }
  ) =>
    json<{ updated: number; warnings?: string[] }>(
      `/api/creator-runs/${runId}/bulk-test-review`,
      {
        method: "POST",
        body: JSON.stringify({ test_ids: testIds, ...body }),
      }
    ),
  exportSuiteReport: (runId: string) =>
    json<{
      path: string;
      absolute_path: string;
      index_html: string;
      test_count: number;
      profile: string;
    }>(`/api/creator-runs/${encodeURIComponent(runId)}/export-suite-report`, {
      method: "POST",
    }),
  exportForImporter: (runId: string) =>
    json<{
      path: string;
      absolute_path: string;
      test_count: number;
      export_preflight_warnings?: string[];
      payload: Record<string, unknown>;
    }>(`/api/creator-runs/${runId}/export-for-importer`, { method: "POST" }),
  importBatch: (path: string) =>
    json<{
      creator_run_id: string;
      tests_imported: number;
      batch_revision: number;
      import_kind: "new" | "updated";
      run_is_new: boolean;
      source_path?: string;
    }>("/api/import/test-case-batch", {
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
  importerInstances: () =>
    json<{
      instances: {
        id: string;
        label: string;
        jira_site: string;
        default_mapping: string;
        risk_tier: string;
        credential_hint?: string;
      }[];
    }>("/api/importer/instances"),
  importerMappings: () =>
    json<{
      mappings: {
        id: string;
        path: string;
        environment?: string;
        project_key?: string;
        default_folder?: string;
        jira_site?: string;
      }[];
    }>("/api/importer/mappings"),
  importerJiraProjects: (jiraInstanceId: string, mappingPath?: string, query?: string) => {
    const params = new URLSearchParams({ jira_instance_id: jiraInstanceId });
    if (mappingPath) params.set("mapping_path", mappingPath);
    if (query) params.set("query", query);
    return json<{
      status: string;
      jira_site?: string;
      projects: { key: string; id: string; name: string }[];
      message?: string;
    }>(`/api/importer/jira-projects?${params}`);
  },
  importerPlan: (body: {
    jira_instance_id: string;
    folder_path: string;
    create_folder_if_missing: boolean;
    mapping_path?: string | null;
    project_key_override?: string | null;
    payload_path?: string | null;
    creator_run_id?: string | null;
    skip_requirement_link?: boolean;
    reviewer_gate_acknowledged?: boolean;
  }) => json<ImporterPlanResult>("/api/importer/plan", { method: "POST", body: JSON.stringify(body) }),
  telemetryRejectionReasons: () =>
    json<{ reasons: { id: string; label: string }[] }>("/api/telemetry/rejection-reasons"),
  telemetrySummary: () => json<Record<string, unknown>>("/api/telemetry/summary"),
  importerExecute: (body: {
    jira_instance_id: string;
    folder_path: string;
    create_folder_if_missing: boolean;
    mapping_path?: string | null;
    project_key_override?: string | null;
    payload_path?: string | null;
    creator_run_id?: string | null;
    skip_requirement_link?: boolean;
    reviewer_gate_acknowledged?: boolean;
    production_confirm?: string;
  }) =>
    json<{
      status: string;
      created: number;
      failed: number;
      total: number;
      report_dir: string;
      results: { draft_id: string; action?: string; xray_key?: string | null }[];
      persist?: { updated: number; skipped: number };
    }>("/api/importer/execute", { method: "POST", body: JSON.stringify(body) }),
  recordImporterResults: (body: {
    creator_run_id: string;
    report_path?: string | null;
    results?: { draft_id: string; xray_test_key?: string; xray_key?: string }[];
  }) =>
    json<{ updated: number; skipped: number; details: unknown[] }>(
      "/api/importer/record-results",
      { method: "POST", body: JSON.stringify(body) }
    ),
};

export type ImporterPlanResult = {
  schema_version: string;
  mode: string;
  jira_instance: { id: string; label: string; jira_site: string; risk_tier: string };
  mapping: {
    path: string;
    project_key?: string;
    project_id?: string | null;
    default_folder_path?: string;
    jira_site?: string;
  };
  target: {
    folder_path: string;
    create_folder_if_missing: boolean;
    action: string;
    warnings: string[];
    create_folder_mutation?: { mutation: string; variables: Record<string, unknown> } | null;
  };
  project_key: string;
  project_resolution?: {
    project_key?: string;
    project_id?: string;
    project_name?: string;
    mapping_file_project_id?: string | null;
    mapping_conflict?: boolean;
    resolve_error?: string;
    resolved_via?: string;
  };
  reviewer_gate?: {
    linked?: boolean;
    requires_acknowledgement?: boolean;
    level?: string;
    messages?: string[];
    gate_status?: string | null;
    review_ref_path?: string;
  };
  reviewer_gate_acknowledged?: boolean;
  pm_safe_summary?: string;
  export_preflight_warnings?: string[];
  importer_defaults?: Record<string, unknown>;
  credentials: {
    xray_client_id: boolean;
    xray_client_secret: boolean;
    jira_email: boolean;
    jira_api_token: boolean;
    execute_ready: boolean;
    credential_hint?: string;
  };
  summary: { total: number; valid: number; invalid: number; action: string };
  tests: {
    draft_id: string;
    title?: string;
    validation_errors: string[];
    action: string;
  }[];
  cursor_prompt?: string;
};
