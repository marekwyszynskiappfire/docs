import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { SOURCE_STATUS_LABEL } from "../types/review-payload";

type Alert = {
  pipeline_run_id: string;
  run_label: string;
  unit_id: string;
  jira_key: string;
  source: string;
  status: string;
  detail?: string;
};

type RunGroup = {
  pipeline_run_id: string;
  run_label: string;
  alerts: Alert[];
  epicKeys: string[];
};

type SortColumn = "jira_key" | "source" | "status" | "detail";
type SortDir = "asc" | "desc";

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

function sortValue(a: Alert, col: SortColumn): string {
  switch (col) {
    case "jira_key":
      return a.jira_key;
    case "source":
      return a.source;
    case "status":
      return a.status;
    case "detail":
      return a.detail ?? "";
  }
}

function sortAlerts(alerts: Alert[], col: SortColumn, dir: SortDir): Alert[] {
  const mult = dir === "asc" ? 1 : -1;
  return [...alerts].sort(
    (a, b) =>
      sortValue(a, col).localeCompare(sortValue(b, col), undefined, {
        sensitivity: "base",
        numeric: true,
      }) * mult
  );
}

function groupAlertsByRun(alerts: Alert[]): RunGroup[] {
  const map = new Map<string, RunGroup>();
  for (const a of alerts) {
    let g = map.get(a.pipeline_run_id);
    if (!g) {
      g = {
        pipeline_run_id: a.pipeline_run_id,
        run_label: a.run_label,
        alerts: [],
        epicKeys: [],
      };
      map.set(a.pipeline_run_id, g);
    }
    g.alerts.push(a);
    if (!g.epicKeys.includes(a.jira_key)) g.epicKeys.push(a.jira_key);
  }
  return [...map.values()].sort((a, b) => {
    if (b.alerts.length !== a.alerts.length) return b.alerts.length - a.alerts.length;
    return a.run_label.localeCompare(b.run_label, undefined, { sensitivity: "base" });
  });
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

  const runGroups = useMemo(
    () => (data?.alerts ? groupAlertsByRun(data.alerts) : []),
    [data?.alerts]
  );

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
        {runGroups.map((group, index) => (
          <details
            key={group.pipeline_run_id}
            className="context-alerts-run"
            open={runGroups.length === 1 || index === 0}
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
                {sortAlerts(group.alerts, sortColumn, sortDir).map((a) => (
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
