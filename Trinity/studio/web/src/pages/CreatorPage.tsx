import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

export default function CreatorPage() {
  const [runs, setRuns] = useState<
    { id: string; label: string; test_count?: number; status: string }[]
  >([]);
  const [batchPath, setBatchPath] = useState("Trinity/creator/samples/demo-story.suite.json");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const load = () => {
    api.creatorRuns().then(setRuns).catch((e) => setError(String(e)));
  };

  useEffect(() => {
    load();
  }, []);

  const onImport = async () => {
    setBusy(true);
    setError("");
    try {
      await api.importBatch(batchPath);
      load();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <h2>Creator runs</h2>
      <div className="panel">
        <h3 style={{ marginTop: 0 }}>Import TestCaseDraft batch</h3>
        <p className="muted">
          Path to a suite batch JSON (<code>tests[]</code>, TestCaseDraft schema) relative to the DOCS repo root.
        </p>
        <input value={batchPath} onChange={(e) => setBatchPath(e.target.value)} />
        <div className="btn-row">
          <button type="button" onClick={onImport} disabled={busy}>
            Import batch
          </button>
        </div>
        {error && <p className="error">{error}</p>}
      </div>

      <div className="panel">
        <table className="data">
          <thead>
            <tr>
              <th>Run</th>
              <th>Tests</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((r) => (
              <tr key={r.id}>
                <td>
                  <Link to={`/creator/${encodeURIComponent(r.id)}`}>{r.label}</Link>
                </td>
                <td>{r.test_count}</td>
                <td>{r.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {runs.length === 0 && <p className="muted">No Creator batches imported yet.</p>}
      </div>
    </>
  );
}
