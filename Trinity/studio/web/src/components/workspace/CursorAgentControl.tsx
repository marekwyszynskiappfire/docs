import { useEffect, useState } from "react";
import { api, type CursorAgentRun } from "../../api";

type Props = {
  label?: string;
  launch: () => Promise<CursorAgentRun>;
  disabled?: boolean;
  onFinished?: (run: CursorAgentRun) => void;
};

const ACTIVE = new Set(["queued", "running"]);

export default function CursorAgentControl({
  label = "Run in Cursor",
  launch,
  disabled = false,
  onFinished,
}: Props) {
  const [run, setRun] = useState<CursorAgentRun | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!run || !ACTIVE.has(run.status)) return;
    const timer = window.setTimeout(() => {
      api
        .cursorAgentRun(run.id)
        .then((next) => {
          setRun(next);
          if (!ACTIVE.has(next.status)) onFinished?.(next);
        })
        .catch((reason) => setError(String(reason)));
    }, 1500);
    return () => window.clearTimeout(timer);
  }, [run, onFinished]);

  const start = async () => {
    setBusy(true);
    setError("");
    try {
      setRun(await launch());
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
      setRun(await api.cancelCursorAgent(run.id));
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
