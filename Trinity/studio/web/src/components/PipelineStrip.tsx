import { Link } from "react-router-dom";
import type { Stats } from "../api";

type Props = {
  stats: Stats | null;
};

export default function PipelineStrip({ stats }: Props) {
  if (!stats) return null;
  const reviewPct =
    stats.review_units > 0
      ? Math.round((stats.review_units_approved / stats.review_units) * 100)
      : 0;
  const creatorReady = stats.test_cases_ready_for_import ?? 0;

  return (
    <section className="pipeline-strip" aria-label="Trinity pipeline">
      <div className="pipeline-step">
        <span className="pipeline-step__badge">1</span>
        <div>
          <strong>Reviewer</strong>
          <p className="muted">
            {stats.review_units} units · {stats.review_units_approved} approved
            {stats.review_units > 0 ? ` (${reviewPct}%)` : ""}
          </p>
        </div>
      </div>
      <div className="pipeline-step__arrow" aria-hidden="true">→</div>
      <div className="pipeline-step">
        <span className="pipeline-step__badge">2</span>
        <div>
          <strong>Creator</strong>
          <p className="muted">
            {stats.creator_runs} runs · {stats.test_cases_approved}/{stats.test_cases} approved
          </p>
        </div>
        <Link to="/creator" className="pipeline-step__link">Open</Link>
      </div>
      <div className="pipeline-step__arrow" aria-hidden="true">→</div>
      <div className="pipeline-step">
        <span className="pipeline-step__badge">3</span>
        <div>
          <strong>Importer</strong>
          <p className="muted">
            {creatorReady} ready for Xray · {stats.test_cases_imported_xray} imported
          </p>
        </div>
        <Link to="/importer" className="pipeline-step__link">Open</Link>
      </div>
    </section>
  );
}
