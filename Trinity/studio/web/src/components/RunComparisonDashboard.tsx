import { useMemo } from "react";
import { PipelineRunCompare } from "../api";
import SortableDataTable from "./SortableDataTable";
import TcReadinessChart from "./TcReadinessChart";

const LOWER_IS_BETTER = new Set([
  "epics_tc_creation_not_ready",
  "epics_tc_creation_unknown",
  "issues_spotted_findings_total",
  "issues_spotted_findings_open",
  "test_cases_amended_total",
]);

function deltaClass(metricKey: string, delta: number): string {
  if (delta === 0) return "";
  const improved = LOWER_IS_BETTER.has(metricKey) ? delta < 0 : delta > 0;
  return improved ? "compare-delta-up" : "compare-delta-down";
}

function cellHighlight(
  metricKey: string,
  val: number | null | undefined,
  row: { min: number | null; max: number | null }
): string | undefined {
  if (val == null || row.min == null || row.max == null || row.min === row.max) {
    return undefined;
  }
  const best = LOWER_IS_BETTER.has(metricKey) ? row.min : row.max;
  const worst = LOWER_IS_BETTER.has(metricKey) ? row.max : row.min;
  if (val === best) return "compare-cell-high";
  if (val === worst) return "compare-cell-low";
  return undefined;
}

type Props = {
  data: PipelineRunCompare;
};

export default function RunComparisonDashboard({ data }: Props) {
  const metricColumns = useMemo(
    () => [
      { id: "label", header: "Metric", getValue: (row: PipelineRunCompare["metrics"][0]) => row.label },
      ...data.runs.map((r) => ({
        id: r.pipeline_run_id,
        header: r.pipeline_label,
        align: "right" as const,
        getValue: (row: PipelineRunCompare["metrics"][0]) => row.values[r.pipeline_run_id],
        render: (row: PipelineRunCompare["metrics"][0]) => {
          const val = row.values[r.pipeline_run_id];
          return (
            <span className={cellHighlight(row.key, val, row) ?? undefined}>{val ?? "—"}</span>
          );
        },
      })),
    ],
    [data.runs]
  );

  const deltaRows = useMemo(
    () =>
      data.deltas_from_baseline.map((d) => ({
        ...d,
        otherLabel:
          data.runs.find((r) => r.pipeline_run_id === d.other_run_id)?.pipeline_label ??
          d.other_run_id,
      })),
    [data.deltas_from_baseline, data.runs]
  );

  return (
    <div className="stats-dashboard compare-dashboard">
      <p className="muted compare-baseline-note">
        Baseline for deltas: <code>{data.baseline_run_id}</code> (first selected run). Compared at{" "}
        {new Date(data.compared_at).toLocaleString()}.
      </p>

      <div className="compare-run-cards">
        {data.runs.map((run) => (
          <div key={run.pipeline_run_id} className="panel compare-run-card">
            <h3 style={{ marginTop: 0 }}>{run.pipeline_label}</h3>
            <p className="muted" style={{ margin: "0 0 0.75rem" }}>
              <code>{run.pipeline_run_id}</code>
            </p>
            <TcReadinessChart summary={run.summary} />
          </div>
        ))}
      </div>

      <div className="panel">
        <h3 style={{ marginTop: 0 }}>Metric comparison</h3>
        <SortableDataTable
          className="data compare-metrics-table"
          rows={data.metrics}
          rowKey={(row) => row.key}
          defaultSort={{ columnId: "label", dir: "asc" }}
          columns={metricColumns}
        />
      </div>

      {deltaRows.length > 0 && (
        <div className="panel">
          <h3 style={{ marginTop: 0 }}>Change vs baseline</h3>
          <SortableDataTable
            rows={deltaRows}
            rowKey={(d) => `${d.metric}-${d.other_run_id}`}
            columns={[
              { id: "label", header: "Metric", getValue: (d) => d.label },
              { id: "other", header: "Other run", getValue: (d) => d.otherLabel },
              { id: "baseline", header: "Baseline", getValue: (d) => d.baseline, align: "right" },
              { id: "otherVal", header: "Other", getValue: (d) => d.other, align: "right" },
              {
                id: "delta",
                header: "Δ",
                getValue: (d) => d.delta,
                align: "right",
                render: (d) => {
                  const sign = d.delta > 0 ? "+" : "";
                  return <span className={deltaClass(d.metric, d.delta)}>{sign}{d.delta}</span>;
                },
              },
            ]}
          />
        </div>
      )}
    </div>
  );
}
