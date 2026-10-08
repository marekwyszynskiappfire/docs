# Trinity operator manual

Hub: [`README.md`](README.md) · Preflight: [`PREFLIGHT.md`](PREFLIGHT.md) · **Testing:** [`TESTING.md`](TESTING.md)

## Reviewer — portfolio interview (Cursor)

The Reviewer skill runs an **interactive interview** before the first gather:

1. **portfolio_id** — stable program name (e.g. `2026-Q4-planning`).
2. **Scope** — Jira filter URL, JQL, epic keys, or epic URL.
3. **Pass type** — full sweep, rescan delta, or new epics only.
4. Product config, persona, child-scan depth, outputs, Creator handoff defaults, Jira comment policy.

Config is saved to `Trinity/reviewer/config/runs/{portfolio_id}.json`.

**Return visits:** the skill asks whether configuration changed; if not, it confirms the same scope and reuses the file.

**Skip interview:** only when the operator explicitly says **skip config** after the prompt.

Run the skill in Cursor with the `trinity-reviewer` skill installed (`./Trinity/scripts/install-trinity-skills.sh`).

## Trinity Studio — Personas & Reviewer configs

```bash
./Trinity/studio/scripts/start.sh
```

| Nav | Purpose |
|-----|---------|
| **Personas** | Edit `Trinity/personas/*.md` (Reviewer tone, automation-first Q# framing) |
| **Reviewer configs** | Create/edit portfolio run JSON (validated against `run-config.schema.json`) |

Private configs: save as `{portfolio_id}-local.json` — pattern `*-local.json` is gitignored under `config/runs/`.

Committed example: [`reviewer/config/runs/example.demo-portfolio.json`](reviewer/config/runs/example.demo-portfolio.json).

Studio does **not** start Reviewer gathers (no MCP from Studio in v1). On **Reviewer configs**, use **Copy Cursor prompt** (includes import command), then paste into Cursor. **List new epics** works for `epic_keys` / `epic_url` scope (JQL/filter URLs must be resolved in Cursor first).

CLI: `python3 Trinity/reviewer/scripts/list_new_epics.py <portfolio_id>`

### JQL / filter scope

1. Set scope kind **jql** or **filter_url** and paste the JQL or filter URL in **scope value**.
2. In **Cursor**, run Jira search (Epics only, paginate to `isLast`).
3. In Studio → **Resolved epic keys** → paste keys → **Save pasted keys** (stored as `resolved_epic_keys` on the config).
4. **List new epics** and **new_epics_only** pass type use `resolved_epic_keys` when present.
5. **Resolve from scope** works inline for **epic_keys** / **epic_url** only.

**Resolve from scope:** inline for epic keys/URL; for JQL/filter — uses `JIRA_*` in `Trinity/studio/.env` when set, otherwise copies a **Cursor MCP prompt** (**Copy JQL resolve prompt**).

## Run page — Creator handoff

After import, open a pipeline run on the Dashboard:

- Toggle **In Creator** per epic (or bulk **Include all** / **Exclude not_fit**).
- **Copy JQL**, **Copy handoff JSON**, or **Download JSON** for Creator planning.
- If the imported folder has a portfolio build, the **portfolio report path** is shown (open `portfolio/index.html` from the repo).

## Send to Creator (approved unit)

1. Open a review unit → complete QA edits → **Approve & export for Creator**.
2. **Send to Creator** copies a markdown prompt with `review_ref` (exported `review-payload.json` under `Trinity/studio/data/exports/`).
3. Disabled when **not_fit** (not suitable for test design).
4. Follow the link to **Creator** after the Cursor run to import `suite-payload.json`.
5. Review **3–5 journey** drafts; edit automation fit / blockers; **approve** or **reject**; check **Fit for Xray import** when approved.
6. On the Creator run page: bulk actions, filter **Ready for Xray import**, **Export for Importer** (JSON under `Trinity/studio/data/exports/creator/`).

## Import Reviewer results

```bash
./Trinity/studio/scripts/import-run.sh Trinity/reviewer/runs/<portfolio-run-folder>
```

Then review units on the Dashboard, approve payloads, export for Creator.

---

Pipeline overview: [`PIPELINE.md`](PIPELINE.md). Step-by-step validation: [`TESTING.md`](TESTING.md).
