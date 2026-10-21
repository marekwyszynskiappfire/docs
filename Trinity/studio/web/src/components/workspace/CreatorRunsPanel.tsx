import { useState } from "react";
import { api, WorkspaceEpic } from "../../api";

type Props = {
  epics: WorkspaceEpic[];
  onNote: (message: string) => void;
};

export default function CreatorRunsPanel({ epics, onNote }: Props) {
  const runs = epics.filter((epic) => epic.creator_run_id);
  const [paths, setPaths] = useState<Record<string, string>>({});
  const [busyId, setBusyId] = useState<string | null>(null);
  const [error, setError] = useState("");

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
    <details className="panel ws-creator-runs">
      <summary>Creator runs{runs.length > 0 ? ` · ${runs.length}` : ""}</summary>
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
      {error && <p className="error">{error}</p>}
    </details>
  );
}
