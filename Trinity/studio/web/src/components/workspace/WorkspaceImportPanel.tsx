import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api, ImporterPlanResult, WorkspaceEpic } from "../../api";
import CursorAgentControl from "./CursorAgentControl";

type Instance = {
  id: string;
  label: string;
  jira_site: string;
  risk_tier: string;
  credential_hint?: string;
};

type Mapping = {
  id: string;
  path: string;
  project_key?: string;
  default_folder?: string;
  jira_site?: string;
};

type Props = {
  epics: WorkspaceEpic[];
  focusKey: string | null;
  previewAllKey?: boolean;
  onImported: () => void;
};

type BatchPlan = {
  key: string;
  valid: number;
  total: number;
  ready: boolean;
  detail: string;
};

export default function WorkspaceImportPanel({ epics, focusKey, previewAllKey = false, onImported }: Props) {
  const ready = epics.filter(
    (epic) => epic.stage === "import" && epic.tests.marked > 0 && epic.creator_run_id
  );
  const [epicKey, setEpicKey] = useState(focusKey && ready.some((e) => e.jira_key === focusKey) ? focusKey : ready[0]?.jira_key ?? "");
  const [instances, setInstances] = useState<Instance[]>([]);
  const [mappings, setMappings] = useState<Mapping[]>([]);
  const [jiraInstanceId, setJiraInstanceId] = useState("");
  const [mappingPath, setMappingPath] = useState("");
  const [folderPath, setFolderPath] = useState("/Trinity imports");
  const [createFolder, setCreateFolder] = useState(true);
  const [projectKey, setProjectKey] = useState("");
  const [prodConfirm, setProdConfirm] = useState("");
  const [reviewerGateAck, setReviewerGateAck] = useState(false);
  const [idempotencyAck, setIdempotencyAck] = useState(false);
  const [plan, setPlan] = useState<ImporterPlanResult | null>(null);
  const [batchPlans, setBatchPlans] = useState<BatchPlan[] | null>(null);
  const [error, setError] = useState("");
  const [note, setNote] = useState("");
  const [loading, setLoading] = useState(false);
  const [executing, setExecuting] = useState(false);

  const epic = ready.find((item) => item.jira_key === epicKey) ?? ready[0];

  useEffect(() => {
    if (focusKey && ready.some((item) => item.jira_key === focusKey)) setEpicKey(focusKey);
  }, [focusKey, ready.map((item) => item.jira_key).join("|")]);

  const [payloadPath, setPayloadPath] = useState("");

  useEffect(() => {
    Promise.all([api.importerInstances(), api.importerMappings()])
      .then(([inst, maps]) => {
        setInstances(inst.instances);
        setMappings(maps.mappings);
        const preferred = inst.instances.find((item) => item.risk_tier !== "production") ?? inst.instances[0];
        if (preferred) setJiraInstanceId((current) => current || preferred.id);
      })
      .catch((reason) => setError(String(reason)));
  }, []);

  const selectedInstance = instances.find((item) => item.id === jiraInstanceId);
  const isProduction = selectedInstance?.risk_tier === "production";
  const mappingOptions = useMemo(() => {
    if (!selectedInstance) return mappings;
    const site = selectedInstance.jira_site.replace(/\/$/, "");
    const filtered = mappings.filter((item) => !item.jira_site || item.jira_site.replace(/\/$/, "") === site);
    return filtered.length ? filtered : mappings;
  }, [mappings, selectedInstance]);

  useEffect(() => {
    if (!jiraInstanceId || mappingOptions.length === 0) return;
    const match =
      mappingOptions.find((item) => item.id === jiraInstanceId) ||
      mappingOptions.find((item) => jiraInstanceId.includes("sandbox") && item.id.includes("sandbox")) ||
      mappingOptions.find((item) => jiraInstanceId.includes("production") && item.id.includes("production")) ||
      mappingOptions[0];
    setMappingPath(match.path);
    if (match.default_folder) setFolderPath(match.default_folder);
    if (match.project_key) setProjectKey(match.project_key);
  }, [jiraInstanceId, mappingOptions]);

  useEffect(() => {
    setPlan(null);
    setBatchPlans(null);
    setReviewerGateAck(false);
    setIdempotencyAck(false);
    setNote("");
  }, [epic?.creator_run_id, jiraInstanceId, mappingPath, folderPath, projectKey, payloadPath]);

  const usingPayload = payloadPath.trim().length > 0;
  const requestBody = {
    jira_instance_id: jiraInstanceId,
    folder_path: folderPath,
    create_folder_if_missing: createFolder,
    mapping_path: mappingPath || null,
    project_key_override: projectKey.trim() || null,
    creator_run_id: usingPayload ? null : epic?.creator_run_id ?? null,
    payload_path: usingPayload ? payloadPath.trim() : null,
    reviewer_gate_acknowledged: reviewerGateAck,
    idempotency_acknowledged: idempotencyAck,
  };

  const preview = async () => {
    setError("");
    setNote("");
    if (!usingPayload && !epic?.creator_run_id) {
      setError("Choose an Epic that is ready, or enter a path to importer-payload.json.");
      return;
    }
    if (isProduction && prodConfirm.trim() !== "PRODUCTION") {
      setError("Production instance selected. Type PRODUCTION to preview the plan.");
      return;
    }
    setLoading(true);
    try {
      setPlan(await api.importerPlan(requestBody));
    } catch (reason) {
      setError(String(reason));
    } finally {
      setLoading(false);
    }
  };

  const previewAll = async () => {
    setError("");
    setNote("");
    if (isProduction && prodConfirm.trim() !== "PRODUCTION") {
      setError("Production instance selected. Type PRODUCTION to preview the plans.");
      return;
    }
    setLoading(true);
    const rows: BatchPlan[] = [];
    for (const item of ready) {
      if (!item.creator_run_id) continue;
      try {
        const result = await api.importerPlan({
          ...requestBody,
          payload_path: null,
          creator_run_id: item.creator_run_id,
        });
        rows.push({
          key: item.jira_key,
          valid: result.summary.valid,
          total: result.summary.total,
          ready: result.credentials.execute_ready,
          detail: result.credentials.execute_ready
            ? "Ready to write."
            : result.execute_blockers?.join(", ") || "Not ready to write.",
        });
      } catch (reason) {
        rows.push({ key: item.jira_key, valid: 0, total: item.tests.marked, ready: false, detail: String(reason) });
      }
    }
    setBatchPlans(rows);
    setLoading(false);
  };

  const execute = async () => {
    setError("");
    if (!plan?.credentials.execute_ready) {
      setError("Preview the plan again after the confirmations are checked.");
      return;
    }
    if (isProduction && prodConfirm.trim() !== "PRODUCTION") {
      setError("Type PRODUCTION before writing to the production instance.");
      return;
    }
    setExecuting(true);
    try {
      const result = await api.importerExecute({
        ...requestBody,
        production_confirm: isProduction ? prodConfirm.trim() : undefined,
      });
      setNote(`${result.created} of ${result.total} test(s) created in Xray.`);
      setPlan(null);
      onImported();
    } catch (reason) {
      setError(String(reason));
    } finally {
      setExecuting(false);
    }
  };

  return (
    <section className="panel ws-import" id="ws-import">
      <h3>Xray import plan</h3>
      <p className="muted">
        {epic
          ? `${epic.tests.marked} test(s) from ${epic.jira_key}. Preview shows what would be written. Write to Xray runs only after this plan is ready.`
          : "No Epic on this workspace is ready to write. Enter a path to importer-payload.json to plan from that file."}
      </p>
      {ready.length > 1 && (
        <label>
          Epic
          <select value={epic.jira_key} onChange={(event) => setEpicKey(event.target.value)}>
            {ready.map((item) => (
              <option key={item.jira_key} value={item.jira_key}>
                {item.jira_key} · {item.tests.marked} chosen
              </option>
            ))}
          </select>
        </label>
      )}
      <label>
        Jira instance
        <select value={jiraInstanceId} onChange={(event) => setJiraInstanceId(event.target.value)}>
          {instances.map((item) => (
            <option key={item.id} value={item.id}>
              {item.label} ({item.risk_tier})
            </option>
          ))}
        </select>
      </label>
      {isProduction && (
        <div className="production-guard">
          <p>
            <span className="risk-pill risk-pill--production">PRODUCTION</span> Type PRODUCTION before a preview or a write.
          </p>
          <label>
            Confirmation
            <input
              value={prodConfirm}
              onChange={(event) => setProdConfirm(event.target.value)}
              placeholder="Type PRODUCTION"
              autoComplete="off"
            />
          </label>
        </div>
      )}
      <label>
        Mapping
        <select value={mappingPath} onChange={(event) => setMappingPath(event.target.value)}>
          {mappingOptions.map((item) => (
            <option key={item.id} value={item.path}>
              {item.id}
              {item.project_key ? ` · ${item.project_key}` : ""}
            </option>
          ))}
        </select>
      </label>
      <label>
        Project key
        <input value={projectKey} onChange={(event) => setProjectKey(event.target.value.toUpperCase())} />
      </label>
      <label>
        Test Repository folder
        <input value={folderPath} onChange={(event) => setFolderPath(event.target.value)} />
      </label>
      <label className="checkbox-row">
        <input type="checkbox" checked={createFolder} onChange={(event) => setCreateFolder(event.target.checked)} />
        Create the folder if it is missing
      </label>
      <label>
        Payload file
        <input
          value={payloadPath}
          onChange={(event) => setPayloadPath(event.target.value)}
          placeholder="Trinity/studio/data/exports/creator/RUN/importer-payload.json"
          aria-label="Importer payload path"
          spellCheck={false}
        />
      </label>
      <p className="muted">
        A payload path plans and writes that file instead of the Epic selected above. More → Importer still has the same
        fields.
      </p>
      <div className="btn-row">
        <button type="button" onClick={preview} disabled={loading || !jiraInstanceId}>
          {loading ? "Previewing…" : "Preview import plan"}
        </button>
        {previewAllKey && ready.length > 1 && !usingPayload && (
          <button type="button" className="secondary" onClick={previewAll} disabled={loading || !jiraInstanceId}>
            Preview plans for {ready.length} Epics
          </button>
        )}
        {epic?.creator_run_id && (
          <Link to={`/importer?creator_run_id=${encodeURIComponent(epic.creator_run_id)}`}>Full Importer page</Link>
        )}
      </div>
      {batchPlans && (
        <ul className="ws-plan-tests">
          {batchPlans.map((row) => (
            <li key={row.key}>
              {row.key}: {row.valid}/{row.total} ready · {row.detail}
            </li>
          ))}
        </ul>
      )}
      {error && <p className="error">{error}</p>}
      {note && <p className="ok-msg">{note}</p>}
      {plan && (
        <div className="ws-plan">
          <p>
            {plan.summary.valid}/{plan.summary.total} tests ready · project <code>{plan.project_key}</code> · folder{" "}
            <code>{plan.target.folder_path}</code>
          </p>
          {plan.reviewer_gate?.requires_acknowledgement && (
            <label className="checkbox-row">
              <input
                type="checkbox"
                checked={reviewerGateAck}
                onChange={(event) => setReviewerGateAck(event.target.checked)}
              />
              I accept proceeding with the Reviewer findings listed in the plan
            </label>
          )}
          {(plan.reviewer_gate?.messages ?? []).map((message) => (
            <p key={message} className="muted">
              {message}
            </p>
          ))}
          {plan.idempotency?.requires_acknowledgement && (
            <label className="checkbox-row">
              <input
                type="checkbox"
                checked={idempotencyAck}
                onChange={(event) => setIdempotencyAck(event.target.checked)}
              />
              I understand some of these tests already have Xray keys
            </label>
          )}
          {(plan.idempotency?.warnings ?? []).map((message) => (
            <p key={message} className="muted">
              {message}
            </p>
          ))}
          <ul className="ws-plan-tests">
            {plan.tests.map((test) => (
              <li key={test.draft_id}>
                {test.draft_id}
                {test.title ? ` · ${test.title}` : ""} · {test.action}
                {test.validation_errors.length > 0 ? ` · ${test.validation_errors.join("; ")}` : ""}
              </li>
            ))}
          </ul>
          <p className="muted">
            {plan.credentials.execute_ready
              ? "Plan is ready to write."
              : `Not ready to write${plan.execute_blockers?.length ? `: ${plan.execute_blockers.join(", ")}` : ". Fix the tests above, or check the confirmations and preview again."}`}
          </p>
          <button type="button" onClick={execute} disabled={!plan.credentials.execute_ready || executing}>
            {executing ? "Writing…" : "Write to Xray"}
          </button>
          {plan.cursor_prompt && (
            <details className="ws-importer-prompt">
              <summary>Importer Cursor prompt</summary>
              <p className="muted">
                Paste this into a new Cursor chat when you want trinity-importer to write, instead of Write to Xray here.
              </p>
              <div className="btn-row">
                <CursorAgentControl
                  label="Run Importer in Cursor"
                  disabled={!plan.credentials.execute_ready}
                  launch={() =>
                    api.launchImporterAgent({
                      ...requestBody,
                      production_confirm: isProduction ? prodConfirm.trim() : undefined,
                    })
                  }
                  onFinished={(run) =>
                    setNote(
                      run.status === "finished"
                        ? "Importer agent finished. Record the Xray keys below."
                        : `Importer agent ended with status ${run.status}.`
                    )
                  }
                />
                <button
                  type="button"
                  className="secondary"
                  onClick={async () => {
                    try {
                      await navigator.clipboard.writeText(plan.cursor_prompt ?? "");
                      setNote("Importer prompt copied. Paste it into a new Cursor chat.");
                    } catch {
                      setNote("Copy failed. Select the prompt text below.");
                    }
                  }}
                >
                  Copy Cursor prompt
                </button>
              </div>
              <pre className="prompt-pre">{plan.cursor_prompt}</pre>
            </details>
          )}
        </div>
      )}
    </section>
  );
}
