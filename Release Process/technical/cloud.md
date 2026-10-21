# Cloud release — technical

**Status:** extracted from [PPM Release Checklist](https://appfire.atlassian.net/wiki/spaces/PROC/pages/277840434/PPM+Release+Checklist) (v36).  
**Not ownership.** Who runs each job is **Open** — see [process.md](../process.md).  
**Platforms here:** Jira Cloud and Monday.com (Monday historically follows Cloud sanity).

Process, gates, and RACI: [process.md](../process.md). DC: [dc.md](dc.md).

---

## Kickoff (shared with DC until O-06 is decided)

From the checklist **Major release** section.

- Cut the preprod branch — [Creating branches](https://appfire.atlassian.net/wiki/spaces/SOFTWAREPLANT/pages/278832765/Creating+branches), Jenkins [Create PPM Release branch](https://ci.softwareplant.com/job/RELEASE/job/GIT%20-%20create%20PPM%20RELEASE%20branch/).
- Update Fix Version — [Update version in Jira Issues](https://appfire.atlassian.net/wiki/spaces/SOFTWAREPLANT/pages/278835376/Update+version+in+Jira+Issues), Jenkins [Update Version in Jira issues](https://ci.softwareplant.com/job/RELEASE/job/Update%20version%20in%20Jira%20Issues/).
- Add preprod to Affected Version on unresolved issues — [filter 22099](https://appfire.atlassian.net/issues/?filter=22099).
- Point [dashboard 10537](https://appfire.atlassian.net/jira/dashboards/10537) filters at the new preprod: [Next Major Release Open Blocking Bugs (Cloud+Server)](https://appfire.atlassian.net/issues/?filter=13091), [Blocking Bugs - Monday](https://appfire.atlassian.net/issues/?filter=14793).
- Run [Upgrade Tasks Tests](https://ci.softwareplant.com/job/QA/job/UPGRADE_TASKS/job/UPGRADE_TASK_TESTS_JIRA_CLOUD_CRON/).
- Copy/update the table on [2025 Release - log of events](https://appfire.atlassian.net/wiki/spaces/SOFTWAREPLANT/pages/1589608512/2025+Release+-+log+of+events) (Plan / Updated Plan / Event). **TBD:** 2026 log page.
- Point [dashboard 10623](https://appfire.atlassian.net/jira/dashboards/10623) scope filters: [Upcoming Jira Cloud Feature Release Scope](https://appfire.atlassian.net/issues/?filter=14028), [Upcoming Monday Feature Release Scope](https://appfire.atlassian.net/issues/?filter=16221), [Upcoming Jira DC Feature Release Scope](https://appfire.atlassian.net/issues/?filter=14029).

---

## Jira Cloud — test run

### Manual

- Create Manual Test Run as a copy of the previous execution; check for new tests via [filter 17844](https://appfire.atlassian.net/issues/?filter=17844). Example previous: [TC-5752](https://appfire.atlassian.net/projects/TC?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.xpandit.plugins.xray__testing-board&ac.testExecutionKey=TC-5752&ac.testKey=TC-4869#!page=test-executions).
- Environments:
  - Tags: [Create PPM tag v2](https://ci.softwareplant.com/job/RELEASE/job/GIT%20-%20Create%20PPM%20tag%20v2/).
  - Servers: [How to create server from CM](https://appfire.atlassian.net/wiki/spaces/SOFTWAREPLANT/pages/278846658/How+to+create+server+from+CM).
  - Instances: [Creating Jira Cloud instance with data on production](https://appfire.atlassian.net/wiki/spaces/SOFTWAREPLANT/pages/278828153/Creating+Jira+Cloud+instance+with+data+on+production+environment), [Instance migration in Cloud Manager](https://appfire.atlassian.net/wiki/spaces/SOFTWAREPLANT/pages/278830640/Instance+migration+in+Cloud+Manager+production+environment).
  - Name suffix `ampli-dev`. Enable automatic performance/stability collection.
  - RUM during TR: [RUM Events Testing Procedure during Test Runs](https://appfireteam.atlassian.net/wiki/spaces/SPM/pages/97657585744/RUM+Events+Testing+Procedure+during+Test+Runs).
- Start the Test Run; Slack [#bp-status-release-feature](https://appfireworkspace.slack.com/archives/C034T18L5RQ).

### Automatic

- Create Automatic Test Run from previous; check new tests via [filter 22117](https://appfire.atlassian.net/issues/?filter=22117).
- Run [E2E All](https://ci.softwareplant.com/job/PPM/job/E2E/job/ALL/).
- After a successful build, Automation Team fills the Test Run from the build; send results to QA for analysis.

### Legion (process step — not in the old checklist)

After e2e on the release branch: [Legion](https://docs-dts.appfire.net/platform-documentation/qa-coe/legion/). QA selects and executes extra manual tests. See process P3.

---

## Daily during TR and bugfix

- Update [Release Roadmap](https://jira.softwareplant.com/plugins/servlet/softwareplant-bigpicture/#/box/PROG-571/g) daily.
- Slack [#bp-status-release-feature](https://appfireworkspace.slack.com/archives/C034T18L5RQ).
- Monitor [dashboard 10537](https://appfire.atlassian.net/jira/dashboards/10537): assignment, truly blocking, ETA — [PROCESS Monitoring and Bugfixing](https://appfire.atlassian.net/wiki/spaces/PROC/pages/939786568/PROCESS+Monitoring+and+Bugfixing).
- Performance vs previous preprod: [Looker 17bb42d4](https://lookerstudio.google.com/u/0/reporting/17bb42d4-e99e-46df-8690-755d0361572b/page/I4s1D), [Looker 5bd52170](https://lookerstudio.google.com/u/0/reporting/5bd52170-2457-4a9a-82a0-0de2d3f469f0/page/p_lw9dbjio4c).
- After TR, testers deliver RUM per the procedure linked above.

---

## Sanity

Checklist note: *sanity tests are in the automation phase — this step may change soon*.

- Create Sanity Test Run (copy previous or from existing set).
- Environments: [Create PPM tag v2](https://ci.softwareplant.com/job/RELEASE/job/GIT%20-%20Create%20PPM%20tag%20v2/), [CM servers](https://appfire.atlassian.net/wiki/spaces/SOFTWAREPLANT/pages/278846658/How+to+create+server+from+CM), [instance migration](https://appfire.atlassian.net/wiki/spaces/SOFTWAREPLANT/pages/278830640/Instance+migration+in+Cloud+Manager+production+environment).
- Execute; Slack [#bp-status-release-feature](https://appfireworkspace.slack.com/archives/C034T18L5RQ).

Monday and DC historically **start after JC sanity** when a canary candidate exists.

---

## Deployment on production

### Canary

- Build production-sized servers in Cloud Manager in **ap-southeast-2** (match current production count per product). Cap ~200–250 tenants per server per product; confirm with PPM-Infrastructure if unsure. [How to create server from CM](https://appfire.atlassian.net/wiki/spaces/SOFTWAREPLANT/pages/278846658/How+to+create+server+from+CM).
- Migrate tenants from each production server in that region to the new version (canary).
- Set server config Test → Canary; fill **Previous version** (previous production).
- Slack Infra on [bp-cloud-releases](https://appfireworkspace.slack.com/archives/C050AJDDPS5): canary start and planned 100% date.
- Slack Technical Writing on [bp-marketing-release](https://appfireworkspace.slack.com/archives/C06FBDFFKEK): planned 100% date.
- Monitor Kibana; stop migration and call Infra if needed. Status on [#bp-status-release-feature](https://appfireworkspace.slack.com/archives/C034T18L5RQ).
- End of canary, before 100%: [Performance Stability Monitoring Procedure during Canary Release](https://appfireteam.atlassian.net/wiki/spaces/SPM/pages/97619084050/Performance+Stability+Monitoring+Procedure+during+Canary+Release).

QA CoE note (2025): first canary ~10% of tenants, watch logs 2–4 days, then 100% if clean.

### Full release

- Slack Infra on [bp-cloud-releases](https://appfireworkspace.slack.com/archives/C050AJDDPS5); ask for a new empty Marketplace manifest if they are not shipping a changed one.
- Set server config to Production; **Previous version** = previous production. Change **one** server per product.
- [Automatic version release v2](https://ci.softwareplant.com/view/RELEASE/job/RELEASE/job/JIRA%20-%20Automatic%20Version%20Release%20v2/). Then compare:
  - `fixVersion = "release tag" AND status != Done`
  - `fixVersion = "preprod tag" AND status = "Waiting for release"`
  Fix mismatches by hand.
- Marketplace (private App Listing): summary + release notes + docs link. **Do not publish** at this checklist step (Infra/manifest handling may differ — confirm).

---

## After the Cloud release

- [Product Releases](https://appfireteam.atlassian.net/wiki/spaces/CBW/pages/9771069252/Product+Releases) table.
- [Plugin Compatibility](https://appfire.atlassian.net/wiki/spaces/DLPDRAFT/pages/298057849/Plugin+Compatibility) and sync.
- [ONE Releases tab](https://appfire.atlassian.net/projects/ONE?selectedItem=com.atlassian.jira.jira-projects-plugin%3Arelease-page&status=no-filter): release tags, descriptions; archive TR/sanity tags.
- Known internal issues filter:  
  `project = ONE AND affectedVersion = "preprod/date/version" AND status NOT IN (Done, Canceled) AND issuetype = Bug AND "Bug Type[Dropdown]" = Internal`  
  Export keys; save `issuekey in (...)` as “Known internal issues after release x.y”.
- [BP Release bugfixing](https://appfire.atlassian.net/plugins/servlet/ac/eu.softwareplant.bigpicture/bigpicture#!box/REL-4/o/hierarchy?redirect=true), [BigPicture Bugs Per Version](https://appfire.atlassian.net/jira/dashboards/11104).
- End Date on [BigPicture Bugs](https://appfire.atlassian.net/plugins/servlet/ac/eu.softwareplant.bigpicture/bigpicture-mainMenu-overview?project.key=ONE&project.id=10344#!box/PROG-815/g?redirect=true) for issues in this version.

---

## Monday

Same cycle as Cloud; work starts after JC sanity if Monday blockers were fixed in-cycle.

### Sanity

- Create Sanity Monday Test Run (copy previous or from set).
- Environment: https://appfire-band.monday.com/
- Execute and monitor.

### Production

- Build **Monday** servers in Cloud Manager in **us-east-1**, matching current production count. [How to create server from CM](https://appfire.atlassian.net/wiki/spaces/SOFTWAREPLANT/pages/278846658/How+to+create+server+from+CM).
- Migrate tenants (canary).
- [Automatic version release v2](https://ci.softwareplant.com/view/RELEASE/job/RELEASE/job/JIRA%20-%20Automatic%20Version%20Release%20v2/).

**Open (O-07):** keep Monday in this Cloud file or split.

---

## Hotfix {#hotfix}

Only when production is blocked, critical, severe performance, or security. Coordinate with the release owners; Cloud also with Infrastructure. QA tests the fix unless it cannot be verified (technical-only).

- Develop and test on the hotfix branch (fast sanity).
- [Create PPM tag v2](https://ci.softwareplant.com/job/RELEASE/job/GIT%20-%20Create%20PPM%20tag%20v2/).
- Slack [bp-cloud-releases](https://appfireworkspace.slack.com/archives/C050AJDDPS5): time, who builds servers.
- [Automatic version release v2](https://ci.softwareplant.com/view/RELEASE/job/RELEASE/job/JIRA%20-%20Automatic%20Version%20Release%20v2/) + the same Jira filter check as full release.
- ONE Releases tab; Plugin Compatibility; Product Releases table.

### Monday hotfix

- Fix on hotfix branch.
- Monday CM servers in us-east-1; tenant migrate (canary).
- Automatic version release v2.

---

## Custom releases

Off-Marketplace build for a named support case: production + fix (server or jar), individual migrate or jar delivery. Merge the fix into next feature preprod and develop quickly. Avoid standing up a long-lived Cloud server for one tenant.
