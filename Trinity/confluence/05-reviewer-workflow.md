# Reviewer workflow

<!-- Confluence title: Trinity — Reviewer workflow -->

Operator manual (narrative): `Trinity/reviewer/MANUAL.md` (draft for Confluence).

## 1. Configure portfolio

Studio → **Reviewer configs**:

- **portfolio_id** — stable name (e.g. `2026-Q1-okr-fields`).
- **scope** — epic keys, JQL, filter URL, or epic URL.
- **pass_type** — `full_sweep`, `rescan_delta`, or `new_epics_only`.
- **persona_id** — file under `Trinity/personas/`.
- **jira_comment_policy** — `generate_review_before_post` (generate files; Studio can post after triage).

Save → `Trinity/reviewer/config/runs/{portfolio_id}.json`.

## 2. Resolve scope (JQL / filter)

For **epic_keys** / **epic_url**, Studio can **Resolve from scope**.

For **JQL** or **filter URL**:

1. Use **Copy JQL resolve prompt** in Studio, or
2. Set `JIRA_*` in `Trinity/studio/.env` and use REST resolve when available.

Paste resolved keys into **Resolved epic keys** on the config page.

Sample prompt: `Trinity/confluence/samples/jql-resolve-prompt.md`.

## 3. Start gather in Cursor

**Copy Cursor prompt** from Reviewer configs → new Cursor chat.

Sample shape: `Trinity/confluence/samples/reviewer-portfolio-start.md`.

## 4. Artifacts

Under `Trinity/reviewer/runs/<run-id>/`:

```
<EPIC-KEY>/review-payload.json
<EPIC-KEY>/review-report.html   (optional)
portfolio/index.html            (optional portfolio build)
```

**Folder name = epic Jira key** (must match `scope.value` in the JSON).

## 5. Jira comments (Reviewer vs Studio)

| Path | Behaviour |
|------|-----------|
| Reviewer skill | Writes `jira-comment-full.txt` / `short` on disk; copy-paste unless product `auto-post` (rare) |
| Studio | **Jira epic comment** panel after `studio_qa` triage; REST post with confirm + production gate |

Policy: never post `invalid` items; `discuss` only if **send_to_epic** checked in Studio.

## 6. Import to Studio

```bash
./Trinity/studio/scripts/import-run.sh Trinity/reviewer/runs/<run-folder>
```

Next page: **06 — Studio review & Jira comments**.
