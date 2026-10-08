import { useEffect, useState } from "react";
import { api, type ReviewerRunConfig } from "../api";
import { buildReviewerCursorPrompt } from "../lib/reviewerPrompt";

const DEFAULT_CONFIG: ReviewerRunConfig = {
  config_version: "1.0",
  portfolio_id: "",
  label: "",
  persona_id: "reviewer-expert-qa-automation.md",
  product_id: "default",
  scope: { kind: "epic_keys", value: "" },
  pass_type: "full_sweep",
  child_scan: "epic_only_inventory",
  planning_dates: "jira_due_then_end",
  artifacts_dir: "Trinity/reviewer/runs",
  creator_handoff_exclude_not_fit: true,
  jira_comment_policy: "generate_review_before_post",
  notes: "",
};

export default function ReviewerConfigsPage() {
  const [list, setList] = useState<{ portfolio_id: string; label: string }[]>([]);
  const [personas, setPersonas] = useState<{ id: string }[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [form, setForm] = useState<ReviewerRunConfig>({ ...DEFAULT_CONFIG });
  const [creating, setCreating] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [newEpicsInfo, setNewEpicsInfo] = useState<string>("");
  const [pasteKeysText, setPasteKeysText] = useState("");

  const loadList = () => {
    api.reviewerRunConfigs().then(setList).catch((e) => setError(String(e)));
  };

  useEffect(() => {
    loadList();
    api.personas().then(setPersonas).catch(() => setPersonas([]));
  }, []);

  useEffect(() => {
    if (creating) return;
    if (!selected) return;
    setError("");
    api
      .reviewerRunConfig(selected)
      .then((cfg) => {
        setForm(cfg);
        setPasteKeysText((cfg.resolved_epic_keys ?? []).join("\n"));
      })
      .catch((e) => setError(String(e)));
  }, [selected, creating]);

  const startCreate = () => {
    setCreating(true);
    setSelected(null);
    setForm({ ...DEFAULT_CONFIG, portfolio_id: "", label: "" });
    setMessage("");
    setError("");
  };

  const onSave = async () => {
    const pid = form.portfolio_id.trim();
    if (!pid) {
      setError("portfolio_id is required");
      return;
    }
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const saved = await api.saveReviewerRunConfig(pid, form);
      setForm(saved);
      setCreating(false);
      setSelected(pid);
      loadList();
      setMessage(`Saved Trinity/reviewer/config/runs/${pid}.json`);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  };

  const patch = (patchObj: Partial<ReviewerRunConfig>) => setForm((f) => ({ ...f, ...patchObj }));

  const copyPrompt = async () => {
    if (!form.portfolio_id) {
      setError("Save config with a portfolio_id first");
      return;
    }
    const text = buildReviewerCursorPrompt(form);
    try {
      await navigator.clipboard.writeText(text);
      setMessage("Cursor prompt copied to clipboard");
      setError("");
    } catch {
      setError("Clipboard failed — copy from preview below");
    }
  };

  const resolveScope = async () => {
    const pid = form.portfolio_id.trim();
    if (!pid) {
      setError("Save config first");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const r = await api.resolveReviewerScope(pid);
      if (r.status === "resolved" && r.config) {
        setForm(r.config);
        setPasteKeysText((r.config.resolved_epic_keys ?? []).join("\n"));
        setMessage(
          `Resolved ${r.config.resolved_epic_keys?.length ?? 0} epic key(s)` +
            (r.warning ? ` — ${r.warning}` : "")
        );
      } else if (r.prompt) {
        await navigator.clipboard.writeText(r.prompt);
        setMessage(r.message ?? "Cursor resolve prompt copied — run in Cursor, then paste keys here.");
      } else {
        setError(r.message ?? "Could not resolve scope");
      }
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  };

  const copyJqlResolvePrompt = async () => {
    const pid = form.portfolio_id.trim();
    if (!pid) {
      setError("Save config first");
      return;
    }
    setError("");
    try {
      const r = await api.resolveScopePrompt(pid);
      await navigator.clipboard.writeText(r.prompt);
      setMessage("JQL resolve prompt copied for Cursor");
    } catch (e) {
      setError(String(e));
    }
  };

  const savePastedKeys = async () => {
    const pid = form.portfolio_id.trim();
    if (!pid) {
      setError("Save config first");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const r = await api.pasteResolvedKeys(pid, pasteKeysText);
      setForm(r.config);
      setPasteKeysText((r.config.resolved_epic_keys ?? []).join("\n"));
      setMessage(
        `Stored ${r.resolved_count} epic key(s)` + (r.warning ? ` — ${r.warning}` : "")
      );
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  };

  const clearResolved = async () => {
    const pid = form.portfolio_id.trim();
    if (!pid) return;
    setBusy(true);
    try {
      const cfg = await api.clearResolvedKeys(pid);
      setForm(cfg);
      setPasteKeysText("");
      setMessage("Cleared resolved epic keys");
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  };

  const listNewEpics = async () => {
    const pid = form.portfolio_id.trim();
    if (!pid) {
      setError("portfolio_id required");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const r = await api.reviewerNewEpics(pid);
      if (r.error && !r.epics_in_scope.length) {
        setError(r.error);
        setNewEpicsInfo("");
      } else {
        const lines = [
          r.scope_resolution_note ? `Note: ${r.scope_resolution_note}` : "",
          `Run folder: ${r.run_folder}`,
          `New (${r.new_epics.length}): ${r.new_epics.join(", ") || "—"}`,
          `Already scanned (${r.already_scanned.length}): ${r.already_scanned.join(", ") || "—"}`,
        ].filter(Boolean);
        setNewEpicsInfo(lines.join("\n"));
        setMessage("New epics list updated");
      }
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <h2>Reviewer configs</h2>
      <p className="muted">
        Portfolio run programs for the Reviewer skill interview. Files:{" "}
        <code>Trinity/reviewer/config/runs/{`{portfolio_id}`}.json</code>. Use{" "}
        <code>*-local.json</code> for private configs (gitignored).
      </p>

      <div className="panel" style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
        <div style={{ minWidth: "12rem" }}>
          <div className="btn-row">
            <button type="button" onClick={startCreate}>New config</button>
          </div>
          <ul className="persona-list" style={{ marginTop: "0.75rem" }}>
            {list.map((c) => (
              <li key={c.portfolio_id}>
                <button
                  type="button"
                  className={selected === c.portfolio_id && !creating ? "persona-active" : ""}
                  onClick={() => {
                    setCreating(false);
                    setSelected(c.portfolio_id);
                  }}
                >
                  {c.portfolio_id}
                </button>
              </li>
            ))}
          </ul>
        </div>

        <div style={{ flex: 1, minWidth: "22rem" }}>
          {(creating || selected) && (
            <>
              <label>
                portfolio_id
                <input
                  value={form.portfolio_id}
                  disabled={!creating && !!selected}
                  onChange={(e) => patch({ portfolio_id: e.target.value })}
                  placeholder="2026-Q4-my-program"
                />
              </label>
              <label>
                Label
                <input
                  value={form.label ?? ""}
                  onChange={(e) => patch({ label: e.target.value })}
                />
              </label>
              <label>
                Persona
                <select
                  value={form.persona_id}
                  onChange={(e) => patch({ persona_id: e.target.value })}
                >
                  {personas.map((p) => (
                    <option key={p.id} value={p.id}>{p.id}</option>
                  ))}
                  {!personas.length && (
                    <option value={form.persona_id}>{form.persona_id}</option>
                  )}
                </select>
              </label>
              <label>
                Product config
                <input
                  value={form.product_id}
                  onChange={(e) => patch({ product_id: e.target.value })}
                  placeholder="default"
                />
              </label>
              <label>
                Scope kind
                <select
                  value={form.scope.kind}
                  onChange={(e) =>
                    patch({
                      scope: {
                        ...form.scope,
                        kind: e.target.value as ReviewerRunConfig["scope"]["kind"],
                      },
                    })
                  }
                >
                  <option value="filter_url">Jira filter URL</option>
                  <option value="jql">JQL</option>
                  <option value="epic_keys">Epic keys (comma-separated)</option>
                  <option value="epic_url">Single epic URL</option>
                </select>
              </label>
              <label>
                Scope value
                <textarea
                  className="scope-value"
                  value={form.scope.value}
                  onChange={(e) =>
                    patch({ scope: { ...form.scope, value: e.target.value } })
                  }
                  rows={4}
                />
              </label>
              <div className="panel" style={{ marginTop: "0.75rem", background: "var(--bg)" }}>
                <h4 style={{ marginTop: 0 }}>Resolved epic keys</h4>
                <p className="muted" style={{ fontSize: "0.85rem" }}>
                  For <strong>JQL</strong> or <strong>filter URL</strong>: run search in Cursor
                  (Atlassian MCP, Epics only), paste keys below.{" "}
                  <code>scope.value</code> stays the source JQL for Creator handoff.
                </p>
                {form.resolved_at && (
                  <p className="muted" style={{ fontSize: "0.8rem" }}>
                    Last resolved: {form.resolved_at} ({form.resolved_source ?? "—"}) ·{" "}
                    {form.resolved_epic_keys?.length ?? 0} keys
                  </p>
                )}
                <label>
                  Paste keys (one per line or comma-separated)
                  <textarea
                    className="scope-value"
                    value={pasteKeysText}
                    onChange={(e) => setPasteKeysText(e.target.value)}
                    rows={5}
                    placeholder="ONE-12345&#10;ONE-67890"
                  />
                </label>
                <div className="btn-row">
                  <button type="button" disabled={busy} onClick={savePastedKeys}>
                    Save pasted keys
                  </button>
                  <button
                    type="button"
                    className="secondary"
                    disabled={busy}
                    onClick={resolveScope}
                  >
                    Resolve from scope
                  </button>
                  <button
                    type="button"
                    className="secondary"
                    disabled={busy}
                    onClick={copyJqlResolvePrompt}
                  >
                    Copy JQL resolve prompt
                  </button>
                  <button
                    type="button"
                    className="secondary"
                    disabled={busy}
                    onClick={clearResolved}
                  >
                    Clear resolved
                  </button>
                </div>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
                <label>
                  Pass type
                  <select
                    value={form.pass_type}
                    onChange={(e) =>
                      patch({
                        pass_type: e.target.value as ReviewerRunConfig["pass_type"],
                      })
                    }
                  >
                    <option value="full_sweep">Full sweep</option>
                    <option value="rescan_delta">Rescan (delta)</option>
                    <option value="new_epics_only">New epics only</option>
                  </select>
                </label>
                <label>
                  Child scans
                  <select
                    value={form.child_scan}
                    onChange={(e) =>
                      patch({
                        child_scan: e.target.value as ReviewerRunConfig["child_scan"],
                      })
                    }
                  >
                    <option value="epic_only_inventory">Epic + inventory (default)</option>
                    <option value="include_child_checklists">Include child checklists</option>
                  </select>
                </label>
              </div>
              <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginTop: "0.75rem" }}>
                <input
                  type="checkbox"
                  checked={form.creator_handoff_exclude_not_fit}
                  onChange={(e) =>
                    patch({ creator_handoff_exclude_not_fit: e.target.checked })
                  }
                />
                Exclude not_fit epics from Creator handoff
              </label>
              <label>
                Notes
                <textarea
                  className="scope-value"
                  rows={2}
                  value={form.notes ?? ""}
                  onChange={(e) => patch({ notes: e.target.value })}
                />
              </label>
              <div className="btn-row">
                <button type="button" onClick={onSave} disabled={busy}>
                  Save to repo
                </button>
                <button
                  type="button"
                  onClick={copyPrompt}
                  disabled={!form.portfolio_id.trim()}
                >
                  Copy Cursor prompt
                </button>
                <button type="button" onClick={listNewEpics} disabled={busy || !form.portfolio_id.trim()}>
                  List new epics
                </button>
              </div>
              {form.portfolio_id.trim() && (
                <details className="prompt-preview" style={{ marginTop: "1rem" }}>
                  <summary className="muted">Prompt preview</summary>
                  <pre className="prompt-pre">{buildReviewerCursorPrompt(form)}</pre>
                </details>
              )}
              {newEpicsInfo && (
                <pre className="prompt-pre" style={{ marginTop: "0.75rem" }}>{newEpicsInfo}</pre>
              )}
            </>
          )}
          {!creating && !selected && (
            <p className="muted">Select a config or create a new one.</p>
          )}
        </div>
      </div>

      {message && <p className="muted">{message}</p>}
      {error && <p className="error">{error}</p>}
    </>
  );
}
