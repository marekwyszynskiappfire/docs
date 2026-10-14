import { jiraIssueBrowseUrl } from "../lib/jiraIssueBrowseUrl";

type Props = {
  issueKey: string;
  className?: string;
  host?: string | null;
};

/** External link to the Jira issue (browse URL). */
export default function JiraKeyLink({ issueKey, className, host }: Props) {
  if (!issueKey) return null;
  const href = jiraIssueBrowseUrl(issueKey, host);
  return (
    <a href={href} target="_blank" rel="noopener noreferrer" className={className}>
      {issueKey}
    </a>
  );
}
