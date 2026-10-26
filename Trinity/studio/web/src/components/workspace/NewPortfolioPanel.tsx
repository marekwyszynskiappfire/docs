import { useState } from "react";
import { Link } from "react-router-dom";
import { api, type ReviewerRunConfig } from "../../api";
import ReviewerConfigFields from "../ReviewerConfigFields";
import { buildReviewerCursorPrompt } from "../../lib/reviewerPrompt";
import CursorAgentControl from "./CursorAgentControl";

function readableError(reason: unknown): string {
  const text = String(reason).replace(/^Error:\s*/, "");
  try {
    const parsed = JSON.parse(text) as { detail?: unknown };
    if (typeof parsed.detail === "string") return parsed.detail;
  } catch {
    /* response was already plain text */
  }
  return text;
}

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

export default function NewPortfolioPanel() {
  const [ready, setReady] = useState(false);
  const [form, setForm] = useState<ReviewerRunConfig>({ ...DEFAULT_CONFIG });
  const [personas, setPersonas] = useState<{ id: string }[]>([]);
  const [pasteKeysText, setPasteKeysText] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);

  const open = () => {
    if (ready) return;
    setReady(true);
    api.personas().then(setPersonas).catch(() => setPersonas([]));
  };

  const save = async () => {
    const portfolioId = form.portfolio_id.trim();
    if (!portfolioId) {
      setError("Enter a portfolio id before saving.");
      return;
    }
    if (!form.scope.value.trim()) {
      setError("Enter a scope value before saving.");
      return;
    }
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const savedConfig = await api.saveReviewerRunConfig(portfolioId, form);
      setForm(savedConfig);
      setSaved(true);
      setMessage(
        `Saved Trinity/reviewer/config/runs/${portfolioId}.json. Copy the Reviewer prompt, run it in Cursor, then import the review folder on this page.`
      );
    } catch (reason) {
      setError(readableError(reason));
    } finally {
      setBusy(false);
    }
  };

  const copyPrompt = async () => {
    if (!form.portfolio_id.trim()) {
      setError("Enter a portfolio id before copying the prompt.");
      return;
    }
    try {
      await navigator.clipboard.writeText(buildReviewerCursorPrompt(form));
      setMessage("Reviewer prompt copied.");
      setError("");
    } catch {
      setError("Copy failed. Save the portfolio, then copy the prompt from More → Reviewer configs.");
    }
  };

  const resolveScope = async () => {
    const portfolioId = form.portfolio_id.trim();
    if (!portfolioId || !saved) {
      setError("Save the portfolio before resolving scope.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const result = await api.resolveReviewerScope(portfolioId);
      if (result.status === "resolved" && result.config) {
        setForm(result.config);
        setPasteKeysText((result.config.resolved_epic_keys ?? []).join("\n"));
        setMessage(`Resolved ${result.config.resolved_epic_keys?.length ?? 0} epic key(s).`);
      } else if (result.prompt) {
        await navigator.clipboard.writeText(result.prompt);
        setMessage(result.message ?? "JQL resolve prompt copied. Paste the keys back here.");
      } else {
        setError(result.message ?? "Could not resolve scope");
      }
    } catch (reason) {
      setError(readableError(reason));
    } finally {
      setBusy(false);
    }
  };

  const copyJql = async () => {
    const portfolioId = form.portfolio_id.trim();
    if (!portfolioId || !saved) {
      setError("Save the portfolio before copying the JQL prompt.");
      return;
    }
    try {
      const result = await api.resolveScopePrompt(portfolioId);
      await navigator.clipboard.writeText(result.prompt);
      setMessage("JQL resolve prompt copied.");
      setError("");
    } catch (reason) {
      setError(readableError(reason));
    }
  };

  const savePastedKeys = async () => {
    const portfolioId = form.portfolio_id.trim();
    if (!portfolioId || !saved) {
      setError("Save the portfolio before storing epic keys.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const result = await api.pasteResolvedKeys(portfolioId, pasteKeysText);
      setForm(result.config);
      setPasteKeysText((result.config.resolved_epic_keys ?? []).join("\n"));
      setMessage(`Stored ${result.resolved_count} epic key(s).`);
    } catch (reason) {
      setError(readableError(reason));
    } finally {
      setBusy(false);
    }
  };

  const clearResolved = async () => {
    const portfolioId = form.portfolio_id.trim();
    if (!portfolioId || !saved) return;
    setBusy(true);
    setError("");
    try {
      const config = await api.clearResolvedKeys(portfolioId);
      setForm(config);
      setPasteKeysText("");
      setMessage("Cleared resolved epic keys.");
    } catch (reason) {
      setError(readableError(reason));
    } finally {
      setBusy(false);
    }
  };

  return (
    <details
      className="panel ws-new-portfolio"
      onToggle={(event) => {
        if (event.currentTarget.open) open();
      }}
    >
      <summary>New portfolio</summary>
      <p className="muted">
        Create the first portfolio here, before a workspace exists. This writes{" "}
        <code>Trinity/reviewer/config/runs/{"{portfolio_id}"}.json</code>.{" "}
        <Link to="/reviewer-configs">More → Reviewer configs</Link> still lists every portfolio.
      </p>
      {error && <p className="error">{error}</p>}
      {message && <p className="muted">{message}</p>}
      {ready && (
        <ReviewerConfigFields
          form={form}
          personas={personas}
          pasteKeysText={pasteKeysText}
          busy={busy}
          onChange={(patch) => {
            setSaved(false);
            setError("");
            setForm((current) => ({ ...current, ...patch }));
          }}
          onPasteKeysText={setPasteKeysText}
          onSave={save}
          onSavePastedKeys={savePastedKeys}
          onResolveScope={resolveScope}
          onCopyJqlPrompt={copyJql}
          onClearResolved={clearResolved}
          extraActions={
            <>
              <CursorAgentControl
                label="Run Reviewer in Cursor"
                disabled={!saved}
                attach={
                  saved && form.portfolio_id.trim()
                    ? { stage: "reviewer", portfolioId: form.portfolio_id.trim() }
                    : undefined
                }
                launch={() => api.launchReviewerAgent(form.portfolio_id.trim())}
                onFinished={(run) =>
                  setMessage(
                    run.status === "finished"
                      ? "Reviewer agent finished. Import the review folder below."
                      : `Reviewer agent ended with status ${run.status}.`
                  )
                }
              />
              <button type="button" className="secondary" onClick={copyPrompt} disabled={!form.portfolio_id.trim()}>
                Copy Reviewer prompt
              </button>
            </>
          }
        />
      )}
    </details>
  );
}
