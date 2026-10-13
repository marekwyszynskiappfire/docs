import { useCallback, useEffect, useMemo, useState } from "react";
import { api, JiraCommentPreview, JiraStatus } from "../api";

type VariantChoice = "auto" | "full" | "short" | "studio";

type Props = {
  unitId: string;
  jiraKey: string;
  revision: number | null;
  draftDirty: boolean;
  defaultOpen: boolean;
};

const VARIANTS: { id: VariantChoice; label: string }[] = [
  { id: "auto", label: "Smart (auto)" },
  { id: "studio", label: "Studio" },
  { id: "full", label: "Full" },
  { id: "short", label: "Short" },
];

function isProductionHost(host: string | null | undefined): boolean {
  return (host ?? "").toLowerCase().includes("appfire.atlassian.net");
}

export default function JiraEpicCommentPanel({
  unitId,
  jiraKey,
  revision,
  draftDirty,
  defaultOpen,
}: Props) {
  const [open, setOpen] = useState(defaultOpen);

  useEffect(() => {
    if (defaultOpen) setOpen(true);
  }, [defaultOpen]);
  const [jiraStatus, setJiraStatus] = useState<JiraStatus | null>(null);
  const [variant, setVariant] = useState<VariantChoice>("auto");
  const [preview, setPreview] = useState<JiraCommentPreview | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewError, setPreviewError] = useState("");
  const [unlockEdit, setUnlockEdit] = useState(false);
  const [editedBody, setEditedBody] = useState("");
  const [confirmKey, setConfirmKey] = useState("");
  const [reviewed, setReviewed] = useState(false);
  const [allowDuplicate, setAllowDuplicate] = useState(false);
  const [prodConfirm, setProdConfirm] = useState("");
  const [posting, setPosting] = useState(false);
  const [postError, setPostError] = useState("");
  const [postSuccess, setPostSuccess] = useState("");
  const [history, setHistory] = useState<
    {
      id: number;
      variant: string;
      jira_comment_id: string | null;
      jira_comment_url: string | null;
      payload_revision_id: number | null;
      created_at: string;
    }[]
  >([]);

  const production = isProductionHost(jiraStatus?.jira_base_url_host);
  const lastPostRevision = history[0]?.payload_revision_id ?? null;
  const payloadChangedSincePost =
    lastPostRevision != null && revision != null && revision > lastPostRevision;

  const loadStatus = useCallback(() => {
    api
      .jiraStatus()
      .then(setJiraStatus)
      .catch(() => setJiraStatus(null));
  }, []);

  const loadHistory = useCallback(() => {
    api
      .jiraCommentHistory(unitId)
      .then((r) => setHistory(r.posts))
      .catch(() => setHistory([]));
  }, [unitId]);

  const refreshPreview = useCallback(() => {
    if (draftDirty) {
      setPreviewError("Save draft first — preview uses the latest saved payload.");
      return;
    }
    setPreviewLoading(true);
    setPreviewError("");
    api
      .jiraCommentPreview(unitId, variant, unlockEdit)
      .then((p) => {
        setPreview(p);
        setEditedBody(p.body);
        if (!unlockEdit) {
          setAllowDuplicate(false);
        }
      })
      .catch((e) => {
        setPreview(null);
        setPreviewError(String(e));
      })
      .finally(() => setPreviewLoading(false));
  }, [unitId, variant, draftDirty, unlockEdit]);

  useEffect(() => {
    loadStatus();
    loadHistory();
  }, [loadStatus, loadHistory]);

  useEffect(() => {
    if (!open || draftDirty) return;
    const t = window.setTimeout(refreshPreview, 200);
    return () => window.clearTimeout(t);
  }, [open, variant, revision, draftDirty, refreshPreview]);

  const displayBody = unlockEdit ? editedBody : (preview?.body ?? "");
  const blockers = preview?.blockers ?? [];
  const warnings = preview?.warnings ?? [];
  const canPost =
    jiraStatus?.configured &&
    !draftDirty &&
    Boolean(displayBody.trim()) &&
    blockers.length === 0 &&
    confirmKey.trim() === jiraKey &&
    reviewed &&
    (!production || prodConfirm.trim() === "PRODUCTION") &&
    (!preview?.duplicate_warning || allowDuplicate);

  const onUseRecommendation = () => {
    const rec = preview?.recommendation?.variant as VariantChoice | undefined;
    if (rec && VARIANTS.some((v) => v.id === rec)) {
      setVariant(rec);
    } else if (rec) {
      setVariant("auto");
    }
  };

  const onPost = async () => {
    setPostError("");
    setPostSuccess("");
    if (!canPost) return;
    setPosting(true);
    try {
      const res = await api.jiraCommentPost(unitId, {
        variant,
        confirm_issue_key: confirmKey.trim(),
        body: unlockEdit ? editedBody : undefined,
        preview_edited: unlockEdit,
        production_confirm: production ? prodConfirm.trim() : undefined,
        allow_duplicate: allowDuplicate,
      });
      setPostSuccess(`Posted ${res.variant} comment at ${res.posted_at}`);
      loadHistory();
      refreshPreview();
    } catch (e) {
      setPostError(String(e));
    } finally {
      setPosting(false);
    }
  };

  const statusChip = useMemo(() => {
    if (!jiraStatus) return { label: "Jira status unknown", tone: "muted" as const };
    if (jiraStatus.configured) {
      return {
        label: `Jira ready · ${jiraStatus.jira_base_url_host ?? "host"}`,
        tone: production ? ("warn" as const) : ("ok" as const),
      };
    }
    return { label: "Jira credentials missing (.env)", tone: "warn" as const };
  }, [jiraStatus, production]);

  return (
    <details
      className="panel"
      style={{ marginTop: "1rem" }}
      open={open}
      onToggle={(e) => setOpen((e.target as HTMLDetailsElement).open)}
    >
      <summary style={{ cursor: "pointer", fontWeight: 600 }}>Jira epic comment</summary>

      <p className="muted" style={{ marginTop: "0.75rem" }}>
        Preview and post Reviewer-style feedback to{" "}
        <code>{jiraKey}</code>. Preview always reflects the saved payload.
      </p>

      <p
        className={
          statusChip.tone === "ok"
            ? "muted ok-msg"
            : statusChip.tone === "warn"
              ? "error"
              : "muted"
        }
        style={{ marginTop: "0.5rem" }}
      >
        {statusChip.label}
      </p>

      {draftDirty && (
        <p className="error" style={{ marginTop: "0.5rem" }}>
          Unsaved triage changes — save draft, then refresh preview.
        </p>
      )}

      {payloadChangedSincePost && (
        <p className="error" style={{ marginTop: "0.5rem" }}>
          Payload changed since last Jira post — refresh preview before posting again.
        </p>
      )}

      {preview?.recommendation && (
        <div className="panel" style={{ marginTop: "0.75rem", background: "var(--surface-2, #f6f8fa)" }}>
          <strong>Recommendation:</strong> {preview.recommendation.variant}
          {preview.recommendation.reasons?.length ? (
            <ul className="muted" style={{ margin: "0.35rem 0 0.5rem" }}>
              {preview.recommendation.reasons.map((r) => (
                <li key={r}>{r}</li>
              ))}
            </ul>
          ) : null}
          <button type="button" className="secondary" onClick={onUseRecommendation}>
            Use recommendation
          </button>
        </div>
      )}

      <div className="btn-row" style={{ marginTop: "0.75rem" }}>
        {VARIANTS.map((v) => (
          <button
            key={v.id}
            type="button"
            className={variant === v.id ? "" : "secondary"}
            onClick={() => setVariant(v.id)}
          >
            {v.label}
          </button>
        ))}
        <button type="button" className="secondary" onClick={refreshPreview} disabled={previewLoading}>
          {previewLoading ? "Refreshing…" : "Refresh preview"}
        </button>
      </div>

      {previewError && <p className="error">{previewError}</p>}

      {warnings.length > 0 && (
        <ul className="error">
          {warnings.map((w) => (
            <li key={w}>{w}</li>
          ))}
        </ul>
      )}

      {preview?.duplicate_warning && (
        <p className="error" style={{ marginTop: "0.5rem" }}>
          {preview.duplicate_warning}
        </p>
      )}

      <label style={{ display: "block", marginTop: "0.75rem" }}>
        Preview
        <textarea
          readOnly={!unlockEdit}
          value={displayBody}
          onChange={(e) => setEditedBody(e.target.value)}
          rows={14}
          style={{ width: "100%", marginTop: "0.35rem", fontFamily: "monospace", fontSize: "0.85rem" }}
        />
      </label>

      <div className="btn-row">
        <button
          type="button"
          className="secondary"
          onClick={() => navigator.clipboard.writeText(displayBody)}
          disabled={!displayBody.trim()}
        >
          Copy
        </button>
        <button
          type="button"
          className="secondary"
          onClick={() => {
            if (unlockEdit) {
              setUnlockEdit(false);
              setEditedBody(preview?.body ?? "");
            } else {
              setUnlockEdit(true);
            }
          }}
        >
          {unlockEdit ? "Lock wording" : "Unlock wording"}
        </button>
      </div>

      <div style={{ marginTop: "1rem" }}>
        <label>
          <input
            type="checkbox"
            checked={reviewed}
            onChange={(e) => setReviewed(e.target.checked)}
          />
          I reviewed the preview
        </label>
      </div>

      {preview?.duplicate_warning && (
        <div style={{ marginTop: "0.5rem" }}>
          <label>
            <input
              type="checkbox"
              checked={allowDuplicate}
              onChange={(e) => setAllowDuplicate(e.target.checked)}
            />
            Post anyway (duplicate within 24h)
          </label>
        </div>
      )}

      <label style={{ display: "block", marginTop: "0.5rem" }}>
        Type issue key to confirm post
        <input
          type="text"
          value={confirmKey}
          onChange={(e) => setConfirmKey(e.target.value)}
          placeholder={jiraKey}
          style={{ width: "100%", maxWidth: "16rem", marginTop: "0.25rem" }}
        />
      </label>

      {production && (
        <label style={{ display: "block", marginTop: "0.5rem" }}>
          Production gate — type PRODUCTION
          <input
            type="text"
            value={prodConfirm}
            onChange={(e) => setProdConfirm(e.target.value)}
            style={{ width: "100%", maxWidth: "16rem", marginTop: "0.25rem" }}
          />
        </label>
      )}

      <div className="btn-row" style={{ marginTop: "0.75rem" }}>
        <button type="button" onClick={onPost} disabled={!canPost || posting}>
          {posting ? "Posting…" : "Post to Jira"}
        </button>
      </div>

      {postError && <p className="error">{postError}</p>}
      {postSuccess && <p className="muted ok-msg">{postSuccess}</p>}

      {history.length > 0 && (
        <div style={{ marginTop: "1rem" }}>
          <h4 style={{ marginBottom: "0.35rem" }}>Recent posts</h4>
          <ul className="muted">
            {history.slice(0, 5).map((h) => (
              <li key={h.id}>
                {h.created_at} · {h.variant}
                {h.jira_comment_url ? (
                  <>
                    {" · "}
                    <a href={h.jira_comment_url} target="_blank" rel="noreferrer">
                      comment {h.jira_comment_id}
                    </a>
                  </>
                ) : null}
                {h.payload_revision_id != null ? ` · rev ${h.payload_revision_id}` : null}
              </li>
            ))}
          </ul>
        </div>
      )}
    </details>
  );
}
