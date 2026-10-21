import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api, type PipelineRunStatistics } from "../api";
import { groupContextLoadedAlertsByRun, type ContextLoadedAlert } from "../lib/contextLoadedAlerts";
import { SOURCE_STATUS_LABEL } from "../types/review-payload";
import JiraKeyLink from "./JiraKeyLink";
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

function AlertTable({ alerts }: { alerts: Alert[] }) {
  return (
    <SortableDataTable
      className="data child-table context-alerts-table"
      rows={alerts}
      rowKey={(alert) => `${alert.unit_id}-${alert.source}-${alert.status}`}
      defaultSort={{ columnId: "jira_key", dir: "asc" }}
      columns={[
        {
          id: "jira_key",
          header: "Epic",
          getValue: (alert) => alert.jira_key,
          render: (alert) => <JiraKeyLink issueKey={alert.jira_key} />,
        },
        { id: "source", header: "Source", getValue: (alert) => alert.source },
        {
          id: "status",
          header: "Status",
          getValue: (alert) => alert.status,
          render: (alert) => (
            <span className={`status-pill ${contextStatusPillClass(alert.status)}`}>
              {contextStatusLabel(alert.status)}
            </span>
          ),
        },
        {
          id: "detail",
          header: "Detail",
          getValue: (alert) => alert.detail,
          cellClassName: "muted",
        },
      ]}
    />
  );
}

type Props = {
  /** When set, the panel shows this run’s sources and readiness on the same screen. */
  runId?: string;
};

export default function ContextLoadedAlertsPanel({ runId }: Props) {
  const [data, setData] = useState<{ alert_count: number; alerts: Alert[] } | null>(null);
  const [stats, setStats] = useState<PipelineRunStatistics | null>(null);

  useEffect(() => {
    api.contextLoadedAlerts().then(setData).catch(() => setData(null));
  }, []);

  useEffect(() => {
    if (!runId) {
      setStats(null);
      return;
    }
    api
      .runStatistics(runId)
      .then(setStats)
      .catch(() => setStats(null));
  }, [runId]);

  const alerts = useMemo(
    () => (data?.alerts ?? []).filter((alert) => !runId || alert.pipeline_run_id === runId),
    [data, runId]
  );
  const runGroups = useMemo(() => groupContextLoadedAlertsByRun(alerts), [alerts]);
  const scopedGroup = runId ? runGroups[0] : undefined;
  const failed = alerts.filter((alert) => alert.status === "failed").length;
  const unavailable = alerts.filter((alert) => alert.status === "unavailable").length;
  const summary = stats?.summary;

  return (
    <details className="panel context-alerts-panel">
      <summary className="context-alerts-summary">
        <span>Data sources needing attention</span>
        <span className="status-pill pill-failed">{failed} could not read</span>
        <span className="status-pill pill-unavailable">{unavailable} unavailable</span>
        {summary && (
          <>
            <span className="stat-chip stat-chip--ready">{summary.epics_tc_creation_ready ?? 0} ready</span>
            <span className="stat-chip stat-chip--reservations">
              {summary.epics_tc_creation_ready_with_reservations ?? 0} with reservations
            </span>
            <span className="stat-chip stat-chip--warn">
              {summary.epics_tc_creation_not_ready ?? summary.epics_not_ready_for_test_design} not ready
            </span>
          </>
        )}
      </summary>
      {summary && (
        <div className="stat-grid stat-grid--readiness context-alerts-stats">
          <div className="stat-card stat-card--ready">
            <div className="label">Ready for TC creation</div>
            <div className="value">{summary.epics_tc_creation_ready ?? 0}</div>
          </div>
          <div className="stat-card stat-card--reservations">
            <div className="label">Ready with reservations</div>
            <div className="value">{summary.epics_tc_creation_ready_with_reservations ?? 0}</div>
          </div>
          <div className="stat-card stat-card--warn">
            <div className="label">Not ready for TC creation</div>
            <div className="value">
              {summary.epics_tc_creation_not_ready ?? summary.epics_not_ready_for_test_design}
            </div>
          </div>
          <div className="stat-card">
            <div className="label">Epics reviewed</div>
            <div className="value">{summary.epics_reviewed}</div>
          </div>
          <div className="stat-card">
            <div className="label">Open findings</div>
            <div className="value">{summary.issues_spotted_findings_open}</div>
          </div>
          <div className="stat-card">
            <div className="label">Tests drafted</div>
            <div className="value">{summary.test_cases_drafted_total}</div>
          </div>
          <div className="stat-card">
            <div className="label">Sent to import</div>
            <div className="value">{summary.test_cases_sent_to_import_total}</div>
          </div>
          <div className="stat-card">
            <div className="label">In Xray</div>
            <div className="value">{summary.test_cases_imported_to_xray_total}</div>
          </div>
        </div>
      )}
      {runGroups.length === 0 ? (
        <p className="muted" style={{ marginBottom: 0 }}>
          No failed or unavailable sources in {runId ? "this run" : "the latest epic payloads"}.
        </p>
      ) : scopedGroup ? (
        <AlertTable alerts={scopedGroup.alerts} />
      ) : (
        <div className="context-alerts-runs">
          {runGroups.map((group) => (
            <details key={group.pipeline_run_id} className="context-alerts-run">
              <summary className="context-alerts-run-summary">
                <Link
                  to={`/workspace/${group.pipeline_run_id}`}
                  className="context-alerts-run-link"
                  onClick={(event) => event.stopPropagation()}
                >
                  {group.run_label}
                </Link>
                <span className="status-pill pill-failed">
                  {group.alerts.filter((alert) => alert.status === "failed").length} could not read
                </span>
                <span className="status-pill pill-unavailable">
                  {group.alerts.filter((alert) => alert.status === "unavailable").length} unavailable
                </span>
              </summary>
              <AlertTable alerts={group.alerts} />
            </details>
          ))}
        </div>
      )}
    </details>
  );
}
