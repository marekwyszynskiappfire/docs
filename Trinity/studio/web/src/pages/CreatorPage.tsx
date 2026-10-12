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
  const [products, setProducts] = useState<
    {
      product_id: string;
      name: string;
      golden_title?: string;
      golden_test_count?: number;
      importer_default_project_key?: string;
    }[]
  >([]);

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
    api.creatorProducts().then((d) => setProducts(d.products)).catch(() => {});
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
      {products.length > 0 && (
        <div className="panel">
          <h3 style={{ marginTop: 0 }}>Product golden corpora (IQ-12)</h3>
          <p className="muted">
            Pick <code>product_id</code> in Reviewer run config and Creator batch JSON. Non-TC imports use{" "}
            <code>requirements</code> (neutral journeys + ONE folder defaults).
          </p>
          <table className="data">
            <thead>
              <tr>
                <th>Product</th>
                <th>Golden corpus</th>
                <th>Importer project</th>
              </tr>
            </thead>
            <tbody>
              {products.map((p) => (
                <tr key={p.product_id}>
                  <td>
                    <code>{p.product_id}</code>
                    <span className="muted"> — {p.name}</span>
                  </td>
                  <td>
                    {p.golden_title ?? "—"}
                    {p.golden_test_count != null ? ` (${p.golden_test_count} refs)` : ""}
                  </td>
                  <td>{p.importer_default_project_key ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

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
