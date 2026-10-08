import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, PipelineRun, Stats } from "../api";

export default function HomePage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [runs, setRuns] = useState<PipelineRun[]>([]);
  const [importPath, setImportPath] = useState(
    "Trinity/reviewer/runs/<your-run-folder>"
  );
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const load = () => {
    api.stats().then(setStats).catch((e) => setError(String(e)));
    api.runs().then(setRuns).catch((e) => setError(String(e)));
  };

  useEffect(() => {
    load();
  }, []);

  const onImport = async () => {
    setBusy(true);
    setError("");
    try {
      await api.importRun(importPath);
      load();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="label">Pipeline runs</div>
            <div className="value">{stats.pipeline_runs}</div>
          </div>
          <div className="stat-card">
            <div className="label">Review units</div>
            <div className="value">{stats.review_units}</div>
          </div>
          <div className="stat-card">
            <div className="label">Approved reviews</div>
            <div className="value">{stats.review_units_approved}</div>
          </div>
          <div className="stat-card">
            <div className="label">Open findings</div>
            <div className="value">{stats.open_findings_latest}</div>
          </div>
          <div className="stat-card">
            <div className="label">Open questions</div>
            <div className="value">{stats.open_questions_latest}</div>
          </div>
          <div className="stat-card">
            <div className="label">Test cases</div>
            <div className="value">{stats.test_cases}</div>
          </div>
          <div className="stat-card">
            <div className="label">TC approved</div>
            <div className="value">{stats.test_cases_approved}</div>
          </div>
          <div className="stat-card">
            <div className="label">Automatable</div>
            <div className="value">{stats.test_cases_automation_candidate}</div>
          </div>
        </div>
      )}

      <div className="panel">
        <h2 style={{ marginTop: 0 }}>Import Reviewer run</h2>
        <p className="muted">
          Path relative to DOCS repo root, or absolute. Imports all{" "}
          <code>ONE-*/review-payload.json</code> into SQLite with revision history.
        </p>
        <input
          value={importPath}
          onChange={(e) => setImportPath(e.target.value)}
          aria-label="Reviewer run folder path"
        />
        <div className="btn-row">
          <button type="button" onClick={onImport} disabled={busy}>
            {busy ? "Importing…" : "Import run"}
          </button>
        </div>
        {error && <p className="error">{error}</p>}
      </div>

      <div className="panel">
        <h2 style={{ marginTop: 0 }}>Runs</h2>
        {runs.length === 0 && <p className="muted">No runs yet. Import a Reviewer folder.</p>}
        <table className="data">
          <thead>
            <tr>
              <th>Run</th>
              <th>Units</th>
              <th>Updated</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((r) => (
              <tr key={r.id}>
                <td>
                  <Link to={`/runs/${r.id}`}>{r.label}</Link>
                </td>
                <td>{r.unit_count ?? "—"}</td>
                <td className="muted">{r.updated_at.slice(0, 19)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
