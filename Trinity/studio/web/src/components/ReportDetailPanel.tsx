import type { ReviewReport } from "../types/review-payload";

function SourcedList({ items }: { items: ({ text?: string; source?: string } | string)[] }) {
  return (
    <ul className="prose-list">
      {items.map((it, i) => (
        <li key={i}>
          {typeof it === "string" ? it : it.text}
          {typeof it !== "string" && it.source && <span className="muted"> ({it.source})</span>}
        </li>
      ))}
    </ul>
  );
}

export default function ReportDetailPanel({ report }: { report?: ReviewReport }) {
  if (!report) return null;
  const hasDetail =
    (report.facts && report.facts.length > 0) ||
    (report.not_stated && report.not_stated.length > 0) ||
    (report.risks && report.risks.length > 0) ||
    (report.testing_focus && report.testing_focus.length > 0);
  if (!hasDetail) return null;

  return (
    <div className="panel report-detail">
      {report.facts && report.facts.length > 0 && (
        <details open className="report-block">
          <summary>Information identified</summary>
          <SourcedList items={report.facts} />
        </details>
      )}
      {report.not_stated && report.not_stated.length > 0 && (
        <details className="report-block">
          <summary>Not stated</summary>
          <ul className="prose-list">
            {report.not_stated.map((t, i) => (
              <li key={i}>{t}</li>
            ))}
          </ul>
        </details>
      )}
      {report.risks && report.risks.length > 0 && (
        <details className="report-block">
          <summary>Risks</summary>
          <SourcedList items={report.risks} />
        </details>
      )}
      {report.testing_focus && report.testing_focus.length > 0 && (
        <details className="report-block">
          <summary>Testing focus</summary>
          <ul className="prose-list">
            {report.testing_focus.map((t, i) => (
              <li key={i}>{t.text}</li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}
