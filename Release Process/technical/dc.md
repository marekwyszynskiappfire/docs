# Data Center release — technical

**Status:** extracted from [PPM Release Checklist](https://appfire.atlassian.net/wiki/spaces/PROC/pages/277840434/PPM+Release+Checklist) (v36).  
**Not ownership.** Who runs each job is **Open** — see [process.md](../process.md).

Process, gates, and RACI: [process.md](../process.md). Cloud: [cloud.md](cloud.md).

Historically DC ships **about once a quarter** (roughly the second month). Work
starts **after Jira Cloud sanity**, when a canary-candidate Cloud version
exists. In-cycle DC blockers are fixed by Development during the Cloud cycle.

**Open (O-06):** independent DC train vs this coupling to Cloud sanity.

---

## Kickoff (shared with Cloud until O-06 is decided)

Same Major release jobs as Cloud: preprod branch, Fix Version, Affected
Version, dashboards 10537 and 10623 (including [Upcoming Jira DC Feature Release Scope](https://appfire.atlassian.net/issues/?filter=14029)),
upgrade-task tests, release event log. Details: [cloud.md](cloud.md#kickoff-shared-with-dc-until-o-06-is-decided).

---

## Sanity Test Run

- Create Sanity DC Test Run (copy previous or from existing set).
- Environment: [JIRA_DC_START](https://ci.softwareplant.com/job/QA/job/PERSONAL/job/_JIRA_DC/job/JIRA_DC_START/).
- Start and monitor the Test Run.

---

## Deployment on production

- Build jars: [RELEASE_SERVER_GITHUB](https://ci.softwareplant.com/job/RELEASE/job/RELEASE_SERVER_GITHUB/).
- Atlassian Marketplace vendor account: **new private app versions** for BP, BG, BPE, BT.
  - Required fields, Release Summary, Release Notes, Compatibility.
  - **Publish** all apps.
- [Automatic version release v2](https://ci.softwareplant.com/view/RELEASE/job/RELEASE/job/JIRA%20-%20Automatic%20Version%20Release%20v2/). Then compare:
  - `fixVersion = "release tag" AND status != Done`
  - `fixVersion = "preprod tag" AND status = "Waiting for release"`
  Fix mismatches by hand.

---

## After the DC release

- [Plugin Compatibility](https://appfire.atlassian.net/wiki/spaces/DLPDRAFT/pages/298057849/Plugin+Compatibility) and sync.
- [ONE Releases tab](https://appfire.atlassian.net/projects/ONE?selectedItem=com.atlassian.jira.jira-projects-plugin%3Arelease-page&status=no-filter): tags and descriptions.
- Only if **not** already done with the Cloud ship of this version:
  - [Product Releases](https://appfireteam.atlassian.net/wiki/spaces/CBW/pages/9771069252/Product+Releases)
  - [BP Release bugfixing](https://appfire.atlassian.net/plugins/servlet/ac/eu.softwareplant.bigpicture/bigpicture#!box/REL-4/o/hierarchy?redirect=true)
  - [BigPicture Bugs Per Version](https://appfire.atlassian.net/jira/dashboards/11104)
  - End Date on [BigPicture Bugs](https://appfire.atlassian.net/plugins/servlet/ac/eu.softwareplant.bigpicture/bigpicture-mainMenu-overview?project.key=ONE&project.id=10344#!box/PROG-815/g?redirect=true)
- Bump version on **develop**: [GIT-Update_PPM_version](https://ci.softwareplant.com/job/RELEASE/job/GIT-Update_PPM_version/) — [Update PPM version after DC release](https://appfire.atlassian.net/wiki/spaces/SOFTWAREPLANT/pages/2893350017/Update+PPM+version+after+DC+release).

---

## Hotfix {#hotfix}

Same entry bar as Cloud: blocking/critical, severe performance, or security.
Fast sanity of the fix (unless unverifiable technical-only).

- Develop and test on the hotfix branch.
- Bump version on the hotfix branch: Jenkins [Update version in Jira Issues](https://ci.softwareplant.com/job/RELEASE/job/Update%20version%20in%20Jira%20Issues/).
- Jars: [RELEASE_SERVER_GITHUB](https://ci.softwareplant.com/job/RELEASE/job/RELEASE_SERVER_GITHUB/).
- Marketplace: private versions for BP, BG, BPE, BT; fill fields; **publish**.
- [Automatic version release v2](https://ci.softwareplant.com/view/RELEASE/job/RELEASE/job/JIRA%20-%20Automatic%20Version%20Release%20v2/) + the same Jira filter check.
- ONE Releases tab; Plugin Compatibility; Product Releases table.

---

## Custom releases

Same rule as Cloud: rare off-Marketplace jar (customer production version +
fix). Land the fix in the next feature preprod and develop as soon as possible.
Custom jars should stay rare.
