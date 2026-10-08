import type { ContextLoadedEntry } from "../types/review-payload";
import { SOURCE_STATUS_LABEL } from "../types/review-payload";

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

  return (
    <div className="panel data-sources">
      <details open className="report-block">
        <summary>
          Data sources ({analyzed} analyzed · {problems} unavailable or failed)
        </summary>
        <div className="table-scroll">
          <table className="data">
            <thead>
              <tr>
                <th>Source</th>
                <th>Status</th>
                <th>Detail</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((s, i) => (
                <tr key={`${s.source}-${i}`}>
                  <td>{s.source}</td>
                  <td>
                    <span className={`status-pill ${statusClass(s.status)}`}>
                      {SOURCE_STATUS_LABEL[s.status] ?? s.status}
                    </span>
                  </td>
                  <td className="muted detail-cell">{detailFor(s)}</td>
                </tr>
              ))}
            </tbody>
          </table>
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
