import { useState } from "react";
import type { StudioQaAddedQuestion } from "../types/studio-qa";

type Props = {
  nextIndex: number;
  onAdd: (q: StudioQaAddedQuestion, decisionItemId: string) => void;
};

export default function AddQaQuestionForm({ nextIndex, onAdd }: Props) {
  const [open, setOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [context, setContext] = useState("");
  const [topic, setTopic] = useState("Scope");
  const [owner, setOwner] = useState("PM");

  const submit = () => {
    const text = question.trim();
    if (!text) return;
    const qid = `QA-${nextIndex}`;
    onAdd(
      {
        question_id: qid,
        topic,
        question: text,
        context: context.trim(),
        source: "QA Studio review",
        priority: "High",
        owner_hint: owner,
        origin: "qa_studio",
        send_to_epic: true,
        status: "open",
      },
      qid
    );
    setQuestion("");
    setContext("");
    setOpen(false);
  };

  return (
    <div className="add-qa-question">
      <div className="btn-row">
        <button type="button" className="secondary" onClick={() => setOpen(true)}>
          Add QA question
        </button>
      </div>
      {open && (
        <div className="panel">
          <h3 style={{ marginTop: 0 }}>New question for the epic</h3>
          <label className="stack-label">
            Question
            <textarea value={question} onChange={(e) => setQuestion(e.target.value)} rows={4} />
          </label>
          <label className="stack-label">
            Why (context)
            <textarea value={context} onChange={(e) => setContext(e.target.value)} rows={3} />
          </label>
          <label className="stack-label">
            Topic
            <input value={topic} onChange={(e) => setTopic(e.target.value)} />
          </label>
          <label className="stack-label">
            Owner
            <select value={owner} onChange={(e) => setOwner(e.target.value)}>
              <option value="PM">PM</option>
              <option value="PO">PO</option>
              <option value="UX">UX</option>
              <option value="EM">EM</option>
            </select>
          </label>
          <div className="btn-row">
            <button type="button" onClick={submit}>Add to list</button>
            <button type="button" className="secondary" onClick={() => setOpen(false)}>
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
