/** Epic review UI — inlined in index.html; keep in sync. */

function esc(s) {
  const d = document.createElement("div");
  d.textContent = s ?? "";
  return d.innerHTML;
}

function questionBody(q) {
  return (q.question || q.text || "").trim();
}

function ensureStudioQa(payload) {
  if (!payload.studio_qa || typeof payload.studio_qa !== "object") {
    payload.studio_qa = { version: 1, decisions: {}, added_questions: [] };
  }
  if (!payload.studio_qa.decisions) payload.studio_qa.decisions = {};
  if (!payload.studio_qa.added_questions) payload.studio_qa.added_questions = [];
  return payload.studio_qa;
}

function getDecision(studio, itemId) {
  const d = studio.decisions[itemId];
  return d
    ? { validity: d.validity || "pending", send_to_epic: !!d.send_to_epic, comment: d.comment || "" }
    : { validity: "pending", send_to_epic: false, comment: "" };
}

function setDecisionField(payload, itemId, patch) {
  const studio = ensureStudioQa(payload);
  const prev = getDecision(studio, itemId);
  const next = Object.assign({}, prev, patch);
  if (patch.validity === "valid" && patch.send_to_epic === undefined) next.send_to_epic = true;
  if (patch.validity === "invalid" && patch.send_to_epic === undefined) next.send_to_epic = false;
  studio.decisions[itemId] = next;
}

function severityClass(sev) {
  if (!sev) return "badge";
  const s = String(sev).toUpperCase();
  if (s === "CRITICAL" || s === "HIGH") return "badge sev-high";
  if (s === "MEDIUM") return "badge sev-med";
  return "badge sev-low";
}

function qaDecisionBlock(payload, itemId, label) {
  const d = getDecision(ensureStudioQa(payload), itemId);
  const v = d.validity;
  return `<div class="qa-review" data-item-id="${esc(itemId)}">
    <div class="field-label">${esc(label)}</div>
    <div class="decision-actions">
      <button type="button" class="dec-btn${v === "valid" ? " active-valid" : ""}" data-validity="valid">Valid — send to epic</button>
      <button type="button" class="dec-btn${v === "invalid" ? " active-invalid" : ""}" data-validity="invalid">Do not ask</button>
      <button type="button" class="dec-btn${v === "discuss" ? " active-discuss" : ""}" data-validity="discuss">Discuss</button>
    </div>
    <label class="inline-label send-epic-row${v === "invalid" ? " muted" : ""}">
      <input type="checkbox" class="send-epic" ${d.send_to_epic ? "checked" : ""} ${v === "invalid" ? "disabled" : ""} />
      Include in epic feedback
    </label>
    <label class="stack-label">QA comment
      <textarea class="qa-comment" rows="3" placeholder="Rationale, wording tweaks, or why this should not go to the epic…">${esc(d.comment)}</textarea>
    </label>
  </div>`;
}

const SOURCE_STATUS_LABEL = {
  analyzed: "Analyzed",
  unavailable: "Unavailable",
  failed: "Could not read",
  not_applicable: "Not applicable",
};

function sourceStatusClass(st) {
  if (st === "analyzed") return "pill-analyzed";
  if (st === "unavailable") return "pill-unavailable";
  if (st === "failed") return "pill-failed";
  return "pill-na";
}

function renderDataSources(payload) {
  const entries = payload.context_loaded || [];
  if (!entries.length) return "";
  const analyzed = entries.filter((s) => s.status === "analyzed").length;
  const problems = entries.filter((s) => s.status === "unavailable" || s.status === "failed").length;
  const rows = entries
    .map((s) => {
      const detail =
        s.status === "unavailable" || s.status === "failed" ? s.reason || "" : s.detail || "";
      const label = SOURCE_STATUS_LABEL[s.status] || s.status;
      return `<tr>
        <td>${esc(s.source)}</td>
        <td><span class="status-pill ${sourceStatusClass(s.status)}">${esc(label)}</span></td>
        <td class="muted detail-cell">${esc(detail)}</td>
      </tr>`;
    })
    .join("");
  const note =
    problems === 0
      ? '<p class="muted" style="margin-top:0.75rem;margin-bottom:0">No sources were unavailable or failed in this run.</p>'
      : "";
  return `<div class="panel data-sources">
    <details open class="report-block">
      <summary>Data sources (${analyzed} analyzed · ${problems} unavailable or failed)</summary>
      <div class="table-scroll">
        <table class="data">
          <thead><tr><th>Source</th><th>Status</th><th>Detail</th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
      ${note}
    </details>
  </div>`;
}

function renderSourcedList(items) {
  if (!items || !items.length) return "";
  return (
    '<ul class="prose-list">' +
    items
      .map((it) => {
        if (typeof it === "string") return `<li>${esc(it)}</li>`;
        const src = it.source ? ` <span class="muted">(${esc(it.source)})</span>` : "";
        return `<li>${esc(it.text || "")}${src}</li>`;
      })
      .join("") +
    "</ul>"
  );
}

function renderReportDetail(payload) {
  const report = payload.report || {};
  const parts = [];
  if (report.facts && report.facts.length) {
    parts.push(
      `<details open class="report-block"><summary>Information identified</summary>${renderSourcedList(report.facts)}</details>`
    );
  }
  if (report.not_stated && report.not_stated.length) {
    parts.push(
      `<details class="report-block"><summary>Not stated</summary><ul class="prose-list">${report.not_stated
        .map((t) => `<li>${esc(t)}</li>`)
        .join("")}</ul></details>`
    );
  }
  if (report.risks && report.risks.length) {
    parts.push(
      `<details class="report-block"><summary>Risks</summary>${renderSourcedList(report.risks)}</details>`
    );
  }
  if (report.testing_focus && report.testing_focus.length) {
    parts.push(
      `<details class="report-block"><summary>Testing focus</summary><ul class="prose-list">${report.testing_focus
        .map((t) => `<li>${esc(t.text || "")}</li>`)
        .join("")}</ul></details>`
    );
  }
  if (!parts.length) return "";
  return `<div class="panel report-detail">${parts.join("")}</div>`;
}

function renderReportSummary(payload) {
  const report = payload.report || {};
  const gate = payload.gate && payload.gate.status;
  if (!report.readiness_line && !gate) return "";
  let html = '<div class="panel report-summary">';
  if (gate) {
    html += `<p class="gate-line">Gate <span class="badge">${esc(gate)}</span>`;
    if (report.qa_planning_fit) {
      html += ` · Planning fit <span class="badge">${esc(report.qa_planning_fit)}</span>`;
    }
    html += "</p>";
  }
  if (report.readiness_line) html += `<p class="readiness">${esc(report.readiness_line)}</p>`;
  if (report.next_action) {
    html += `<p class="muted"><strong>Next action:</strong> ${esc(report.next_action)}</p>`;
  }
  html += "</div>";
  return html;
}

function renderQuestionCard(payload, q, i, itemId, isQaAdded) {
  const unblocks =
    q.unblocks && q.unblocks.length
      ? `<div class="field-block"><div class="field-label">Unblocks</div><p class="mono unblocks">${esc(
          q.unblocks.join(" · ")
        )}</p></div>`
      : "";
  const addedBadge = isQaAdded ? '<span class="badge">QA-added</span>' : "";
  return `<article class="review-card${isQaAdded ? " qa-added" : ""}" data-q-index="${i}" data-item-id="${esc(itemId)}">
    <header class="review-card-head">
      <span class="mono">${esc(q.question_id || "Q" + (i + 1))}</span>
      ${addedBadge}
      ${q.topic ? `<span class="badge">${esc(q.topic)}</span>` : ""}
      ${q.priority ? `<span class="badge">${esc(q.priority)}</span>` : ""}
      ${q.owner_hint ? `<span class="badge owner">${esc(q.owner_hint)}</span>` : ""}
    </header>
    <p class="prose question-body">${esc(questionBody(q) || "—")}</p>
    ${
      q.context
        ? `<div class="field-block"><div class="field-label">Why</div><p class="prose muted-block">${esc(q.context)}</p></div>`
        : ""
    }
    ${
      q.source
        ? `<div class="field-block"><div class="field-label">Source</div><p class="prose">${esc(q.source)}</p></div>`
        : ""
    }
    ${unblocks}
    ${qaDecisionBlock(payload, itemId, "QA review")}
  </article>`;
}

function renderQuestions(payload) {
  const qs = payload.questions || [];
  const studio = ensureStudioQa(payload);
  const added = studio.added_questions || [];
  if (!qs.length && !added.length) return '<p class="muted">No questions in this payload.</p>';
  let html = '<div class="card-list">';
  qs.forEach((q, i) => {
    const id = q.question_id || "Q" + (i + 1);
    html += renderQuestionCard(payload, q, i, id, false);
  });
  added.forEach((q, i) => {
    const id = q.question_id || "QA-" + (i + 1);
    html += renderQuestionCard(payload, q, "a" + i, id, true);
  });
  html += "</div>";
  html += `<div class="btnrow"><button type="button" id="addQaQuestionBtn" class="sec">Add QA question</button></div>`;
  html += `<div id="newQaQuestionForm" class="panel hide">
    <h3 style="margin-top:0">New question for the epic</h3>
    <label class="stack-label">Question<textarea id="newQText" rows="4"></textarea></label>
    <label class="stack-label">Why (context)<textarea id="newQContext" rows="3"></textarea></label>
    <label class="stack-label">Topic<input id="newQTopic" value="Scope" /></label>
    <label class="stack-label">Owner<select id="newQOwner"><option>PM</option><option>PO</option><option>UX</option><option>EM</option></select></label>
    <div class="btnrow"><button type="button" id="saveNewQBtn">Add to list</button><button type="button" id="cancelNewQBtn" class="sec">Cancel</button></div>
  </div>`;
  return html;
}

function renderFindings(payload) {
  const fs = payload.findings || [];
  if (!fs.length) return '<p class="muted">No findings.</p>';
  return (
    '<div class="card-list">' +
    fs
      .map((f, i) => {
        const fid = f.finding_id || "F" + i;
        return `<article class="review-card" data-f-index="${i}" data-item-id="${esc(fid)}">
          <header class="review-card-head">
            <span class="mono">${esc(f.finding_id)}</span>
            <span class="${severityClass(f.severity)}">${esc(f.severity)}</span>
            ${f.category ? `<span class="badge">${esc(f.category)}</span>` : ""}
            ${f.checklist_ref ? `<span class="badge mono">${esc(f.checklist_ref)}</span>` : ""}
            ${f.owner_hint ? `<span class="badge owner">${esc(f.owner_hint)}</span>` : ""}
          </header>
          <p class="prose">${esc(f.finding_summary)}</p>
          ${
            f.testing_impact
              ? `<div class="field-block"><div class="field-label">Testing impact</div><p class="prose">${esc(
                  f.testing_impact
                )}</p></div>`
              : ""
          }
          ${f.excerpt_quote ? `<blockquote class="excerpt">${esc(f.excerpt_quote)}</blockquote>` : ""}
          ${f.source ? `<p class="muted source-line">Source: ${esc(f.source)}</p>` : ""}
          ${qaDecisionBlock(payload, fid, "QA review (finding)")}
        </article>`;
      })
      .join("") +
    "</div>"
  );
}

function bindQaHandlers(payload) {
  document.querySelectorAll(".qa-review").forEach((root) => {
    const itemId = root.getAttribute("data-item-id");
    root.querySelectorAll(".dec-btn").forEach((btn) => {
      btn.onclick = () => {
        const validity = btn.getAttribute("data-validity");
        setDecisionField(payload, itemId, { validity });
        paintUnitReview(payload);
      };
    });
    const send = root.querySelector(".send-epic");
    if (send) {
      send.onchange = () => setDecisionField(payload, itemId, { send_to_epic: send.checked });
    }
    const comment = root.querySelector(".qa-comment");
    if (comment) {
      comment.oninput = () => setDecisionField(payload, itemId, { comment: comment.value });
    }
  });

  const addBtn = document.getElementById("addQaQuestionBtn");
  const form = document.getElementById("newQaQuestionForm");
  const cancelBtn = document.getElementById("cancelNewQBtn");
  const saveBtn = document.getElementById("saveNewQBtn");
  if (addBtn && form) {
    addBtn.onclick = () => form.classList.remove("hide");
  }
  if (cancelBtn && form) {
    cancelBtn.onclick = () => form.classList.add("hide");
  }
  if (saveBtn && form) {
    saveBtn.onclick = () => {
      const studio = ensureStudioQa(payload);
      const n = (studio.added_questions.length || 0) + 1;
      const qid = "QA-" + n;
      const question = document.getElementById("newQText").value.trim();
      if (!question) return;
      studio.added_questions.push({
        question_id: qid,
        topic: document.getElementById("newQTopic").value.trim() || "Scope",
        question,
        context: document.getElementById("newQContext").value.trim(),
        source: "QA Studio review",
        priority: "High",
        owner_hint: document.getElementById("newQOwner").value,
        origin: "qa_studio",
        send_to_epic: true,
        status: "open",
      });
      setDecisionField(payload, qid, { validity: "valid", send_to_epic: true });
      form.classList.add("hide");
      document.getElementById("newQText").value = "";
      document.getElementById("newQContext").value = "";
      paintUnitReview(payload);
    };
  }
}

function paintUnitReview(payload) {
  const detailEl = document.getElementById("reportDetail");
  if (detailEl) detailEl.innerHTML = renderDataSources(payload) + renderReportDetail(payload);
  const summaryEl = document.getElementById("reportSummary");
  if (summaryEl) summaryEl.innerHTML = renderReportSummary(payload);
  document.getElementById("questions").innerHTML = renderQuestions(payload);
  document.getElementById("findings").innerHTML = renderFindings(payload);
  bindQaHandlers(payload);
}

function buildEpicFeedbackDownload(payload, jiraKey) {
  const studio = ensureStudioQa(payload);
  const decisions = studio.decisions || {};
  const lines = [];
  function pushItem(type, id, body, why, extra) {
    const d = decisions[id] || {};
    if (!d.send_to_epic) return;
    lines.push({ type, id, validity: d.validity, comment: d.comment || "", body, why, ...extra });
  }
  (payload.questions || []).forEach((q) => {
    const id = q.question_id;
    pushItem("question", id, questionBody(q), q.context, { topic: q.topic, owner_hint: q.owner_hint });
  });
  (studio.added_questions || []).forEach((q) => {
    pushItem("question", q.question_id, q.question, q.context, {
      topic: q.topic,
      owner_hint: q.owner_hint,
      origin: "qa_studio",
    });
  });
  (payload.findings || []).forEach((f) => {
    pushItem("finding", f.finding_id, f.finding_summary, f.testing_impact, {
      severity: f.severity,
      checklist_ref: f.checklist_ref,
    });
  });
  return {
    run_id: payload.run_id,
    jira_key: jiraKey,
    exported_at: new Date().toISOString(),
    items: lines,
  };
}
