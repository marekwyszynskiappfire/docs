import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, ReviewerRunConfig } from "../../api";
import { buildReviewerCursorPrompt } from "../../lib/reviewerPrompt";
import CursorAgentControl from "./CursorAgentControl";

type Props = {
  portfolioId: string | null;
  pipelineRunId: string;
  workspacePath: string;
  epicKeys: string[];
  reloadToken?: number;
  onCopied: (message: string) => void;
};

export default function ReviewerPromptPanel({
  portfolioId,
  pipelineRunId,
  workspacePath,
  epicKeys,
  reloadToken = 0,
  onCopied,
}: Props) {
  const [active, setActive] = useState(false);
  const [config, setConfig] = useState<ReviewerRunConfig | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!active || !portfolioId) return;
    api
      .reviewerRunConfig(portfolioId)
      .then((next) => {
        setConfig(next);
        setError("");
      })
      .catch((reason) => setError(String(reason)));
  }, [active, portfolioId, reloadToken]);

  const prompt = config
    ? buildReviewerCursorPrompt(config, {
        workspaceUrl: `${window.location.origin}${workspacePath}`,
        epicKeys,
      })
    : "";

  const copy = async () => {
    if (!prompt) return;
    try {
      await navigator.clipboard.writeText(prompt);
      onCopied("Reviewer prompt copied. Paste it into a new Cursor chat.");
    } catch {
      onCopied("Copy failed. Select the prompt text below.");
    }
  };

  return (
    <details
      className="panel ws-reviewer-prompt"
      onToggle={(event) => {
        if (event.currentTarget.open) setActive(true);
      }}
    >
      <summary>
        Reviewer prompt
        {portfolioId ? <span className="muted"> · {portfolioId}</span> : null}
      </summary>
      {!portfolioId && (
        <p className="muted">
          This run has no portfolio config, so there is no Reviewer prompt to copy. Create the
          portfolio under <Link to="/reviewer-configs">Reviewer configs</Link>, then import the run
          again.
        </p>
      )}
      {error && <p className="error">{error}</p>}
      {active && portfolioId && !config && !error && <p className="muted">Loading prompt…</p>}
      {config && (
        <>
          <p className="muted">
            Same portfolio prompt as Reviewer configs, with this run’s workspace and Epics. Questions
            and comments in the prompt must be unanswered decisions someone can act on.
          </p>
          <div className="btn-row">
            <CursorAgentControl
              label="Run Reviewer in Cursor"
              launch={() => api.launchReviewerAgent(config.portfolio_id, pipelineRunId)}
              onFinished={() => onCopied("Reviewer agent finished. Check the review folder now.")}
            />
            <button type="button" className="secondary" onClick={copy}>
              Copy Cursor prompt
            </button>
          </div>
          <pre className="prompt-pre">{prompt}</pre>
        </>
      )}
    </details>
  );
}
