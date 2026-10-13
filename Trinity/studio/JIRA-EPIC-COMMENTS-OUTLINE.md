# Studio → Jira epic comments (implementation outline)

**Status:** Planned (post-pilot).  
**Goal:** Let operators preview and post Reviewer/Studio feedback to the **Epic issue in Jira** from Trinity Studio, with the same safety model as Reviewer §12 (generate → review → explicit confirm → write).

**Interactive prototype:** open Canvas `jira-epic-comments` in Cursor (stepper + smart variant + unlock-to-edit).

---

## Product decisions (confirmed)

| Topic | Decision | Rationale |
|-------|----------|-----------|
| QA comments in wiki | **Appendix per item** — `_QA note:_` under each Q/F that has `send_to_epic` | Keeps Reviewer bullets intact; PO sees rationale without rewriting agent text |
| Default variant | **Smart** — studio if any `send_to_epic` → else full on first post → else short if ≤3 priority Qs → else full | Reduces wrong-template mistakes; operator can override |
| Preview editing | **Read-only until “Unlock wording”** | Safe default; edits flagged in telemetry; does not mutate `review-payload.json` |
| `invalid` validity | **Never post** | “Do not ask” must not reach Jira |
| `discuss` validity | Post **only if** `send_to_epic` checked | Discuss is internal until explicitly included |
| Re-post | **Always new comment** | Simpler audit; append footer `Follow-up (Studio {timestamp})` + link to previous comment id when history exists |
| Production Jira | **Gate like Importer** — production host requires confirm string + prefer `.env.production` overlay for token | Same muscle memory as Xray execute |
| Redaction | **Warn on preview; block post** if hard patterns remain (align with future IQ-17 block mode) | Safer than warn-only for customer-visible Jira |

**Related:** [`reviewer/SKILL.md` §12](../reviewer/SKILL.md) · [`reviewer/reference.md` § Jira comment templates](../reviewer/reference.md) · [`web/src/types/studio-qa.ts`](web/src/types/studio-qa.ts) · [`CONTRACTS.md`](../CONTRACTS.md) · ADR 0002 (telemetry, redaction posture).

---

## Problem today

| Path | What exists | Gap |
|------|-------------|-----|
| Reviewer | `jira-comment-full.txt` / `jira-comment-short.txt` on disk | No Studio action; manual paste or ad-hoc MCP |
| Studio | `studio_qa` + **Download epic feedback** JSON | No Jira write; operator composes comment manually |

Studio already has Jira REST usage patterns via **Importer** (`JIRA_*` in `.env`, `list_jira_projects`). Reuse auth and host selection — do not invent a second credential model.

---

## Non-goals (v1)

- Posting to **child stories** (Epic only unless we add explicit scope later).
- Auto-post on approve (always **confirm** in UI).
- Replacing Reviewer skill gather or `render_report.py` ownership of template shape.
- Xray / test issue comments (Importer domain).

---

## User stories

1. **Preview** — On epic unit page, see rendered wiki markup for **short** and **full** comment (read-only), reflecting latest saved payload + `studio_qa`.
2. **Post** — After checkbox + typed confirm (and optional production gate), create **one** Jira comment on `review_unit.jira_key`.
3. **Audit** — Record `metric_event` + show last posted comment id/url in Studio.
4. **Regenerate** — If payload changed since last render, “Refresh preview” re-runs renderer logic server-side.

**Studio variant** = items with `send_to_epic` after triage (same as epic-feedback JSON, rendered as wiki).

---

## Recommended product defaults (v1 — proposed lock)

| # | Question | **Recommendation** | Rationale |
|---|----------|-------------------|-----------|
| 1 | Where do QA comments go? | **Appendix per item** — under each included Q/F, add `_QA note:_ {comment}` | Keeps Reviewer-generated wording intact; audit-friendly |
| 2 | Invalid / discuss? | **Invalid:** never post. **Discuss:** post only if `send_to_epic` checked | Matches existing Studio toggles; no surprise PO noise |
| 3 | Re-post? | **Always new Jira comment** | Jira audit trail; link chain in `jira_comment_post` table |
| 4 | Production? | **Mirror Importer** — `production_confirm` + `.env.production` when host is prod | One mental model for writes |
| 5 | Duplicate post? | **Warn** if same `request_hash` within 24h; allow override with second checkbox | Stops double-click accidents |
| 6 | Preview edit? | **Read-only by default**; “Unlock wording” enables textarea; store `edited_from_preview` flag in telemetry | Operator typos without forking renderer |

### Smart variant recommendation (interactive UI)

Server returns `recommendation: { variant, reasons: string[] }` on preview:

```
if any send_to_epic items     → studio
else if no prior jira_comment_post for unit → full
else if open_high_priority_questions ≤ 3  → short
else                                       → full
```

UI shows a **Callout** (like Importer plan warnings) with one-click **Use recommendation**.

**Interactive canvas (spec prototype):** open **`jira-epic-comments`** in Cursor Canvases (stepper + smart variant + unlock-to-edit).

---

## Comment content strategy

### Source of truth

| Layer | Fields |
|-------|--------|
| Reviewer payload | `questions`, `findings`, `report`, `gate`, `context_loaded`, … |
| Studio overlay | `studio_qa.decisions`, `studio_qa.added_questions` |

### Generation (single code path)

**Do not** hand-build wiki strings in TypeScript.

1. **Preferred:** Invoke existing `Trinity/reviewer/scripts/render_report.py` Jira render functions on a **temp or in-memory payload** (subprocess from Studio server, same as CI smoke).
2. **Filter for Studio variant:** Same rules as `buildEpicFeedback()` (`send_to_epic`, skip `invalid`).
3. **QA notes:** For each included item, append wiki line `_QA note:_ {studio_qa.decisions[id].comment}` when non-empty (confirmed: appendix style).
4. **Outputs:** `body_full`, `body_short`, `body_studio` (filtered + QA appendix).

If subprocess is too heavy for v1, **extract** `render_jira_full` / `render_jira_short` into importable Python module under `Trinity/reviewer/` and call from `studio/server/jira_epic_comment.py`.

### Redaction

- Run the same redaction pass Reviewer documents **before** preview and **before** POST (reuse shared helper if one exists; otherwise port minimal pattern list from SKILL § redaction).
- If redaction changes text, surface **warnings** in preview (like Importer preflight).

---

## API (FastAPI router `routers/jira_epic_comments.py`)

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/units/{unit_id}/jira-comment/preview?variant=full\|short\|studio\|auto` | Wiki body + `warnings[]` + `recommendation` + `generated_at` + `payload_revision` |
| `POST` | `/api/units/{unit_id}/jira-comment/post` | Body: `{ variant, confirm_issue_key, dry_run?: false }` |
| `GET` | `/api/units/{unit_id}/jira-comment/history` | Last N posts from SQLite (new table) |

**Post body validation**

- `confirm_issue_key` must equal unit’s `jira_key` (typo guard).
- Optional `production_confirm` string when `JIRA_BASE_URL` matches production host (mirror Importer execute).
- Reject if `JIRA_EMAIL` / `JIRA_API_TOKEN` missing → 503 with link to `.env.example`.

**Jira write**

- REST: `POST /rest/api/3/issue/{issueKey}/comment` with `body` in Atlassian Document Format **or** wiki if site still accepts storage wiki (match what Reviewer templates use today — **wiki markup** in `.txt` files; verify ADF conversion or use `body` wiki renderer endpoint for Cloud).
- Store returned `comment.id` + `self` link in `jira_comment_post` table.

---

## Data model (SQLite)

```sql
CREATE TABLE jira_comment_post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  review_unit_id TEXT NOT NULL,
  jira_issue_key TEXT NOT NULL,
  variant TEXT NOT NULL,           -- full | short | studio
  jira_comment_id TEXT,
  jira_comment_url TEXT,
  payload_revision_id INTEGER,     -- optional FK to review_payload_revision
  posted_by TEXT DEFAULT 'human',
  created_at TEXT NOT NULL,
  request_hash TEXT                -- idempotency: hash(variant + revision + body)
);
```

Idempotency: optional **block duplicate** post within 5 minutes with same hash (warn in UI).

---

## UI (React `UnitReviewPage`) — interactive flow

New collapsible panel **“Jira epic comment”** (default **open** when `send_to_epic` count &gt; 0 or gate needs clarification).

| Step | Interaction | System behavior |
|------|-------------|-----------------|
| **0** | Credentials chip (green/amber) | `GET /api/jira/status` — email set, base URL host, prod vs sandbox |
| **1** | Recommendation callout + **Use recommendation** / manual variant pills | `preview` returns `recommendation` + `reasons[]` |
| **2** | **Included items** list (studio only) — links to Q/F anchors on page; toggling `send_to_epic` triggers debounced preview refresh | Same filter as `buildEpicFeedback` |
| **3** | Preview pane + **Copy** + optional **Unlock wording** | Regenerate disables unlock (reset body from server) |
| **4** | Redaction / empty-variant warnings | Block post on empty studio variant; warn on redaction |
| **5** | Checkboxes + issue key echo + prod confirm field if needed | Enable **Post to Jira** |
| **6** | Success: link to Jira comment + “Posted at …” in history strip | Refresh history |

**Post-save nudge:** if payload revision &gt; last post revision, show banner: “Payload changed since last Jira post — refresh preview.”

Run-level batch post → **v2** (wizard with per-epic confirm list).

---

## Config

| Setting | Location | Notes |
|---------|----------|--------|
| `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_BASE_URL` | `studio/.env` | Same as scope resolve / project list |
| `jira_comment_policy` | Reviewer run config | Studio respects `generate_review_before_post`; never bypass |
| Production gate | env host allowlist | Same list as Importer production confirm |

Optional: `JIRA_COMMENT_VISIBILITY` (internal vs public) if Appfire uses restricted comments — discover via Jira API capabilities in spike.

---

## Telemetry

`metric_event` types:

- `jira_comment_preview`
- `jira_comment_post_success`
- `jira_comment_post_failure` (no issue body in payload — error code only)

Align with [`METRICS.md`](../METRICS.md) and scorecard evidence export.

---

## Implementation phases

### Phase 0 — Spike (0.5–1 day)

- [ ] Confirm Jira Cloud comment API + wiki markup path for `appfire.atlassian.net`.
- [ ] Prove `render_report.py` can run against Studio payload JSON (with `studio_qa`) without breaking `--strict`.
- [ ] Document ADF vs wiki decision in this file.

### Phase 1 — MVP (2–3 days)

- [ ] `jira_epic_comment.py` + preview/post endpoints + migration.
- [ ] Unit page UI: preview + post + history.
- [ ] Pytest: mock Jira HTTP; fixture payload from `fixtures/demo-reviewer-run`.
- [ ] Vitest: preview panel smoke (mock fetch).

### Phase 2 — Studio filter + polish (1–2 days)

- [ ] `studio` variant merges `buildEpicFeedback` rules into rendered comment.
- [ ] Redaction warnings in preview.
- [ ] `GITHUB-BACKLOG` closed; update `GUIDE.md` § “send back to epic”.

### Phase 3 — Optional

- [ ] Batch post per run with per-epic checklist.
- [ ] Cursor prompt export (“post this comment via MCP”) for operators without REST in Studio.
- [ ] Two-way: link Jira comment id back into `studio_qa` metadata.

---

## Open questions (confirm with QA lead)

Defaults above are **recommended**; override via comment on this doc or GitHub issue.

1. ~~Studio QA comments~~ → **Appendix per item** (recommended).
2. ~~Invalid / discuss~~ → **Invalid excluded; discuss if send_to_epic** (recommended).
3. ~~Re-post~~ → **New comment + duplicate warn** (recommended).
4. ~~Sandbox default~~ → **Importer parity for prod** (recommended).
5. **ADF vs wiki** — spike only (Phase 0); renderer today emits wiki.
6. **Internal comment visibility** — spike if Appfire uses Jira restricted comments.

---

## Test plan

| Case | Expect |
|------|--------|
| No credentials | Preview works; post 503 with setup hint |
| Demo fixture `ONE-90001` | Preview generates; post blocked or sandbox-only key |
| `send_to_epic` false on all items | Studio variant empty → 400 with message |
| Redaction tripwire | Warning banner; post still blocked if severity=block (if we add block mode) |
| Wrong `confirm_issue_key` | 400 |

---

## Docs to update when shipped

- [`QUICKSTART.md`](../QUICKSTART.md) — optional step (sandbox only).
- [`GUIDE.md`](../GUIDE.md) — replace “manual paste” with Studio flow.
- [`TESTING.md`](../TESTING.md) — one sandbox post checklist.
- [`parity-matrix.md`](../parity-matrix.md) — Studio vs Reviewer Jira comment parity row.
