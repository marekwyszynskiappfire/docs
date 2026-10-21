import { useCallback, useEffect, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { api, EpicChildInventory, ReviewUnit } from "../api";
import CursorCostPanel from "../components/CursorCostPanel";
import RunManageActions from "../components/RunManageActions";
import RunStatisticsPanel from "../components/RunStatisticsPanel";
import JiraKeyLink from "../components/JiraKeyLink";
import SortableDataTable from "../components/SortableDataTable";

type Handoff = {
  creator_jql?: string;
  included_epics?: string[];
  excluded_from_creator_count?: number;
  portfolio_report_path?: string | null;
  source_path?: string | null;
  handoff_export?: Record<string, unknown>;
};

export default function RunPage() {
  const { runId } = useParams<{ runId: string }>();
  const [units, setUnits] = useState<ReviewUnit[]>([]);
  const [sourcePath, setSourcePath] = useState<string | null>(null);
  const [handoff, setHandoff] = useState<Handoff | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [childInventory, setChildInventory] = useState<EpicChildInventory | null>(null);
  const [runLabel, setRunLabel] = useState("");
  const [reportIndex, setReportIndex] = useState<
    Record<string, { open_url: string | null; report_exists: boolean }>
  >({});
  const [portfolioOpenUrl, setPortfolioOpenUrl] = useState<string | null>(null);
  const [searchParams, setSearchParams] = useSearchParams();
  const tab: "overview" | "statistics" =
    searchParams.get("tab") === "statistics" ? "statistics" : "overview";
  const setTab = (next: "overview" | "statistics") => {
    if (next === "overview") {
      searchParams.delete("tab");
      setSearchParams(searchParams, { replace: true });
    } else {
      setSearchParams({ tab: "statistics" }, { replace: true });
    }
  };

  const reload = useCallback(async () => {
    if (!runId) return;
    const r = await api.run(runId);
    setUnits(r.units);
    setRunLabel(r.label);
    setSourcePath(r.source_path);
    const h = await api.creatorHandoff(runId);
    setHandoff(h as Handoff);
    const inv = await api.runChildInventory(runId);
    setChildInventory(inv);
    const reports = await api.runReviewReports(runId);
    setPortfolioOpenUrl(reports.portfolio_open_url);
    const idx: Record<string, { open_url: string | null; report_exists: boolean }> = {};
    for (const e of reports.epics) {
      idx[e.unit_id] = { open_url: e.open_url, report_exists: e.report_exists };
    }
    setReportIndex(idx);
  }, [runId]);

  useEffect(() => {
    if (!runId) return;
    reload().catch((e) => setError(String(e)));
  }, [runId, reload]);

  const copyText = async (text: string, okMsg: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setMessage(okMsg);
      setError("");
    } catch {
      setError("Clipboard failed");
    }
  };

  const exportJson = handoff?.handoff_export ?? handoff;

  const downloadHandoff = () => {
    if (!exportJson || !runId) return;
    const blob = new Blob([JSON.stringify(exportJson, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `creator-handoff-${runId}.json`;
    a.click();
    URL.revokeObjectURL(url);
    setMessage("Downloaded creator-handoff JSON");
  };

  const setAllCreator = async (
    include: boolean,
    filter?: (u: ReviewUnit) => boolean
  ) => {
    setBusy(true);
    setError("");
    try {
      const targets = filter ? units.filter(filter) : units;
      await Promise.all(
        targets.map((u) => api.patchUnit(u.id, { include_in_creator: include }))
      );
      await reload();
      setMessage(
        include
          ? `Included ${targets.length} epic(s) for Creator`
          : `Excluded ${targets.length} epic(s) from Creator`
      );
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  };

  const toggleCreator = async (u: ReviewUnit) => {
    await api.patchUnit(u.id, { include_in_creator: !u.include_in_creator });
    await reload();
  };

  const gateClass = (gate: string | null) => {
    const g = (gate || "").toUpperCase();
    if (g.includes("GREEN") || g === "PASS") return "badge ok";
    if (g.includes("AMBER") || g.includes("WARN")) return "badge sev-med";
    if (g.includes("RED") || g.includes("BLOCK")) return "badge sev-high";
    return "badge";
  };

  const fitClass = (fit: string | null) => {
    if (fit === "not_fit") return "badge sev-high";
    if (fit === "fit" || fit === "good") return "badge ok";
    return "badge sev-low";
  };

  if (!runId) return null;

  return (
    <>
      <p>
        <Link to="/">← Workspace</Link>
        {runId && (
          <>
            {" · "}
            <Link to={`/workspace/${encodeURIComponent(runId)}`}>Open workspace</Link>
          </>
        )}
      </p>
      <h2>{runLabel || runId}</h2>
      {runId && (
        <RunManageActions
          kind="pipeline"
          runId={runId}
          label={runLabel || runId}
          onRenamed={setRunLabel}
        />
      )}
      {sourcePath && (
        <p className="muted">
          Imported from: <code>{sourcePath}</code>
        </p>
      )}
      {error && <p className="error">{error}</p>}
      {message && <p className="muted">{message}</p>}

      <div className="run-tabs btn-row" role="tablist" aria-label="Pipeline run views">
        <button
          type="button"
          role="tab"
          aria-selected={tab === "overview"}
          className={tab === "overview" ? "" : "secondary"}
          onClick={() => setTab("overview")}
        >
          Overview
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={tab === "statistics"}
          className={tab === "statistics" ? "" : "secondary"}
          onClick={() => setTab("statistics")}
        >
          Statistics
        </button>
      </div>

      {tab === "statistics" && <RunStatisticsPanel runId={runId} />}

      {tab === "overview" && (
        <>
      <CursorCostPanel pipelineRunId={runId} />

      {handoff && (
        <div className="panel">
          <h3 style={{ marginTop: 0 }}>Creator handoff</h3>
          <p className="muted">
            Included: {handoff.included_epics?.length ?? 0} epic(s) · excluded from Creator:{" "}
            {handoff.excluded_from_creator_count ?? 0}
          </p>
          {(portfolioOpenUrl || handoff.portfolio_report_path) && (
            <p>
              Portfolio report:{" "}
              {portfolioOpenUrl ? (
                <a href={portfolioOpenUrl} target="_blank" rel="noreferrer">
                  Open Profile A portfolio HTML
                </a>
              ) : (
                <code>{handoff.portfolio_report_path}</code>
              )}
              {handoff.portfolio_report_path && (
                <button
                  type="button"
                  className="secondary"
                  style={{ marginLeft: "0.5rem" }}
                  onClick={() =>
                    copyText(handoff.portfolio_report_path!, "Portfolio path copied")
                  }
                >
                  Copy path
                </button>
              )}
            </p>
          )}
          <label>
            Creator JQL (live from Studio toggles)
            <textarea
              readOnly
              value={String(handoff.creator_jql ?? "")}
              rows={3}
              aria-label="Creator JQL"
            />
          </label>
          <div className="btn-row">
            <button
              type="button"
              onClick={() => copyText(String(handoff.creator_jql ?? ""), "JQL copied")}
            >
              Copy JQL
            </button>
            <button
              type="button"
              onClick={() =>
                copyText(JSON.stringify(exportJson, null, 2), "Handoff JSON copied")
              }
            >
              Copy handoff JSON
            </button>
            <button type="button" className="secondary" onClick={downloadHandoff}>
              Download JSON
            </button>
          </div>
          <details style={{ marginTop: "0.75rem" }}>
            <summary className="muted">Handoff JSON preview</summary>
            <pre className="prompt-pre">{JSON.stringify(exportJson, null, 2)}</pre>
          </details>
        </div>
      )}

      {childInventory && childInventory.epics.some((e) => e.child_count > 0) && (
        <details className="panel child-inventory-panel">
          <summary className="child-inventory-panel-summary">
            <span className="child-inventory-panel-title">Child inventory (Reviewer rollup)</span>
            <span className="muted child-inventory-panel-meta">
              {childInventory.total_children != null
                ? `${childInventory.total_children} children`
                : ""}
              {childInventory.run_status_mix &&
              Object.keys(childInventory.run_status_mix).length > 0
                ? ` · ${api.formatMix(childInventory.run_status_mix)}`
                : ""}
            </span>
          </summary>
          <div className="child-inventory-panel-body">
            <p className="muted" style={{ marginTop: 0 }}>
              Full child set from latest payload per epic — parity with Reviewer HTML § children.
            </p>
            {childInventory.epics.map((epic) =>
              epic.child_count === 0 ? null : (
                <details key={epic.unit_id} className="child-inventory-epic">
                  <summary>
                    <JiraKeyLink issueKey={epic.jira_key} /> — {epic.child_count} children (
                    {api.formatMix(epic.status_mix)})
                  </summary>
                  <SortableDataTable
                    className="data child-table"
                    rows={epic.children}
                    rowKey={(c, i) => c.key ?? c.summary ?? String(i)}
                    defaultSort={{ columnId: "key", dir: "asc" }}
                    columns={[
                      {
                        id: "key",
                        header: "Key",
                        getValue: (c) => c.key,
                        render: (c) =>
                          c.key ? <JiraKeyLink issueKey={c.key} /> : "—",
                      },
                      { id: "type", header: "Type", getValue: (c) => c.type },
                      { id: "status", header: "Status", getValue: (c) => c.status },
                      {
                        id: "summary",
                        header: "Summary",
                        getValue: (c) => c.summary,
                        cellClassName: "muted",
                      },
                    ]}
                  />
                </details>
              )
            )}
          </div>
        </details>
      )}

      <div className="panel">
        <div className="btn-row" style={{ marginBottom: "0.75rem" }}>
          <button type="button" disabled={busy} onClick={() => setAllCreator(true)}>
            Include all
          </button>
          <button type="button" disabled={busy} onClick={() => setAllCreator(false)}>
            Exclude all
          </button>
          <button
            type="button"
            disabled={busy}
            className="secondary"
            onClick={() => setAllCreator(false, (u) => u.qa_planning_fit === "not_fit")}
          >
            Exclude not_fit
          </button>
        </div>
        <SortableDataTable
          rows={units}
          rowKey={(u) => u.id}
          defaultSort={{ columnId: "jira_key", dir: "asc" }}
          columns={[
            {
              id: "jira_key",
              header: "Epic",
              getValue: (u) => u.jira_key,
              render: (u) => (
                <>
                  <strong>
                    <JiraKeyLink issueKey={u.jira_key} />
                  </strong>
                  <div className="muted">{u.summary}</div>
                </>
              ),
            },
            {
              id: "gate",
              header: "Gate",
              getValue: (u) => u.gate_status,
              render: (u) => (
                <span className={gateClass(u.gate_status)}>{u.gate_status ?? "—"}</span>
              ),
            },
            {
              id: "fit",
              header: "Test design fit",
              getValue: (u) => u.qa_planning_fit,
              render: (u) => (
                <span className={fitClass(u.qa_planning_fit)}>{u.qa_planning_fit ?? "—"}</span>
              ),
            },
            {
              id: "creator",
              header: "In Creator",
              getValue: (u) => (u.include_in_creator ? 1 : 0),
              render: (u) => (
                <label style={{ display: "flex", alignItems: "center", gap: "0.35rem", margin: 0 }}>
                  <input
                    type="checkbox"
                    checked={Boolean(u.include_in_creator)}
                    onChange={() => toggleCreator(u)}
                  />
                  {u.include_in_creator ? "Yes" : "No"}
                </label>
              ),
            },
            {
              id: "approved",
              header: "Approved",
              getValue: (u) => (u.approved_revision_id ? 1 : 0),
              render: (u) =>
                u.approved_revision_id ? (
                  <span className="badge ok">yes</span>
                ) : (
                  <span className="badge">no</span>
                ),
            },
            {
              id: "actions",
              header: "Actions",
              getValue: () => "",
              render: (u) => (
                <>
                  <Link to={`/units/${u.id}`}>Edit review</Link>
                  {reportIndex[u.id]?.report_exists && reportIndex[u.id]?.open_url && (
                    <>
                      {" · "}
                      <a href={reportIndex[u.id].open_url!} target="_blank" rel="noreferrer">
                        HTML
                      </a>
                    </>
                  )}
                </>
              ),
            },
          ]}
        />
      </div>
        </>
      )}
    </>
  );
}
