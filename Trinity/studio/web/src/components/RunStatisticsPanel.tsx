import { useCallback, useEffect, useState } from "react";
import { api, PipelineRunStatistics } from "../api";
import SortableDataTable from "./SortableDataTable";
import TcReadinessChart from "./TcReadinessChart";

type Props = {
  runId: string;
};

function formatDuration(seconds: number | null | undefined): string {
  if (seconds == null || Number.isNaN(seconds)) return "—";
  if (seconds < 60) return `${Math.round(seconds)}s`;
  const m = Math.floor(seconds / 60);
  const s = Math.round(seconds % 60);
  if (m < 60) return `${m}m ${s}s`;
  const h = Math.floor(m / 60);
  return `${h}h ${m % 60}m`;
}

function formatTs(iso: string | null | undefined): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

export default function RunStatisticsPanel({ runId }: Props) {
  const [report, setReport] = useState<PipelineRunStatistics | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    setLoading(true);
    setError("");
    api
      .runStatistics(runId)
      .then(setReport)
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, [runId]);

  useEffect(() => {
    load();
  }, [load]);

  const downloadExport = async () => {
    try {
      const bundle = await api.runStatisticsExport(runId);
      const blob = new Blob([JSON.stringify(bundle, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `pipeline-statistics-${runId}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(String(e));
    }
  };

  if (loading && !report) {
    return <p className="muted">Computing statistics…</p>;
  }
  if (error && !report) {
    return <p className="error">{error}</p>;
  }
  if (!report) return null;

  const s = report.summary;
  const ctx = report.product_context;

  return (
    <div className="panel run-statistics">
      <div className="btn-row" style={{ justifyContent: "space-between", alignItems: "center" }}>
        <p className="muted" style={{ margin: 0 }}>
          Snapshot computed {formatTs(report.computed_at)} · schema v{report.schema_version}
        </p>
        <div className="btn-row">
          <button type="button" className="secondary" onClick={load} disabled={loading}>
            Refresh
          </button>
          <button type="button" onClick={downloadExport}>Download export JSON</button>
        </div>
      </div>

      <h3 style={{ marginTop: "1rem" }}>Product &amp; Jira context</h3>
      <SortableDataTable
        className="data compact-stats"
        rows={[
          { id: "product", label: "Product id", value: ctx.product_id ?? "—", code: false },
          {
            id: "reviewer",
            label: "Reviewer run id",
            value: ctx.reviewer_run_id ?? report.pipeline_run_id,
            code: true,
          },
          {
            id: "projects",
            label: "Jira project(s)",
            value: (ctx.jira_projects ?? []).join(", ") || "—",
            code: false,
          },
          {
            id: "jql",
            label: "Source JQL",
            value: ctx.source_jql ?? ctx.trigger_value ?? "—",
            code: true,
            muted: true,
          },
          {
            id: "path",
            label: "Imported from",
            value: ctx.source_path ?? "—",
            code: true,
            muted: true,
          },
        ]}
        rowKey={(r) => r.id}
        defaultSort={{ columnId: "label", dir: "asc" }}
        columns={[
          { id: "label", header: "Field", getValue: (r) => r.label },
          {
            id: "value",
            header: "Value",
            getValue: (r) => r.value,
            render: (r) =>
              r.code ? (
                <code className={r.muted ? "muted" : undefined}>{r.value}</code>
              ) : (
                <span className={r.muted ? "muted" : undefined}>{r.value}</span>
              ),
          },
        ]}
      />

      <h3>E2E summary</h3>
      <div className="stat-grid stat-grid--readiness">
        <div className="stat-card stat-card--ready">
          <div className="label">Ready for TC creation</div>
          <div className="value">{s.epics_tc_creation_ready ?? 0}</div>
        </div>
        <div className="stat-card stat-card--reservations">
          <div className="label">Ready with reservations</div>
          <div className="value">{s.epics_tc_creation_ready_with_reservations ?? 0}</div>
        </div>
        <div className="stat-card stat-card--warn">
          <div className="label">Not ready for TC creation</div>
          <div className="value">{s.epics_tc_creation_not_ready ?? s.epics_not_ready_for_test_design}</div>
        </div>
        {(s.epics_tc_creation_unknown ?? 0) > 0 && (
          <div className="stat-card">
            <div className="label">Readiness unknown</div>
            <div className="value">{s.epics_tc_creation_unknown}</div>
          </div>
        )}
      </div>
      <div className="stat-grid">
        <div className="stat-card">
          <div className="label">Epics reviewed</div>
          <div className="value">{s.epics_reviewed}</div>
        </div>
        <div className="stat-card">
          <div className="label">Issues spotted (findings)</div>
          <div className="value">{s.issues_spotted_findings_total}</div>
          <div className="muted">{s.issues_spotted_findings_open} still open</div>
        </div>
        <div className="stat-card">
          <div className="label">Questions marked for epic (suggested)</div>
          <div className="value">{s.questions_marked_for_epic_suggested}</div>
          <div className="muted">{s.questions_posted_to_epic_suggested} posted to Jira</div>
        </div>
        <div className="stat-card">
          <div className="label">New questions marked for epic</div>
          <div className="value">{s.questions_marked_for_epic_new}</div>
          <div className="muted">{s.questions_posted_to_epic_new} posted to Jira</div>
        </div>
        <div className="stat-card">
          <div className="label">Epics selected for Creator</div>
          <div className="value">{s.epics_selected_for_test_case_creation}</div>
          <div className="muted">{s.epics_review_approved} review-approved</div>
        </div>
        <div className="stat-card">
          <div className="label">Test cases drafted</div>
          <div className="value">{s.test_cases_drafted_total}</div>
        </div>
        <div className="stat-card">
          <div className="label">Test cases amended</div>
          <div className="value">{s.test_cases_amended_total}</div>
        </div>
        <div className="stat-card">
          <div className="label">Sent to import</div>
          <div className="value">{s.test_cases_sent_to_import_total}</div>
        </div>
        <div className="stat-card">
          <div className="label">Imported to Xray</div>
          <div className="value">{s.test_cases_imported_to_xray_total}</div>
        </div>
      </div>

      <h3>Phase timing</h3>
      <SortableDataTable
        rows={report.phases.map((p, index) => ({ ...p, sortIndex: index }))}
        rowKey={(p) => p.phase}
        defaultSort={{ columnId: "sortIndex", dir: "asc" }}
        columns={[
          {
            id: "phase",
            header: "Phase",
            getValue: (p) => p.label,
            render: (p) => (
              <>
                {p.label}
                {p.notes && <div className="muted">{p.notes}</div>}
              </>
            ),
          },
          { id: "started", header: "Started", getValue: (p) => p.started_at },
          { id: "ended", header: "Ended", getValue: (p) => p.ended_at },
          {
            id: "duration",
            header: "Duration",
            getValue: (p) => p.duration_seconds,
            render: (p) => formatDuration(p.duration_seconds),
          },
          { id: "sortIndex", header: "Order", getValue: (p) => p.sortIndex, hidden: true },
        ]}
      />

      <h3>Test cases per epic (drafted)</h3>
      {Object.keys(report.test_cases_per_epic_drafted).length === 0 ? (
        <p className="muted">No Creator batches linked to this pipeline run yet.</p>
      ) : (
        <SortableDataTable
          rows={Object.entries(report.test_cases_per_epic_drafted).map(([epic, count]) => ({
            epic,
            count,
          }))}
          rowKey={(r) => r.epic}
          columns={[
            { id: "epic", header: "Epic", getValue: (r) => r.epic },
            { id: "count", header: "Test cases drafted", getValue: (r) => r.count, align: "right" },
          ]}
        />
      )}

      <details style={{ marginTop: "1.25rem" }} open>
        <summary>Per-epic detail ({report.epics.length} epics)</summary>
        <SortableDataTable
          className="data child-table"
          rows={report.epics}
          rowKey={(e) => e.unit_id}
          defaultSort={{ columnId: "jira_key", dir: "asc" }}
          columns={[
            {
              id: "jira_key",
              header: "Epic",
              getValue: (e) => e.jira_key,
              render: (e) => (
                <>
                  <strong>{e.jira_key}</strong>
                  <div className="muted">{e.summary}</div>
                </>
              ),
            },
            { id: "gate", header: "Gate", getValue: (e) => e.gate_status },
            { id: "fit", header: "Planning fit", getValue: (e) => e.qa_planning_fit },
            {
              id: "readiness",
              header: "TC readiness",
              getValue: (e) => e.tc_creation_readiness ?? "",
              render: (e) => (
                <span className="badge">
                  {e.tc_creation_readiness ?? (e.not_ready_for_test_design ? "not_ready" : "—")}
                </span>
              ),
            },
            {
              id: "findings",
              header: "Findings",
              getValue: (e) => e.findings_total,
              align: "right",
            },
            {
              id: "creator",
              header: "In Creator",
              getValue: (e) => (e.include_in_creator ? 1 : 0),
              render: (e) => (e.include_in_creator ? "yes" : "—"),
            },
            { id: "tcs", header: "TCs", getValue: (e) => e.test_cases_drafted, align: "right" },
            { id: "amended", header: "Amended", getValue: (e) => e.test_cases_amended, align: "right" },
            {
              id: "xray",
              header: "Xray",
              getValue: (e) => e.xray_test_keys.join(", "),
            },
          ]}
        />
      </details>
    </div>
  );
}
