const DEFAULT_HOST = "appfire.atlassian.net";

/** Build https://{host}/browse/{KEY} for Jira issue keys shown in Studio. */
export function jiraIssueBrowseUrl(issueKey: string, host?: string | null): string {
  const h = (host || DEFAULT_HOST).replace(/^https?:\/\//, "").replace(/\/$/, "");
  return `https://${h}/browse/${issueKey}`;
}
