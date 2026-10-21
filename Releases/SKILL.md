---
name: jira-release-dashboards
description: Creates or updates Jira release dashboards with one Filter Results gadget per release, using linked defects or release-window JQL. Validates Xray Test Executions have actual test-run activity before including them. Use for major-release, Fast Sanity, regression, or similar multi-release Jira dashboards.
---

# Jira Release Dashboards

Build or update a Jira dashboard from verified release Test Executions.

## Required inputs

Obtain or infer:

1. Jira site and project.
2. Test Execution naming pattern and platform.
3. Number of releases.
4. Bug selection policy:
   - `linked`: Bugs linked to the Test Execution.
   - `release-window`: Bugs with the release affected version created within an
     explicit test window.
5. Dashboard name and sharing policy.

Default to the production site named by the user. Never infer production from a
local `.env`; confirm the host before writes.

## Workflow

### 1. Discover candidates

Search Jira for all matching Test Executions, ordered newest first. Group by
release version. Do not assume Jira status proves execution.

Exclude:

- unrelated platforms;
- templates and duplicates;
- assignment/team copies;
- Test Executions with no Xray test runs;
- versions outside the requested release count.

For naming and duplicate-selection guidance, read
[`reference.md`](reference.md).

### 2. Verify actual Xray execution

When the user requires executed Test Executions, query Xray GraphQL
`getTestExecutions` and inspect `testRuns`.

Include a Test Execution only when:

```text
testRuns.total > 0
AND at least one run status is not TODO / TO DO
```

Report the status distribution. Jira workflow status such as `To Do`, `Done`,
or `In Progress` is not evidence of execution.

If multiple Test Executions for one release have activity:

1. Prefer the canonical platform-specific execution.
2. Prefer the execution whose defects and affected-version instructions belong
   to the release.
3. Ask the user only if the remaining choice changes dashboard results.

### 3. Define bug filters

Use one saved filter per release.

Linked-defect default:

```jql
issue in linkedIssues("TC-123") AND issuetype = Bug
ORDER BY statusCategory ASC, priority DESC, key ASC
```

Release-window mode:

```jql
issuetype = Bug
AND affectedVersion = "preprod/YYYY-MM-DD/X.Y"
AND created >= "YYYY-MM-DD HH:mm"
AND created <= "YYYY-MM-DD"
ORDER BY created ASC
```

Never silently replace linked-defect mode with affected-version mode. Explain
the evidence gap and obtain confirmation unless the user already requested the
broader release-window view.

### 4. Prepare a manifest

Copy [`examples/dashboard-manifest.json`](examples/dashboard-manifest.json) to
a run-specific, gitignored location or `/tmp`. Fill every release entry with
the verified Test Execution key and final JQL.

Do not place API tokens in the manifest.

### 5. Dry-run, then execute

```bash
python3 Releases/scripts/jira_release_dashboard.py MANIFEST.json
python3 Releases/scripts/jira_release_dashboard.py MANIFEST.json --execute
```

The script reads:

- `JIRA_BASE_URL`
- `JIRA_EMAIL`
- `JIRA_API_TOKEN`
- optional `JIRA_INSECURE_SSL=1`

It creates or updates:

- saved filters;
- logged-in-user filter sharing;
- the dashboard;
- one configured Filter Results gadget per release.

The script writes `dashboard-state.json` beside the manifest by default. Keep
that file for reliable updates.

### 6. Verify

After execution:

1. Confirm the dashboard has exactly one gadget per manifest release.
2. Read every gadget `config` property and verify its filter ID.
3. Run each JQL and record the issue count.
4. Confirm filters and dashboard are shared as intended.
5. Provide links to the dashboard, Test Executions, and saved filters.

If browser login is unavailable, REST verification is sufficient; do not ask
for credentials or automate interactive authentication.

## Safety

- Dry-run before Jira writes.
- Reuse exact-name objects or state IDs; do not create duplicates.
- Never delete dashboards, gadgets, or filters automatically.
- Never expose secrets in output, files, shell arguments, or logs.
- Stop on the first partial write failure and report created object IDs.
- Do not modify unrelated dashboards or filters.
