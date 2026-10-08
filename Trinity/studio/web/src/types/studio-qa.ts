/** QA human review layer — stored on payload as `studio_qa` (not in Reviewer schema). */

export type QaValidity = "pending" | "valid" | "invalid" | "discuss";

export type QaItemDecision = {
  validity?: QaValidity;
  send_to_epic?: boolean;
  comment?: string;
};

export type StudioQaAddedQuestion = {
  question_id: string;
  topic?: string;
  question: string;
  context?: string;
  source?: string;
  priority?: string;
  owner_hint?: string;
  origin: "qa_studio";
  send_to_epic?: boolean;
  status?: "open";
};

export type StudioQa = {
  version?: number;
  decisions?: Record<string, QaItemDecision>;
  added_questions?: StudioQaAddedQuestion[];
};

export function readStudioQa(payload: Record<string, unknown>): StudioQa {
  const existing = payload.studio_qa as StudioQa | undefined;
  if (!existing || typeof existing !== "object") {
    return { version: 1, decisions: {}, added_questions: [] };
  }
  return {
    version: existing.version ?? 1,
    decisions: { ...(existing.decisions ?? {}) },
    added_questions: [...(existing.added_questions ?? [])],
  };
}

/** Ensures `payload.studio_qa` exists (immutable update). */
export function attachStudioQa(payload: Record<string, unknown>): Record<string, unknown> {
  if (payload.studio_qa && typeof payload.studio_qa === "object") {
    return payload;
  }
  return { ...payload, studio_qa: readStudioQa(payload) };
}

export function getDecision(studio: StudioQa, itemId: string): QaItemDecision {
  return studio.decisions?.[itemId] ?? { validity: "pending", send_to_epic: false, comment: "" };
}

export function applyDecisionPatch(
  studio: StudioQa,
  itemId: string,
  patch: Partial<QaItemDecision>
): StudioQa {
  const prev = getDecision(studio, itemId);
  const next = { ...prev, ...patch };
  if (patch.validity === "valid" && patch.send_to_epic === undefined) {
    next.send_to_epic = true;
  }
  if (patch.validity === "invalid" && patch.send_to_epic === undefined) {
    next.send_to_epic = false;
  }
  return {
    ...studio,
    decisions: { ...studio.decisions, [itemId]: next },
  };
}

export type EpicFeedbackItem = {
  type: "question" | "finding";
  id: string;
  validity?: QaValidity;
  comment: string;
  body?: string;
  why?: string;
  topic?: string;
  owner_hint?: string;
  origin?: string;
  severity?: string;
  checklist_ref?: string;
};

export type EpicFeedbackExport = {
  run_id?: string;
  jira_key: string;
  exported_at: string;
  items: EpicFeedbackItem[];
};

export function buildEpicFeedback(
  payload: Record<string, unknown>,
  jiraKey: string,
  questionBody: (q: { question?: string; text?: string }) => string
): EpicFeedbackExport {
  const studio = (payload.studio_qa as StudioQa) ?? { decisions: {}, added_questions: [] };
  const decisions = studio.decisions ?? {};
  const items: EpicFeedbackItem[] = [];

  const push = (
    type: "question" | "finding",
    id: string,
    body: string | undefined,
    why: string | undefined,
    extra: Partial<EpicFeedbackItem>
  ) => {
    const d = decisions[id] ?? {};
    if (!d.send_to_epic) return;
    items.push({
      type,
      id,
      validity: d.validity,
      comment: d.comment ?? "",
      body,
      why,
      ...extra,
    });
  };

  const questions = (payload.questions as { question_id?: string; context?: string; topic?: string; owner_hint?: string }[]) ?? [];
  for (const q of questions) {
    if (!q.question_id) continue;
    push("question", q.question_id, questionBody(q), q.context, {
      topic: q.topic,
      owner_hint: q.owner_hint,
    });
  }
  for (const q of studio.added_questions ?? []) {
    push("question", q.question_id, q.question, q.context, {
      topic: q.topic,
      owner_hint: q.owner_hint,
      origin: "qa_studio",
    });
  }
  const findings =
    (payload.findings as { finding_id?: string; finding_summary?: string; testing_impact?: string; severity?: string; checklist_ref?: string }[]) ?? [];
  for (const f of findings) {
    if (!f.finding_id) continue;
    push("finding", f.finding_id, f.finding_summary, f.testing_impact, {
      severity: f.severity,
      checklist_ref: f.checklist_ref,
    });
  }

  return {
    run_id: payload.run_id as string | undefined,
    jira_key: jiraKey,
    exported_at: new Date().toISOString(),
    items,
  };
}

export function downloadJson(filename: string, data: unknown) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
