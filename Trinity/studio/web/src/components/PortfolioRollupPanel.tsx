import { Link } from "react-router-dom";
import { api, PortfolioRollup } from "../api";

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
        <table className="data">
          <thead>
            <tr>
              <th>Run</th>
              <th>Epics</th>
              <th>Approved</th>
              <th>Gate mix</th>
              <th>Fit mix</th>
              <th>Open F / Q</th>
              <th>Creator</th>
              <th>Tests</th>
            </tr>
          </thead>
          <tbody>
            {rollup.runs.map((r) => (
              <tr key={r.id}>
                <td>
                  <Link to={`/runs/${r.id}`}>{r.label}</Link>
                </td>
                <td>{r.unit_count}</td>
                <td>{r.units_approved}</td>
                <td className="muted mix-cell">{api.formatMix(r.gate_mix)}</td>
                <td className="muted mix-cell">{api.formatMix(r.fit_mix)}</td>
                <td>
                  {r.open_findings_latest} / {r.open_questions_latest}
                </td>
                <td>{r.creator_runs}</td>
                <td>
                  {r.test_cases_approved}/{r.test_cases}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
