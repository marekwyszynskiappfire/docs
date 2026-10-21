import { useState } from "react";
import { Link } from "react-router-dom";
import { api, WorkspaceEpic } from "../../api";

type OtherRun = { id: string; label: string; test_count?: number; status: string };

type Props = {
  epics: WorkspaceEpic[];
  onNote: (message: string) => void;
  onImported: () => void;
};

export default function CreatorRunsPanel({ epics, onNote, onImported }: Props) {
  const runs = epics.filter((epic) => epic.creator_run_id);
  const [paths, setPaths] = useState<Record<string, string>>({});
  const [busyId, setBusyId] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [otherRuns, setOtherRuns] = useState<OtherRun[] | null>(null);
  const [suitePath, setSuitePath] = useState("");
  const [importing, setImporting] = useState(false);

  const loadOthers = () => {
    const linked = new Set(runs.map((epic) => epic.creator_run_id));
    api
      .creatorRuns()
      .then((rows) => setOtherRuns(rows.filter((row) => !linked.has(row.id))))
      .catch((reason) => setError(String(reason)));
  };

  const importSuite = async () => {
    const path = suitePath.trim();
    if (!path) {
      setError("Enter the path to suite-payload.json or another suite batch.");
      return;
    }
    setImporting(true);
    setError("");
    try {
      const result = await api.importBatch(path);
      onNote(
        `Imported ${result.tests_imported} test(s) into Creator run ${result.creator_run_id}.`
      );
      onImported();
      setOtherRuns(null);
    } catch (reason) {
      setError(String(reason));
    } finally {
      setImporting(false);
    }
  };

  const exportRun = async (creatorRunId: string) => {
    setBusyId(creatorRunId);
    setError("");
    try {
      const result = await api.exportForImporter(creatorRunId);
      setPaths((current) => ({ ...current, [creatorRunId]: result.path }));
      const warnings = result.export_preflight_warnings?.length
        ? ` ${result.export_preflight_warnings.join("; ")}`
        : "";
      onNote(`Exported ${result.test_count} test(s) for Importer.${warnings}`);
    } catch (reason) {
      setError(String(reason));
    } finally {
      setBusyId(null);
    }
  };

  return (
    <details
      className="panel ws-creator-runs"
      onToggle={(event) => {
        if (event.currentTarget.open) loadOthers();
      }}
    >
      <summary>Creator runs{runs.length > 0 ? ` · ${runs.length} on this workspace` : ""}</summary>
      {runs.length === 0 ? (
        <p className="muted">No Creator runs in this workspace yet. Import a suite on an Epic first.</p>
      ) : (
        <table className="data">
          <thead>
            <tr>
              <th>Epic</th>
              <th>Tests</th>
              <th>Approved</th>
              <th>Marked</th>
              <th>Status</th>
              <th>Export</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((epic) => {
              const creatorRunId = epic.creator_run_id!;
              return (
                <tr key={creatorRunId}>
                  <td>
                    <strong>{epic.jira_key}</strong>
                    <div>
                      <code>{creatorRunId}</code>
                    </div>
                  </td>
                  <td>{epic.tests.total}</td>
                  <td>{epic.tests.approved}</td>
                  <td>{epic.tests.marked}</td>
                  <td>{epic.creator_run_status ?? "—"}</td>
                  <td>
                    <button
                      type="button"
                      onClick={() => exportRun(creatorRunId)}
                      disabled={busyId === creatorRunId}
                    >
                      {busyId === creatorRunId ? "Exporting…" : "Export for Importer"}
                    </button>
                    {paths[creatorRunId] && (
                      <p className="muted">
                        <code>{paths[creatorRunId]}</code>
                      </p>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
      <p className="muted">
        Export writes the approved and marked tests to <code>importer-payload.json</code>. The Xray plan on this
        workspace uses the Creator run directly.
      </p>
      <label>
        Suite file not on an Epic here
        <input
          value={suitePath}
          onChange={(event) => setSuitePath(event.target.value)}
          placeholder="Trinity/creator/artifacts/EPIC/suite-payload.json"
          aria-label="Suite file path"
          spellCheck={false}
        />
      </label>
      <div className="btn-row">
        <button type="button" onClick={importSuite} disabled={importing}>
          {importing ? "Importing…" : "Import suite"}
        </button>
      </div>
      <p className="muted">
        This imports a suite even when its Epic is not on this workspace. The file’s <code>review_ref</code> decides
        which run it joins.
      </p>
      {otherRuns && otherRuns.length > 0 && (
        <>
          <p className="muted">Other Creator runs in Studio</p>
          <table className="data">
            <thead>
              <tr>
                <th>Run</th>
                <th>Tests</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {otherRuns.map((run) => (
                <tr key={run.id}>
                  <td>
                    <Link to={`/creator/${encodeURIComponent(run.id)}`}>{run.label}</Link>
                    <div>
                      <code>{run.id}</code>
                    </div>
                  </td>
                  <td>{run.test_count ?? "—"}</td>
                  <td>{run.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
      {error && <p className="error">{error}</p>}
    </details>
  );
}
