# Jira release dashboard reference

## Candidate search

Example Jira Cloud Fast Sanity search:

```jql
project = TC
AND issuetype = "Test Execution"
AND summary ~ "Fast Sanity"
AND summary ~ "Jira Cloud"
ORDER BY created DESC
```

Example manual major-release search:

```jql
project = TC
AND issuetype = "Test Execution"
AND summary ~ "Major Release Test Run Jira Cloud Manual"
ORDER BY created DESC
```

Search broadly enough to find prefixed copies such as `[Sanity]`, then verify
each candidate rather than selecting by Jira status.

## Xray execution check

Authenticate:

```http
POST https://xray.cloud.getxray.app/api/v2/authenticate
Content-Type: application/json

{"client_id":"...","client_secret":"..."}
```

Query:

```graphql
query Executions($jql: String!, $limit: Int!) {
  getTestExecutions(jql: $jql, limit: $limit) {
    total
    results {
      issueId
      jira(fields: ["key", "summary", "status", "created"])
      testRuns(limit: 100) {
        total
        results {
          status { name }
        }
      }
    }
  }
}
```

Treat `PASSED`, `FAILED`, `EXECUTING`, and `ABORTED` as execution activity.
Treat `TODO` and `TO DO` as not executed. An execution with zero test runs is
empty even when its Jira status is Done.

## Canonical execution selection

For duplicate-looking candidates:

1. Eliminate candidates with zero Xray test runs.
2. Match the requested host/platform.
3. Prefer the issue containing environment, commit, and bug-reporting
   instructions.
4. Inspect Defect links.
5. Prefer one canonical execution per release unless the user requests separate
   team or environment gadgets.

Do not rely on prefixes (`[Sanity]`, `[TR]`) or Jira workflow status.

## Jira REST endpoints

The helper uses Jira Cloud REST v3:

- `GET/POST/PUT /rest/api/3/filter`
- `POST /rest/api/3/filter/{id}/permission`
- `GET/POST/PUT /rest/api/3/dashboard`
- `GET/POST/PUT /rest/api/3/dashboard/{id}/gadget`
- `PUT /rest/api/3/dashboard/{id}/items/{itemId}/properties/config`

Filter Results gadget URI:

```text
rest/gadgets/1.0/g/com.atlassian.jira.gadgets:filter-results-gadget/gadgets/filter-results-gadget.xml
```

Configuration:

```json
{
  "filterId": "12345",
  "num": "20",
  "columnNames": "issuetype|issuekey|summary|priority|status|assignee",
  "refresh": "false",
  "isConfigured": "true"
}
```

For authenticated-user sharing, Jira may return `type: "loggedin"` even when
the create request used `type: "authenticated"`.
