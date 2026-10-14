type ReadinessSummary = {
  epics_reviewed: number;
  epics_tc_creation_ready: number;
  epics_tc_creation_ready_with_reservations: number;
  epics_tc_creation_not_ready: number;
  epics_tc_creation_unknown?: number;
};

const SEGMENTS = [
  { key: "ready", field: "epics_tc_creation_ready" as const, label: "Ready", className: "tc-bar-ready" },
  {
    key: "reservations",
    field: "epics_tc_creation_ready_with_reservations" as const,
    label: "Ready with reservations",
    className: "tc-bar-reservations",
  },
  { key: "not_ready", field: "epics_tc_creation_not_ready" as const, label: "Not ready", className: "tc-bar-not-ready" },
  { key: "unknown", field: "epics_tc_creation_unknown" as const, label: "Unknown", className: "tc-bar-unknown" },
];

type Props = {
  summary: ReadinessSummary;
  title?: string;
};

export default function TcReadinessChart({ summary, title }: Props) {
  const total = Math.max(summary.epics_reviewed, 1);
  const unknown = summary.epics_tc_creation_unknown ?? 0;

  return (
    <div className="tc-readiness-dashboard">
      {title && <h3 className="tc-readiness-title">{title}</h3>}
      <div className="tc-readiness-bar" role="img" aria-label="Epic TC creation readiness distribution">
        {SEGMENTS.map((seg) => {
          const n = seg.field === "epics_tc_creation_unknown" ? unknown : summary[seg.field];
          if (n <= 0) return null;
          const pct = (n / total) * 100;
          return (
            <div
              key={seg.key}
              className={`tc-readiness-segment ${seg.className}`}
              style={{ width: `${pct}%` }}
              title={`${seg.label}: ${n}`}
            />
          );
        })}
      </div>
      <div className="tc-readiness-legend">
        {SEGMENTS.map((seg) => {
          const n = seg.field === "epics_tc_creation_unknown" ? unknown : summary[seg.field];
          return (
            <div key={seg.key} className="tc-readiness-legend-item">
              <span className={`tc-legend-swatch ${seg.className}`} />
              <span className="tc-legend-label">{seg.label}</span>
              <strong>{n}</strong>
              <span className="muted">({Math.round((n / total) * 100)}%)</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
