import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import ImportFeedback from "../components/ImportFeedback";

type RunRow = {
  id: string;
  label: string;
  test_count?: number;
  batch_revision?: number;
  status: string;
};

export default function CreatorPage() {
  const [runs, setRuns] = useState<RunRow[]>([]);
  const [batchPath, setBatchPath] = useState("Trinity/creator/samples/demo-story.suite.json");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [highlightId, setHighlightId] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<{
    kind: "new" | "updated";
    title: string;
    detail: string;
    runId: string;
  } | null>(null);

  const load = () => {
    api.creatorRuns().then(setRuns).catch((e) => setError(String(e)));
  };

  useEffect(() => {
    load();
  }, []);

  const onImport = async () => {
    setBusy(true);
    setError("");
    setFeedback(null);
    try {
      const res = await api.importBatch(batchPath);
      const isNew = res.import_kind === "new";
      setFeedback({
        kind: res.import_kind,
        runId: res.creator_run_id,
        title: isNew
          ? `Imported new Creator run “${res.creator_run_id}”`
          : `Updated existing Creator run “${res.creator_run_id}”`,
        detail: isNew
          ? `${res.tests_imported} test(s) loaded (batch revision ${res.batch_revision}).`
          : `Re-imported ${res.tests_imported} test(s). Batch revision is now ${res.batch_revision}. Review status on existing rows is unchanged until you edit tests.`,
      });
      setHighlightId(res.creator_run_id);
      window.setTimeout(() => setHighlightId(null), 8000);
      load();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <h2>Creator runs</h2>
      <div className="panel">
        <h3 style={{ marginTop: 0 }}>Import TestCaseDraft batch</h3>
        <p className="muted">
          Path to a suite batch JSON (<code>tests[]</code>, TestCaseDraft schema) relative to the DOCS repo root.
        </p>
        <input value={batchPath} onChange={(e) => setBatchPath(e.target.value)} />
        <div className="btn-row">
          <button type="button" onClick={onImport} disabled={busy}>
            Import batch
          </button>
        </div>
        {feedback && (
          <ImportFeedback
            kind={feedback.kind}
            title={feedback.title}
            detail={feedback.detail}
            linkTo={`/creator/${encodeURIComponent(feedback.runId)}`}
            linkLabel="Open run →"
            onDismiss={() => setFeedback(null)}
          />
        )}
        {error && <p className="error">{error}</p>}
      </div>

      <div className="panel">
        <table className="data">
          <thead>
            <tr>
              <th>Run</th>
              <th>Tests</th>
              <th>Batch rev.</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((r) => (
              <tr key={r.id} className={highlightId === r.id ? "row-highlight" : undefined}>
                <td>
                  <Link to={`/creator/${encodeURIComponent(r.id)}`}>{r.label}</Link>
                  {highlightId === r.id && (
                    <span className={`import-kind-pill import-kind-pill--${feedback?.kind ?? "new"}`}>
                      {feedback?.kind === "updated" ? "Updated" : "New"}
                    </span>
                  )}
                </td>
                <td>{r.test_count}</td>
                <td>{r.batch_revision ?? "—"}</td>
                <td>{r.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {runs.length === 0 && <p className="muted">No Creator batches imported yet.</p>}
      </div>
    </>
  );
}
