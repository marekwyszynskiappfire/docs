import { Link } from "react-router-dom";
import type { Stats } from "../api";

export type HomePhase = "start" | "approve" | "generate" | "review_tests" | "import_xray" | "caught_up";

type Focus = { id: string; label: string } | null;

type Props = {
  stats: Stats | null;
  phase: HomePhase;
  focus: Focus;
};

const PHASE_STEP = {
  start: "reviewer",
  approve: "reviewer",
  generate: "workspace",
  review_tests: "workspace",
  import_xray: "importer",
  caught_up: "done",
} as const;

export default function PipelineStrip({ stats, phase, focus }: Props) {
  if (!stats) return null;
  const workspaceHref = focus ? `/workspace/${encodeURIComponent(focus.id)}` : "/";
  const label = focus?.label ?? "the portfolio";
  const copy = actionCopy(phase, label);
  const href = phase === "start" ? "#new-portfolio" : phase === "import_xray" ? "/importer" : workspaceHref;
  const current = PHASE_STEP[phase];
  const steps = [
    {
      id: "reviewer",
      title: "Reviewer",
      detail:
        current === "reviewer"
          ? phase === "start"
            ? "Save a portfolio, then run Reviewer"
            : "Read the review and approve the Epic"
          : `${stats.review_units_approved} of ${stats.review_units} approved`,
    },
    {
      id: "workspace",
      title: "Workspace",
      detail:
        phase === "generate"
          ? "Generate tests on the Epic"
          : phase === "review_tests"
            ? "Approve or reject each test"
            : current === "reviewer"
              ? "After the review is approved"
              : `${stats.test_cases_approved}/${stats.test_cases} tests approved`,
    },
    {
      id: "importer",
      title: "Importer",
      detail: phase === "import_xray" ? "Preview the Xray plan" : "After tests are chosen for Xray",
    },
  ];

  return (
    <section className="now-board" id="what-now" aria-label="What to do now">
      <div className="now-board__action">
        <p className="now-board__eyebrow">Now</p>
        <h2>{copy.title}</h2>
        <p>{copy.detail}</p>
        {phase !== "caught_up" && (
          <Link className="now-board__button" to={href}>
            {copy.label}
          </Link>
        )}
      </div>
      <ol className="now-board__steps">
        {steps.map((step, index) => {
          const state =
            current === "done" ? "is-done" : step.id === current ? "is-now" : index < stepIndex(current) ? "is-done" : "";
          return (
            <li key={step.id} className={state}>
              <span className="now-step__mark" aria-hidden="true">
                {state === "is-done" ? "✓" : index + 1}
              </span>
              <div>
                <strong>{step.title}</strong>
                <p>{step.detail}</p>
              </div>
            </li>
          );
        })}
      </ol>
    </section>
  );
}

function stepIndex(id: string): number {
  return ["reviewer", "workspace", "importer"].indexOf(id);
}

function actionCopy(phase: HomePhase, label: string): { title: string; detail: string; label: string } {
  if (phase === "start") {
    return {
      title: "Run a review",
      detail: "Open New portfolio, save it, and choose Run Reviewer in Cursor. Import the review folder when the agent finishes.",
      label: "Go to New portfolio",
    };
  }
  if (phase === "approve") {
    return {
      title: "Approve the review",
      detail: `Open the ${label} workspace, read the verdict, and approve the Epic.`,
      label: `Open ${label} workspace`,
    };
  }
  if (phase === "generate") {
    return {
      title: "Generate tests",
      detail: `The ${label} review is approved. In the workspace, choose Generate tests on the Epic. Creator lists the suite after it is imported.`,
      label: `Open ${label} workspace`,
    };
  }
  if (phase === "review_tests") {
    return {
      title: "Review the tests",
      detail: `Open the ${label} workspace and approve or reject each test.`,
      label: `Open ${label} workspace`,
    };
  }
  if (phase === "import_xray") {
    return {
      title: "Import to Xray",
      detail: "Approved tests are ready. Open Importer to preview the plan before anything is written.",
      label: "Open Importer",
    };
  }
  return {
    title: "Up to date",
    detail: `${label} has no waiting step.`,
    label: "",
  };
}
