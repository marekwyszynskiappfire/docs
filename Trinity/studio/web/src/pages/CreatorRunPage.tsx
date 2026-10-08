import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, CreatorTestRow } from "../api";

type Filter = "all" | "pending" | "approved" | "rejected" | "ready_for_import";

export default function CreatorRunPage() {
  const { runId } = useParams<{ runId: string }>();
  const [tests, setTests] = useState<CreatorTestRow[]>([]);
  const [summary, setSummary] = useState({
    total: 0,
    approved: 0,
    rejected: 0,
    ready_for_import: 0,
  });
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [filter, setFilter] = useState<Filter>("all");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [exportPath, setExportPath] = useState("");

  const load = useCallback(() => {
    if (!runId) return;
    api
      .creatorRun(runId)
      .then((d) => {
        setTests(d.tests);
        setSummary(d.summary);
      })
      .catch((e) => setError(String(e)));
  }, [runId]);

  useEffect(() => {
    load();
  }, [load]);

  const filtered = useMemo(() => {
    return tests.filter((t) => {
      if (filter === "all") return true;
      if (filter === "ready_for_import") {
        return t.human_review_status === "approved" && t.marked_for_xray_import;
      }
      if (filter === "pending") {
        return t.human_review_status === "pending" || t.human_review_status === "edited";
      }
      return t.human_review_status === filter;
    });
  }, [tests, filter]);

  const toggle = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const selectAllVisible = () => {
    setSelected(new Set(filtered.map((t) => t.id)));
  };

  const bulk = async (body: {
    human_review_status?: string;
    marked_for_xray_import?: boolean;
  }) => {
    if (!runId || selected.size === 0) return;
    setError("");
    try {
      const res = await api.bulkTestReview(runId, [...selected], body);
      setMessage(`Updated ${res.updated} test(s)`);
      setSelected(new Set());
      load();
    } catch (e) {
      setError(String(e));
    }
  };

  const onExport = async () => {
    if (!runId) return;
    setError("");
    try {
      const res = await api.exportForImporter(runId);
      setExportPath(res.path);
      setMessage(`Exported ${res.test_count} test(s) for Importer`);
    } catch (e) {
      setError(String(e));
    }
  };

  if (!runId) return null;

  return (
    <>
      <p>
        <Link to="/creator">← Creator</Link>
      </p>
      <h2>{runId}</h2>
      <p className="muted">
        {summary.total} tests · {summary.approved} approved · {summary.rejected} rejected ·{" "}
        {summary.ready_for_import} ready for Xray import
      </p>
      {message && <p className="muted">{message}</p>}
      {error && <p className="error">{error}</p>}
      {exportPath && (
        <p className="muted">
          Importer payload: <code>{exportPath}</code>
          {" · "}
          <Link
            to={`/importer?creator_run_id=${encodeURIComponent(runId)}&payload_path=${encodeURIComponent(exportPath)}`}
          >
            Open in Importer
          </Link>
        </p>
      )}

      <div className="panel">
        <div className="btn-row" style={{ flexWrap: "wrap", alignItems: "center" }}>
          <label>
            Filter
            <select value={filter} onChange={(e) => setFilter(e.target.value as Filter)}>
              <option value="all">All</option>
              <option value="pending">Pending / edited</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
              <option value="ready_for_import">Ready for Xray import</option>
            </select>
          </label>
          <button type="button" className="secondary" onClick={selectAllVisible}>
            Select visible
          </button>
          <button type="button" onClick={() => bulk({ human_review_status: "approved" })}>
            Approve selected
          </button>
          <button type="button" className="secondary" onClick={() => bulk({ human_review_status: "rejected" })}>
            Reject selected
          </button>
          <button
            type="button"
            onClick={() => bulk({ marked_for_xray_import: true })}
            title="Only applies to already-approved rows"
          >
            Mark for Xray import
          </button>
          <button type="button" className="secondary" onClick={() => bulk({ marked_for_xray_import: false })}>
            Unmark import
          </button>
          <button type="button" onClick={onExport}>
            Export for Importer
          </button>
        </div>
      </div>

      <div className="panel">
        <table className="data">
          <thead>
            <tr>
              <th></th>
              <th>ID</th>
              <th>Title</th>
              <th>Review</th>
              <th>Automation</th>
              <th>Xray</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((t) => (
              <tr key={t.id}>
                <td>
                  <input
                    type="checkbox"
                    checked={selected.has(t.id)}
                    onChange={() => toggle(t.id)}
                  />
                </td>
                <td>{t.draft_id}</td>
                <td>{t.title}</td>
                <td>{t.human_review_status}</td>
                <td>{t.automation_fit ?? "—"}</td>
                <td>{t.marked_for_xray_import ? "✓" : ""}</td>
                <td>
                  <Link to={`/tests/${t.id}`}>Edit</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && <p className="muted">No tests match this filter.</p>}
      </div>
    </>
  );
}
