import { useEffect, useRef } from "react";
import type { CursorPrompt, WorkspaceStage } from "../../api";

type Props = {
  open: boolean;
  stages: WorkspaceStage[];
  reviewPrompt: CursorPrompt | null;
  onClose: () => void;
  onShowTips: () => void;
  onCopyReviewPrompt: () => void;
};

export default function ProcessHelp({
  open,
  stages,
  reviewPrompt,
  onClose,
  onShowTips,
  onCopyReviewPrompt,
}: Props) {
  const closeButton = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!open) return;
    closeButton.current?.focus();
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;
  return (
    <aside className="ws-help" role="dialog" aria-modal="false" aria-labelledby="ws-help-title">
      <div className="ws-help-head">
        <h2 id="ws-help-title">Process help</h2>
        <button type="button" className="secondary" ref={closeButton} onClick={onClose}>
          Close
        </button>
      </div>
      <ol className="ws-help-stages">
        {stages.map((stage) => (
          <li key={stage.id}>
            <strong>{stage.title}</strong>
            {stage.status === "current" && <span className="ws-help-here"> — you are here</span>}
            <p>{stage.description}</p>
            <p className="muted">Done when: {stage.done_when}</p>
          </li>
        ))}
      </ol>
      <h3>Recovery</h3>
      <p className="muted">
        Answers came back from the Epic owners? Rescan in Cursor. Studio reuses this workspace and
        adds a revision only for Epics that changed.
      </p>
      <div className="btn-row">
        {reviewPrompt && (
          <button type="button" className="secondary" onClick={onCopyReviewPrompt}>
            Copy rescan prompt
          </button>
        )}
        <button type="button" className="secondary" onClick={onShowTips}>
          Show tips again
        </button>
      </div>
    </aside>
  );
}
