import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import {
  groupContextLoadedAlertsByRun,
  sortContextLoadedAlerts,
  type ContextLoadedAlert,
  type ContextLoadedSortColumn,
  type ContextLoadedSortDir,
} from "../lib/contextLoadedAlerts";
import { SOURCE_STATUS_LABEL } from "../types/review-payload";

type Alert = ContextLoadedAlert;
type SortColumn = ContextLoadedSortColumn;
type SortDir = ContextLoadedSortDir;

function contextStatusPillClass(status: string): string {
  switch (status) {
    case "failed":
      return "pill-failed";
    case "unavailable":
      return "pill-unavailable";
    case "analyzed":
      return "pill-analyzed";
    case "not_applicable":
      return "pill-na";
    default:
      return "pill-na";
  }
}

function contextStatusLabel(status: string): string {
  if (status in SOURCE_STATUS_LABEL) {
    return SOURCE_STATUS_LABEL[status as keyof typeof SOURCE_STATUS_LABEL];
  }
  return status;
}

type SortableHeaderProps = {
  label: string;
  column: SortColumn;
  sortColumn: SortColumn;
  sortDir: SortDir;
  onSort: (column: SortColumn) => void;
};

function SortableHeader({ label, column, sortColumn, sortDir, onSort }: SortableHeaderProps) {
  const active = sortColumn === column;
  return (
    <th
      scope="col"
      aria-sort={active ? (sortDir === "asc" ? "ascending" : "descending") : "none"}
    >
      <button
        type="button"
        className={`th-sort${active ? " th-sort--active" : ""}`}
        onClick={() => onSort(column)}
      >
        <span>{label}</span>
        {active && <span className="th-sort-indicator" aria-hidden="true">{sortDir === "asc" ? "▲" : "▼"}</span>}
      </button>
    </th>
  );
}

export default function ContextLoadedAlertsPanel() {
  const [data, setData] = useState<{ alert_count: number; alerts: Alert[] } | null>(null);
  const [sortColumn, setSortColumn] = useState<SortColumn>("jira_key");
  const [sortDir, setSortDir] = useState<SortDir>("asc");
  /** Per-run expand state — do not use controlled `open={bool}` without onToggle (breaks <details>). */
  const [expandedRuns, setExpandedRuns] = useState<Record<string, boolean>>({});

  useEffect(() => {
    api.contextLoadedAlerts().then(setData).catch(() => setData(null));
  }, []);

  const onSort = (column: SortColumn) => {
    if (sortColumn === column) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortColumn(column);
      setSortDir("asc");
    }
  };

  const alerts = data?.alerts ?? [];
  const runGroups = useMemo(() => groupContextLoadedAlertsByRun(alerts), [alerts]);

  useEffect(() => {
    if (!runGroups.length) return;
    setExpandedRuns((prev) => {
      const next = { ...prev };
      runGroups.forEach((g, index) => {
        if (next[g.pipeline_run_id] === undefined) {
          next[g.pipeline_run_id] = runGroups.length === 1 || index === 0;
        }
      });
      return next;
    });
  }, [runGroups]);

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
      <p className="muted context-alerts-lead">
        {data.alert_count} issue(s) across {runGroups.length} run(s) — click column headers to sort.
      </p>
      <div className="context-alerts-runs">
        {runGroups.map((group) => (
          <details
            key={group.pipeline_run_id}
            className="context-alerts-run"
            open={expandedRuns[group.pipeline_run_id] ?? false}
            onToggle={(e) => {
              const open = e.currentTarget.open;
              setExpandedRuns((prev) => ({ ...prev, [group.pipeline_run_id]: open }));
            }}
          >
            <summary className="context-alerts-run-summary">
              <Link
                to={`/runs/${group.pipeline_run_id}`}
                className="context-alerts-run-link"
                onClick={(e) => e.stopPropagation()}
              >
                {group.run_label}
              </Link>
              <span className="muted context-alerts-run-meta">
                {group.alerts.length} issue{group.alerts.length === 1 ? "" : "s"} ·{" "}
                {group.epicKeys.length} epic{group.epicKeys.length === 1 ? "" : "s"}
              </span>
            </summary>
            <table className="data child-table context-alerts-table">
              <thead>
                <tr>
                  <SortableHeader
                    label="Epic"
                    column="jira_key"
                    sortColumn={sortColumn}
                    sortDir={sortDir}
                    onSort={onSort}
                  />
                  <SortableHeader
                    label="Source"
                    column="source"
                    sortColumn={sortColumn}
                    sortDir={sortDir}
                    onSort={onSort}
                  />
                  <SortableHeader
                    label="Status"
                    column="status"
                    sortColumn={sortColumn}
                    sortDir={sortDir}
                    onSort={onSort}
                  />
                  <SortableHeader
                    label="Detail"
                    column="detail"
                    sortColumn={sortColumn}
                    sortDir={sortDir}
                    onSort={onSort}
                  />
                </tr>
              </thead>
              <tbody>
                {sortContextLoadedAlerts(group.alerts, sortColumn, sortDir).map((a) => (
                  <tr key={`${a.unit_id}-${a.source}-${a.status}`}>
                    <td>
                      <Link to={`/units/${a.unit_id}`}>{a.jira_key}</Link>
                    </td>
                    <td>{a.source}</td>
                    <td>
                      <span className={`status-pill ${contextStatusPillClass(a.status)}`}>
                        {contextStatusLabel(a.status)}
                      </span>
                    </td>
                    <td className="muted">{a.detail ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </details>
        ))}
      </div>
    </div>
  );
}
