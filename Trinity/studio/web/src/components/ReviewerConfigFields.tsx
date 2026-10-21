import type { ReactNode } from "react";
import type { ReviewerRunConfig } from "../api";

type Props = {
  form: ReviewerRunConfig;
  personas: { id: string }[];
  pasteKeysText: string;
  busy: boolean;
  lockPortfolioId?: boolean;
  onChange: (patch: Partial<ReviewerRunConfig>) => void;
  onPasteKeysText: (value: string) => void;
  onSave: () => void;
  onSavePastedKeys: () => void;
  onResolveScope: () => void;
  onCopyJqlPrompt: () => void;
  onClearResolved: () => void;
  extraActions?: ReactNode;
  footer?: ReactNode;
};

export default function ReviewerConfigFields({
  form,
  personas,
  pasteKeysText,
  busy,
  lockPortfolioId = false,
  onChange,
  onPasteKeysText,
  onSave,
  onSavePastedKeys,
  onResolveScope,
  onCopyJqlPrompt,
  onClearResolved,
  extraActions,
  footer,
}: Props) {
  return (
    <>
      <label>
        portfolio_id
        <input
          value={form.portfolio_id}
          disabled={lockPortfolioId}
          onChange={(event) => onChange({ portfolio_id: event.target.value })}
          placeholder="2026-Q4-my-program"
        />
      </label>
      <label>
        Label
        <input value={form.label ?? ""} onChange={(event) => onChange({ label: event.target.value })} />
      </label>
      <label>
        Persona
        <select value={form.persona_id} onChange={(event) => onChange({ persona_id: event.target.value })}>
          {personas.map((persona) => (
            <option key={persona.id} value={persona.id}>
              {persona.id}
            </option>
          ))}
          {!personas.some((persona) => persona.id === form.persona_id) && (
            <option value={form.persona_id}>{form.persona_id}</option>
          )}
        </select>
      </label>
      <label>
        Product config
        <input
          value={form.product_id}
          onChange={(event) => onChange({ product_id: event.target.value })}
          placeholder="default"
        />
      </label>
      <label>
        Scope kind
        <select
          value={form.scope.kind}
          onChange={(event) =>
            onChange({
              scope: {
                ...form.scope,
                kind: event.target.value as ReviewerRunConfig["scope"]["kind"],
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
          onChange={(event) => onChange({ scope: { ...form.scope, value: event.target.value } })}
          rows={4}
        />
      </label>
      <div className="panel" style={{ marginTop: "0.75rem", background: "var(--bg)" }}>
        <h4 style={{ marginTop: 0 }}>Resolved epic keys</h4>
        <p className="muted">
          For JQL or a filter URL, paste the Epic keys the search returned. Scope value stays the source for the
          Creator handoff.
        </p>
        {form.resolved_at && (
          <p className="muted">
            Last resolved: {form.resolved_at} ({form.resolved_source ?? "—"}) · {form.resolved_epic_keys?.length ?? 0}{" "}
            keys
          </p>
        )}
        <label>
          Paste keys (one per line or comma-separated)
          <textarea
            className="scope-value"
            value={pasteKeysText}
            onChange={(event) => onPasteKeysText(event.target.value)}
            rows={5}
            placeholder={"ONE-12345\nONE-67890"}
          />
        </label>
        <div className="btn-row">
          <button type="button" disabled={busy} onClick={onSavePastedKeys}>
            Save pasted keys
          </button>
          <button type="button" className="secondary" disabled={busy} onClick={onResolveScope}>
            Resolve from scope
          </button>
          <button type="button" className="secondary" disabled={busy} onClick={onCopyJqlPrompt}>
            Copy JQL resolve prompt
          </button>
          <button type="button" className="secondary" disabled={busy} onClick={onClearResolved}>
            Clear resolved
          </button>
        </div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
        <label>
          Pass type
          <select
            value={form.pass_type}
            onChange={(event) =>
              onChange({ pass_type: event.target.value as ReviewerRunConfig["pass_type"] })
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
            onChange={(event) =>
              onChange({ child_scan: event.target.value as ReviewerRunConfig["child_scan"] })
            }
          >
            <option value="epic_only_inventory">Epic + inventory (default)</option>
            <option value="include_child_checklists">Include child checklists</option>
          </select>
        </label>
      </div>
      <label className="checkbox-row">
        <input
          type="checkbox"
          checked={form.creator_handoff_exclude_not_fit}
          onChange={(event) => onChange({ creator_handoff_exclude_not_fit: event.target.checked })}
        />
        Exclude not_fit epics from Creator handoff
      </label>
      <label>
        Notes
        <textarea
          className="scope-value"
          rows={2}
          value={form.notes ?? ""}
          onChange={(event) => onChange({ notes: event.target.value })}
        />
      </label>
      <div className="btn-row">
        <button type="button" onClick={onSave} disabled={busy}>
          Save to repo
        </button>
        {extraActions}
      </div>
      {footer}
    </>
  );
}
