import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api, PipelineRun, PipelineRunCompare } from "../api";
import RunComparisonDashboard from "../components/RunComparisonDashboard";
import RunStatisticsPanel from "../components/RunStatisticsPanel";
import TcReadinessChart from "../components/TcReadinessChart";

type Mode = "single" | "compare";

export default function StatisticsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [runs, setRuns] = useState<PipelineRun[]>([]);
  const [error, setError] = useState("");
  const [compareData, setCompareData] = useState<PipelineRunCompare | null>(null);
  const [compareLoading, setCompareLoading] = useState(false);
  const compareRequestId = useRef(0);
  const [singleSummary, setSingleSummary] = useState<
    import("../api").PipelineRunStatistics["summary"] | null
  >(null);

  const mode: Mode = searchParams.get("mode") === "compare" ? "compare" : "single";
  const runIdFromUrl = searchParams.get("run") ?? "";
  const compareIds = useMemo(
    () =>
      (searchParams.get("compare") ?? "")
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
    [searchParams]
  );

  useEffect(() => {
    api.runs().then(setRuns).catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    if (runs.length === 0) return;
    if (mode === "single" && !runIdFromUrl) {
      const next = new URLSearchParams(searchParams);
      next.set("run", runs[0].id);
      setSearchParams(next, { replace: true });
    }
    if (mode === "compare" && compareIds.length < 2 && runs.length >= 2) {
      const next = new URLSearchParams(searchParams);
      next.set("compare", `${runs[0].id},${runs[1].id}`);
      setSearchParams(next, { replace: true });
    }
  }, [runs, mode, runIdFromUrl, compareIds.length, searchParams, setSearchParams]);

  const compareKey = compareIds.join(",");

  const loadCompare = useCallback(() => {
    if (compareIds.length < 2) {
      setCompareData(null);
      setCompareLoading(false);
      return;
    }
    const requestId = ++compareRequestId.current;
    setCompareData(null);
    setCompareLoading(true);
    setError("");
    api
      .compareStatistics(compareIds)
      .then((data) => {
        if (requestId !== compareRequestId.current) return;
        const key = data.runs.map((r) => r.pipeline_run_id).join(",");
        if (key !== compareIds.join(",")) return;
        setCompareData(data);
      })
      .catch((e) => {
        if (requestId !== compareRequestId.current) return;
        setCompareData(null);
        setError(String(e));
      })
      .finally(() => {
        if (requestId === compareRequestId.current) {
          setCompareLoading(false);
        }
      });
  }, [compareIds]);

  useEffect(() => {
    if (mode === "compare") {
      loadCompare();
    }
  }, [mode, loadCompare]);

  useEffect(() => {
    if (mode !== "single" || !runIdFromUrl) {
      setSingleSummary(null);
      return;
    }
    api
      .runStatistics(runIdFromUrl)
      .then((r) => setSingleSummary(r.summary))
      .catch(() => setSingleSummary(null));
  }, [mode, runIdFromUrl]);

  const setMode = (next: Mode) => {
    const params = new URLSearchParams(searchParams);
    params.set("mode", next);
    setSearchParams(params);
  };

  const toggleCompareRun = (id: string) => {
    const set = new Set(compareIds);
    if (set.has(id)) set.delete(id);
    else if (set.size < 5) set.add(id);
    const params = new URLSearchParams(searchParams);
    params.set("mode", "compare");
    params.set("compare", Array.from(set).join(","));
    setSearchParams(params);
  };

  const selectedRun = runs.find((r) => r.id === runIdFromUrl) ?? null;

  return (
    <div className="stats-dashboard-page">
      <header className="stats-dashboard-header panel">
        <div>
          <h2 style={{ margin: 0 }}>Pipeline statistics</h2>
          <p className="muted" style={{ margin: "0.35rem 0 0" }}>
            Reviewer → Creator → Importer metrics, TC creation readiness, and run comparison.
          </p>
        </div>
        <div className="run-tabs btn-row" role="tablist" aria-label="Statistics view">
          <button
            type="button"
            role="tab"
            aria-selected={mode === "single"}
            className={mode === "single" ? "" : "secondary"}
            onClick={() => setMode("single")}
          >
            Single run
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={mode === "compare"}
            className={mode === "compare" ? "" : "secondary"}
            onClick={() => setMode("compare")}
          >
            Compare runs
          </button>
        </div>
      </header>

      {error && <p className="error">{error}</p>}

      {mode === "single" && (
        <>
          <div className="panel stats-run-picker">
            {runs.length === 0 ? (
              <p className="muted">Import a Reviewer run on the Dashboard first.</p>
            ) : (
              <label>
                Pipeline run
                <select
                  value={runIdFromUrl}
                  onChange={(e) => {
                    const params = new URLSearchParams(searchParams);
                    params.set("run", e.target.value);
                    setSearchParams(params);
                  }}
                  aria-label="Pipeline run"
                >
                  {runs.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.label} ({r.unit_count ?? 0} epics)
                    </option>
                  ))}
                </select>
              </label>
            )}
            {selectedRun && (
              <p className="muted" style={{ margin: "0.75rem 0 0" }}>
                <Link to={`/runs/${encodeURIComponent(selectedRun.id)}?tab=statistics`}>
                  Open on run page
                </Link>
              </p>
            )}
          </div>

          {singleSummary && (
            <div className="panel stats-hero-readiness">
              <TcReadinessChart summary={singleSummary} title="Epic readiness for test case creation" />
              <p className="muted tc-readiness-help">
                <strong>Ready</strong> — Reviewer <code>report.qa_planning_fit</code> ={" "}
                <code>fit</code>. <strong>Reservations</strong> — <code>provisional</code> (often
                with gate <code>PASS_WITH_WARNINGS</code>). <strong>Not ready</strong> —{" "}
                <code>not_fit</code> and scope-lock signals.
              </p>
            </div>
          )}

          {selectedRun && <RunStatisticsPanel runId={selectedRun.id} />}
        </>
      )}

      {mode === "compare" && (
        <>
          <div className="panel">
            <h3 style={{ marginTop: 0 }}>Select runs to compare (2–5)</h3>
            <p className="muted">First selected run is the baseline for Δ columns.</p>
            <div className="compare-run-picker">
              {runs.map((r) => {
                const checked = compareIds.includes(r.id);
                const order = compareIds.indexOf(r.id);
                return (
                  <label key={r.id} className={`compare-run-chip ${checked ? "checked" : ""}`}>
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => toggleCompareRun(r.id)}
                      disabled={!checked && compareIds.length >= 5}
                    />
                    <span>
                      {r.label}
                      {checked && order === 0 && <span className="baseline-tag">baseline</span>}
                    </span>
                  </label>
                );
              })}
            </div>
            <div className="btn-row" style={{ marginTop: "0.75rem" }}>
              <button type="button" onClick={loadCompare} disabled={compareIds.length < 2 || compareLoading}>
                {compareLoading ? "Comparing…" : "Refresh comparison"}
              </button>
            </div>
          </div>

          {compareIds.length < 2 && (
            <p className="muted">Select at least two runs to compare.</p>
          )}
          {compareLoading && compareIds.length >= 2 && !compareData && (
            <p className="muted">Loading comparison…</p>
          )}
          {compareData &&
            compareIds.length >= 2 &&
            compareData.runs.map((r) => r.pipeline_run_id).join(",") === compareKey && (
              <RunComparisonDashboard data={compareData} />
            )}
        </>
      )}
    </div>
  );
}
