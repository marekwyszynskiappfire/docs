import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../../api";

type Props = {
  runId: string;
  onImported: () => void;
  onNote: (message: string) => void;
};

export default function ReviewFolderImport({ runId, onImported, onNote }: Props) {
  const navigate = useNavigate();
  const [path, setPath] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const importFolder = async () => {
    const folder = path.trim();
    if (!folder) {
      setError("Enter the folder that contains the Epic directories.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const result = await api.importRun(folder);
      if (result.pipeline_run_id === runId) {
        onNote(`Imported ${result.units_imported} Epic(s) into this workspace.`);
        onImported();
      } else {
        navigate(`/workspace/${encodeURIComponent(result.pipeline_run_id)}`);
      }
    } catch (reason) {
      setError(String(reason));
    } finally {
      setBusy(false);
    }
  };

  return (
    <details className="panel ws-review-import">
      <summary>Import a review folder</summary>
      <p className="muted">
        Use this when the review is not in Studio yet. Path is relative to the DOCS repo, or absolute. The folder
        must contain one directory per Epic, each with <code>review-payload.json</code>.
      </p>
      <label>
        Review folder
        <input
          value={path}
          onChange={(event) => setPath(event.target.value)}
          placeholder="Trinity/reviewer/runs/your-portfolio"
          spellCheck={false}
          aria-label="Review folder"
        />
      </label>
      <div className="btn-row">
        <button type="button" onClick={importFolder} disabled={busy}>
          {busy ? "Importing…" : "Import and open"}
        </button>
      </div>
      {error && <p className="error">{error}</p>}
    </details>
  );
}
