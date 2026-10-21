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

export type HandoffStatus =
  | "awaiting_cursor"
  | "output_detected"
  | "invalid_output"
  | "imported"
  | "stale_output";

export type CoverageProfileId = "smoke" | "core" | "balanced" | "thorough" | "edge";

export type CoverageProfile = {
  id: CoverageProfileId;
  label: string;
  position: number;
  test_count_min: number;
  test_count_max: number;
  summary: string;
};

export type CoverageProfileUpdate = {
  coverage_profile: CoverageProfileId;
  override?: CoverageProfileId | null;
  refreshed: { epic_key: string; status: HandoffStatus; id: string }[];
  message: string;
};

export type TestabilityVerdict =
  | "testable_now"
  | "testable_with_clarifications"
  | "not_testable_yet";

export type WorkspaceStageId = "review" | "draft" | "test_review" | "import";

export type CursorPrompt = {
  handoff_id: string;
  status: HandoffStatus;
  prompt_version: string;
  text: string;
};

export type WorkspaceAction = {
  epic_key: string | null;
  unit_id: string | null;
  current_stage: WorkspaceStageId | "done";
  title: string;
  reason: string;
  completion_signal: string;
  primary: {
    kind:
      | "approve_review"
      | "prepare_creator"
      | "copy_prompt"
      | "accept_changes"
      | "review_tests"
      | "open_importer"
      | "open_unit"
      | "none";
    label: string;
    handoff_id?: string;
    path?: string;
  };
  cursor_prompt: CursorPrompt | null;
};

export type PortfolioAction = {
  kind: "prepare_creator_batch" | "copy_creator_prompts" | "review_selected_tests" | "preview_import_plans";
  label: string;
  epic_keys: string[];
  unit_ids?: string[];
  handoff_ids?: string[];
};

export type WorkspaceEpic = {
  unit_id: string;
  jira_key: string;
  summary: string | null;
  qa_planning_fit: string | null;
  gate_status: string | null;
  verdict: TestabilityVerdict;
  testability_reasons: string[];
  readiness_label: string | null;
  readiness_line: string | null;
  blocker_questions: {
    question_id: string | null;
    question: string | null;
    context: string | null;
    owner_hint: string | null;
    priority: string | null;
  }[];
  other_question_count: number;
  approved: boolean;
  coverage_profile: CoverageProfileId | null;
  effective_coverage_profile: CoverageProfile;
  creator_run_id: string | null;
  creator_run_status: string | null;
  tests: {
    total: number;
    pending: number;
    approved: number;
    rejected: number;
    marked: number;
    in_xray: number;
  };
  stage: WorkspaceStageId | "blocked" | "done";
  creator_handoff: {
    id: string;
    status: HandoffStatus;
    error: string | null;
    expected_path: string;
    prompt: string;
  } | null;
};

export type WorkspaceStage = {
  id: WorkspaceStageId;
  title: string;
  description: string;
  done_when: string;
  status: "complete" | "current" | "upcoming";
};

export type WorkspaceSummary = {
  pipeline_run_id: string;
  label: string;
  workspace_path: string;
  coverage_profile: CoverageProfileId;
  coverage_profiles: CoverageProfile[];
  stages: WorkspaceStage[];
  next_action: WorkspaceAction;
  portfolio_actions: PortfolioAction[];
  review_prompt: CursorPrompt | null;
  epics: WorkspaceEpic[];
  watch_handoff_ids: string[];
};

export type CursorHandoff = {
  id: string;
  status: HandoffStatus;
  error: string | null;
  retry_count: number;
  copied_at: string | null;
};

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

export type PortfolioRollupRun = {
  id: string;
  label: string;
  updated_at: string;
  unit_count: number;
  units_approved: number;
  units_in_creator: number;
  gate_mix: Record<string, number>;
  fit_mix: Record<string, number>;
  open_findings_latest: number;
  open_questions_latest: number;
  creator_runs: number;
  test_cases: number;
  test_cases_approved: number;
};

export type PortfolioRollup = {
  generated_at: string;
  global: {
    gate_mix: Record<string, number>;
    fit_mix: Record<string, number>;
    pipeline_runs: number;
  };
  runs: PortfolioRollupRun[];
};

export type EpicChildRow = {
  key: string | null;
  type: string | null;
  status: string | null;
  summary: string | null;
};

export type EpicChildInventory = {
  pipeline_run_id: string;
  total_children?: number;
  run_status_mix?: Record<string, number>;
  epics: {
    unit_id: string;
    jira_key: string;
    child_count: number;
    status_mix: Record<string, number>;
    children: EpicChildRow[];
  }[];
};

export type PipelineRunPhase = {
  phase: string;
  label: string;
  started_at: string | null;
  ended_at: string | null;
  duration_seconds: number | null;
  notes?: string | null;
};

export type PipelineRunStatistics = {
  schema_version: number;
  pipeline_run_id: string;
  pipeline_label: string;
  computed_at: string;
  product_context: {
    product_id: string | null;
    trigger_type: string;
    trigger_value: string;
    source_path: string | null;
    jira_projects: string[];
    reviewer_run_id?: string | null;
    source_jql?: string | null;
    creator_jql?: string | null;
  };
  summary: {
    epics_reviewed: number;
    issues_spotted_findings_total: number;
    issues_spotted_findings_open: number;
    epics_not_ready_for_test_design: number;
    epics_tc_creation_ready: number;
    epics_tc_creation_ready_with_reservations: number;
    epics_tc_creation_not_ready: number;
    epics_tc_creation_unknown?: number;
    epics_tc_creation_mix?: Record<string, number>;
    questions_marked_for_epic_suggested: number;
    questions_marked_for_epic_new: number;
    questions_posted_to_epic_suggested: number;
    questions_posted_to_epic_new: number;
    jira_comment_posts_success: number;
    epics_selected_for_test_case_creation: number;
    epics_review_approved: number;
    test_cases_drafted_total: number;
    test_cases_amended_total: number;
    test_cases_sent_to_import_total: number;
    test_cases_imported_to_xray_total: number;
    creator_runs_linked: number;
  };
  test_cases_per_epic_drafted: Record<string, number>;
  phases: PipelineRunPhase[];
  epics: {
    unit_id: string;
    jira_key: string;
    summary: string | null;
    gate_status?: string | null;
    qa_planning_fit?: string | null;
    findings_total: number;
    not_ready_for_test_design: boolean;
    tc_creation_readiness?: string;
    include_in_creator: boolean;
    test_cases_drafted: number;
    test_cases_amended: number;
    xray_test_keys: string[];
  }[];
};

export type PipelineRunCompare = {
  compared_at: string;
  baseline_run_id: string;
  runs: {
    pipeline_run_id: string;
    pipeline_label: string;
    computed_at: string;
    summary: PipelineRunStatistics["summary"];
    overall_duration_seconds: number | null;
  }[];
  metrics: {
    key: string;
    label: string;
    values: Record<string, number | null>;
    min: number | null;
    max: number | null;
  }[];
  deltas_from_baseline: {
    metric: string;
    label: string;
    baseline_run_id: string;
    other_run_id: string;
    baseline: number;
    other: number;
    delta: number;
  }[];
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
  execution_tier?: string | null;
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

function formatMix(mix: Record<string, number> | undefined): string {
  if (!mix || !Object.keys(mix).length) return "—";
  return Object.entries(mix)
    .sort((a, b) => b[1] - a[1])
    .map(([k, v]) => `${k}: ${v}`)
    .join(" · ");
}

export const api = {
  stats: () => json<Stats>("/api/stats"),
  portfolioRollup: () => json<PortfolioRollup>("/api/portfolio-rollup"),
  contextLoadedAlerts: () =>
    json<{
      alert_count: number;
      alerts: {
        pipeline_run_id: string;
        run_label: string;
        unit_id: string;
        jira_key: string;
        source: string;
        source_type?: string;
        status: string;
        detail?: string;
      }[];
      statuses_flagged: string[];
    }>("/api/context-loaded-alerts"),
  runReviewReports: (runId: string) =>
    json<{
      source_path: string | null;
      portfolio_report_exists: boolean;
      portfolio_open_url: string | null;
      epics: {
        unit_id: string;
        jira_key: string;
        report_exists: boolean;
        report_relative_path: string | null;
        open_url: string | null;
      }[];
    }>(`/api/runs/${encodeURIComponent(runId)}/review-reports`),
  runChildInventory: (runId: string) =>
    json<EpicChildInventory>(`/api/runs/${encodeURIComponent(runId)}/child-inventory`),
  formatMix,
  runs: () => json<PipelineRun[]>("/api/runs"),
  renamePipelineRun: (runId: string, label: string) =>
    json<{ id: string; label: string }>(`/api/runs/${encodeURIComponent(runId)}`, {
      method: "PATCH",
      body: JSON.stringify({ label }),
    }),
  deletePipelineRun: (runId: string) =>
    json<{ deleted: boolean; id: string }>(`/api/runs/${encodeURIComponent(runId)}`, {
      method: "DELETE",
    }),
  renameCreatorRun: (runId: string, label: string) =>
    json<{ id: string; label: string }>(`/api/creator-runs/${encodeURIComponent(runId)}`, {
      method: "PATCH",
      body: JSON.stringify({ label }),
    }),
  deleteCreatorRun: (runId: string) =>
    json<{ deleted: boolean; id: string }>(`/api/creator-runs/${encodeURIComponent(runId)}`, {
      method: "DELETE",
    }),
  run: (id: string) =>
    json<{ units: ReviewUnit[]; creator_handoff?: unknown } & PipelineRun>(
      `/api/runs/${id}`
    ),
  runStatistics: (runId: string) =>
    json<PipelineRunStatistics>(
      `/api/runs/${encodeURIComponent(runId)}/statistics`
    ),
  runStatisticsExport: (runId: string) =>
    json<{ exported_at: string; export_kind: string; report: PipelineRunStatistics }>(
      `/api/runs/${encodeURIComponent(runId)}/statistics/export`
    ),
  compareStatistics: (runIds: string[]) =>
    json<PipelineRunCompare>(
      `/api/statistics/compare?runs=${runIds.map(encodeURIComponent).join(",")}`
    ),
  workspace: (runId: string) =>
    json<WorkspaceSummary>(`/api/workspace/${encodeURIComponent(runId)}`),
  setCoverageProfile: (runId: string, profile: CoverageProfileId) =>
    json<CoverageProfileUpdate>(`/api/workspace/${encodeURIComponent(runId)}/coverage-profile`, {
      method: "PUT",
      body: JSON.stringify({ profile }),
    }),
  setEpicCoverageProfile: (runId: string, unitId: string, profile: CoverageProfileId | null) =>
    json<CoverageProfileUpdate>(
      `/api/workspace/${encodeURIComponent(runId)}/units/${encodeURIComponent(unitId)}/coverage-profile`,
      { method: "PUT", body: JSON.stringify({ profile }) }
    ),
  prepareCreatorBatch: (runId: string) =>
    json<{ prepared: { id: string; epic_key: string }[] }>(
      `/api/workspace/${encodeURIComponent(runId)}/prepare-creator-batch`,
      { method: "POST" }
    ),
  prepareCreator: (runId: string, unitId: string) =>
    json<CursorHandoff>(
      `/api/workspace/${encodeURIComponent(runId)}/units/${encodeURIComponent(unitId)}/prepare-creator`,
      { method: "POST" }
    ),
  checkHandoff: (runId: string, handoffId: string, acceptChanges = false) =>
    json<CursorHandoff>(
      `/api/workspace/${encodeURIComponent(runId)}/handoffs/${encodeURIComponent(handoffId)}/check`,
      { method: "POST", body: JSON.stringify({ accept_changes: acceptChanges }) }
    ),
  markHandoffCopied: (runId: string, handoffId: string) =>
    json<CursorHandoff>(
      `/api/workspace/${encodeURIComponent(runId)}/handoffs/${encodeURIComponent(handoffId)}/copied`,
      { method: "POST" }
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
    body: {
      human_review_status?: string;
      marked_for_xray_import?: boolean;
      rejection_reason?: string;
    }
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
    json<{ id: string; content: string; content_sha256: string }>(
      `/api/personas/${encodeURIComponent(filename)}`
    ),
  savePersona: (filename: string, content: string, expectedSha256: string) =>
    json<{ id: string; saved: boolean; content_sha256: string }>(
      `/api/personas/${encodeURIComponent(filename)}`,
      { method: "PUT", body: JSON.stringify({ content, expected_sha256: expectedSha256 }) }
    ),
  personaRevisions: (filename: string) =>
    json<{ id: number; content_sha256: string; created_at: string; excerpt: string }[]>(
      `/api/personas/${encodeURIComponent(filename)}/revisions`
    ),
  restorePersona: (filename: string, revisionId: number, expectedSha256: string) =>
    json<{ id: string; content: string; content_sha256: string }>(
      `/api/personas/${encodeURIComponent(filename)}/revisions/${revisionId}/restore`,
      { method: "POST", body: JSON.stringify({ expected_sha256: expectedSha256 }) }
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
    idempotency_acknowledged?: boolean;
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
    idempotency_acknowledged?: boolean;
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
  cursorUsageStages: () =>
    json<{ stages: { id: string; label: string }[] }>("/api/cursor-usage/stages"),
  beginCursorSession: (body: {
    stage: string;
    pipeline_run_id?: string;
    creator_run_id?: string;
  }) =>
    json<{
      path: string;
      stage: string;
      pipeline_run_id?: string;
      creator_run_id?: string;
    }>("/api/cursor-session", { method: "POST", body: JSON.stringify(body) }),
  cursorUsageSummary: (opts: { pipelineRunId?: string; creatorRunId?: string }) => {
    const params = new URLSearchParams();
    if (opts.pipelineRunId) params.set("pipeline_run_id", opts.pipelineRunId);
    if (opts.creatorRunId) params.set("creator_run_id", opts.creatorRunId);
    return json<CursorUsageSummary>(`/api/cursor-usage/summary?${params}`);
  },
  cursorUsageBackfill: (hoursBack = 48) =>
    json<{
      updated?: number;
      error?: string;
      skipped?: string;
      conversations_matched?: number;
    }>(`/api/cursor-usage/backfill?hours_back=${hoursBack}`, { method: "POST" }),
  jiraStatus: () => json<JiraStatus>("/api/jira/status"),
  jiraCommentPreview: (unitId: string, variant: string, previewEdited = false) => {
    const params = new URLSearchParams({ variant });
    if (previewEdited) params.set("preview_edited", "true");
    return json<JiraCommentPreview>(
      `/api/units/${encodeURIComponent(unitId)}/jira-comment/preview?${params}`
    );
  },
  jiraCommentHistory: (unitId: string) =>
    json<{ posts: JiraCommentHistoryPost[] }>(
      `/api/units/${encodeURIComponent(unitId)}/jira-comment/history`
    ),
  jiraCommentPost: (
    unitId: string,
    body: {
      variant: string;
      confirm_issue_key: string;
      body?: string;
      preview_edited?: boolean;
      production_confirm?: string;
      allow_duplicate?: boolean;
    }
  ) =>
    json<JiraCommentPostResult>(
      `/api/units/${encodeURIComponent(unitId)}/jira-comment/post`,
      { method: "POST", body: JSON.stringify(body) }
    ),
};

export type JiraStatus = {
  configured: boolean;
  jira_base_url_set: boolean;
  jira_email_set: boolean;
  jira_token_set: boolean;
  jira_base_url_host: string | null;
};

export type JiraCommentPreview = {
  variant: string;
  recommendation: { variant: string; reasons: string[] };
  body: string;
  warnings: string[];
  blockers: string[];
  epic_feedback_count: number;
  jira_key?: string;
  payload_revision_id?: number;
  duplicate_warning?: string;
  request_hash?: string;
};

export type JiraCommentPostResult = {
  posted_at: string;
  variant: string;
  jira_comment_id: string;
  jira_comment_url: string;
  preview_edited: boolean;
};

export type JiraCommentHistoryPost = {
  id: number;
  review_unit_id: string;
  jira_issue_key: string;
  variant: string;
  jira_comment_id: string | null;
  jira_comment_url: string | null;
  payload_revision_id: number | null;
  preview_edited: number;
  request_hash: string | null;
  created_at: string;
};

export type CursorUsageSummary = {
  pipeline_run_id?: string;
  creator_run_id?: string;
  currency: string;
  total_cost_cents: number;
  total_cost_display?: string;
  total_input_tokens?: number | null;
  total_output_tokens?: number | null;
  sessions_pending_cost: number;
  models_used: { model: string; sessions: number }[];
  by_stage: {
    stage: string;
    label: string;
    sessions: number;
    cost_cents: number;
    cost_pending_sessions: number;
    input_tokens: number;
    output_tokens: number;
    models: string[];
  }[];
  admin_api_configured: boolean;
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
  export_preflight_redaction?: string[];
  idempotency?: {
    requires_acknowledgement?: boolean;
    warnings?: string[];
    acknowledged?: boolean;
  };
  execute_blockers?: string[];
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
    xray_test_type?: string;
    test_type_coercion?: string;
    validation_errors: string[];
    action: string;
  }[];
  cursor_prompt?: string;
};
