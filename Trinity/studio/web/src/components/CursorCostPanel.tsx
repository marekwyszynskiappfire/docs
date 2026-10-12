import { useCallback, useEffect, useState } from "react";
import { api, CursorUsageSummary } from "../api";

type Props = {
  pipelineRunId?: string;
  creatorRunId?: string;
};

export default function CursorCostPanel({ pipelineRunId, creatorRunId }: Props) {
  const [summary, setSummary] = useState<CursorUsageSummary | null>(null);
  const [stages, setStages] = useState<{ id: string; label: string }[]>([]);
  const [stage, setStage] = useState("reviewer_analyze");
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  const load = useCallback(() => {
    if (!pipelineRunId && !creatorRunId) return;
    api
      .cursorUsageSummary({ pipelineRunId, creatorRunId })
      .then(setSummary)
      .catch((e) => setErr(String(e)));
  }, [pipelineRunId, creatorRunId]);

  useEffect(() => {
    load();
    api.cursorUsageStages().then((r) => setStages(r.stages)).catch(() => {});
  }, [load]);

  const armSession = async () => {
    setBusy(true);
    setErr("");
    try {
      const res = await api.beginCursorSession({
        stage,
        pipeline_run_id: pipelineRunId,
        creator_run_id: creatorRunId,
      });
      setMsg(
        `Cursor session armed for stage “${res.stage}”. Start a new Agent chat in this repo; cost is recorded on session end.`
      );
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  };

  const backfill = async () => {
    setBusy(true);
    setErr("");
    try {
      const res = await api.cursorUsageBackfill();
      setMsg(
        res.error
          ? `Backfill: ${res.error}`
          : `Backfill updated ${res.updated ?? 0} row(s) from Admin API.`
      );
      load();
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  };

  if (!pipelineRunId && !creatorRunId) return null;

  return (
    <div className="panel">
      <h3 style={{ marginTop: 0 }}>Cursor cost (this pipeline)</h3>
      <p className="muted">
        When Trinity runs in Cursor, arm a stage before each Agent session. Hooks record model and{" "}
        <code>conversation_id</code>; dollar cost is filled from the Cursor Team Admin API when configured.
      </p>
      <div className="btn-row" style={{ flexWrap: "wrap", gap: "0.5rem", alignItems: "flex-end" }}>
        <label>
          Next Agent stage
          <select value={stage} onChange={(e) => setStage(e.target.value)} disabled={busy}>
            {stages.map((s) => (
              <option key={s.id} value={s.id}>{s.label}</option>
            ))}
          </select>
        </label>
        <button type="button" onClick={armSession} disabled={busy}>
          Arm Cursor session
        </button>
        <button type="button" className="secondary" onClick={backfill} disabled={busy}>
          Backfill cost from Cursor API
        </button>
      </div>
      {msg && <p className="muted">{msg}</p>}
      {err && <p className="error">{err}</p>}
      {summary && (
        <>
          <p>
            <strong>Total:</strong> {summary.total_cost_display ?? "$0.00"}
            {summary.sessions_pending_cost > 0 && (
              <span className="muted">
                {" "}
                · {summary.sessions_pending_cost} session(s) awaiting cost backfill
              </span>
            )}
          </p>
          {summary.models_used.length > 0 && (
            <p className="muted">
              Models:{" "}
              {summary.models_used.map((m) => `${m.model} (${m.sessions})`).join(" · ")}
            </p>
          )}
          {summary.by_stage.length > 0 ? (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Stage</th>
                  <th>Sessions</th>
                  <th>Cost</th>
                  <th>Tokens (in / out)</th>
                </tr>
              </thead>
              <tbody>
                {summary.by_stage.map((row) => (
                  <tr key={row.stage}>
                    <td>{row.label}</td>
                    <td>{row.sessions}</td>
                    <td>
                      {row.cost_cents > 0 ? `$${(row.cost_cents / 100).toFixed(2)}` : "—"}
                      {row.cost_pending_sessions > 0 && (
                        <span className="muted"> ({row.cost_pending_sessions} pending)</span>
                      )}
                    </td>
                    <td>
                      {row.input_tokens || row.output_tokens
                        ? `${row.input_tokens ?? 0} / ${row.output_tokens ?? 0}`
                        : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="muted">No Cursor sessions recorded yet for this run.</p>
          )}
          {!summary.admin_api_configured && (
            <p className="muted">
              Set <code>CURSOR_ADMIN_API_KEY</code> in <code>Trinity/studio/.env</code> to backfill{" "}
              <code>chargedCents</code>. See <code>Trinity/CURSOR-COST.md</code>.
            </p>
          )}
        </>
      )}
    </div>
  );
}
