import { Link, useParams } from "react-router-dom";
import UnitReviewPanel from "../components/UnitReviewPanel";

export default function UnitReviewPage() {
  const { unitId } = useParams<{ unitId: string }>();
  if (!unitId) return <p className="error">Missing Epic.</p>;

  return (
    <>
      <p>
        <Link to="/">Workspace</Link>
      </p>
      <UnitReviewPanel unitId={unitId} />
    </>
  );
}
