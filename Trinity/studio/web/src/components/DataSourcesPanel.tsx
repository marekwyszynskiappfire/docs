import type { ContextLoadedEntry } from "../types/review-payload";
import { SOURCE_STATUS_LABEL } from "../types/review-payload";
import SortableDataTable from "./SortableDataTable";

function statusClass(status: ContextLoadedEntry["status"]) {
  switch (status) {
    case "analyzed":
      return "pill-analyzed";
    case "unavailable":
      return "pill-unavailable";
    case "failed":
      return "pill-failed";
    default:
      return "pill-na";
  }
}

function detailFor(entry: ContextLoadedEntry) {
  if (entry.status === "unavailable" || entry.status === "failed") {
    return entry.reason || "";
  }
  return entry.detail || "";
}

type Props = {
  entries: ContextLoadedEntry[];
};

export default function DataSourcesPanel({ entries }: Props) {
  if (!entries.length) return null;

  const analyzed = entries.filter((s) => s.status === "analyzed").length;
  const problems = entries.filter((s) => s.status === "unavailable" || s.status === "failed").length;

  const rows = entries.map((entry, index) => ({ entry, index }));

  return (
    <div className="panel data-sources">
      <details open className="report-block">
        <summary>
          Data sources ({analyzed} analyzed · {problems} unavailable or failed)
        </summary>
        <div className="table-scroll">
          <SortableDataTable
            rows={rows}
            rowKey={(r) => `${r.entry.source}-${r.index}`}
            defaultSort={{ columnId: "source", dir: "asc" }}
            columns={[
              { id: "source", header: "Source", getValue: (r) => r.entry.source },
              {
                id: "status",
                header: "Status",
                getValue: (r) => r.entry.status,
                render: (r) => (
                  <span className={`status-pill ${statusClass(r.entry.status)}`}>
                    {SOURCE_STATUS_LABEL[r.entry.status] ?? r.entry.status}
                  </span>
                ),
              },
              {
                id: "detail",
                header: "Detail",
                getValue: (r) => detailFor(r.entry),
                cellClassName: "muted detail-cell",
              },
            ]}
          />
        </div>
        {problems === 0 && (
          <p className="muted" style={{ marginTop: "0.75rem", marginBottom: 0 }}>
            No sources were unavailable or failed in this run.
          </p>
        )}
      </details>
    </div>
  );
}
