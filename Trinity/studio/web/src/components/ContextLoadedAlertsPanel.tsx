import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { groupContextLoadedAlertsByRun, type ContextLoadedAlert } from "../lib/contextLoadedAlerts";
import { SOURCE_STATUS_LABEL } from "../types/review-payload";
import SortableDataTable from "./SortableDataTable";

type Alert = ContextLoadedAlert;

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

export default function ContextLoadedAlertsPanel() {
  const [data, setData] = useState<{ alert_count: number; alerts: Alert[] } | null>(null);
  /** Per-run expand state — do not use controlled `open={bool}` without onToggle (breaks <details>). */
  const [expandedRuns, setExpandedRuns] = useState<Record<string, boolean>>({});

  useEffect(() => {
    api.contextLoadedAlerts().then(setData).catch(() => setData(null));
  }, []);

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
            <SortableDataTable
              className="data child-table context-alerts-table"
              rows={group.alerts}
              rowKey={(a) => `${a.unit_id}-${a.source}-${a.status}`}
              defaultSort={{ columnId: "jira_key", dir: "asc" }}
              columns={[
                {
                  id: "jira_key",
                  header: "Epic",
                  getValue: (a) => a.jira_key,
                  render: (a) => <Link to={`/units/${a.unit_id}`}>{a.jira_key}</Link>,
                },
                { id: "source", header: "Source", getValue: (a) => a.source },
                {
                  id: "status",
                  header: "Status",
                  getValue: (a) => a.status,
                  render: (a) => (
                    <span className={`status-pill ${contextStatusPillClass(a.status)}`}>
                      {contextStatusLabel(a.status)}
                    </span>
                  ),
                },
                {
                  id: "detail",
                  header: "Detail",
                  getValue: (a) => a.detail,
                  cellClassName: "muted",
                },
              ]}
            />
          </details>
        ))}
      </div>
    </div>
  );
}
