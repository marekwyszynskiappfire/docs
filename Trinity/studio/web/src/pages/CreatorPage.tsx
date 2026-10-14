import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import ImportFeedback from "../components/ImportFeedback";
import ReviewerRunsTable from "../components/ReviewerRunsTable";
import RunListRowActions from "../components/RunListRowActions";
import SortableDataTable from "../components/SortableDataTable";

type RunRow = {
  id: string;
  label: string;
  test_count?: number;
  batch_revision?: number;
  status: string;
};

export default function CreatorPage() {
  const [runs, setRuns] = useState<RunRow[]>([]);
  const [reviewerRuns, setReviewerRuns] = useState<
    { id: string; label: string; unit_count?: number }[]
  >([]);
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
    api.runs().then(setReviewerRuns).catch(() => {});
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
          <SortableDataTable
            rows={products}
            rowKey={(p) => p.product_id}
            defaultSort={{ columnId: "product_id", dir: "asc" }}
            columns={[
              {
                id: "product_id",
                header: "Product",
                getValue: (p) => p.product_id,
                render: (p) => (
                  <>
                    <code>{p.product_id}</code>
                    <span className="muted"> — {p.name}</span>
                  </>
                ),
              },
              {
                id: "golden",
                header: "Golden corpus",
                getValue: (p) => p.golden_title,
                render: (p) =>
                  `${p.golden_title ?? "—"}${
                    p.golden_test_count != null ? ` (${p.golden_test_count} refs)` : ""
                  }`,
              },
              {
                id: "project",
                header: "Importer project",
                getValue: (p) => p.importer_default_project_key,
              },
            ]}
          />
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
        <SortableDataTable
          rows={runs}
          rowKey={(r) => r.id}
          rowClassName={(r) => (highlightId === r.id ? "row-highlight" : undefined)}
          defaultSort={{ columnId: "label", dir: "asc" }}
          columns={[
            {
              id: "label",
              header: "Run",
              getValue: (r) => r.label,
              render: (r) => (
                <>
                  <Link to={`/creator/${encodeURIComponent(r.id)}`}>{r.label}</Link>
                  {highlightId === r.id && (
                    <span className={`import-kind-pill import-kind-pill--${feedback?.kind ?? "new"}`}>
                      {feedback?.kind === "updated" ? "Updated" : "New"}
                    </span>
                  )}
                </>
              ),
            },
            {
              id: "id",
              header: "Studio ID",
              getValue: (r) => r.id,
              render: (r) => <code className="run-id-cell">{r.id}</code>,
            },
            { id: "tests", header: "Tests", getValue: (r) => r.test_count ?? null, align: "right" },
            { id: "batch", header: "Batch rev.", getValue: (r) => r.batch_revision ?? null, align: "right" },
            { id: "status", header: "Status", getValue: (r) => r.status },
            {
              id: "actions",
              header: "Actions",
              getValue: () => "",
              render: (r) => (
                <RunListRowActions kind="creator" runId={r.id} label={r.label} onChanged={load} />
              ),
            },
          ]}
        />
        {runs.length === 0 && <p className="muted">No Creator batches imported yet.</p>}
      </div>

      <div className="panel">
        <h3 style={{ marginTop: 0 }}>Reviewer runs</h3>
        <p className="muted">
          Epic review imports use stable <code>pr-…</code> IDs. Manage from Dashboard or here.
        </p>
        {reviewerRuns.length === 0 ? (
          <p className="muted">No Reviewer runs imported.</p>
        ) : (
          <ReviewerRunsTable runs={reviewerRuns} onChanged={load} />
        )}
      </div>
    </>
  );
}
