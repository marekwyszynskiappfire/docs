import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, CoverageProfile, CoverageProfileId, CreatorTestRow, WorkspaceEpic } from "../../api";
import Term from "./Term";

const VERDICT_LABEL: Record<WorkspaceEpic["verdict"], string> = {
  testable_now: "Testable now",
  testable_with_clarifications: "Testable with clarifications",
  not_testable_yet: "Not testable yet",
};

const STAGE_LABEL: Record<WorkspaceEpic["stage"], string> = {
  review: "Review not approved",
  draft: "Waiting for tests",
  test_review: "Tests to review",
  import: "Ready for Xray",
  blocked: "Not testable yet",
  done: "Done",
};

type Props = {
  runId: string;
  profiles: CoverageProfile[];
  portfolioLabel: string;
  epic: WorkspaceEpic;
  expanded: boolean;
  openTestId: string | null;
  rejectionReasons: { id: string; label: string }[];
  selectedTests: Record<string, string>;
  onToggle: () => void;
  onToggleTest: (testId: string) => void;
  onToggleSelected: (testId: string, creatorRunId: string, selected: boolean) => void;
  onChanged: () => void;
  onError: (message: string) => void;
};

export default function EpicAccordion({
  runId,
  profiles,
  portfolioLabel,
  epic,
  expanded,
  openTestId,
  rejectionReasons,
  selectedTests,
  onToggle,
  onToggleTest,
  onToggleSelected,
  onChanged,
  onError,
}: Props) {
  const regionId = `epic-${epic.jira_key}`;
  return (
    <section className="ws-epic" id={`ws-${epic.jira_key}`}>
      <h3 className="ws-epic-heading">
        <button
          type="button"
          className="ws-accordion-trigger"
          aria-expanded={expanded}
          aria-controls={regionId}
          onClick={onToggle}
        >
          <span className="ws-epic-key">{epic.jira_key}</span>
          <span className="ws-epic-summary">{epic.summary}</span>
          <span className={`ws-badge ws-verdict--${epic.verdict}`}>{VERDICT_LABEL[epic.verdict]}</span>
          <span className="ws-badge">{STAGE_LABEL[epic.stage]}</span>
        </button>
      </h3>
      {expanded && (
        <div id={regionId} role="region" aria-label={`${epic.jira_key} details`} className="ws-epic-body">
          <EpicReview epic={epic} />
          <EpicDepth
            runId={runId}
            epic={epic}
            profiles={profiles}
            portfolioLabel={portfolioLabel}
            onChanged={onChanged}
            onError={onError}
          />
          {epic.creator_handoff && <HandoffLine epic={epic} />}
          {epic.creator_run_id && (
            <EpicTests
              creatorRunId={epic.creator_run_id}
              openTestId={openTestId}
              rejectionReasons={rejectionReasons}
              selectedTests={selectedTests}
              onToggleTest={onToggleTest}
              onToggleSelected={onToggleSelected}
              onChanged={onChanged}
              onError={onError}
            />
          )}
          <p className="muted ws-advanced">
            <Link to={`/units/${epic.unit_id}`}>Advanced details</Link> — findings, sources, and
            Jira comment drafts.
          </p>
        </div>
      )}
    </section>
  );
}

function EpicReview({ epic }: { epic: WorkspaceEpic }) {
  return (
    <div className="ws-review">
      <p>
        <Term id="testability">Testability</Term>: <strong>{VERDICT_LABEL[epic.verdict]}</strong>
        {epic.approved ? " · Review approved" : " · Review not approved yet"}
      </p>
      {epic.testability_reasons.length > 0 && (
        <ul className="ws-reasons">
          {epic.testability_reasons.map((reason) => (
            <li key={reason}>{reason}</li>
          ))}
        </ul>
      )}
      {epic.readiness_line && <p>{epic.readiness_line}</p>}
      {epic.blocker_questions.length > 0 ? (
        <>
          <h4>
            <Term id="blocker">Blocker questions</Term> ({epic.blocker_questions.length})
          </h4>
          <ol className="ws-questions">
            {epic.blocker_questions.map((q) => (
              <li key={q.question_id ?? q.question ?? ""}>
                <strong>{q.question_id}</strong> {q.question}
                {q.owner_hint && <span className="muted"> · owner {q.owner_hint}</span>}
                {q.context && <p className="muted">{q.context}</p>}
              </li>
            ))}
          </ol>
        </>
      ) : (
        <p className="muted">No blocker questions.</p>
      )}
      {epic.other_question_count > 0 && (
        <p className="muted">
          {epic.other_question_count} other open question(s) under Advanced details.
        </p>
      )}
    </div>
  );
}

function EpicDepth({
  runId,
  epic,
  profiles,
  portfolioLabel,
  onChanged,
  onError,
}: {
  runId: string;
  epic: WorkspaceEpic;
  profiles: CoverageProfile[];
  portfolioLabel: string;
  onChanged: () => void;
  onError: (message: string) => void;
}) {
  const [pending, setPending] = useState(false);
  const effective = epic.effective_coverage_profile;
  return (
    <label className="ws-epic-depth">
      Coverage depth for this Epic
      <select
        value={epic.coverage_profile ?? ""}
        disabled={pending}
        onChange={(event) => {
          const next = event.target.value;
          setPending(true);
          api
            .setEpicCoverageProfile(runId, epic.unit_id, (next || null) as CoverageProfileId | null)
            .then(() => onChanged())
            .catch((reason) => onError(String(reason)))
            .finally(() => setPending(false));
        }}
      >
        <option value="">Portfolio default ({portfolioLabel})</option>
        {profiles.map((profile) => (
          <option key={profile.id} value={profile.id}>
            {profile.label} · {profile.test_count_min}–{profile.test_count_max}
          </option>
        ))}
      </select>
      <span className="muted">
        Using {effective.label}: {effective.summary}
      </span>
    </label>
  );
}

function HandoffLine({ epic }: { epic: WorkspaceEpic }) {
  const handoff = epic.creator_handoff!;
  const text: Record<string, string> = {
    awaiting_cursor: "Waiting for Cursor to write the suite.",
    output_detected: "Suite file found. Importing once it stops changing.",
    invalid_output: handoff.error ?? "The suite file could not be read.",
    imported: "Suite imported.",
    stale_output: handoff.error?.startsWith("Coverage depth changed")
      ? handoff.error
      : "The suite file changed after import.",
  };
  return (
    <p className={handoff.status === "invalid_output" ? "error" : "muted"}>
      Creator <Term id="handoff">handoff</Term>: {text[handoff.status]} <code>{handoff.expected_path}</code>
    </p>
  );
}

function EpicTests({
  creatorRunId,
  openTestId,
  rejectionReasons,
  selectedTests,
  onToggleTest,
  onToggleSelected,
  onChanged,
  onError,
}: {
  creatorRunId: string;
  openTestId: string | null;
  rejectionReasons: { id: string; label: string }[];
  selectedTests: Record<string, string>;
  onToggleTest: (testId: string) => void;
  onToggleSelected: (testId: string, creatorRunId: string, selected: boolean) => void;
  onChanged: () => void;
  onError: (message: string) => void;
}) {
  const [tests, setTests] = useState<CreatorTestRow[] | null>(null);

  const load = () =>
    api
      .creatorRun(creatorRunId)
      .then((body) => setTests(body.tests))
      .catch((reason) => onError(String(reason)));

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [creatorRunId]);

  const patch = async (
    id: string,
    body: { human_review_status?: string; marked_for_xray_import?: boolean; rejection_reason?: string }
  ) => {
    try {
      await api.patchTest(id, body);
      await load();
      onChanged();
    } catch (reason) {
      onError(String(reason));
    }
  };

  if (!tests) return <p className="muted">Loading tests…</p>;
  return (
    <div className="ws-tests">
      <h4>Test cases ({tests.length})</h4>
      {tests.map((test) => (
        <TestAccordion
          key={test.id}
          test={test}
          expanded={openTestId === test.id}
          selected={Boolean(selectedTests[test.id])}
          rejectionReasons={rejectionReasons}
          onToggle={() => onToggleTest(test.id)}
          onToggleSelected={(on) => onToggleSelected(test.id, creatorRunId, on)}
          onPatch={(body) => patch(test.id, body)}
        />
      ))}
    </div>
  );
}

type Step = { step?: string; expected_result?: string };

function TestAccordion({
  test,
  expanded,
  selected,
  rejectionReasons,
  onToggle,
  onToggleSelected,
  onPatch,
}: {
  test: CreatorTestRow;
  expanded: boolean;
  selected: boolean;
  rejectionReasons: { id: string; label: string }[];
  onToggle: () => void;
  onToggleSelected: (selected: boolean) => void;
  onPatch: (body: {
    human_review_status?: string;
    marked_for_xray_import?: boolean;
    rejection_reason?: string;
  }) => void;
}) {
  const [steps, setSteps] = useState<Step[] | null>(null);
  const [reason, setReason] = useState("");
  const regionId = `test-${test.id}`;

  useEffect(() => {
    if (!expanded || steps) return;
    api
      .test(test.id)
      .then((body) => setSteps((body.case?.steps as Step[]) ?? []))
      .catch(() => setSteps([]));
  }, [expanded, steps, test.id]);

  const status = test.human_review_status;
  const approved = status === "approved";
  const selectable = status === "pending" || status === "edited";
  return (
    <div className="ws-test">
      <div className="ws-test-line">
        {selectable && (
          <input
            type="checkbox"
            className="ws-select"
            checked={selected}
            aria-label={`Select ${test.draft_id ?? test.title}`}
            onChange={(event) => onToggleSelected(event.target.checked)}
          />
        )}
      <button
        type="button"
        className="ws-accordion-trigger ws-test-trigger"
        aria-expanded={expanded}
        aria-controls={regionId}
        onClick={onToggle}
      >
        <span className="ws-epic-key">{test.draft_id}</span>
        <span className="ws-epic-summary">{test.title}</span>
        {test.execution_tier && <span className="ws-badge">{test.execution_tier}</span>}
        <span className={`ws-badge ws-test--${status}`}>{status}</span>
        {test.xray_test_key && <span className="ws-badge">{test.xray_test_key}</span>}
      </button>
      </div>
      {expanded && (
        <div id={regionId} role="region" aria-label={`${test.draft_id} steps`} className="ws-test-body">
          {steps === null ? (
            <p className="muted">Loading steps…</p>
          ) : steps.length === 0 ? (
            <p className="muted">No steps recorded.</p>
          ) : (
            <table className="data">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Action</th>
                  <th>Expected result</th>
                </tr>
              </thead>
              <tbody>
                {steps.map((step, index) => (
                  <tr key={index}>
                    <td>{index + 1}</td>
                    <td>{step.step}</td>
                    <td>{step.expected_result}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          <div className="btn-row">
            <button type="button" onClick={() => onPatch({ human_review_status: "approved" })} disabled={approved}>
              Approve
            </button>
            <label>
              <span className="visually-hidden">Rejection reason</span>
              <select value={reason} onChange={(event) => setReason(event.target.value)}>
                <option value="">Reason for rejecting…</option>
                {rejectionReasons.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.label}
                  </option>
                ))}
              </select>
            </label>
            <button
              type="button"
              className="secondary"
              disabled={!reason || status === "rejected"}
              onClick={() => onPatch({ human_review_status: "rejected", rejection_reason: reason })}
            >
              Reject
            </button>
            {approved && (
              <label className="ws-check">
                <input
                  type="checkbox"
                  checked={Boolean(test.marked_for_xray_import)}
                  onChange={(event) => onPatch({ marked_for_xray_import: event.target.checked })}
                />
                Send to Xray
              </label>
            )}
            <Link to={`/tests/${encodeURIComponent(test.id)}`}>Edit test</Link>
          </div>
        </div>
      )}
    </div>
  );
}
