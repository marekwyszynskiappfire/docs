import { useEffect, useRef, useState } from "react";
import { api, type CursorAgentRun } from "../../api";

type AttachTarget = {
  stage?: CursorAgentRun["stage"];
  pipelineRunId?: string;
  handoffId?: string;
  portfolioId?: string;
  creatorRunId?: string;
};

type Props = {
  label?: string;
  launch: () => Promise<CursorAgentRun>;
  disabled?: boolean;
  onFinished?: (run: CursorAgentRun) => void;
  attach?: AttachTarget;
};

const ACTIVE = new Set(["queued", "running"]);
const MAX_POLL_FAILURES = 8;

export default function CursorAgentControl({
  label = "Run in Cursor",
  launch,
  disabled = false,
  onFinished,
  attach,
}: Props) {
  const attachKey = attach ? JSON.stringify(attach) : "";
  const [run, setRun] = useState<CursorAgentRun | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [pollFailures, setPollFailures] = useState(0);
  const onFinishedRef = useRef(onFinished);
  onFinishedRef.current = onFinished;

  useEffect(() => {
    if (!attachKey) return;
    const target = JSON.parse(attachKey) as AttachTarget;
    let cancelled = false;
    api
      .cursorAgentRuns({
        stage: target.stage,
        pipelineRunId: target.pipelineRunId,
        handoffId: target.handoffId,
        portfolioId: target.portfolioId,
        creatorRunId: target.creatorRunId,
        activeOnly: true,
      })
      .then((rows) => {
        if (cancelled || !rows[0]) return;
        setRun((current) => current ?? rows[0]);
        setPollFailures(0);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [attachKey]);

  useEffect(() => {
    if (!run || !ACTIVE.has(run.status)) return;
    if (pollFailures >= MAX_POLL_FAILURES) return;
    const delay = Math.min(1500 * 2 ** pollFailures, 15000);
    const timer = window.setTimeout(() => {
      api
        .cursorAgentRun(run.id)
        .then((next) => {
          setPollFailures(0);
          setError("");
          setRun(next);
          if (!ACTIVE.has(next.status)) onFinishedRef.current?.(next);
        })
        .catch((reason) => {
          setPollFailures((count) => count + 1);
          setError(
            pollFailures + 1 >= MAX_POLL_FAILURES
              ? `${String(reason).replace(/^Error:\s*/, "")} Status checks stopped. Use Run again after the agent finishes, or refresh the page.`
              : "Reconnecting to the Cursor agent…"
          );
        });
    }, delay);
    return () => window.clearTimeout(timer);
  }, [run, pollFailures]);

  const start = async () => {
    setBusy(true);
    setError("");
    setPollFailures(0);
    try {
      const next = await launch();
      setRun(next);
      if (!ACTIVE.has(next.status)) onFinishedRef.current?.(next);
    } catch (reason) {
      setError(String(reason).replace(/^Error:\s*/, ""));
    } finally {
      setBusy(false);
    }
  };

  const cancel = async () => {
    if (!run) return;
    setBusy(true);
    setError("");
    try {
      const next = await api.cancelCursorAgent(run.id);
      setRun(next);
      if (!ACTIVE.has(next.status)) onFinishedRef.current?.(next);
    } catch (reason) {
      setError(String(reason).replace(/^Error:\s*/, ""));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="cursor-agent-control">
      <div className="btn-row">
        <button type="button" onClick={start} disabled={disabled || busy || !!(run && ACTIVE.has(run.status))}>
          {busy ? "Starting…" : run && !ACTIVE.has(run.status) ? `Run again in Cursor` : label}
        </button>
        {run && ACTIVE.has(run.status) && (
          <button type="button" className="secondary" onClick={cancel} disabled={busy}>
            Cancel
          </button>
        )}
        {run && (
          <span role="status">
            Cursor: <code>{run.status}</code>
            {run.sdk_run_id ? ` · ${run.sdk_run_id}` : ""}
          </span>
        )}
      </div>
      {run?.error && <p className="error">{run.error}</p>}
      {error && <p className="error">{error}</p>}
      {run?.final_text && (
        <details>
          <summary>Cursor result</summary>
          <pre className="prompt-pre">{run.final_text}</pre>
        </details>
      )}
    </div>
  );
}
