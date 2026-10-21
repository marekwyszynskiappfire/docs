import { useState } from "react";
import { api, WorkspaceEpic } from "../../api";

type Props = {
  epics: WorkspaceEpic[];
  focusKey: string | null;
  onRecorded: () => void;
};

export default function XrayKeyRecord({ epics, focusKey, onRecorded }: Props) {
  const runs = epics.filter((epic) => epic.creator_run_id);
  const initial = runs.find((epic) => epic.jira_key === focusKey)?.creator_run_id ?? runs[0]?.creator_run_id ?? "";
  const [creatorRunId, setCreatorRunId] = useState(initial);
  const [path, setPath] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [note, setNote] = useState("");

  const selected = creatorRunId || initial;

  const record = async () => {
    const report = path.trim();
    if (!selected) {
      setError("Import a suite before recording Xray keys.");
      return;
    }
    if (!report) {
      setError("Enter the path to xray-import-report.json or the folder that contains it.");
      return;
    }
    setBusy(true);
    setError("");
    setNote("");
    try {
      const result = await api.recordImporterResults({
        creator_run_id: selected,
        report_path: report,
      });
      setNote(`Stored ${result.updated} Xray key(s). ${result.skipped} skipped.`);
      onRecorded();
    } catch (reason) {
      setError(String(reason));
    } finally {
      setBusy(false);
    }
  };

  return (
    <details className="panel ws-xray-record">
      <summary>Record Xray keys</summary>
      <p className="muted">
        After trinity-importer writes from Cursor, point this at <code>xray-import-report.json</code> or the folder
        that contains it. Studio stores each key on the matching test.
      </p>
      {runs.length === 0 ? (
        <p className="muted">No Creator runs in this workspace yet.</p>
      ) : (
        <>
          {runs.length > 1 ? (
            <label>
              Creator run
              <select value={selected} onChange={(event) => setCreatorRunId(event.target.value)}>
                {runs.map((epic) => (
                  <option key={epic.creator_run_id!} value={epic.creator_run_id!}>
                    {epic.jira_key} · {epic.creator_run_id}
                  </option>
                ))}
              </select>
            </label>
          ) : (
            <p>
              Creator run <code>{runs[0].creator_run_id}</code> · {runs[0].jira_key}
            </p>
          )}
          <label>
            Report file or folder
            <input
              value={path}
              onChange={(event) => setPath(event.target.value)}
              placeholder="Trinity/studio/data/exports/creator/RUN/xray-import-run"
              spellCheck={false}
              aria-label="Xray import report"
            />
          </label>
          <div className="btn-row">
            <button type="button" onClick={record} disabled={busy}>
              {busy ? "Storing…" : "Persist Xray keys"}
            </button>
          </div>
        </>
      )}
      {note && <p className="ok-msg">{note}</p>}
      {error && <p className="error">{error}</p>}
    </details>
  );
}
