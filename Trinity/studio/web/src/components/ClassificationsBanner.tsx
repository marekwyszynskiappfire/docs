export type Classifications = {
  testability?: string;
  test_scope_confidence?: string;
  risk?: { level?: string; rationale_tags?: string[] };
  automation_candidate?: { value?: string; rationale?: string; suggested_level?: string };
  readiness?: { value?: string; human_label?: string };
};

type Props = {
  classifications?: Classifications | null;
  compact?: boolean;
};

export default function ClassificationsBanner({ classifications, compact }: Props) {
  if (!classifications) return null;

  const readiness =
    classifications.readiness?.human_label ||
    classifications.readiness?.value ||
    null;
  const risk = classifications.risk?.level;
  const tags = classifications.risk?.rationale_tags?.join(", ");
  const auto = classifications.automation_candidate?.value;

  const hasContent =
    classifications.testability ||
    classifications.test_scope_confidence ||
    risk ||
    readiness ||
    auto;

  if (!hasContent) return null;

  if (compact) {
    return (
      <p className="classifications-strip muted">
        {readiness && <span className="badge">{readiness}</span>}
        {risk && <span className="badge sev-med">Risk {risk}</span>}
        {classifications.testability && (
          <span>Testability {classifications.testability}</span>
        )}
      </p>
    );
  }

  return (
    <div className="panel classifications-banner">
      <h3 style={{ marginTop: 0 }}>Classifications & readiness</h3>
      <dl className="classifications-dl">
        {readiness && (
          <>
            <dt>Readiness</dt>
            <dd>{readiness}</dd>
          </>
        )}
        {classifications.testability && (
          <>
            <dt>Testability</dt>
            <dd>{classifications.testability}</dd>
          </>
        )}
        {classifications.test_scope_confidence && (
          <>
            <dt>Scope confidence</dt>
            <dd>{classifications.test_scope_confidence}</dd>
          </>
        )}
        {risk && (
          <>
            <dt>Risk</dt>
            <dd>
              {risk}
              {tags ? ` — ${tags}` : ""}
            </dd>
          </>
        )}
        {auto && auto !== "TBD" && (
          <>
            <dt>Automation (epic signal)</dt>
            <dd>
              {auto}
              {classifications.automation_candidate?.rationale
                ? ` — ${classifications.automation_candidate.rationale}`
                : ""}
            </dd>
          </>
        )}
      </dl>
    </div>
  );
}
