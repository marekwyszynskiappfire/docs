import type { WorkspaceStage } from "../../api";

export default function WorkspaceStepper({ stages }: { stages: WorkspaceStage[] }) {
  return (
    <ol className="ws-stepper" aria-label="Process stages">
      {stages.map((stage, index) => (
        <li
          key={stage.id}
          className={`ws-step ws-step--${stage.status}`}
          aria-current={stage.status === "current" ? "step" : undefined}
        >
          <span className="ws-step-num" aria-hidden="true">
            {stage.status === "complete" ? "✓" : index + 1}
          </span>
          <span className="ws-step-title">{stage.title}</span>
          <span className="visually-hidden">
            {stage.status === "complete" ? " (done)" : stage.status === "current" ? " (current)" : ""}
          </span>
        </li>
      ))}
    </ol>
  );
}
