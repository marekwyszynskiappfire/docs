/** Mirrors The Reviewer `review-payload.schema.json` (subset used in Studio). */

export type QuestionStatus = "open" | "resolved";

export type ClarificationQuestion = {
  question_id?: string;
  topic?: string;
  question?: string;
  /** Legacy / mistaken import key — always prefer `question`. */
  text?: string;
  context?: string;
  source?: string;
  priority?: string;
  unblocks?: string[];
  owner_hint?: string;
  status?: QuestionStatus;
  /** Studio-only: PM answer while editing (not in Reviewer schema). */
  pm_response?: string;
  answer?: string;
};

export type ReviewFinding = {
  finding_id?: string;
  severity?: string;
  category?: string;
  checklist_ref?: string;
  finding_summary?: string;
  testing_impact?: string;
  excerpt_quote?: string;
  owner_hint?: string;
  source?: string;
  status?: QuestionStatus;
};

export type ContextLoadedEntry = {
  source: string;
  type?: string;
  status: "analyzed" | "unavailable" | "failed" | "not_applicable";
  detail?: string;
  reason?: string;
};

export const SOURCE_STATUS_LABEL: Record<ContextLoadedEntry["status"], string> = {
  analyzed: "Analyzed",
  unavailable: "Unavailable",
  failed: "Could not read",
  not_applicable: "Not applicable",
};

export type ReviewReport = {
  readiness_line?: string;
  facts?: { text?: string; source?: string }[];
  not_stated?: string[];
  risks?: { text?: string; source?: string }[];
  testing_focus?: { text?: string; blocks?: string[] }[];
  next_action?: string;
  qa_planning_fit?: string;
};

export function questionBody(q: ClarificationQuestion): string {
  const body = (q.question ?? q.text ?? "").trim();
  return body;
}

export function pmResponse(q: ClarificationQuestion): string {
  return q.pm_response ?? q.answer ?? "";
}
