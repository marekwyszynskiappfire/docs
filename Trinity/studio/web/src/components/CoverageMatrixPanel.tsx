import type { CreatorCoverage } from "../api";

function joinIds(ids: string[] | undefined) {
  if (!ids?.length) return "—";
  return ids.join(", ");
}

function statusClass(status: string) {
  const s = status.toUpperCase();
  if (s === "COVERED" || s === "N/A") return "coverage-status coverage-status--ok";
  if (s === "PARTIAL") return "coverage-status coverage-status--partial";
  return "coverage-status coverage-status--gap";
}

export default function CoverageMatrixPanel({ coverage }: { coverage: CreatorCoverage | null }) {
  if (!coverage) return null;

  if (!coverage.available) {
    return (
      <div className="panel coverage-panel">
        <h3 style={{ marginTop: 0 }}>Epic coverage matrix</h3>
        <p className="muted">{coverage.message}</p>
        {coverage.approved_ac_ids && coverage.approved_ac_ids.length > 0 && (
          <p className="muted">
            AC/goal ids on approved tests: <code>{coverage.approved_ac_ids.join(", ")}</code>
          </p>
        )}
      </div>
    );
  }

  const gaps = coverage.gap_count ?? 0;
  const matrix = coverage.matrix ?? [];

  return (
    <div className="panel coverage-panel">
      <div className="coverage-panel__header">
        <h3 style={{ margin: 0 }}>Epic coverage matrix</h3>
        <span className={gaps > 0 ? "coverage-gap-pill" : "coverage-ok-pill"}>
          {gaps > 0 ? `${gaps} gap(s)` : "No review gaps"}
        </span>
      </div>
      <p className="muted" style={{ marginTop: "0.5rem" }}>
        From batch revision {coverage.batch_revision ?? "—"}
        {coverage.source_requirement_keys?.length
          ? ` · requirements ${coverage.source_requirement_keys.join(", ")}`
          : ""}
        . Gaps highlight UNCOVERED/PARTIAL rows and ACs not linked on approved tests.
      </p>

      {(coverage.uncovered_goals?.length ?? 0) > 0 && (
        <div className="coverage-callout coverage-callout--gap">
          <strong>Uncovered goals</strong>
          <ul>
            {coverage.uncovered_goals!.map((g) => (
              <li key={g}>{g}</li>
            ))}
          </ul>
        </div>
      )}

      {(coverage.warnings?.length ?? 0) > 0 && (
        <div className="coverage-callout coverage-callout--warn">
          <strong>Coverage warnings</strong>
          <ul>
            {coverage.warnings!.map((w) => (
              <li key={w}>{w}</li>
            ))}
          </ul>
        </div>
      )}

      <table className="data coverage-table">
        <thead>
          <tr>
            <th>AC / goal</th>
            <th>Batch</th>
            <th>Batch tests</th>
            <th>Approved tests</th>
            <th>Gap</th>
          </tr>
        </thead>
        <tbody>
          {matrix.map((row) => (
            <tr key={row.ac_id} className={row.review_gap ? "coverage-row-gap" : undefined}>
              <td>
                <code>{row.ac_id}</code>
                {row.jira_key ? <span className="muted"> · {row.jira_key}</span> : null}
              </td>
              <td>
                <span className={statusClass(row.batch_status)}>{row.batch_status}</span>
              </td>
              <td>{joinIds(row.batch_covered_by)}</td>
              <td>{joinIds(row.approved_covered_by)}</td>
              <td className="muted">{row.review_gap ? row.gap_reason ?? "Gap" : "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {matrix.length === 0 && (
        <p className="muted">No matrix[] in coverage_report — check batch JSON or Reviewer handoff.</p>
      )}

      {(coverage.catalog_coverage?.length ?? 0) > 0 && (
        <>
          <h4>Catalog coverage</h4>
          {coverage.catalog_coverage_pct != null && (
            <p className="muted">{coverage.catalog_coverage_pct}% catalog items covered or N/A</p>
          )}
          <table className="data coverage-table">
            <thead>
              <tr>
                <th>Catalog id</th>
                <th>Tier</th>
                <th>Status</th>
                <th>Tests</th>
              </tr>
            </thead>
            <tbody>
              {coverage.catalog_coverage!.map((c) => (
                <tr key={c.catalog_id} className={c.status === "UNCOVERED" ? "coverage-row-gap" : undefined}>
                  <td><code>{c.catalog_id}</code></td>
                  <td>{c.tier}</td>
                  <td><span className={statusClass(c.status)}>{c.status}</span></td>
                  <td>{joinIds(c.covered_by)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
