import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, PipelineRollup, PipelineRun, Stats } from "../api";
import ImportFeedback from "../components/ImportFeedback";
import NewPortfolioPanel from "../components/workspace/NewPortfolioPanel";
import PipelineStrip from "../components/PipelineStrip";
import ContextLoadedAlertsPanel from "../components/ContextLoadedAlertsPanel";
import PortfolioRollupPanel from "../components/PortfolioRollupPanel";
import RunListRowActions from "../components/RunListRowActions";
import SortableDataTable from "../components/SortableDataTable";

export default function HomePage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [rollup, setRollup] = useState<PortfolioRollup | null>(null);
  const [runs, setRuns] = useState<PipelineRun[]>([]);
  const [importPath, setImportPath] = useState(
    "Trinity/studio/fixtures/demo-reviewer-run"
  );
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
    api.stats().then(setStats).catch((e) => setError(String(e)));
    api.portfolioRollup().then(setRollup).catch((e) => setError(String(e)));
    api.runs().then(setRuns).catch((e) => setError(String(e)));
  };

  useEffect(() => {
    load();
  }, []);

  const onImport = async () => {
    setBusy(true);
    setError("");
    setFeedback(null);
    try {
      const res = await api.importRun(importPath);
      const isNew = res.import_kind === "new";
      setFeedback({
        kind: res.import_kind,
        runId: res.pipeline_run_id,
        title: isNew
          ? `Imported new Reviewer run “${res.pipeline_run_id}”`
          : `Re-imported Reviewer run “${res.pipeline_run_id}”`,
        detail: isNew
          ? `${res.units_imported} epic unit(s) added from folder.`
          : `${res.units_imported} epic unit(s) processed; new payload revision(s) stored for each updated epic.`,
      });
      setHighlightId(res.pipeline_run_id);
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
      <p className="page-lead">
        Local workbench for Epic review, test design, and Xray import. Operator guide:{" "}
        <code>Trinity/GUIDE.md</code>
      </p>
      <PipelineStrip stats={stats} />
      {rollup && <PortfolioRollupPanel rollup={rollup} />}
      <ContextLoadedAlertsPanel />
      {stats && (
        <div className="stats-grid">
          <div className="stat-card stat-card--review">
            <div className="label">Pipeline runs</div>
            <div className="value">{stats.pipeline_runs}</div>
          </div>
          <div className="stat-card stat-card--review">
            <div className="label">Review units</div>
            <div className="value">{stats.review_units}</div>
          </div>
          <div className="stat-card stat-card--review">
            <div className="label">Approved reviews</div>
            <div className="value">{stats.review_units_approved}</div>
          </div>
          <div className="stat-card stat-card--warn">
            <div className="label">Open findings</div>
            <div className="value">{stats.open_findings_latest}</div>
          </div>
          <div className="stat-card stat-card--warn">
            <div className="label">Open questions</div>
            <div className="value">{stats.open_questions_latest}</div>
          </div>
          <div className="stat-card stat-card--creator">
            <div className="label">Test cases</div>
            <div className="value">{stats.test_cases}</div>
          </div>
          <div className="stat-card stat-card--creator">
            <div className="label">TC approved</div>
            <div className="value">{stats.test_cases_approved}</div>
          </div>
          <div className="stat-card stat-card--creator">
            <div className="label">Automatable</div>
            <div className="value">{stats.test_cases_automation_candidate}</div>
          </div>
          <div className="stat-card stat-card--import">
            <div className="label">Ready for Xray</div>
            <div className="value">{stats.test_cases_ready_for_import ?? 0}</div>
          </div>
        </div>
      )}

      <NewPortfolioPanel />

      <div className="panel">
        <h2 style={{ marginTop: 0 }}>Import Reviewer run</h2>
        <p className="muted">
          Path relative to DOCS repo root, or absolute. Imports all{" "}
          <code>ONE-*/review-payload.json</code> into SQLite with revision history.
        </p>
        <input
          value={importPath}
          onChange={(e) => setImportPath(e.target.value)}
          aria-label="Reviewer run folder path"
        />
        <div className="btn-row">
          <button type="button" onClick={onImport} disabled={busy}>
            {busy ? "Importing…" : "Import run"}
          </button>
        </div>
        {feedback && (
          <ImportFeedback
            kind={feedback.kind}
            title={feedback.title}
            detail={feedback.detail}
            linkTo={`/workspace/${encodeURIComponent(feedback.runId)}`}
            linkLabel="Open workspace"
            onDismiss={() => setFeedback(null)}
          />
        )}
        {error && <p className="error">{error}</p>}
      </div>

      <div className="panel">
        <h2 style={{ marginTop: 0 }}>Runs</h2>
        {runs.length === 0 && (
          <div className="empty-callout">
            <h3>No Reviewer runs yet</h3>
            <p className="muted" style={{ margin: 0 }}>
              Open <strong>New portfolio</strong>, save it, and copy the Reviewer prompt. After Cursor
              writes the review folder, import it below. Or run <code>seed-demo.sh</code>, then choose{" "}
              <strong>Open workspace</strong>.
            </p>
          </div>
        )}
        <SortableDataTable
          rows={runs}
          rowKey={(r) => r.id}
          rowClassName={(r) => (highlightId === r.id ? "row-highlight" : undefined)}
          defaultSort={{ columnId: "updated", dir: "desc" }}
          columns={[
            {
              id: "label",
              header: "Run",
              getValue: (r) => r.label,
              render: (r) => (
                <>
                  <Link to={`/runs/${r.id}`}>{r.label}</Link>
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
            {
              id: "units",
              header: "Units",
              getValue: (r) => r.unit_count ?? null,
              align: "right",
            },
            {
              id: "updated",
              header: "Updated",
              getValue: (r) => r.updated_at,
              render: (r) => <span className="muted">{r.updated_at.slice(0, 19)}</span>,
            },
            {
              id: "actions",
              header: "Actions",
              getValue: () => "",
              render: (r) => (
                <>
                  <Link to={`/workspace/${encodeURIComponent(r.id)}`}>Open workspace</Link>
                  {" · "}
                  <Link to={`/runs/${encodeURIComponent(r.id)}?tab=statistics`}>Statistics</Link>
                  {" · "}
                  <RunListRowActions kind="pipeline" runId={r.id} label={r.label} onChanged={load} />
                </>
              ),
            },
          ]}
        />
      </div>
    </>
  );
}
