import { useState } from "react";
import { api } from "../api";

type Kind = "pipeline" | "creator";

type Props = {
  kind: Kind;
  runId: string;
  label: string;
  onChanged: () => void;
};

/** Inline rename/delete for table rows (stays on list page). */
export default function RunListRowActions({ kind, runId, label, onChanged }: Props) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(label);
  const [busy, setBusy] = useState(false);

  const save = async () => {
    const next = draft.trim();
    if (!next) return;
    setBusy(true);
    try {
      if (kind === "pipeline") await api.renamePipelineRun(runId, next);
      else await api.renameCreatorRun(runId, next);
      setEditing(false);
      onChanged();
    } finally {
      setBusy(false);
    }
  };

  const del = async () => {
    if (!window.confirm(`Delete run ${runId} (“${label}”)?`)) return;
    setBusy(true);
    try {
      if (kind === "pipeline") await api.deletePipelineRun(runId);
      else await api.deleteCreatorRun(runId);
      onChanged();
    } finally {
      setBusy(false);
    }
  };

  if (editing) {
    return (
      <span className="run-row-actions">
        <input
          className="run-row-input"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          disabled={busy}
        />
        <button type="button" disabled={busy} onClick={save}>Save</button>
        <button type="button" className="secondary" disabled={busy} onClick={() => setEditing(false)}>
          ✕
        </button>
      </span>
    );
  }

  return (
    <span className="run-row-actions">
      <button type="button" className="secondary" disabled={busy} onClick={() => setEditing(true)}>
        Rename
      </button>
      <button type="button" className="danger" disabled={busy} onClick={del}>
        Delete
      </button>
    </span>
  );
}
