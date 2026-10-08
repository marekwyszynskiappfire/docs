import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";

export default function CreatorRunPage() {
  const { runId } = useParams<{ runId: string }>();
  const [tests, setTests] = useState<
    { id: string; draft_id: string; title: string; human_review_status: string }[]
  >([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!runId) return;
    api
      .creatorRun(runId)
      .then((d) => setTests(d.tests))
      .catch((e) => setError(String(e)));
  }, [runId]);

  if (!runId) return null;

  return (
    <>
      <p>
        <Link to="/creator">← Creator</Link>
      </p>
      <h2>{runId}</h2>
      {error && <p className="error">{error}</p>}
      <div className="panel">
        <table className="data">
          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Review</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {tests.map((t) => (
              <tr key={t.id}>
                <td>{t.draft_id}</td>
                <td>{t.title}</td>
                <td>{t.human_review_status}</td>
                <td>
                  <Link to={`/tests/${t.id}`}>Edit</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
