import type { WorkspaceAction } from "../../api";
import { api } from "../../api";
import Term from "./Term";
import CursorAgentControl from "./CursorAgentControl";

type Props = {
  action: WorkspaceAction;
  pipelineRunId: string;
  busy: boolean;
  note: string;
  onPrimary: () => void;
  onCheckNow: (handoffId: string) => void;
};

const WAITING = new Set(["awaiting_cursor", "output_detected", "invalid_output"]);

export default function NextActionCard({ action, pipelineRunId, busy, note, onPrimary, onCheckNow }: Props) {
  const prompt = action.cursor_prompt;
  const waiting = prompt && WAITING.has(prompt.status);
  return (
    <section className="panel ws-next" aria-labelledby="ws-next-title" aria-live="polite">
      <p className="ws-next-eyebrow">Next step</p>
      <h2 id="ws-next-title" className="ws-next-title">
        {action.title}
      </h2>
      <p>{action.reason}</p>
      {action.completion_signal && (
        <p className="muted">
          <strong>Done when:</strong> {action.completion_signal}
        </p>
      )}
      {action.primary.kind !== "none" && (
        <div className="btn-row">
          <button type="button" onClick={onPrimary} disabled={busy}>
            {action.primary.label}
          </button>
          {prompt && (
            <CursorAgentControl
              launch={() => api.launchHandoffAgent(pipelineRunId, prompt.handoff_id)}
              onFinished={() => onCheckNow(prompt.handoff_id)}
            />
          )}
          {waiting && prompt && (
            <button
              type="button"
              className="secondary"
              onClick={() => onCheckNow(prompt.handoff_id)}
              disabled={busy}
            >
              Check for the file now
            </button>
          )}
          {note && <span role="status">{note}</span>}
        </div>
      )}
      {prompt && (
        <details className="ws-prompt">
          <summary>
            Show the Cursor prompt (status: <code>{prompt.status}</code>)
          </summary>
          <p className="muted">
            This is a Cursor <Term id="handoff">handoff</Term>. Paste the prompt into Cursor chat.
          </p>
          <textarea readOnly value={prompt.text} rows={14} aria-label="Cursor prompt" />
        </details>
      )}
    </section>
  );
}
