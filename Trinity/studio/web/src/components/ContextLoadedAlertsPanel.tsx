import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

export default function ContextLoadedAlertsPanel() {
  const [data, setData] = useState<{
    alert_count: number;
    alerts: {
      pipeline_run_id: string;
      run_label: string;
      unit_id: string;
      jira_key: string;
      source: string;
      status: string;
      detail?: string;
    }[];
  } | null>(null);

  useEffect(() => {
    api.contextLoadedAlerts().then(setData).catch(() => setData(null));
  }, []);

  if (!data || data.alert_count === 0) {
    return (
      <div className="panel context-alerts-panel">
        <h3 style={{ marginTop: 0 }}>Data sources (P10)</h3>
        <p className="muted" style={{ marginBottom: 0 }}>
          No failed or unavailable <code>context_loaded</code> entries in latest epic payloads.
        </p>
      </div>
    );
  }

  return (
    <div className="panel context-alerts-panel">
      <h3 style={{ marginTop: 0 }}>Data sources needing attention</h3>
      <p className="muted">
        Latest payload per epic with <code>context_loaded</code> status{" "}
        <strong>failed</strong> or <strong>unavailable</strong> (Reviewer / MCP).
      </p>
      <table className="data">
        <thead>
          <tr>
            <th>Run</th>
            <th>Epic</th>
            <th>Source</th>
            <th>Status</th>
            <th>Detail</th>
          </tr>
        </thead>
        <tbody>
          {data.alerts.map((a) => (
            <tr key={`${a.unit_id}-${a.source}-${a.status}`}>
              <td>
                <Link to={`/runs/${a.pipeline_run_id}`}>{a.run_label}</Link>
              </td>
              <td>
                <Link to={`/units/${a.unit_id}`}>{a.jira_key}</Link>
              </td>
              <td>{a.source}</td>
              <td>
                <span className="badge sev-med">{a.status}</span>
              </td>
              <td className="muted">{a.detail ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
