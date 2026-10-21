import { useState } from "react";
import { Link } from "react-router-dom";
import { api, ReviewerRunConfig } from "../../api";
import { buildReviewerCursorPrompt } from "../../lib/reviewerPrompt";

type Props = {
  portfolioId: string | null;
  workspacePath: string;
  epicKeys: string[];
  onCopied: (message: string) => void;
};

export default function ReviewerPromptPanel({
  portfolioId,
  workspacePath,
  epicKeys,
  onCopied,
}: Props) {
  const [active, setActive] = useState(false);
  const [config, setConfig] = useState<ReviewerRunConfig | null>(null);
  const [error, setError] = useState("");

  const open = () => {
    setActive(true);
    if (!portfolioId || config || error) return;
    api
      .reviewerRunConfig(portfolioId)
      .then(setConfig)
      .catch((reason) => setError(String(reason)));
  };

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
        if (event.currentTarget.open) open();
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
            <button type="button" onClick={copy}>
              Copy Cursor prompt
            </button>
          </div>
          <pre className="prompt-pre">{prompt}</pre>
        </>
      )}
    </details>
  );
}
