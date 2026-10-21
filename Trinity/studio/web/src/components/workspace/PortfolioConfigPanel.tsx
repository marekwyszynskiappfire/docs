import { useState } from "react";
import { Link } from "react-router-dom";
import { api, ReviewerRunConfig } from "../../api";
import ReviewerConfigFields from "../ReviewerConfigFields";

type Props = {
  portfolioId: string | null;
  onSaved: () => void;
  onNote: (message: string) => void;
};

export default function PortfolioConfigPanel({ portfolioId, onSaved, onNote }: Props) {
  const [active, setActive] = useState(false);
  const [form, setForm] = useState<ReviewerRunConfig | null>(null);
  const [personas, setPersonas] = useState<{ id: string }[]>([]);
  const [pasteKeysText, setPasteKeysText] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const open = () => {
    setActive(true);
    if (!portfolioId || form) return;
    api
      .reviewerRunConfig(portfolioId)
      .then((config) => {
        setForm(config);
        setPasteKeysText((config.resolved_epic_keys ?? []).join("\n"));
      })
      .catch((reason) => setError(String(reason)));
    api.personas().then(setPersonas).catch(() => setPersonas([]));
  };

  const save = async () => {
    if (!form || !portfolioId) return;
    setBusy(true);
    setError("");
    try {
      const saved = await api.saveReviewerRunConfig(portfolioId, form);
      setForm(saved);
      onSaved();
      onNote(`Saved portfolio ${portfolioId}. Copy the Reviewer prompt again if scope or persona changed.`);
    } catch (reason) {
      setError(String(reason));
    } finally {
      setBusy(false);
    }
  };

  const savePastedKeys = async () => {
    if (!portfolioId) return;
    setBusy(true);
    setError("");
    try {
      const result = await api.pasteResolvedKeys(portfolioId, pasteKeysText);
      setForm(result.config);
      setPasteKeysText((result.config.resolved_epic_keys ?? []).join("\n"));
      onSaved();
      onNote(`Stored ${result.resolved_count} epic key(s).`);
    } catch (reason) {
      setError(String(reason));
    } finally {
      setBusy(false);
    }
  };

  const resolveScope = async () => {
    if (!portfolioId) return;
    setBusy(true);
    setError("");
    try {
      const result = await api.resolveReviewerScope(portfolioId);
      if (result.status === "resolved" && result.config) {
        setForm(result.config);
        setPasteKeysText((result.config.resolved_epic_keys ?? []).join("\n"));
        onSaved();
        onNote(`Resolved ${result.config.resolved_epic_keys?.length ?? 0} epic key(s).`);
      } else if (result.prompt) {
        await navigator.clipboard.writeText(result.prompt);
        onNote(result.message ?? "JQL resolve prompt copied. Paste the keys back here.");
      } else {
        setError(result.message ?? "Could not resolve scope");
      }
    } catch (reason) {
      setError(String(reason));
    } finally {
      setBusy(false);
    }
  };

  const copyJql = async () => {
    if (!portfolioId) return;
    try {
      const result = await api.resolveScopePrompt(portfolioId);
      await navigator.clipboard.writeText(result.prompt);
      onNote("JQL resolve prompt copied.");
    } catch (reason) {
      setError(String(reason));
    }
  };

  const clearResolved = async () => {
    if (!portfolioId) return;
    setBusy(true);
    setError("");
    try {
      const config = await api.clearResolvedKeys(portfolioId);
      setForm(config);
      setPasteKeysText("");
      onSaved();
      onNote("Cleared resolved epic keys.");
    } catch (reason) {
      setError(String(reason));
    } finally {
      setBusy(false);
    }
  };

  return (
    <details
      className="panel ws-portfolio-config"
      onToggle={(event) => {
        if (event.currentTarget.open) open();
      }}
    >
      <summary>
        Portfolio
        {portfolioId ? <span className="muted"> · {portfolioId}</span> : null}
      </summary>
      {!portfolioId && (
        <p className="muted">
          This run has no portfolio config. Create the first one under{" "}
          <Link to="/reviewer-configs">Reviewer configs</Link>.
        </p>
      )}
      {error && <p className="error">{error}</p>}
      {active && portfolioId && !form && !error && <p className="muted">Loading portfolio…</p>}
      {form && (
        <ReviewerConfigFields
          form={form}
          personas={personas}
          pasteKeysText={pasteKeysText}
          busy={busy}
          lockPortfolioId
          onChange={(patch) => setForm((current) => (current ? { ...current, ...patch } : current))}
          onPasteKeysText={setPasteKeysText}
          onSave={save}
          onSavePastedKeys={savePastedKeys}
          onResolveScope={resolveScope}
          onCopyJqlPrompt={copyJql}
          onClearResolved={clearResolved}
        />
      )}
    </details>
  );
}
