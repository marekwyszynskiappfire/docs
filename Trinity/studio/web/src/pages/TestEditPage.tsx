import { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { api } from "../api";
import SortableDataTable from "../components/SortableDataTable";
import {
  TIER_PRIORITY,
  buildPriorityScore,
  scoreFromTier,
  type PriorityScore,
} from "../lib/priorityScore";

type Step = { step: string; expected_result: string; test_data?: string };
type PersonaNotes = {
  qa_engineer?: string;
  test_architect?: string;
  automation_engineer?: string;
};

export default function TestEditPage() {
  const { testId } = useParams<{ testId: string }>();
  const location = useLocation();
  const from = (location.state as { backTo?: string; backLabel?: string } | null) ?? {};
  const [workspacePath, setWorkspacePath] = useState<string | null>(null);
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
        const pipeline = d.test.pipeline_run_id;
        const epic = d.test.jira_key;
        setWorkspacePath(
          pipeline
            ? `/workspace/${encodeURIComponent(pipeline)}${epic ? `?epic=${encodeURIComponent(epic)}` : ""}`
            : null
        );
        setReviewStatus(d.test.human_review_status ?? "pending");
        setMarkedForImport(Boolean(d.test.marked_for_xray_import));
        const blockers = (d.case?.automation_blockers as string[]) ?? [];
        setBlockersText(blockers.join("\n"));
      })
      .catch((e) => setError(String(e)));
  }, [testId]);

  const steps = (caseObj?.steps as Step[]) ?? [];
  const stepRows = useMemo(
    () => steps.map((s, originalIndex) => ({ ...s, originalIndex })),
    [caseObj?.steps]
  );
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

  const patchPriority = (next: Record<string, unknown>) => {
    const score = next.priority_score as PriorityScore;
    const tier = String(score?.derived_tier || next.execution_tier || "P1");
    const deferrable = tier === "P3" ? true : tier === "P0" || tier === "P1" ? false : Boolean(next.deferrable);
    setCaseObj({
      ...next,
      execution_tier: tier,
      priority: TIER_PRIORITY[tier] ?? "Medium",
      deferrable,
      deferrable_rationale:
        tier === "P3"
          ? String(next.deferrable_rationale || "P3 / score ≤ 6: skip under time pressure after P0–P2 journeys pass.")
          : next.deferrable_rationale,
    });
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
  const score = buildPriorityScore(
    (caseObj.priority_score as Partial<PriorityScore>) ?? {},
    String(caseObj.execution_tier ?? "P1")
  );
  const factorSelect = (
    key: keyof Pick<
      PriorityScore,
      "customer_harm" | "likelihood" | "coverage_criticality" | "automation_value"
    >,
    label: string
  ) => (
    <label>
      {label}
      <select
        value={String(score[key])}
        onChange={(e) => {
          const nextScore = buildPriorityScore(
            { ...score, [key]: Number(e.target.value) },
            String(caseObj.execution_tier ?? "P1")
          );
          patchPriority({ ...caseObj, priority_score: nextScore });
        }}
      >
        {[1, 2, 3, 4, 5].map((n) => (
          <option key={n} value={n}>{n}</option>
        ))}
      </select>
    </label>
  );

  const backTo = from.backTo || workspacePath;
  const backLabel = from.backLabel || "Back to workspace";

  return (
    <>
      {backTo && (
        <p className="test-edit-back">
          <Link to={backTo}>{`← ${backLabel}`}</Link>
        </p>
      )}
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
              onChange={(e) => {
                const tier = e.target.value;
                const prev = (caseObj.priority_score as PriorityScore | undefined) ?? scoreFromTier(tier);
                patchPriority({
                  ...caseObj,
                  execution_tier: tier,
                  priority_score: scoreFromTier(tier, prev.rationale),
                });
              }}
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
        <p className="muted" style={{ marginTop: "0.75rem" }}>
          Priority <strong>{String(caseObj.priority ?? TIER_PRIORITY[score.derived_tier] ?? "High")}</strong>
          {" · "}
          Gate score <strong>{score.total}</strong>/15 (harm + likelihood + coverage)
          {" · "}
          derived tier {score.derived_tier}. Automation value does not change the gate.
        </p>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr 1fr 1fr",
            gap: "0.75rem",
          }}
        >
          {factorSelect("customer_harm", "Customer harm")}
          {factorSelect("likelihood", "Likelihood")}
          {factorSelect("coverage_criticality", "Coverage criticality")}
          {factorSelect("automation_value", "Automation value")}
        </div>
        <label style={{ marginTop: "0.75rem", display: "block" }}>
          Score rationale
          <textarea
            value={score.rationale}
            onChange={(e) =>
              patchPriority({
                ...caseObj,
                priority_score: { ...score, rationale: e.target.value },
              })
            }
            rows={2}
          />
        </label>
        <label style={{ marginTop: "0.75rem", display: "block" }}>
          Customer impact
          <textarea
            value={String(caseObj.customer_impact ?? "")}
            onChange={(e) => setCaseObj({ ...caseObj, customer_impact: e.target.value })}
            rows={2}
          />
        </label>
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
          <SortableDataTable
            className="steps-table"
            rows={stepRows}
            rowKey={(r) => String(r.originalIndex)}
            defaultSort={{ columnId: "stepOrder", dir: "asc" }}
            columns={[
              {
                id: "stepOrder",
                header: "#",
                headerClassName: "steps-col-num",
                cellClassName: "steps-col-num",
                getValue: (r) => r.originalIndex,
                render: (r) => r.originalIndex + 1,
              },
              {
                id: "step",
                header: "Step (action)",
                headerClassName: "steps-col-action",
                cellClassName: "steps-col-action",
                getValue: (r) => r.step,
                render: (r) => (
                  <textarea
                    className="steps-cell"
                    aria-label={`Step ${r.originalIndex + 1} action`}
                    value={r.step}
                    onChange={(e) => updateStep(r.originalIndex, { step: e.target.value })}
                    rows={4}
                  />
                ),
              },
              {
                id: "expected",
                header: "Expected result",
                headerClassName: "steps-col-expected",
                cellClassName: "steps-col-expected",
                getValue: (r) => r.expected_result,
                render: (r) => (
                  <textarea
                    className="steps-cell"
                    aria-label={`Step ${r.originalIndex + 1} expected result`}
                    value={r.expected_result}
                    onChange={(e) => updateStep(r.originalIndex, { expected_result: e.target.value })}
                    rows={4}
                  />
                ),
              },
              {
                id: "actions",
                header: "Actions",
                headerClassName: "steps-col-actions",
                cellClassName: "steps-col-actions",
                getValue: () => "",
                render: (r) => (
                  <button
                    type="button"
                    className="secondary steps-remove"
                    onClick={() => removeStep(r.originalIndex)}
                    disabled={steps.length <= 1}
                    title="Remove step"
                  >
                    Remove
                  </button>
                ),
              },
            ]}
          />
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
