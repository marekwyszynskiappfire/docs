import type { QaItemDecision, QaValidity, StudioQa } from "../types/studio-qa";
import { getDecision } from "../types/studio-qa";

type Props = {
  itemId: string;
  label: string;
  studio: StudioQa;
  onPatch: (itemId: string, patch: Partial<QaItemDecision>) => void;
};

export default function QaItemReview({ itemId, label, studio, onPatch }: Props) {
  const d = getDecision(studio, itemId);
  const v = d.validity ?? "pending";

  const setValidity = (validity: QaValidity) => onPatch(itemId, { validity });

  return (
    <div className="qa-review">
      <div className="field-label">{label}</div>
      <div className="decision-actions">
        <button
          type="button"
          className={`dec-btn${v === "valid" ? " active-valid" : ""}`}
          onClick={() => setValidity("valid")}
        >
          Valid — send to epic
        </button>
        <button
          type="button"
          className={`dec-btn${v === "invalid" ? " active-invalid" : ""}`}
          onClick={() => setValidity("invalid")}
        >
          Do not ask
        </button>
        <button
          type="button"
          className={`dec-btn${v === "discuss" ? " active-discuss" : ""}`}
          onClick={() => setValidity("discuss")}
        >
          Discuss
        </button>
      </div>
      <label className={`inline-label send-epic-row${v === "invalid" ? " muted" : ""}`}>
        <input
          type="checkbox"
          checked={!!d.send_to_epic}
          disabled={v === "invalid"}
          onChange={(e) => onPatch(itemId, { send_to_epic: e.target.checked })}
        />
        Include in epic feedback
      </label>
      <label className="stack-label">
        QA comment
        <textarea
          rows={3}
          placeholder="Rationale, wording tweaks, or why this should not go to the epic…"
          value={d.comment ?? ""}
          onChange={(e) => onPatch(itemId, { comment: e.target.value })}
        />
      </label>
    </div>
  );
}
