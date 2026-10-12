import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

type Kind = "pipeline" | "creator";

type Props = {
  kind: Kind;
  runId: string;
  label: string;
  compact?: boolean;
  onRenamed?: (label: string) => void;
  onDeleted?: () => void;
};

export default function RunManageActions({
  kind,
  runId,
  label,
  compact,
  onRenamed,
  onDeleted,
}: Props) {
  const navigate = useNavigate();
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(label);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  const saveRename = async () => {
    const next = draft.trim();
    if (!next || next === label) {
      setEditing(false);
      setDraft(label);
      return;
    }
    setBusy(true);
    setErr("");
    try {
      if (kind === "pipeline") {
        await api.renamePipelineRun(runId, next);
      } else {
        await api.renameCreatorRun(runId, next);
      }
      onRenamed?.(next);
      setEditing(false);
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  };

  const onDelete = async () => {
    const noun = kind === "pipeline" ? "Reviewer" : "Creator";
    if (
      !window.confirm(
        `Delete ${noun} run ${runId}?\n\n“${label}” and all stored data for this run will be removed from Studio.`
      )
    ) {
      return;
    }
    setBusy(true);
    setErr("");
    try {
      if (kind === "pipeline") {
        await api.deletePipelineRun(runId);
        onDeleted?.();
        navigate("/");
      } else {
        await api.deleteCreatorRun(runId);
        onDeleted?.();
        navigate("/creator");
      }
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className={`run-manage${compact ? " run-manage--compact" : ""}`}>
      <code className="run-id" title="Stable Studio ID for BigQuery / Looker joins">
        {runId}
      </code>
      {editing ? (
        <span className="run-manage-edit">
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            aria-label="Run display name"
            disabled={busy}
          />
          <button type="button" className="secondary" disabled={busy} onClick={saveRename}>
            Save
          </button>
          <button
            type="button"
            className="secondary"
            disabled={busy}
            onClick={() => {
              setEditing(false);
              setDraft(label);
            }}
          >
            Cancel
          </button>
        </span>
      ) : (
        <span className="btn-row run-manage-actions">
          <button type="button" className="secondary" disabled={busy} onClick={() => setEditing(true)}>
            Rename
          </button>
          <button type="button" className="danger" disabled={busy} onClick={onDelete}>
            Delete
          </button>
        </span>
      )}
      {err && <span className="error run-manage-err">{err}</span>}
    </div>
  );
}
