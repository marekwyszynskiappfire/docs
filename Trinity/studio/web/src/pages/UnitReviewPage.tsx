import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import ReviewUnitSections from "../components/ReviewUnitSections";
import type {
  ClarificationQuestion,
  ContextLoadedEntry,
  ReviewFinding,
  ReviewReport,
} from "../types/review-payload";
import { questionBody } from "../types/review-payload";
import {
  applyDecisionPatch,
  buildEpicFeedback,
  downloadJson,
  attachStudioQa,
  readStudioQa,
  type QaItemDecision,
  type StudioQa,
  type StudioQaAddedQuestion,
} from "../types/studio-qa";

export default function UnitReviewPage() {
  const { unitId } = useParams<{ unitId: string }>();
  const [payload, setPayload] = useState<Record<string, unknown> | null>(null);
  const [jiraKey, setJiraKey] = useState("");
  const [summary, setSummary] = useState("");
  const [revision, setRevision] = useState<number | null>(null);
  const [approvedRevision, setApprovedRevision] = useState<number | null>(null);
  const [qaPlanningFit, setQaPlanningFit] = useState<string | null>(null);
  const [creatorHandoff, setCreatorHandoff] = useState<{
    review_ref: string;
    suite_payload_hint: string;
  } | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!unitId) return;
    api
      .unit(unitId)
      .then((d) => {
        setPayload(attachStudioQa({ ...d.payload }));
        setJiraKey(d.unit.jira_key);
        setSummary(d.unit.summary ?? "");
        setRevision(d.revision);
        setApprovedRevision(d.approved_revision);
        setQaPlanningFit(d.unit.qa_planning_fit);
      })
      .catch((e) => setError(String(e)));
  }, [unitId]);

  const questions = (payload?.questions as ClarificationQuestion[]) ?? [];
  const findings = (payload?.findings as ReviewFinding[]) ?? [];
  const report = payload?.report as ReviewReport | undefined;
  const contextLoaded = (payload?.context_loaded as ContextLoadedEntry[]) ?? [];
  const gateStatus = (payload?.gate as { status?: string } | undefined)?.status;

  const studio: StudioQa = useMemo(() => {
    if (!payload) return { version: 1, decisions: {}, added_questions: [] };
    return readStudioQa(payload);
  }, [payload]);

  const patchStudio = useCallback((updater: (s: StudioQa) => StudioQa) => {
    setPayload((prev) => {
      if (!prev) return prev;
      const current = readStudioQa(prev);
      const nextStudio = updater({
        ...current,
        decisions: { ...current.decisions },
        added_questions: [...(current.added_questions ?? [])],
      });
      return { ...prev, studio_qa: nextStudio };
    });
  }, []);

  const onDecisionPatch = useCallback(
    (itemId: string, patch: Partial<QaItemDecision>) => {
      patchStudio((s) => applyDecisionPatch(s, itemId, patch));
    },
    [patchStudio]
  );

  const onAddQuestion = useCallback(
    (q: StudioQaAddedQuestion, itemId: string) => {
      patchStudio((s) => {
        const added = [...(s.added_questions ?? []), q];
        let next = { ...s, added_questions: added };
        next = applyDecisionPatch(next, itemId, { validity: "valid", send_to_epic: true });
        return next;
      });
    },
    [patchStudio]
  );

  const save = async () => {
    if (!unitId || !payload) return;
    setBusy(true);
    setError("");
    try {
      const r = await api.savePayload(unitId, payload);
      setRevision(r.revision);
      setMessage(`Saved revision ${r.revision}`);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  };

  const downloadEpicFeedback = () => {
    if (!payload) return;
    const data = buildEpicFeedback(payload, jiraKey, questionBody);
    downloadJson(`${jiraKey}-epic-feedback.json`, data);
    setMessage(`Downloaded ${data.items.length} item(s) marked for epic feedback.`);
  };

  const sendToCreator = async () => {
    if (!unitId) return;
    setBusy(true);
    setError("");
    try {
      const r = await api.sendToCreator(unitId);
      await navigator.clipboard.writeText(r.prompt);
      setCreatorHandoff({
        review_ref: r.review_ref,
        suite_payload_hint: r.suite_payload_hint,
      });
      setMessage(
        `Creator prompt copied. review_ref: ${r.review_ref}`
      );
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  };

  const blockedForCreator = qaPlanningFit === "not_fit";
  const canSendToCreator = Boolean(approvedRevision) && !blockedForCreator;

  const approveAndExport = async () => {
    if (!unitId || !payload) return;
    setBusy(true);
    setError("");
    try {
      const r = await api.savePayload(unitId, payload);
      setRevision(r.revision);
      await api.approve(unitId);
      const ex = await api.exportUnit(unitId);
      const refreshed = await api.unit(unitId);
      setApprovedRevision(refreshed.approved_revision);
      setMessage(`Approved and exported to ${ex.review_ref ?? ex.path}`);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  };

  if (!payload) {
    return <p className="muted">Loading…</p>;
  }

  return (
    <>
      <p>
        <Link to="/">Dashboard</Link>
        {payload.run_id && (
          <>
            {" · "}
            <Link to={`/runs/${payload.run_id as string}`}>Run</Link>
          </>
        )}
      </p>
      <h2>{jiraKey}</h2>
      {summary && <p className="muted">{summary}</p>}
      <p className="muted">
        Revision {revision ?? "—"} · QA review is saved in <code>studio_qa</code> on the payload.
        Approve exports <code>review-payload.json</code> for The Creator.
      </p>
      {message && <p className="muted ok-msg">{message}</p>}
      {error && <p className="error">{error}</p>}

      <div className="btn-row">
        <button type="button" onClick={save} disabled={busy}>
          Save draft
        </button>
        <button type="button" className="secondary" onClick={downloadEpicFeedback} disabled={busy}>
          Download epic feedback
        </button>
        <button type="button" onClick={approveAndExport} disabled={busy}>
          Approve & export for Creator
        </button>
        <button
          type="button"
          className="secondary"
          onClick={sendToCreator}
          disabled={busy || !canSendToCreator}
          title={
            blockedForCreator
              ? "Not suitable for test design (not_fit)"
              : !approvedRevision
                ? "Approve first"
                : "Copy Creator prompt to clipboard"
          }
        >
          Send to Creator
        </button>
      </div>
      {blockedForCreator && (
        <p className="error" style={{ marginTop: "0.5rem" }}>
          Creator is disabled: epic is <strong>not suitable for test design</strong> (not_fit).
        </p>
      )}
      {!approvedRevision && !blockedForCreator && (
        <p className="muted" style={{ marginTop: "0.5rem" }}>
          Approve & export before Send to Creator.
        </p>
      )}
      {creatorHandoff && (
        <div className="panel" style={{ marginTop: "1rem" }}>
          <h3 style={{ marginTop: 0 }}>Creator handoff</h3>
          <p className="muted">
            <code>{creatorHandoff.review_ref}</code>
          </p>
          <p className="muted">
            After Cursor run, import suite batch: <code>{creatorHandoff.suite_payload_hint}</code>
          </p>
          <Link to="/creator">Open Creator in Studio →</Link>
        </div>
      )}

      <ReviewUnitSections
        contextLoaded={contextLoaded}
        report={report}
        gateStatus={gateStatus}
        questions={questions}
        findings={findings}
        studio={studio}
        onDecisionPatch={onDecisionPatch}
        onAddQuestion={onAddQuestion}
      />
    </>
  );
}
