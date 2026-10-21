import { useEffect, useState } from "react";
import { api } from "../api";
import PersonaEditor from "../components/PersonaEditor";

type Revision = { id: number; content_sha256: string; created_at: string; excerpt: string };

function conflictFrom(error: unknown): { content: string; content_sha256: string; message: string } | null {
  try {
    const body = JSON.parse(String(error)) as { detail?: { content?: string; content_sha256?: string; message?: string } };
    const detail = body.detail;
    if (detail && typeof detail.content === "string" && typeof detail.content_sha256 === "string") {
      return {
        content: detail.content,
        content_sha256: detail.content_sha256,
        message: detail.message || "This persona changed after you opened it.",
      };
    }
  } catch {
    return null;
  }
  return null;
}

export default function PersonasPage() {
  const [list, setList] = useState<{ id: string; label: string }[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [loaded, setLoaded] = useState("");
  const [draft, setDraft] = useState("");
  const [sha, setSha] = useState("");
  const [editorKey, setEditorKey] = useState(0);
  const [revisions, setRevisions] = useState<Revision[]>([]);
  const [dirty, setDirty] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const loadList = () => {
    api
      .personas()
      .then((items) => {
        setList(items);
        if (items.length && !selected) setSelected(items[0].id);
      })
      .catch((reason) => setError(String(reason)));
  };

  useEffect(() => {
    loadList();
  }, []);

  const applyLoaded = (content: string, contentSha: string) => {
    setLoaded(content);
    setDraft(content);
    setSha(contentSha);
    setDirty(false);
    setEditorKey((value) => value + 1);
  };

  useEffect(() => {
    if (!selected) return;
    setError("");
    setMessage("");
    api
      .persona(selected)
      .then((body) => {
        applyLoaded(body.content, body.content_sha256 || "");
      })
      .catch((reason) => setError(String(reason)));
    api
      .personaRevisions(selected)
      .then(setRevisions)
      .catch(() => setRevisions([]));
  }, [selected]);

  useEffect(() => {
    if (!dirty) return;
    const onLeave = (event: BeforeUnloadEvent) => {
      event.preventDefault();
      event.returnValue = "";
    };
    window.addEventListener("beforeunload", onLeave);
    return () => window.removeEventListener("beforeunload", onLeave);
  }, [dirty]);

  const choose = (id: string) => {
    if (id === selected) return;
    if (dirty && !window.confirm("This persona has unsaved edits. Leave them?")) return;
    setSelected(id);
  };

  const onSave = async () => {
    if (!selected || !sha) {
      setError("Studio needs a restart before persona edits can be saved.");
      return;
    }
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const saved = await api.savePersona(selected, draft, sha);
      applyLoaded(draft, saved.content_sha256);
      setMessage(`Saved ${selected}. The file is still Markdown.`);
      setRevisions(await api.personaRevisions(selected));
      loadList();
    } catch (reason) {
      const conflict = conflictFrom(reason);
      if (conflict) {
        applyLoaded(conflict.content, conflict.content_sha256);
        setError(`${conflict.message} The editor now shows the file on disk.`);
      } else {
        setError(String(reason));
      }
    } finally {
      setBusy(false);
    }
  };

  const onRestore = async (revisionId: number) => {
    if (!selected || !sha) return;
    if (dirty && !window.confirm("Restore replaces the open draft and the file on disk.")) return;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const restored = await api.restorePersona(selected, revisionId, sha);
      applyLoaded(restored.content, restored.content_sha256);
      setMessage("Restored the earlier revision.");
      setRevisions(await api.personaRevisions(selected));
    } catch (reason) {
      const conflict = conflictFrom(reason);
      if (conflict) {
        applyLoaded(conflict.content, conflict.content_sha256);
        setError(`${conflict.message} The editor now shows the file on disk.`);
      } else {
        setError(String(reason));
      }
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <h2>Personas</h2>
      <p className="muted">
        Role prompts for Trinity skills. The saved file stays Markdown in <code>Trinity/personas/</code>. Use the
        toolbar to switch between visual, source, and diff. A save is refused if the file changed after you opened it.
      </p>

      <div className="panel" style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
        <div style={{ flex: "0 0 18rem", maxWidth: "22rem" }}>
          <h3 style={{ marginTop: 0 }}>Personas</h3>
          <ul className="persona-list">
            {list.map((item) => (
              <li key={item.id}>
                <button type="button" className={selected === item.id ? "persona-active" : ""} onClick={() => choose(item.id)}>
                  {item.label}
                </button>
              </li>
            ))}
          </ul>
          {list.length === 0 && <p className="muted">No persona .md files found.</p>}
          {revisions.length > 0 && (
            <>
              <h3>Earlier revisions</h3>
              <ul className="persona-list">
                {revisions.map((revision) => (
                  <li key={revision.id}>
                    <button type="button" onClick={() => onRestore(revision.id)} disabled={busy}>
                      {revision.created_at.slice(0, 16)} · {revision.excerpt || "empty"}
                    </button>
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>

        <div style={{ flex: 1, minWidth: "20rem" }}>
          {selected ? (
            <>
              <strong>{selected}</strong>
              <PersonaEditor
                editorKey={`${selected}:${editorKey}`}
                markdown={loaded}
                onChange={(value) => {
                  setDraft(value);
                  setDirty(value !== loaded);
                }}
              />
              <div className="btn-row">
                <button type="button" onClick={onSave} disabled={busy || !dirty || !sha}>
                  Save to repo
                </button>
                {dirty && <span className="muted">Unsaved changes</span>}
              </div>
            </>
          ) : (
            <p className="muted">Select a persona file.</p>
          )}
        </div>
      </div>

      {message && <p className="muted">{message}</p>}
      {error && <p className="error">{error}</p>}
    </>
  );
}
