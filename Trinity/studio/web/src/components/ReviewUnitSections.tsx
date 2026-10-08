import AddQaQuestionForm from "./AddQaQuestionForm";
import DataSourcesPanel from "./DataSourcesPanel";
import QaItemReview from "./QaItemReview";
import ReportDetailPanel from "./ReportDetailPanel";
import type {
  ClarificationQuestion,
  ContextLoadedEntry,
  ReviewFinding,
  ReviewReport,
} from "../types/review-payload";
import { questionBody } from "../types/review-payload";
import type { QaItemDecision, StudioQa, StudioQaAddedQuestion } from "../types/studio-qa";

type Props = {
  contextLoaded?: ContextLoadedEntry[];
  report?: ReviewReport;
  gateStatus?: string;
  questions: ClarificationQuestion[];
  findings: ReviewFinding[];
  studio: StudioQa;
  onDecisionPatch: (itemId: string, patch: Partial<QaItemDecision>) => void;
  onAddQuestion: (q: StudioQaAddedQuestion, itemId: string) => void;
};

function severityClass(sev?: string) {
  if (!sev) return "badge";
  const s = sev.toUpperCase();
  if (s === "CRITICAL" || s === "HIGH") return "badge sev-high";
  if (s === "MEDIUM") return "badge sev-med";
  return "badge sev-low";
}

function QuestionCard({
  q,
  qaAdded,
  studio,
  itemId,
  onDecisionPatch,
}: {
  q: ClarificationQuestion | StudioQaAddedQuestion;
  qaAdded?: boolean;
  studio: StudioQa;
  itemId: string;
  onDecisionPatch: (itemId: string, patch: Partial<QaItemDecision>) => void;
}) {
  return (
    <article className={`review-card${qaAdded ? " qa-added" : ""}`}>
      <header className="review-card-head">
        <span className="mono">{q.question_id}</span>
        {qaAdded && <span className="badge">QA-added</span>}
        {q.topic && <span className="badge">{q.topic}</span>}
        {"priority" in q && q.priority && <span className="badge">{q.priority}</span>}
        {q.owner_hint && <span className="badge owner">{q.owner_hint}</span>}
      </header>
      <p className="prose question-body">{questionBody(q) || "—"}</p>
      {q.context && (
        <div className="field-block">
          <div className="field-label">Why</div>
          <p className="prose muted-block">{q.context}</p>
        </div>
      )}
      {q.source && (
        <div className="field-block">
          <div className="field-label">Source</div>
          <p className="prose">{q.source}</p>
        </div>
      )}
      {"unblocks" in q && q.unblocks && q.unblocks.length > 0 && (
        <div className="field-block">
          <div className="field-label">Unblocks</div>
          <p className="mono unblocks">{q.unblocks.join(" · ")}</p>
        </div>
      )}
      <QaItemReview
        itemId={itemId}
        label="QA review"
        studio={studio}
        onPatch={onDecisionPatch}
      />
    </article>
  );
}

export default function ReviewUnitSections({
  contextLoaded,
  report,
  gateStatus,
  questions,
  findings,
  studio,
  onDecisionPatch,
  onAddQuestion,
}: Props) {
  const added = studio.added_questions ?? [];

  return (
    <>
      <DataSourcesPanel entries={contextLoaded ?? []} />
      <ReportDetailPanel report={report} />

      {(report?.readiness_line || gateStatus) && (
        <div className="panel report-summary">
          {gateStatus && (
            <p className="gate-line">
              Gate <span className="badge">{gateStatus}</span>
              {report?.qa_planning_fit && (
                <>
                  {" "}
                  · Planning fit <span className="badge">{report.qa_planning_fit}</span>
                </>
              )}
            </p>
          )}
          {report?.readiness_line && <p className="readiness">{report.readiness_line}</p>}
          {report?.next_action && (
            <p className="muted">
              <strong>Next action:</strong> {report.next_action}
            </p>
          )}
        </div>
      )}

      <div className="section">
        <h3>Clarification questions</h3>
        <p className="muted section-hint">
          Mark each item: valid (send to epic), do not ask, or discuss. Add your own questions below.
        </p>
        {questions.length === 0 && added.length === 0 && (
          <p className="muted">No questions in this payload.</p>
        )}
        <div className="card-list">
          {questions.map((q, i) => {
            const itemId = q.question_id ?? `Q${i + 1}`;
            return (
              <QuestionCard
                key={itemId}
                q={q}
                itemId={itemId}
                studio={studio}
                onDecisionPatch={onDecisionPatch}
              />
            );
          })}
          {added.map((q) => (
            <QuestionCard
              key={q.question_id}
              q={q}
              qaAdded
              itemId={q.question_id}
              studio={studio}
              onDecisionPatch={onDecisionPatch}
            />
          ))}
        </div>
        <AddQaQuestionForm
          nextIndex={(studio.added_questions?.length ?? 0) + 1}
          onAdd={onAddQuestion}
        />
      </div>

      <div className="section">
        <h3>Findings</h3>
        {findings.length === 0 && <p className="muted">No findings.</p>}
        <div className="card-list">
          {findings.map((f, i) => {
            const fid = f.finding_id ?? `F${i + 1}`;
            return (
              <article key={fid} className="review-card">
                <header className="review-card-head">
                  <span className="mono">{f.finding_id}</span>
                  <span className={severityClass(f.severity)}>{f.severity}</span>
                  {f.category && <span className="badge">{f.category}</span>}
                  {f.checklist_ref && <span className="badge mono">{f.checklist_ref}</span>}
                  {f.owner_hint && <span className="badge owner">{f.owner_hint}</span>}
                </header>
                <p className="prose">{f.finding_summary}</p>
                {f.testing_impact && (
                  <div className="field-block">
                    <div className="field-label">Testing impact</div>
                    <p className="prose">{f.testing_impact}</p>
                  </div>
                )}
                {f.excerpt_quote && <blockquote className="excerpt">{f.excerpt_quote}</blockquote>}
                {f.source && <p className="muted source-line">Source: {f.source}</p>}
                <QaItemReview
                  itemId={fid}
                  label="QA review (finding)"
                  studio={studio}
                  onPatch={onDecisionPatch}
                />
              </article>
            );
          })}
        </div>
      </div>
    </>
  );
}
