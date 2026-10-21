# TC test cleanup reference

## Project

```text
site:        https://appfire.atlassian.net
project.key: TC
project.id:  10356
project url: https://appfire.atlassian.net/jira/software/c/projects/TC
cloud_id:    8e83c2b4-97ae-4335-8a8f-bbdff09d62dd
```

Issue type for cleanup is **Test** (Xray). Related types (Test Execution, Test Plan, Test Set, Precondition) are out of scope unless the user includes them.

Trinity Importer default folder for new Tests is `/Trinity imports` with label `trinity-import`. See `Trinity/importer/config/mappings/appfire-production.json`.

## Candidate search

All Tests in TC:

```jql
project = TC AND issuetype = Test ORDER BY key ASC
```

Trinity imports:

```jql
project = TC AND issuetype = Test AND labels = trinity-import ORDER BY key ASC
```

Unlinked Tests (no Test link to a requirement — verify link type on a sample before relying on this):

```jql
project = TC AND issuetype = Test AND issueLinkType != Test ORDER BY key ASC
```

Narrow by folder in Xray GraphQL (`folder` / `folderPath` on `getTests`), not in JQL, unless a Jira custom field mirrors the path.

## Xray authentication

```http
POST https://xray.cloud.getxray.app/api/v2/authenticate
Content-Type: application/json

{"client_id":"...","client_secret":"..."}
```

Use `XRAY_CLIENT_ID` / `XRAY_CLIENT_SECRET` from `Trinity/studio/.env`.

## Test inventory query

```graphql
query Tests($jql: String!, $limit: Int!, $start: Int!) {
  getTests(jql: $jql, limit: $limit, start: $start) {
    total
    results {
      issueId
      projectId
      folder {
        path
        name
      }
      jira(fields: ["key", "summary", "status", "labels", "priority", "updated", "created"])
      lastModified
    }
  }
}
```

Paginate with `start` until `results` is empty. Cap page size; TC is large.

For execution history on a candidate batch:

```graphql
query TestRuns($jql: String!, $limit: Int!) {
  getTests(jql: $jql, limit: $limit) {
    results {
      issueId
      jira(fields: ["key"])
      testRuns(limit: 5) {
        total
        results {
          status { name }
        }
      }
    }
  }
}
```

Treat `testRuns.total > 0` as execution history. Those keys stay out of **delete** unless the operator lists them.

## Classification

| Bucket | Signal |
|--------|--------|
| keep | Linked to a living requirement, recent runs, or active product folder |
| trinity-import | Label `trinity-import` and/or folder under `/Trinity imports` |
| orphan | No requirement Test link |
| never-executed | `testRuns.total = 0` |
| duplicate | Same summary / steps as another TC key (review before merging) |
| obsolete | Product or feature retired; confirm with owner |
| draft-noise | Placeholder, demo, or clearly incomplete |

Jira workflow status is not evidence of execution.

## Writes (execute only)

Jira Cloud REST v3 on `https://appfire.atlassian.net`:

- Labels / fields: `PUT /rest/api/3/issue/{key}`
- Transitions: `POST /rest/api/3/issue/{key}/transitions`
- Delete: `DELETE /rest/api/3/issue/{key}` — last resort, batched, confirmed keys only
- Saved filters: `POST /rest/api/3/filter` with `sharePermissions: [{ "type": "authenticated" }]` unless the user asks for tighter sharing

Prefer MCP (`user-atlassian_appfire`) for single-issue edits. For bulk filter create, REST with `JIRA_EMAIL` + `JIRA_API_TOKEN` is acceptable (same pattern as `Releases/`).

Record each saved filter as `id` + `https://appfire.atlassian.net/issues/?filter={id}`.
