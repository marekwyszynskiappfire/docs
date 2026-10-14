import type { CreatorCoverage } from "../api";
import SortableDataTable from "./SortableDataTable";

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

      <SortableDataTable
        className="data coverage-table"
        rows={matrix}
        rowKey={(row) => row.ac_id}
        rowClassName={(row) => (row.review_gap ? "coverage-row-gap" : undefined)}
        defaultSort={{ columnId: "ac_id", dir: "asc" }}
        columns={[
          {
            id: "ac_id",
            header: "AC / goal",
            getValue: (row) => row.ac_id,
            render: (row) => (
              <>
                <code>{row.ac_id}</code>
                {row.jira_key ? <span className="muted"> · {row.jira_key}</span> : null}
              </>
            ),
          },
          {
            id: "batch_status",
            header: "Batch",
            getValue: (row) => row.batch_status,
            render: (row) => (
              <span className={statusClass(row.batch_status)}>{row.batch_status}</span>
            ),
          },
          {
            id: "batch_covered",
            header: "Batch tests",
            getValue: (row) => joinIds(row.batch_covered_by),
          },
          {
            id: "approved_covered",
            header: "Approved tests",
            getValue: (row) => joinIds(row.approved_covered_by),
          },
          {
            id: "gap",
            header: "Gap",
            getValue: (row) => (row.review_gap ? row.gap_reason ?? "Gap" : ""),
            cellClassName: "muted",
            render: (row) => (row.review_gap ? row.gap_reason ?? "Gap" : "—"),
          },
        ]}
      />
      {matrix.length === 0 && (
        <p className="muted">No matrix[] in coverage_report — check batch JSON or Reviewer handoff.</p>
      )}

      {(coverage.catalog_coverage?.length ?? 0) > 0 && (
        <>
          <h4>Catalog coverage</h4>
          {coverage.catalog_coverage_pct != null && (
            <p className="muted">{coverage.catalog_coverage_pct}% catalog items covered or N/A</p>
          )}
          <SortableDataTable
            className="data coverage-table"
            rows={coverage.catalog_coverage!}
            rowKey={(c) => c.catalog_id}
            rowClassName={(c) => (c.status === "UNCOVERED" ? "coverage-row-gap" : undefined)}
            defaultSort={{ columnId: "catalog_id", dir: "asc" }}
            columns={[
              {
                id: "catalog_id",
                header: "Catalog id",
                getValue: (c) => c.catalog_id,
                render: (c) => <code>{c.catalog_id}</code>,
              },
              { id: "tier", header: "Tier", getValue: (c) => c.tier },
              {
                id: "status",
                header: "Status",
                getValue: (c) => c.status,
                render: (c) => <span className={statusClass(c.status)}>{c.status}</span>,
              },
              {
                id: "tests",
                header: "Tests",
                getValue: (c) => joinIds(c.covered_by),
              },
            ]}
          />
        </>
      )}
    </div>
  );
}
