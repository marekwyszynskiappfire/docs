import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api, PipelineRollup, PipelineRun, Stats } from "../api";
import ImportFeedback from "../components/ImportFeedback";
import NewPortfolioPanel from "../components/workspace/NewPortfolioPanel";
import PipelineStrip, { type HomePhase } from "../components/PipelineStrip";
import ContextLoadedAlertsPanel from "../components/ContextLoadedAlertsPanel";
import PortfolioRollupPanel from "../components/PortfolioRollupPanel";
import RunListRowActions from "../components/RunListRowActions";
import SortableDataTable from "../components/SortableDataTable";

const DEMO_IMPORT = "Trinity/studio/fixtures/demo-reviewer-run";

function reviewerFolder(sourcePath: string | null): string | null {
  if (!sourcePath) return null;
  const marker = "Trinity/reviewer/runs/";
  const index = sourcePath.indexOf(marker);
  if (index < 0) return null;
  return sourcePath.slice(index).replace(/\/$/, "");
}

export default function HomePage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [rollup, setRollup] = useState<PortfolioRollup | null>(null);
  const [runs, setRuns] = useState<PipelineRun[]>([]);
  const [importPath, setImportPath] = useState(DEMO_IMPORT);
  const importTouched = useRef(false);
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

  useEffect(() => {
    if (importTouched.current || importPath !== DEMO_IMPORT) return;
    const folder = runs.map((run) => reviewerFolder(run.source_path)).find(Boolean);
    if (folder) setImportPath(folder);
  }, [runs, importPath]);

  const onReviewFolder = (folder: string) => {
    importTouched.current = true;
    setImportPath(folder);
    load();
    window.setTimeout(() => {
      document.getElementById("what-now")?.scrollIntoView({ behavior: "smooth", block: "center" });
    }, 0);
  };

  const pendingReview = rollup?.runs.find((run) => run.units_approved < run.unit_count);
  const awaitingTests = rollup?.runs.find((run) => run.units_approved > 0 && run.test_cases === 0);
  const reviewingTests = rollup?.runs.find((run) => run.test_cases > run.test_cases_approved);
  const readyForXray = (stats?.test_cases_ready_for_import ?? 0) > 0;
  const focus = pendingReview ?? awaitingTests ?? reviewingTests ?? rollup?.runs[0] ?? null;
  const phase: HomePhase = !stats
    ? "start"
    : pendingReview
      ? "approve"
      : awaitingTests
        ? "generate"
        : reviewingTests
          ? "review_tests"
          : readyForXray
            ? "import_xray"
            : stats.pipeline_runs === 0
              ? "start"
              : "caught_up";
  const importAlreadyLoaded = runs.some((run) => reviewerFolder(run.source_path) === importPath);

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
      <PipelineStrip stats={stats} phase={phase} focus={focus} />
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

      <NewPortfolioPanel onReviewFolder={onReviewFolder} />

      <div className="panel" id="import-reviewer-run">
        <h2 style={{ marginTop: 0 }}>Import Reviewer run</h2>
        <p className="muted">
          {importAlreadyLoaded
            ? "This folder is already imported. The next step is in the Now card above."
            : "Path relative to DOCS repo root, or absolute. Imports all ONE-*/review-payload.json into SQLite with revision history."}
        </p>
        <input
          value={importPath}
          onChange={(e) => {
            importTouched.current = true;
            setImportPath(e.target.value);
          }}
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
              Open <strong>New portfolio</strong>, save it, and choose <strong>Run Reviewer in Cursor</strong>.
              Copy the prompt only if that launch is unavailable. After Cursor writes the review folder,
              import it below. Or run <code>seed-demo.sh</code>, then choose <strong>Open workspace</strong>.
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
