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

const STAGE_TITLE: Record<CursorAgentRun["stage"], string> = {
  reviewer: "Reviewer is working",
  creator: "Creator is drafting tests",
  importer: "Importer is preparing the plan",
};

const STAGE_HINT: Record<CursorAgentRun["stage"], string> = {
  reviewer:
    "A full Epic review reads Jira, the child issues, and linked pages. Several minutes is normal.",
  creator: "Drafting the suite for this Epic. Several minutes is normal.",
  importer: "Building the Xray plan. This is usually quicker than a review.",
};

function stageTitle(stage: CursorAgentRun["stage"]): string {
  return STAGE_TITLE[stage] ?? "Cursor is working";
}

function stageHint(stage: CursorAgentRun["stage"]): string {
  return STAGE_HINT[stage] ?? "This can take several minutes.";
}

function elapsedLabel(run: CursorAgentRun, now: number): string {
  const start = Date.parse(run.started_at || run.created_at);
  if (!Number.isFinite(start)) return "running";
  const seconds = Math.max(0, Math.floor((now - start) / 1000));
  const minutes = Math.floor(seconds / 60);
  const rest = seconds % 60;
  if (minutes < 1) return `${rest}s`;
  return `${minutes}m ${rest.toString().padStart(2, "0")}s`;
}

function checkLabel(checkedAt: number | null, now: number): string {
  if (!checkedAt) return "Checking Cursor…";
  const seconds = Math.max(0, Math.floor((now - checkedAt) / 1000));
  if (seconds < 2) return "Studio checked Cursor just now";
  return `Studio checked Cursor ${seconds}s ago`;
}
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
  const [checkedAt, setCheckedAt] = useState<number | null>(null);
  const [now, setNow] = useState(() => Date.now());
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
        setCheckedAt(Date.now());
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
          setCheckedAt(Date.now());
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

  const active = !!(run && ACTIVE.has(run.status));

  useEffect(() => {
    if (!active) return;
    const timer = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(timer);
  }, [active]);

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
        {run && !active && (
          <span>
            Cursor: <code>{run.status}</code>
          </span>
        )}
      </div>
      {active && run && (
        <div className="cursor-agent-live">
          <span className="cursor-agent-pulse" aria-hidden="true" />
          <div>
            <p className="cursor-agent-live-title">
              {stageTitle(run.stage)} · {run.status === "queued" ? "starting" : elapsedLabel(run, now)}
            </p>
            <p className="muted" role="status">
              {run.activity || stageHint(run.stage)}
            </p>
            <p className="muted cursor-agent-live-check">{checkLabel(checkedAt, now)}</p>
          </div>
        </div>
      )}
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
