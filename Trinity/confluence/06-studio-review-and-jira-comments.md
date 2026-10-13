# Studio review & Jira epic comments

<!-- Confluence title: Trinity — Studio review & Jira epic comments -->

## Dashboard & runs

After import, the Dashboard lists **pipeline runs**. Each run contains **review units** (one per epic folder).

Run page:

- Toggle **In Creator** per epic.
- Bulk exclude `not_fit`.
- Copy **Creator JQL** and handoff JSON.

## Unit page workflow

1. Skim Reviewer payload (questions, findings, gate, context loaded).
2. Set QA decisions per item (valid / discuss / invalid).
3. Check **Include in epic feedback** where PO should see the item.
4. **Save draft** — creates a new payload revision in SQLite.
5. **Approve & export for Creator** — writes export JSON for Creator handoff.
6. **Send to Creator** — copies Cursor prompt (disabled for `not_fit`).

Optional: open **Profile A HTML** link if `review-report.html` exists in the imported folder.

## Jira epic comment panel

Prerequisites: `JIRA_*` in `Trinity/studio/.env`.

| Step | Action |
|------|--------|
| 0 | Credentials chip on panel (green / amber) |
| 1 | Choose variant or **Use recommendation** (smart: studio → full → short rules) |
| 2 | **Refresh preview** (requires saved payload — save after triage changes) |
| 3 | Review warnings (redaction blockers prevent post) |
| 4 | Optional **Unlock wording** for minor edits |
| 5 | Checkbox + type epic **issue key** to confirm |
| 6 | On `appfire.atlassian.net`, type `PRODUCTION` |
| 7 | **Post to Jira** — always a **new** comment; history shown on panel |

### Sandbox test

Use a real **Epic** key in sandbox, not `DEMO-4500`.

### Known limitation

Comments are sent as Jira Cloud **ADF** with wiki markup as plain lines until ADF/wiki parity is completed (internal spike). Preview text matches what operators should expect in Jira.

Spec: `Trinity/studio/JIRA-EPIC-COMMENTS-OUTLINE.md`.

## Download epic feedback

**Download epic feedback** exports JSON of `send_to_epic` items for ad-hoc tooling; prefer the Jira panel for posting.
