import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api, ImporterPlanResult } from "../api";
import CreatorRunsManageTable from "../components/CreatorRunsManageTable";
import ReviewerRunsTable from "../components/ReviewerRunsTable";
import SortableDataTable from "../components/SortableDataTable";
import CursorAgentControl from "../components/workspace/CursorAgentControl";

const DEFAULT_FOLDER_PATH = "/Trinity imports";

export default function ImporterPage() {
  const [searchParams] = useSearchParams();
  const initialRunId = searchParams.get("creator_run_id") ?? "";
  const initialPayload = searchParams.get("payload_path") ?? "";

  const [instances, setInstances] = useState<
    { id: string; label: string; jira_site: string; risk_tier: string; credential_hint?: string }[]
  >([]);
  const [mappings, setMappings] = useState<
    { id: string; path: string; default_folder?: string; project_key?: string; jira_site?: string }[]
  >([]);

  const [jiraInstanceId, setJiraInstanceId] = useState("");
  const [mappingPath, setMappingPath] = useState("");
  const [folderPath, setFolderPath] = useState(DEFAULT_FOLDER_PATH);
  const [createFolder, setCreateFolder] = useState(true);
  const [projectKey, setProjectKey] = useState("");
  const [jiraProjects, setJiraProjects] = useState<{ key: string; name: string }[]>([]);
  const [projectsHint, setProjectsHint] = useState("");
  const [creatorRunId, setCreatorRunId] = useState(initialRunId);
  const [payloadPath, setPayloadPath] = useState(initialPayload);
  const [skipRequirementLink, setSkipRequirementLink] = useState(false);

  const [plan, setPlan] = useState<ImporterPlanResult | null>(null);
  const [copyMsg, setCopyMsg] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [prodConfirm, setProdConfirm] = useState("");
  const [reportPath, setReportPath] = useState("");
  const [recordMsg, setRecordMsg] = useState("");
  const [reviewerGateAck, setReviewerGateAck] = useState(false);
  const [idempotencyAck, setIdempotencyAck] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [creatorRuns, setCreatorRuns] = useState<
    { id: string; label: string; test_count?: number; status: string }[]
  >([]);
  const [reviewerRuns, setReviewerRuns] = useState<
    { id: string; label: string; unit_count?: number }[]
  >([]);
  const [executeResult, setExecuteResult] = useState<{
    created: number;
    failed: number;
    report_dir?: string;
    results?: { draft_id: string; xray_key?: string; action?: string }[];
  } | null>(null);

  const loadMeta = useCallback(() => {
    setError("");
    fetch("/api/health")
      .then((r) => (r.ok ? r.json() : null))
      .then((health: { features?: string[] } | null) => {
        if (health && !health.features?.includes("importer_plan")) {
          throw new Error(
            "Studio API is outdated (missing Importer). Restart: ./Trinity/studio/scripts/start.sh"
          );
        }
      })
      .then(() => Promise.all([api.importerInstances(), api.importerMappings()]))
      .then(([inst, maps]) => {
        setInstances(inst.instances);
        setMappings(maps.mappings);
        if (inst.instances.length) {
          setJiraInstanceId((prev) => {
            if (prev && inst.instances.some((i) => i.id === prev)) return prev;
            const sandbox = inst.instances.find((i) => i.risk_tier !== "production");
            return (sandbox ?? inst.instances[0]).id;
          });
        }
      })
      .catch((e) => {
        const msg = String(e);
        if (msg.includes("Not Found") || msg.includes('"detail":"Not Found"')) {
          setError(
            "Importer API not found — the API on :8765 was started before Importer was added. Stop it and run ./Trinity/studio/scripts/start.sh again."
          );
        } else {
          setError(msg.replace(/^Error:\s*/, ""));
        }
      });
  }, []);

  const loadStudioRuns = useCallback(() => {
    api.creatorRuns().then(setCreatorRuns).catch(() => {});
    api.runs().then(setReviewerRuns).catch(() => {});
  }, []);

  useEffect(() => {
    loadMeta();
    loadStudioRuns();
  }, [loadMeta, loadStudioRuns]);

  useEffect(() => {
    if (!creatorRunId && !payloadPath) return;
    const params = new URLSearchParams();
    if (creatorRunId) params.set("creator_run_id", creatorRunId);
    if (payloadPath) params.set("payload_path", payloadPath);
    fetch(`/api/importer/defaults?${params}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((d: { default_jira_project_key?: string; suggested_folder_path?: string } | null) => {
        if (!d) return;
        if (d.default_jira_project_key && !projectKey) {
          setProjectKey(d.default_jira_project_key);
        }
        if (
          d.suggested_folder_path &&
          (folderPath === DEFAULT_FOLDER_PATH || folderPath === "/Trinity sandbox")
        ) {
          setFolderPath(d.suggested_folder_path);
        }
      })
      .catch(() => {});
  }, [creatorRunId, payloadPath]);

  const sortedCreatorRuns = useMemo(
    () => [...creatorRuns].sort((a, b) => a.label.localeCompare(b.label, undefined, { sensitivity: "base" })),
    [creatorRuns]
  );

  const selectedCreatorRun = useMemo(
    () => creatorRuns.find((r) => r.id === creatorRunId),
    [creatorRuns, creatorRunId]
  );

  const selectedInstance = useMemo(
    () => instances.find((i) => i.id === jiraInstanceId),
    [instances, jiraInstanceId]
  );

  const isProduction = selectedInstance?.risk_tier === "production";

  const requireProductionConfirm = (): boolean => {
    if (!isProduction) return true;
    if (prodConfirm.trim() !== "PRODUCTION") {
      setError('Production instance selected — type PRODUCTION in the confirmation field below.');
      return false;
    }
    return true;
  };

  const mappingOptions = useMemo(() => {
    if (!selectedInstance) return mappings;
    const site = selectedInstance.jira_site.replace(/\/$/, "");
    const filtered = mappings.filter(
      (m) => !m.jira_site || m.jira_site.replace(/\/$/, "") === site
    );
    return filtered.length ? filtered : mappings;
  }, [mappings, selectedInstance]);

  useEffect(() => {
    if (!jiraInstanceId || mappingOptions.length === 0) return;
    const match =
      mappingOptions.find((m) => m.id === jiraInstanceId) ||
      mappingOptions.find(
        (m) => jiraInstanceId.includes("sandbox") && m.id.includes("sandbox")
      ) ||
      mappingOptions.find(
        (m) => jiraInstanceId.includes("production") && m.id.includes("production")
      ) ||
      mappingOptions[0];
    setMappingPath(match.path);
    if (match.default_folder) {
      setFolderPath(match.default_folder);
    }
    if (match.project_key) {
      setProjectKey(match.project_key);
    }
  }, [jiraInstanceId, mappingOptions]);

  useEffect(() => {
    if (!jiraInstanceId || !mappingPath) return;
    api
      .importerJiraProjects(jiraInstanceId, mappingPath)
      .then((res) => {
        if (res.status === "ok") {
          setJiraProjects(res.projects.map((p) => ({ key: p.key, name: p.name })));
          setProjectsHint("");
        } else {
          setJiraProjects([]);
          setProjectsHint(res.message ?? "Could not load Jira projects — type a project key manually.");
        }
      })
      .catch(() => {
        setJiraProjects([]);
        setProjectsHint("Could not load Jira projects — type a project key manually.");
      });
  }, [jiraInstanceId, mappingPath]);

  const onPreview = async () => {
    setError("");
    setPlan(null);
    if (!requireProductionConfirm()) return;
    if (!creatorRunId && !payloadPath) {
      setError("Provide a Creator run id or path to importer-payload.json");
      return;
    }
    setLoading(true);
    try {
      const result = await api.importerPlan({
        jira_instance_id: jiraInstanceId,
        folder_path: folderPath,
        create_folder_if_missing: createFolder,
        mapping_path: mappingPath || null,
        project_key_override: projectKey.trim() || null,
        payload_path: payloadPath || null,
        creator_run_id: creatorRunId || null,
        skip_requirement_link: skipRequirementLink,
        reviewer_gate_acknowledged: reviewerGateAck,
        idempotency_acknowledged: idempotencyAck,
      });
      setPlan(result);
      setCopyMsg("");
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  const onCopyPrompt = async () => {
    if (!plan?.cursor_prompt) return;
    if (!requireProductionConfirm()) return;
    try {
      await navigator.clipboard.writeText(plan.cursor_prompt);
      setCopyMsg("Importer Cursor prompt copied — paste into a new Cursor chat.");
    } catch (e) {
      setCopyMsg(String(e));
    }
  };

  const onExecute = async () => {
    setError("");
    setExecuteResult(null);
    if (!requireProductionConfirm()) return;
    if (!plan?.credentials.execute_ready) {
      setError("Plan is not execute-ready — fix validation, credentials, or Reviewer gate acknowledgement.");
      return;
    }
    if (plan.reviewer_gate?.requires_acknowledgement && !reviewerGateAck) {
      setError("Acknowledge Reviewer gate and re-run Preview before execute.");
      return;
    }
    if (plan.idempotency?.requires_acknowledgement && !idempotencyAck) {
      setError("Acknowledge existing Xray keys and re-run Preview before execute.");
      return;
    }
    setExecuting(true);
    try {
      const res = await api.importerExecute({
        jira_instance_id: jiraInstanceId,
        folder_path: folderPath,
        create_folder_if_missing: createFolder,
        mapping_path: mappingPath || null,
        project_key_override: projectKey.trim() || null,
        payload_path: payloadPath || null,
        creator_run_id: creatorRunId || null,
        skip_requirement_link: skipRequirementLink,
        reviewer_gate_acknowledged: reviewerGateAck,
        idempotency_acknowledged: idempotencyAck,
        production_confirm: isProduction ? prodConfirm.trim() : undefined,
      });
      setExecuteResult(res);
      setRecordMsg(
        `Execute finished: ${res.created}/${res.total} created. Keys persisted when Creator run id was set.`
      );
      if (res.report_dir) setReportPath(res.report_dir);
    } catch (e) {
      setError(String(e));
    } finally {
      setExecuting(false);
    }
  };

  const onRecordResults = async () => {
    setError("");
    setRecordMsg("");
    if (!creatorRunId) {
      setError("Creator run id is required to persist Xray keys");
      return;
    }
    if (!reportPath.trim()) {
      setError("Path to xray-import-report.json or folder containing import reports");
      return;
    }
    try {
      const res = await api.recordImporterResults({
        creator_run_id: creatorRunId,
        report_path: reportPath.trim(),
      });
      setRecordMsg(`Persisted ${res.updated} Xray key(s) to Studio (${res.skipped} skipped).`);
    } catch (e) {
      setError(String(e));
    }
  };

  return (
    <>
      <h2 className="page-title-row">
        Importer
        {selectedInstance && (
          <span
            className={`risk-pill risk-pill--${selectedInstance.risk_tier === "production" ? "production" : "sandbox"}`}
          >
            {selectedInstance.risk_tier}
          </span>
        )}
      </h2>
      <p className="muted">
        Choose the Jira/Xray target, mapping config, and Test Repository folder before dry-run or execute.
        Use <strong>Preview import plan</strong>, then <strong>Execute import batch</strong> when execute-ready (or copy the Cursor prompt).
      </p>
      {error && <p className="error">{error}</p>}

      <div className="panel importer-panel">
        <h3>Target Jira instance</h3>
        <label>
          Instance
          <select value={jiraInstanceId} onChange={(e) => setJiraInstanceId(e.target.value)}>
            {instances.map((i) => (
              <option key={i.id} value={i.id}>
                {i.label} ({i.risk_tier}) — {i.jira_site}
              </option>
            ))}
          </select>
        </label>
        {selectedInstance?.credential_hint && (
          <p className="muted importer-hint">{selectedInstance.credential_hint}</p>
        )}
        {isProduction && (
          <div className="production-guard panel">
            <p>
              <span className="risk-pill risk-pill--production">PRODUCTION</span>
              {" "}
              Xray writes target live Jira. Type <strong>PRODUCTION</strong> to preview the plan or copy
              the execute prompt.
            </p>
            <label>
              Confirmation
              <input
                type="text"
                value={prodConfirm}
                onChange={(e) => setProdConfirm(e.target.value)}
                placeholder="Type PRODUCTION"
                autoComplete="off"
              />
            </label>
          </div>
        )}

        <h3>Import mapping config</h3>
        <label>
          Mapping file
          <select value={mappingPath} onChange={(e) => setMappingPath(e.target.value)}>
            {mappingOptions.map((m) => (
              <option key={m.id} value={m.path}>
                {m.id} — {m.project_key ?? "?"} @ {m.jira_site ?? "?"}
              </option>
            ))}
          </select>
        </label>
        <h3>Jira project for new Tests</h3>
        <p className="muted importer-hint">
          Default <strong>TC</strong> in shipped mappings is the Appfire QA Test project used for the
          committed golden export — not tied to Creator output. Pick any project your account can create
          Tests in, or add a mapping file per project (see{" "}
          <code>Trinity/importer/config/mappings/README.md</code>).
        </p>
        <label>
          Project key
          <input
            type="text"
            list="importer-jira-projects"
            value={projectKey}
            onChange={(e) => setProjectKey(e.target.value.toUpperCase())}
            placeholder="e.g. TC, BPQA"
            required
          />
          <datalist id="importer-jira-projects">
            {jiraProjects.map((p) => (
              <option key={p.key} value={p.key}>
                {p.name}
              </option>
            ))}
          </datalist>
        </label>
        {projectsHint && <p className="muted importer-hint">{projectsHint}</p>}

        <h3>Test Repository location</h3>
        <label>
          Folder path
          <input
            type="text"
            value={folderPath}
            onChange={(e) => setFolderPath(e.target.value)}
            placeholder="/Parent/Child folder"
          />
        </label>
        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={createFolder}
            onChange={(e) => setCreateFolder(e.target.checked)}
          />
          Create folder if it does not exist (Xray <code>createFolder</code> before import)
        </label>
        <p className="muted">
          Paths are Xray Test Repository paths (leading <code>/</code>). Nested folders use{" "}
          <code>/Parent/Child</code>.
        </p>

        <h3>Handoff payload</h3>
        <label>
          Creator run
          <select value={creatorRunId} onChange={(e) => setCreatorRunId(e.target.value)}>
            <option value="">— Select a run —</option>
            {sortedCreatorRuns.map((r) => {
              const meta: string[] = [];
              if (r.test_count != null && r.test_count > 0) meta.push(`${r.test_count} tests`);
              if (r.status && r.status !== "imported") meta.push(r.status);
              const suffix = meta.length ? ` · ${meta.join(" · ")}` : "";
              return (
                <option key={r.id} value={r.id}>
                  {r.label}
                  {suffix}
                </option>
              );
            })}
          </select>
        </label>
        {selectedCreatorRun && (
          <p className="muted importer-hint">
            {selectedCreatorRun.label !== selectedCreatorRun.id ? (
              <>
                Stable id <code>{selectedCreatorRun.id}</code>
                {" · "}
              </>
            ) : null}
            <Link to={`/creator/${encodeURIComponent(selectedCreatorRun.id)}`}>Open in Creator</Link>
          </p>
        )}
        <label>
          Or importer-payload.json path
          <input
            type="text"
            value={payloadPath}
            onChange={(e) => setPayloadPath(e.target.value)}
            placeholder="Trinity/studio/data/exports/creator/…/importer-payload.json"
          />
        </label>
        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={skipRequirementLink}
            onChange={(e) => setSkipRequirementLink(e.target.checked)}
          />
          Skip requirement linking (dry-run only)
        </label>

        <div className="btn-row">
          <button type="button" onClick={onPreview} disabled={loading}>
            {loading ? "Building plan…" : "Preview import plan"}
          </button>
        </div>
      </div>

      {plan && (
        <div className="panel">
          <h3>Import plan (dry-run)</h3>
          <p>
            <span className={`risk-pill risk-pill--${plan.jira_instance.risk_tier}`}>
              {plan.jira_instance.label}
            </span>
            {" · "}
            Folder <code>{plan.target.folder_path}</code>
            {plan.target.create_folder_if_missing ? " · will call createFolder" : " · folder must exist"}
          </p>
          <p className="muted">
            {plan.summary.valid}/{plan.summary.total} tests ready · mapping{" "}
            <code>{plan.mapping.path.split("/").pop()}</code> · project{" "}
            <code>{plan.project_key}</code>
            {plan.project_resolution?.project_id != null && (
              <>
                {" "}
                · id <code>{String(plan.project_resolution.project_id)}</code>
              </>
            )}
          </p>
          {plan.reviewer_gate?.requires_acknowledgement && (
            <div className="production-guard panel">
              <p>
                <strong>Reviewer gate ({plan.reviewer_gate.level})</strong>
              </p>
              <ul className="importer-warnings">
                {(plan.reviewer_gate.messages ?? []).map((m) => (
                  <li key={m}>{m}</li>
                ))}
              </ul>
              {plan.reviewer_gate.review_ref_path && (
                <p className="muted">
                  review_ref: <code>{plan.reviewer_gate.review_ref_path}</code>
                </p>
              )}
              <label className="checkbox-row">
                <input
                  type="checkbox"
                  checked={reviewerGateAck}
                  onChange={(e) => setReviewerGateAck(e.target.checked)}
                />
                I acknowledge Reviewer findings and accept proceeding to Xray import
              </label>
              {!reviewerGateAck && (
                <p className="muted">
                  Re-run <strong>Preview import plan</strong> after checking this box to mark execute
                  ready.
                </p>
              )}
            </div>
          )}
          {plan.pm_safe_summary && (
            <p className="muted">
              <strong>PM summary:</strong> {plan.pm_safe_summary}
            </p>
          )}
          {(plan.export_preflight_warnings?.length ?? 0) > 0 && (
            <ul className="importer-warnings">
              {plan.export_preflight_warnings!.map((w) => (
                <li key={w}>{w}</li>
              ))}
            </ul>
          )}
          {(plan.export_preflight_redaction?.length ?? 0) > 0 && (
            <div className="production-guard panel">
              <p>
                <strong>Export preflight redaction</strong> — execute blocked until tests are fixed
                (or emergency override via <code>STUDIO_IMPORTER_ALLOW_REDACTION_EXECUTE=1</code>).
              </p>
              <ul className="importer-warnings">
                {plan.export_preflight_redaction!.map((w) => (
                  <li key={w}>{w}</li>
                ))}
              </ul>
            </div>
          )}
          {plan.idempotency?.requires_acknowledgement && (
            <div className="production-guard panel">
              <p>
                <strong>Existing Xray keys in Studio</strong>
              </p>
              <ul className="importer-warnings">
                {(plan.idempotency.warnings ?? []).map((m) => (
                  <li key={m}>{m}</li>
                ))}
              </ul>
              <label className="checkbox-row">
                <input
                  type="checkbox"
                  checked={idempotencyAck}
                  onChange={(e) => setIdempotencyAck(e.target.checked)}
                />
                I understand re-import may duplicate or conflict with existing Xray tests
              </label>
              {!idempotencyAck && (
                <p className="muted">
                  Re-run <strong>Preview import plan</strong> after checking this box to mark execute
                  ready.
                </p>
              )}
            </div>
          )}
          {plan.target.warnings.length > 0 && (
            <ul className="importer-warnings">
              {plan.target.warnings.map((w) => (
                <li key={w}>{w}</li>
              ))}
            </ul>
          )}
          <p>
            Credentials for execute: Xray{" "}
            {plan.credentials.xray_client_id && plan.credentials.xray_client_secret ? "✓" : "✗"} · Jira{" "}
            {plan.credentials.jira_email && plan.credentials.jira_api_token ? "✓" : "✗"}
            {plan.credentials.execute_ready ? (
              <span className="ok-msg"> — ready for execute (when enabled)</span>
            ) : (
              <span className="muted">
                — not execute-ready
                {(plan.execute_blockers?.length ?? 0) > 0 && (
                  <> ({plan.execute_blockers!.join(", ")})</>
                )}
              </span>
            )}
          </p>
          <div className="btn-row">
            <button
              type="button"
              onClick={onExecute}
              disabled={!plan.credentials.execute_ready || executing}
            >
              {executing ? "Executing…" : "Execute import batch"}
            </button>
            {plan.cursor_prompt && (
              <CursorAgentControl
                label="Run Importer in Cursor"
                disabled={!plan.credentials.execute_ready}
                attach={creatorRunId ? { stage: "importer", creatorRunId } : undefined}
                launch={() =>
                  api.launchImporterAgent({
                    jira_instance_id: jiraInstanceId,
                    folder_path: folderPath,
                    create_folder_if_missing: createFolder,
                    mapping_path: mappingPath || null,
                    project_key_override: projectKey.trim() || null,
                    payload_path: payloadPath || null,
                    creator_run_id: creatorRunId || null,
                    skip_requirement_link: skipRequirementLink,
                    reviewer_gate_acknowledged: reviewerGateAck,
                    idempotency_acknowledged: idempotencyAck,
                    production_confirm: isProduction ? prodConfirm.trim() : undefined,
                  })
                }
                onFinished={(run) =>
                  setCopyMsg(
                    run.status === "finished"
                      ? "Importer agent finished. Record its Xray keys below."
                      : `Importer agent ended with status ${run.status}.`
                  )
                }
              />
            )}
            <button type="button" onClick={onCopyPrompt} disabled={!plan.cursor_prompt}>
              Copy Cursor prompt
            </button>
          </div>
          {executeResult && (
            <ul className="muted">
              {executeResult.results?.map((r) => (
                <li key={r.draft_id}>
                  {r.draft_id}: {r.action}
                  {r.xray_key ? ` → ${r.xray_key}` : ""}
                </li>
              ))}
            </ul>
          )}
          {copyMsg && <p className="muted">{copyMsg}</p>}
          {isProduction && plan.credentials.execute_ready && (
            <p className="muted">
              After CLI/agent execute, paste the report folder path below to store Xray keys in Studio.
            </p>
          )}
          {plan.cursor_prompt && (
            <details className="prompt-preview" style={{ marginTop: "0.75rem" }}>
              <summary>Preview handoff prompt</summary>
              <pre className="prompt-pre">{plan.cursor_prompt}</pre>
            </details>
          )}
          <SortableDataTable
            rows={plan.tests}
            rowKey={(t) => t.draft_id}
            defaultSort={{ columnId: "draft_id", dir: "asc" }}
            columns={[
              { id: "draft_id", header: "Draft", getValue: (t) => t.draft_id },
              { id: "title", header: "Title", getValue: (t) => t.title },
              {
                id: "type",
                header: "Xray type",
                getValue: (t) => t.xray_test_type ?? "Manual",
                render: (t) => (
                  <>
                    {t.xray_test_type ?? "Manual"}
                    {t.test_type_coercion && (
                      <span className="muted" style={{ display: "block", fontSize: "0.85rem" }}>
                        {t.test_type_coercion}
                      </span>
                    )}
                  </>
                ),
              },
              { id: "action", header: "Action", getValue: (t) => t.action },
              {
                id: "validation",
                header: "Validation",
                getValue: (t) => (t.validation_errors.length === 0 ? "OK" : t.validation_errors.join("; ")),
              },
            ]}
          />
        </div>
      )}

      <div className="panel">
        <h3>Record Xray import results (Studio)</h3>
        <p className="muted">
          After execute, point to <code>xray-import-report.json</code> or a folder (e.g.{" "}
          <code>…/xray-import-run/</code>). Maps <code>draft_id</code> → <code>xray_test_key</code> on
          the Creator run for metrics and scorecard evidence.
        </p>
        <label>
          Report file or folder path
          <input
            type="text"
            value={reportPath}
            onChange={(e) => setReportPath(e.target.value)}
            placeholder="Trinity/studio/data/exports/creator/RUN/xray-import-run"
          />
        </label>
        <div className="btn-row">
          <button type="button" className="secondary" onClick={onRecordResults}>
            Persist Xray keys
          </button>
        </div>
        {recordMsg && <p className="muted">{recordMsg}</p>}
      </div>

      <div className="panel">
        <h3 style={{ marginTop: 0 }}>Reviewer runs</h3>
        {reviewerRuns.length === 0 ? (
          <p className="muted">No Reviewer runs imported.</p>
        ) : (
          <ReviewerRunsTable runs={reviewerRuns} onChanged={loadStudioRuns} />
        )}
      </div>

      <div className="panel">
        <h3 style={{ marginTop: 0 }}>Creator runs (manage)</h3>
        <p className="muted">
          Stable <code>cr-…</code> IDs join to <code>metric_event</code> / BigQuery. Rename is display-only; ID never changes.
        </p>
        {creatorRuns.length === 0 ? (
          <p className="muted">No Creator runs yet.</p>
        ) : (
          <CreatorRunsManageTable
            runs={creatorRuns}
            onChanged={loadStudioRuns}
            onRowAction={(id) => {
              if (creatorRunId === id) setCreatorRunId("");
            }}
          />
        )}
      </div>

      <p>
        <Link to="/creator">← Creator</Link>
      </p>
    </>
  );
}
