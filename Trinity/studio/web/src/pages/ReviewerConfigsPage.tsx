import { useEffect, useState } from "react";
import { api, type ReviewerRunConfig } from "../api";
import ReviewerConfigFields from "../components/ReviewerConfigFields";
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
              <ReviewerConfigFields
                form={form}
                personas={personas}
                pasteKeysText={pasteKeysText}
                busy={busy}
                lockPortfolioId={!creating && !!selected}
                onChange={patch}
                onPasteKeysText={setPasteKeysText}
                onSave={onSave}
                onSavePastedKeys={savePastedKeys}
                onResolveScope={resolveScope}
                onCopyJqlPrompt={copyJqlResolvePrompt}
                onClearResolved={clearResolved}
                extraActions={
                  <>
                    <button type="button" onClick={copyPrompt} disabled={!form.portfolio_id.trim()}>
                      Copy Cursor prompt
                    </button>
                    <button type="button" onClick={listNewEpics} disabled={busy || !form.portfolio_id.trim()}>
                      List new epics
                    </button>
                  </>
                }
                footer={
                  <>
                    {form.portfolio_id.trim() && (
                      <details className="prompt-preview" style={{ marginTop: "1rem" }}>
                        <summary className="muted">Prompt preview</summary>
                        <pre className="prompt-pre">{buildReviewerCursorPrompt(form)}</pre>
                      </details>
                    )}
                    {newEpicsInfo && (
                      <pre className="prompt-pre" style={{ marginTop: "0.75rem" }}>
                        {newEpicsInfo}
                      </pre>
                    )}
                  </>
                }
              />
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
