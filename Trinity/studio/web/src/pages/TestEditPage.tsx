import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";

type Step = { step: string; expected_result: string; test_data?: string };

export default function TestEditPage() {
  const { testId } = useParams<{ testId: string }>();
  const [caseObj, setCaseObj] = useState<Record<string, unknown> | null>(null);
  const [title, setTitle] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!testId) return;
    api
      .test(testId)
      .then((d) => {
        setCaseObj(d.case);
        setTitle(String(d.case?.title ?? ""));
      })
      .catch((e) => setError(String(e)));
  }, [testId]);

  const steps = (caseObj?.steps as Step[]) ?? [];

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

  const save = async (approve: boolean) => {
    if (!testId || !caseObj) return;
    setError("");
    const body = { ...caseObj, title };
    try {
      await api.saveTest(testId, body, approve ? "approved" : "edited");
      setMessage(approve ? "Saved and marked approved" : "Saved");
    } catch (e) {
      setError(String(e));
    }
  };

  if (!caseObj) return <p className="muted">Loading…</p>;

  return (
    <>
      <p>
        <Link to="/creator">Creator</Link>
      </p>
      <h2>{title || "Test case"}</h2>
      {message && <p className="muted">{message}</p>}
      {error && <p className="error">{error}</p>}

      <div className="panel">
        <label>
          Title
          <input value={title} onChange={(e) => setTitle(e.target.value)} />
        </label>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem", marginTop: "0.75rem" }}>
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
        </div>
      </div>

      <div className="panel">
        <h3 style={{ marginTop: 0 }}>Steps</h3>
        {steps.map((s, i) => (
          <div key={i} style={{ marginBottom: "1rem", borderBottom: "1px solid var(--border)", paddingBottom: "0.75rem" }}>
            <strong>Step {i + 1}</strong>
            <label>
              Action
              <textarea value={s.step} onChange={(e) => updateStep(i, { step: e.target.value })} rows={2} />
            </label>
            <label>
              Expected
              <textarea
                value={s.expected_result}
                onChange={(e) => updateStep(i, { expected_result: e.target.value })}
                rows={2}
              />
            </label>
          </div>
        ))}
        <button type="button" className="secondary" onClick={addStep}>Add step</button>
      </div>

      <div className="btn-row">
        <button type="button" onClick={() => save(false)}>Save</button>
        <button type="button" onClick={() => save(true)}>Save & approve</button>
      </div>
    </>
  );
}
