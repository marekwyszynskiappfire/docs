import { useEffect, useState } from "react";
import { api } from "../api";

export default function PersonasPage() {
  const [list, setList] = useState<{ id: string; label: string }[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [content, setContent] = useState("");
  const [dirty, setDirty] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const loadList = () => {
    api
      .personas()
      .then((items) => {
        setList(items);
        if (items.length && !selected) {
          setSelected(items[0].id);
        }
      })
      .catch((e) => setError(String(e)));
  };

  useEffect(() => {
    loadList();
  }, []);

  useEffect(() => {
    if (!selected) return;
    setError("");
    setMessage("");
    api
      .persona(selected)
      .then((d) => {
        setContent(d.content);
        setDirty(false);
      })
      .catch((e) => setError(String(e)));
  }, [selected]);

  const onSave = async () => {
    if (!selected) return;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await api.savePersona(selected, content);
      setDirty(false);
      setMessage(`Saved ${selected} to Trinity/personas/`);
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <h2>Personas</h2>
      <p className="muted">
        Role prompts for Trinity skills. Files live in{" "}
        <code>Trinity/personas/</code> and are referenced from Reviewer run config (
        <code>persona_id</code>).
      </p>

      <div className="panel" style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
        <div style={{ minWidth: "12rem" }}>
          <h3 style={{ marginTop: 0 }}>Files</h3>
          <ul className="persona-list">
            {list.map((p) => (
              <li key={p.id}>
                <button
                  type="button"
                  className={selected === p.id ? "persona-active" : ""}
                  onClick={() => setSelected(p.id)}
                >
                  {p.id}
                </button>
              </li>
            ))}
          </ul>
          {list.length === 0 && <p className="muted">No persona .md files found.</p>}
        </div>

        <div style={{ flex: 1, minWidth: "20rem" }}>
          {selected ? (
            <>
              <label style={{ display: "block" }}>
                <strong>{selected}</strong>
                <textarea
                  className="persona-editor"
                  value={content}
                  onChange={(e) => {
                    setContent(e.target.value);
                    setDirty(true);
                  }}
                  spellCheck={true}
                />
              </label>
              <div className="btn-row">
                <button type="button" onClick={onSave} disabled={busy || !dirty}>
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
