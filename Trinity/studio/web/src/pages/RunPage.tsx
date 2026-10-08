import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, ReviewUnit } from "../api";

type Handoff = {
  creator_jql?: string;
  included_epics?: string[];
  excluded_from_creator_count?: number;
  portfolio_report_path?: string | null;
  source_path?: string | null;
  handoff_export?: Record<string, unknown>;
};

export default function RunPage() {
  const { runId } = useParams<{ runId: string }>();
  const [units, setUnits] = useState<ReviewUnit[]>([]);
  const [sourcePath, setSourcePath] = useState<string | null>(null);
  const [handoff, setHandoff] = useState<Handoff | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  const reload = useCallback(async () => {
    if (!runId) return;
    const r = await api.run(runId);
    setUnits(r.units);
    setSourcePath(r.source_path);
    const h = await api.creatorHandoff(runId);
    setHandoff(h as Handoff);
  }, [runId]);

  useEffect(() => {
    if (!runId) return;
    reload().catch((e) => setError(String(e)));
  }, [runId, reload]);

  const copyText = async (text: string, okMsg: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setMessage(okMsg);
      setError("");
    } catch {
      setError("Clipboard failed");
    }
  };

  const exportJson = handoff?.handoff_export ?? handoff;

  const downloadHandoff = () => {
    if (!exportJson || !runId) return;
    const blob = new Blob([JSON.stringify(exportJson, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `creator-handoff-${runId}.json`;
    a.click();
    URL.revokeObjectURL(url);
    setMessage("Downloaded creator-handoff JSON");
  };

  const setAllCreator = async (
    include: boolean,
    filter?: (u: ReviewUnit) => boolean
  ) => {
    setBusy(true);
    setError("");
    try {
      const targets = filter ? units.filter(filter) : units;
      await Promise.all(
        targets.map((u) => api.patchUnit(u.id, { include_in_creator: include }))
      );
      await reload();
      setMessage(
        include
          ? `Included ${targets.length} epic(s) for Creator`
          : `Excluded ${targets.length} epic(s) from Creator`
      );
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  };

  const toggleCreator = async (u: ReviewUnit) => {
    await api.patchUnit(u.id, { include_in_creator: !u.include_in_creator });
    await reload();
  };

  if (!runId) return null;

  return (
    <>
      <p>
        <Link to="/">← Dashboard</Link>
      </p>
      <h2>{runId}</h2>
      {sourcePath && (
        <p className="muted">
          Imported from: <code>{sourcePath}</code>
        </p>
      )}
      {error && <p className="error">{error}</p>}
      {message && <p className="muted">{message}</p>}

      {handoff && (
        <div className="panel">
          <h3 style={{ marginTop: 0 }}>Creator handoff</h3>
          <p className="muted">
            Included: {handoff.included_epics?.length ?? 0} epic(s) · excluded from Creator:{" "}
            {handoff.excluded_from_creator_count ?? 0}
          </p>
          {handoff.portfolio_report_path && (
            <p>
              Portfolio report:{" "}
              <code>{handoff.portfolio_report_path}</code>
              <span className="btn-row" style={{ display: "inline-flex", marginLeft: "0.5rem" }}>
                <button
                  type="button"
                  className="secondary"
                  onClick={() =>
                    copyText(
                      handoff.portfolio_report_path!,
                      "Portfolio path copied"
                    )
                  }
                >
                  Copy path
                </button>
              </span>
              <span className="muted" style={{ display: "block", marginTop: "0.35rem" }}>
                Open in browser from repo root:{" "}
                <code>open {handoff.portfolio_report_path}</code> (macOS)
              </span>
            </p>
          )}
          <label>
            Creator JQL (live from Studio toggles)
            <textarea
              readOnly
              value={String(handoff.creator_jql ?? "")}
              rows={3}
              aria-label="Creator JQL"
            />
          </label>
          <div className="btn-row">
            <button
              type="button"
              onClick={() => copyText(String(handoff.creator_jql ?? ""), "JQL copied")}
            >
              Copy JQL
            </button>
            <button
              type="button"
              onClick={() =>
                copyText(JSON.stringify(exportJson, null, 2), "Handoff JSON copied")
              }
            >
              Copy handoff JSON
            </button>
            <button type="button" className="secondary" onClick={downloadHandoff}>
              Download JSON
            </button>
          </div>
          <details style={{ marginTop: "0.75rem" }}>
            <summary className="muted">Handoff JSON preview</summary>
            <pre className="prompt-pre">{JSON.stringify(exportJson, null, 2)}</pre>
          </details>
        </div>
      )}

      <div className="panel">
        <div className="btn-row" style={{ marginBottom: "0.75rem" }}>
          <button type="button" disabled={busy} onClick={() => setAllCreator(true)}>
            Include all
          </button>
          <button type="button" disabled={busy} onClick={() => setAllCreator(false)}>
            Exclude all
          </button>
          <button
            type="button"
            disabled={busy}
            className="secondary"
            onClick={() => setAllCreator(false, (u) => u.qa_planning_fit === "not_fit")}
          >
            Exclude not_fit
          </button>
        </div>
        <table className="data">
          <thead>
            <tr>
              <th>Epic</th>
              <th>Gate</th>
              <th>Test design fit</th>
              <th>In Creator</th>
              <th>Approved</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {units.map((u) => (
              <tr key={u.id}>
                <td>
                  <strong>{u.jira_key}</strong>
                  <div className="muted">{u.summary}</div>
                </td>
                <td>{u.gate_status}</td>
                <td>{u.qa_planning_fit ?? "—"}</td>
                <td>
                  <label style={{ display: "flex", alignItems: "center", gap: "0.35rem", margin: 0 }}>
                    <input
                      type="checkbox"
                      checked={Boolean(u.include_in_creator)}
                      onChange={() => toggleCreator(u)}
                    />
                    {u.include_in_creator ? "Yes" : "No"}
                  </label>
                </td>
                <td>
                  {u.approved_revision_id ? (
                    <span className="badge ok">yes</span>
                  ) : (
                    <span className="badge">no</span>
                  )}
                </td>
                <td>
                  <Link to={`/units/${u.id}`}>Edit review</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
