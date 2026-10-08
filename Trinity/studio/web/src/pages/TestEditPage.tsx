import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";

type Step = { step: string; expected_result: string; test_data?: string };
type PersonaNotes = {
  qa_engineer?: string;
  test_architect?: string;
  automation_engineer?: string;
};

export default function TestEditPage() {
  const { testId } = useParams<{ testId: string }>();
  const [caseObj, setCaseObj] = useState<Record<string, unknown> | null>(null);
  const [title, setTitle] = useState("");
  const [creatorRunId, setCreatorRunId] = useState<string | null>(null);
  const [reviewStatus, setReviewStatus] = useState("pending");
  const [markedForImport, setMarkedForImport] = useState(false);
  const [blockersText, setBlockersText] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!testId) return;
    api
      .test(testId)
      .then((d) => {
        setCaseObj(d.case);
        setTitle(String(d.case?.title ?? ""));
        setCreatorRunId(d.test.creator_run_id ?? null);
        setReviewStatus(d.test.human_review_status ?? "pending");
        setMarkedForImport(Boolean(d.test.marked_for_xray_import));
        const blockers = (d.case?.automation_blockers as string[]) ?? [];
        setBlockersText(blockers.join("\n"));
      })
      .catch((e) => setError(String(e)));
  }, [testId]);

  const steps = (caseObj?.steps as Step[]) ?? [];
  const personaNotes = (caseObj?.persona_notes as PersonaNotes) ?? {};

  const syncCaseFromForm = (): Record<string, unknown> => {
    const blockers = blockersText
      .split("\n")
      .map((s) => s.trim())
      .filter(Boolean);
    const fit = String(caseObj?.automation_fit ?? "partial");
    const autoCand =
      fit === "full" || (fit === "partial" && caseObj?.automation_candidate !== false);
    return {
      ...caseObj,
      title,
      automation_blockers: blockers,
      automation_candidate: autoCand,
    };
  };

  const updateStep = (idx: number, patch: Partial<Step>) => {
    if (!caseObj) return;
    const next = [...steps];
    next[idx] = { ...next[idx], ...patch };
    setCaseObj({ ...caseObj, steps: next });
  };

  const addStep = () => {
    if (!caseObj) return;
    setCaseObj({
      ...caseObj,
      steps: [...steps, { step: "", expected_result: "" }],
    });
  };

  const removeStep = (idx: number) => {
    if (!caseObj || steps.length <= 1) return;
    const next = steps.filter((_, i) => i !== idx);
    setCaseObj({ ...caseObj, steps: next });
  };

  const persist = async (status: string, importMark?: boolean) => {
    if (!testId || !caseObj) return;
    setError("");
    const body = syncCaseFromForm();
    const mark =
      importMark !== undefined
        ? importMark
        : status === "approved"
          ? markedForImport
          : false;
    try {
      const res = await api.saveTest(testId, body, status, mark);
      setReviewStatus(res.human_review_status);
      setMarkedForImport(res.marked_for_xray_import);
      setMessage(
        status === "approved"
          ? "Saved and approved"
          : status === "rejected"
            ? "Marked rejected"
            : "Saved"
      );
    } catch (e) {
      setError(String(e));
    }
  };

  if (!caseObj) return <p className="muted">Loading…</p>;

  const canMarkImport = reviewStatus === "approved";

  return (
    <>
      <p>
        <Link to="/creator">Creator</Link>
        {creatorRunId && (
          <>
            {" · "}
            <Link to={`/creator/${encodeURIComponent(creatorRunId)}`}>Run {creatorRunId}</Link>
          </>
        )}
      </p>
      <h2>{title || "Test case"}</h2>
      <p className="muted">
        Review: <strong>{reviewStatus}</strong>
        {markedForImport && canMarkImport && " · marked for Xray import"}
      </p>
      {message && <p className="muted">{message}</p>}
      {error && <p className="error">{error}</p>}

      <div className="panel">
        <label>
          Title
          <input value={title} onChange={(e) => setTitle(e.target.value)} />
        </label>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr 1fr",
            gap: "0.75rem",
            marginTop: "0.75rem",
          }}
        >
          <label>
            Tier
            <select
              value={String(caseObj.execution_tier ?? "P1")}
              onChange={(e) => setCaseObj({ ...caseObj, execution_tier: e.target.value })}
            >
              {["P0", "P1", "P2", "P3"].map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </label>
          <label>
            Type
            <select
              value={String(caseObj.test_type ?? "Manual")}
              onChange={(e) => setCaseObj({ ...caseObj, test_type: e.target.value })}
            >
              {["Manual", "Cucumber", "Generic", "Other"].map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </label>
          <label>
            Automation fit
            <select
              value={String(caseObj.automation_fit ?? "partial")}
              onChange={(e) =>
                setCaseObj({ ...caseObj, automation_fit: e.target.value })
              }
            >
              {["full", "partial", "manual_only"].map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </label>
        </div>
        <label style={{ marginTop: "0.75rem", display: "block" }}>
          Automation blockers (one per line)
          <textarea
            value={blockersText}
            onChange={(e) => setBlockersText(e.target.value)}
            rows={3}
          />
        </label>
        <label style={{ marginTop: "0.5rem", display: "flex", gap: "0.5rem", alignItems: "center" }}>
          <input
            type="checkbox"
            checked={Boolean(caseObj.automation_candidate)}
            onChange={(e) =>
              setCaseObj({ ...caseObj, automation_candidate: e.target.checked })
            }
          />
          Automation backlog candidate
        </label>
        <label
          style={{
            marginTop: "0.5rem",
            display: "flex",
            gap: "0.5rem",
            alignItems: "center",
            opacity: canMarkImport ? 1 : 0.6,
          }}
        >
          <input
            type="checkbox"
            disabled={!canMarkImport}
            checked={markedForImport && canMarkImport}
            onChange={(e) => setMarkedForImport(e.target.checked)}
          />
          Fit for Xray import (Importer)
        </label>
      </div>

      {(personaNotes.qa_engineer ||
        personaNotes.test_architect ||
        personaNotes.automation_engineer) && (
        <div className="panel">
          <h3 style={{ marginTop: 0 }}>Persona notes</h3>
          {personaNotes.qa_engineer && (
            <p><strong>QA:</strong> {personaNotes.qa_engineer}</p>
          )}
          {personaNotes.test_architect && (
            <p><strong>Architect:</strong> {personaNotes.test_architect}</p>
          )}
          {personaNotes.automation_engineer && (
            <p><strong>Automation:</strong> {personaNotes.automation_engineer}</p>
          )}
        </div>
      )}

      <div className="panel">
        <div className="steps-panel-head">
          <h3 style={{ margin: 0 }}>Steps ({steps.length})</h3>
          <p className="muted steps-hint">
            Action and expected result are shown side by side. There is no step limit — use Add step
            for longer journeys.
          </p>
        </div>
        <div className="steps-table-wrap">
          <table className="steps-table">
            <thead>
              <tr>
                <th className="steps-col-num">#</th>
                <th className="steps-col-action">Step (action)</th>
                <th className="steps-col-expected">Expected result</th>
                <th className="steps-col-actions" aria-label="Row actions" />
              </tr>
            </thead>
            <tbody>
              {steps.map((s, i) => (
                <tr key={i}>
                  <td className="steps-col-num">{i + 1}</td>
                  <td>
                    <textarea
                      className="steps-cell"
                      aria-label={`Step ${i + 1} action`}
                      value={s.step}
                      onChange={(e) => updateStep(i, { step: e.target.value })}
                      rows={4}
                    />
                  </td>
                  <td>
                    <textarea
                      className="steps-cell"
                      aria-label={`Step ${i + 1} expected result`}
                      value={s.expected_result}
                      onChange={(e) => updateStep(i, { expected_result: e.target.value })}
                      rows={4}
                    />
                  </td>
                  <td className="steps-col-actions">
                    <button
                      type="button"
                      className="secondary steps-remove"
                      onClick={() => removeStep(i)}
                      disabled={steps.length <= 1}
                      title="Remove step"
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <button type="button" className="secondary" onClick={addStep}>
          Add step
        </button>
      </div>

      <div className="btn-row">
        <button type="button" onClick={() => persist("edited")}>Save</button>
        <button type="button" onClick={() => persist("approved")}>Save & approve</button>
        <button type="button" className="secondary" onClick={() => persist("rejected")}>
          Reject
        </button>
      </div>
    </>
  );
}
