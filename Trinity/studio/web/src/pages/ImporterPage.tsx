import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api, ImporterPlanResult } from "../api";

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

  const [jiraInstanceId, setJiraInstanceId] = useState("appfire-sandbox-774");
  const [mappingPath, setMappingPath] = useState("");
  const [folderPath, setFolderPath] = useState("/Trinity sandbox");
  const [createFolder, setCreateFolder] = useState(true);
  const [projectKey, setProjectKey] = useState("");
  const [creatorRunId, setCreatorRunId] = useState(initialRunId);
  const [payloadPath, setPayloadPath] = useState(initialPayload);
  const [skipRequirementLink, setSkipRequirementLink] = useState(false);

  const [plan, setPlan] = useState<ImporterPlanResult | null>(null);
  const [copyMsg, setCopyMsg] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

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
          setJiraInstanceId((prev) =>
            inst.instances.some((i) => i.id === prev) ? prev : inst.instances[0].id
          );
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

  useEffect(() => {
    loadMeta();
  }, [loadMeta]);

  const selectedInstance = useMemo(
    () => instances.find((i) => i.id === jiraInstanceId),
    [instances, jiraInstanceId]
  );

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
  }, [jiraInstanceId, mappingOptions]);

  const onPreview = async () => {
    setError("");
    setPlan(null);
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
        project_key_override: projectKey || null,
        payload_path: payloadPath || null,
        creator_run_id: creatorRunId || null,
        skip_requirement_link: skipRequirementLink,
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
    try {
      await navigator.clipboard.writeText(plan.cursor_prompt);
      setCopyMsg("Importer Cursor prompt copied — paste into a new Cursor chat.");
    } catch (e) {
      setCopyMsg(String(e));
    }
  };

  return (
    <>
      <h2>Importer</h2>
      <p className="muted">
        Choose the Jira/Xray target, mapping config, and Test Repository folder before dry-run or execute.
        Execute (Xray submit) is planned next — use <strong>Preview import plan</strong> to validate today.
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
        <label>
          Project key override (optional)
          <input
            type="text"
            value={projectKey}
            onChange={(e) => setProjectKey(e.target.value)}
            placeholder="Uses mapping default when empty"
          />
        </label>

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
          Creator run id
          <input
            type="text"
            value={creatorRunId}
            onChange={(e) => setCreatorRunId(e.target.value)}
            placeholder="From Studio Creator run"
          />
        </label>
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
          </p>
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
              <span className="muted"> — set env vars before execute</span>
            )}
          </p>
          <div className="btn-row">
            <button type="button" onClick={onCopyPrompt} disabled={!plan.cursor_prompt}>
              Copy Cursor prompt
            </button>
          </div>
          {copyMsg && <p className="muted">{copyMsg}</p>}
          {plan.cursor_prompt && (
            <details className="prompt-preview" style={{ marginTop: "0.75rem" }}>
              <summary>Preview handoff prompt</summary>
              <pre className="prompt-pre">{plan.cursor_prompt}</pre>
            </details>
          )}
          <table className="data">
            <thead>
              <tr>
                <th>Draft</th>
                <th>Title</th>
                <th>Action</th>
                <th>Validation</th>
              </tr>
            </thead>
            <tbody>
              {plan.tests.map((t) => (
                <tr key={t.draft_id}>
                  <td>{t.draft_id}</td>
                  <td>{t.title}</td>
                  <td>{t.action}</td>
                  <td>
                    {t.validation_errors.length === 0
                      ? "OK"
                      : t.validation_errors.join("; ")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <p>
        <Link to="/creator">← Creator</Link>
      </p>
    </>
  );
}
