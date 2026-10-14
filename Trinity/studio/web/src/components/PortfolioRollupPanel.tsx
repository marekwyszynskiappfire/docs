import { Link } from "react-router-dom";
import { api, PortfolioRollup } from "../api";
import SortableDataTable from "./SortableDataTable";

type Props = { rollup: PortfolioRollup };

export default function PortfolioRollupPanel({ rollup }: Props) {
  const { global: g } = rollup;
  return (
    <div className="panel portfolio-rollup">
      <h2 style={{ marginTop: 0 }}>Portfolio readiness</h2>
      <p className="muted" style={{ marginTop: 0 }}>
        Rollup across imported Reviewer runs (latest payload per epic). Updated{" "}
        {rollup.generated_at.slice(0, 19)}.
      </p>
      <div className="mix-strip">
        <div>
          <span className="label">Gate mix (all epics)</span>
          <span className="mix-value">{api.formatMix(g.gate_mix)}</span>
        </div>
        <div>
          <span className="label">Test design fit</span>
          <span className="mix-value">{api.formatMix(g.fit_mix)}</span>
        </div>
      </div>
      {rollup.runs.length === 0 ? (
        <p className="muted">Import a Reviewer folder to populate portfolio rows.</p>
      ) : (
        <SortableDataTable
          rows={rollup.runs}
          rowKey={(r) => r.id}
          defaultSort={{ columnId: "label", dir: "asc" }}
          columns={[
            {
              id: "label",
              header: "Run",
              getValue: (r) => r.label,
              render: (r) => <Link to={`/runs/${r.id}`}>{r.label}</Link>,
            },
            {
              id: "id",
              header: "Studio ID",
              getValue: (r) => r.id,
              render: (r) => <code className="run-id-cell">{r.id}</code>,
            },
            { id: "units", header: "Epics", getValue: (r) => r.unit_count, align: "right" },
            { id: "approved", header: "Approved", getValue: (r) => r.units_approved, align: "right" },
            {
              id: "gate",
              header: "Gate mix",
              getValue: (r) => api.formatMix(r.gate_mix),
              cellClassName: "muted mix-cell",
            },
            {
              id: "fit",
              header: "Fit mix",
              getValue: (r) => api.formatMix(r.fit_mix),
              cellClassName: "muted mix-cell",
            },
            {
              id: "fq",
              header: "Open F / Q",
              getValue: (r) => r.open_findings_latest,
              render: (r) => `${r.open_findings_latest} / ${r.open_questions_latest}`,
            },
            { id: "creator", header: "Creator", getValue: (r) => r.creator_runs, align: "right" },
            {
              id: "tests",
              header: "Tests",
              getValue: (r) => r.test_cases_approved,
              render: (r) => `${r.test_cases_approved}/${r.test_cases}`,
            },
          ]}
        />
      )}
    </div>
  );
}
