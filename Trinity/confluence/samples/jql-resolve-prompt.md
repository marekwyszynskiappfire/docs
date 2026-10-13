# Sample — resolve JQL / filter to epic keys (Cursor)

Use when Reviewer config scope is **jql** or **filter_url** and keys are not yet in `resolved_epic_keys`.

---

Resolve the following Jira scope to a **deduplicated list of Epic issue keys** (issue type Epic only).

**Scope kind:** `{jql | filter_url}`  
**Scope value:**  
```
{paste JQL or filter URL}
```

**Jira site:** `{e.g. https://appfire.atlassian.net}`

### Rules

1. Paginate until `isLast` (or equivalent) — do not truncate.
2. Return keys one per line, sorted ascending.
3. Exclude non-Epic issues.
4. If the filter is not Epic-only, say so and list what you filtered out.

### Output format

```
EPIC-KEY-1
EPIC-KEY-2
```

I will paste these into Trinity Studio → **Reviewer configs** → **Resolved epic keys** → **Save pasted keys**.
