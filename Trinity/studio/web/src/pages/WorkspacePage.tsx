import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { api, CoverageProfileId, WorkspaceSummary } from "../api";
import EpicAccordion from "../components/workspace/EpicAccordion";
import CoverageDepthControl from "../components/workspace/CoverageDepthControl";
import ContextLoadedAlertsPanel from "../components/ContextLoadedAlertsPanel";
import PortfolioConfigPanel from "../components/workspace/PortfolioConfigPanel";
import ReviewFolderImport from "../components/workspace/ReviewFolderImport";
import ReviewerPromptPanel from "../components/workspace/ReviewerPromptPanel";
import WorkspaceImportPanel from "../components/workspace/WorkspaceImportPanel";
import NextActionCard from "../components/workspace/NextActionCard";
import ProcessHelp from "../components/workspace/ProcessHelp";
import WorkspaceStepper from "../components/workspace/WorkspaceStepper";
import { activeTip, dismissTip, resetTips } from "../lib/workspaceTips";

const POLL_MS = 4000;

export default function WorkspacePage() {
  const { runId = "" } = useParams();
  const navigate = useNavigate();
  const [params, setParams] = useSearchParams();
  const [workspace, setWorkspace] = useState<WorkspaceSummary | null>(null);
  const [error, setError] = useState("");
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);
  const [tipsVersion, setTipsVersion] = useState(0);
  const [rejectionReasons, setRejectionReasons] = useState<{ id: string; label: string }[]>([]);
  const openEpic = params.get("epic");
  const openTest = params.get("test");
  const [expanded, setExpanded] = useState<Set<string>>(() => new Set(openEpic ? [openEpic] : []));
  const [selectedTests, setSelectedTests] = useState<Record<string, string>>({});
  const [portfolioRevision, setPortfolioRevision] = useState(0);

  useEffect(() => {
    if (!openEpic) return;
    setExpanded((current) => (current.has(openEpic) ? current : new Set(current).add(openEpic)));
  }, [openEpic]);

  const load = useCallback(
    () =>
      api
        .workspace(runId)
        .then((body) => {
          setWorkspace(body);
          setError("");
        })
        .catch((reason) => setError(String(reason))),
    [runId]
  );

  useEffect(() => {
    load();
    api
      .telemetryRejectionReasons()
      .then((body) => setRejectionReasons(body.reasons))
      .catch(() => setRejectionReasons([]));
  }, [load]);

  const watched = workspace?.watch_handoff_ids ?? [];
  useEffect(() => {
    if (watched.length === 0) return;
    const timer = window.setInterval(async () => {
      if (document.visibilityState !== "visible") return;
      try {
        const results = await Promise.all(watched.map((id) => api.checkHandoff(runId, id)));
        if (results.some((item) => item.status === "imported" || item.status === "invalid_output")) {
          await load();
        }
      } catch {
        // A failed poll is retried on the next tick; the card keeps its last known state.
      }
    }, POLL_MS);
    return () => window.clearInterval(timer);
  }, [runId, watched.join("|"), load]);

  const setOpen = (epic: string | null, test: string | null = null) => {
    const next = new URLSearchParams(params);
    if (epic) next.set("epic", epic);
    else next.delete("epic");
    if (test) next.set("test", test);
    else next.delete("test");
    setParams(next, { replace: true });
  };

  const copy = async (text: string, handoffId: string, message: string) => {
    try {
      await navigator.clipboard.writeText(text);
      await api.markHandoffCopied(runId, handoffId);
      setNote(message);
    } catch {
      setNote("Copy failed. Open “Show the Cursor prompt” and copy the text.");
    }
  };

  const run = async (work: () => Promise<unknown>) => {
    setBusy(true);
    setNote("");
    try {
      await work();
      await load();
    } catch (reason) {
      setError(String(reason));
    } finally {
      setBusy(false);
    }
  };

  const onPrimary = () => {
    if (!workspace) return;
    const action = workspace.next_action;
    const { primary } = action;
    switch (primary.kind) {
      case "approve_review":
        if (action.unit_id) run(() => api.approve(action.unit_id!));
        break;
      case "prepare_creator":
        if (action.unit_id) {
          run(() => api.prepareCreator(runId, action.unit_id!));
          setOpen(action.epic_key);
        }
        break;
      case "copy_prompt":
        if (action.cursor_prompt) {
          copy(
            action.cursor_prompt.text,
            action.cursor_prompt.handoff_id,
            "Copied. Paste it into Cursor chat. Studio will pick up the file."
          );
        }
        break;
      case "accept_changes":
        if (primary.handoff_id) run(() => api.checkHandoff(runId, primary.handoff_id!, true));
        break;
      case "review_tests":
        setOpen(action.epic_key);
        window.setTimeout(
          () => document.getElementById(`ws-${action.epic_key}`)?.scrollIntoView({ behavior: "smooth" }),
          50
        );
        break;
      case "open_importer":
        document.getElementById("ws-import")?.scrollIntoView({ behavior: "smooth" });
        break;
      case "open_unit":
        if (primary.path) navigate(primary.path);
        break;
      default:
        break;
    }
  };

  const toggleEpic = (key: string) => {
    setExpanded((current) => {
      const next = new Set(current);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
    setOpen(expanded.has(key) ? null : key);
  };

  const onPortfolio = (kind: string) => {
    if (!workspace) return;
    const action = workspace.portfolio_actions.find((item) => item.kind === kind);
    if (!action) return;
    if (kind === "prepare_creator_batch") {
      run(async () => {
        const result = await api.prepareCreatorBatch(runId);
        setNote(
          result.prepared.length
            ? `Prepared prompts for ${result.prepared.map((item) => item.epic_key).join(", ")}.`
            : "Those Epics already have Creator prompts."
        );
      });
      return;
    }
    if (kind === "copy_creator_prompts") {
      const text = workspace.epics
        .filter((epic) => action.epic_keys.includes(epic.jira_key) && epic.creator_handoff)
        .map((epic) => `# ${epic.jira_key}\n\n${epic.creator_handoff?.prompt ?? ""}`)
        .join("\n\n---\n\n");
      const first = action.handoff_ids?.[0];
      if (first) {
        copy(text, first, `Copied ${action.epic_keys.length} Creator prompts. Paste them into Cursor.`);
      }
      return;
    }
    if (kind === "review_selected_tests") {
      setExpanded((current) => new Set([...current, ...action.epic_keys]));
      const first = action.epic_keys[0];
      if (first) {
        setOpen(first);
        window.setTimeout(
          () => document.getElementById(`ws-${first}`)?.scrollIntoView({ behavior: "smooth" }),
          50
        );
      }
      return;
    }
    document.getElementById("ws-import")?.scrollIntoView({ behavior: "smooth" });
  };

  const approveSelected = () => {
    const byRun = new Map<string, string[]>();
    for (const [testId, creatorRunId] of Object.entries(selectedTests)) {
      const ids = byRun.get(creatorRunId) ?? [];
      ids.push(testId);
      byRun.set(creatorRunId, ids);
    }
    run(async () => {
      let updated = 0;
      for (const [creatorRunId, ids] of byRun) {
        const result = await api.bulkTestReview(creatorRunId, ids, { human_review_status: "approved" });
        updated += result.updated;
      }
      setSelectedTests({});
      setNote(`Approved ${updated} selected test${updated === 1 ? "" : "s"}.`);
    });
  };

  const tip = useMemo(
    () => (workspace ? activeTip(workspace) : null),
    // tipsVersion forces a re-read after dismiss/reset.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [workspace, tipsVersion]
  );

  if (error && !workspace) return <p className="error">{error}</p>;
  if (!workspace) return <p className="page-lead">Loading workspace…</p>;

  const portfolioActions = workspace.portfolio_actions ?? [];

  return (
    <div className="ws">
      <div className="ws-head">
        <h2 className="ws-title">{workspace.label}</h2>
        <button type="button" className="secondary" onClick={() => setHelpOpen(true)}>
          Process help
        </button>
      </div>
      <WorkspaceStepper stages={workspace.stages} />
      <ReviewFolderImport runId={runId} onImported={load} onNote={setNote} />
      <ContextLoadedAlertsPanel runId={runId} />
      <CoverageDepthControl
        profiles={workspace.coverage_profiles}
        value={workspace.coverage_profile}
        overrideCount={workspace.epics.filter((epic) => epic.coverage_profile).length}
        disabled={busy}
        onChange={(profile: CoverageProfileId) =>
          run(async () => {
            const result = await api.setCoverageProfile(runId, profile);
            setNote(result.message);
          })
        }
      />
      <PortfolioConfigPanel
        portfolioId={workspace.portfolio_id}
        onSaved={() => setPortfolioRevision((current) => current + 1)}
        onNote={setNote}
      />
      <ReviewerPromptPanel
        portfolioId={workspace.portfolio_id}
        workspacePath={workspace.workspace_path}
        epicKeys={workspace.epics.map((epic) => epic.jira_key)}
        reloadToken={portfolioRevision}
        onCopied={setNote}
      />
      <NextActionCard
        action={workspace.next_action}
        busy={busy}
        note={note}
        onPrimary={onPrimary}
        onCheckNow={(id) => run(() => api.checkHandoff(runId, id))}
      />
      {portfolioActions.length > 0 && (
        <section className="panel ws-portfolio" aria-label="Portfolio actions">
          <p className="ws-next-eyebrow">Across this portfolio</p>
          <div className="btn-row">
            {portfolioActions.map((action) => (
              <button key={action.kind} type="button" className="secondary" onClick={() => onPortfolio(action.kind)} disabled={busy}>
                {action.label}
              </button>
            ))}
            {Object.keys(selectedTests).length > 0 && (
              <button type="button" onClick={approveSelected} disabled={busy}>
                Approve {Object.keys(selectedTests).length} selected
              </button>
            )}
          </div>
        </section>
      )}
      {portfolioActions.length === 0 && Object.keys(selectedTests).length > 0 && (
        <div className="btn-row">
          <button type="button" onClick={approveSelected} disabled={busy}>
            Approve {Object.keys(selectedTests).length} selected
          </button>
        </div>
      )}
      <WorkspaceImportPanel
        epics={workspace.epics}
        focusKey={workspace.next_action.epic_key}
        previewAllKey={portfolioActions.some((action) => action.kind === "preview_import_plans")}
        onImported={load}
      />
      {error && <p className="error">{error}</p>}
      {tip && (
        <div className="ws-tip" role="note">
          <span>{tip.text}</span>
          <button
            type="button"
            className="secondary"
            onClick={() => {
              dismissTip(tip);
              setTipsVersion((v) => v + 1);
            }}
          >
            Got it
          </button>
        </div>
      )}
      <div className="ws-epics">
        {workspace.epics.map((epic) => (
          <EpicAccordion
            key={epic.unit_id}
            runId={runId}
            profiles={workspace.coverage_profiles}
            portfolioLabel={
              workspace.coverage_profiles.find((profile) => profile.id === workspace.coverage_profile)?.label ??
              "Balanced"
            }
            epic={epic}
            expanded={expanded.has(epic.jira_key)}
            openTestId={openEpic === epic.jira_key ? openTest : null}
            rejectionReasons={rejectionReasons}
            selectedTests={selectedTests}
            onToggle={() => toggleEpic(epic.jira_key)}
            onToggleTest={(testId) => setOpen(epic.jira_key, openTest === testId ? null : testId)}
            onToggleSelected={(testId, creatorRunId, on) =>
              setSelectedTests((current) => {
                const next = { ...current };
                if (on) next[testId] = creatorRunId;
                else delete next[testId];
                return next;
              })
            }
            onChanged={load}
            onError={setError}
          />
        ))}
      </div>
      <ProcessHelp
        open={helpOpen}
        stages={workspace.stages}
        reviewPrompt={workspace.review_prompt}
        onClose={() => setHelpOpen(false)}
        onShowTips={() => {
          resetTips();
          setTipsVersion((v) => v + 1);
          setHelpOpen(false);
        }}
        onCopyReviewPrompt={() => {
          const prompt = workspace.review_prompt;
          if (prompt) copy(prompt.text, prompt.handoff_id, "Rescan prompt copied.");
        }}
      />
    </div>
  );
}
