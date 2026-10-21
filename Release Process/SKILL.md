---
name: release-process
description: >-
  Develops and maintains the BigPicture Release Process. Use when documenting
  release phases, Cloud vs DC ownership, canary, sanity, Legion in release,
  hotfixes, or splitting process from the PPM Release Checklist.
---

# BigPicture Release Process

This workstream starts from the PPM Release Checklist as a **technical**
reference. Ownership and process after the Cloud/DC split and the August 2026
QA/Release re-organisation are **Draft** until the named personas review them.

## Source policy

- Technical how-tos come from
  [PPM Release Checklist](https://appfire.atlassian.net/wiki/spaces/PROC/pages/277840434/PPM+Release+Checklist)
  and linked job/docs. Do not invent Jenkins jobs, filters, or Slack channels.
- Do not treat checklist checkboxes or historical “Release Manager” wording as
  current RACI. Engineering is taking some release responsibility from QA;
  who does which step is **Open** until confirmed.
- Align with [`BP QA/qa-dev-cooperation.md`](../BP%20QA/qa-dev-cooperation.md)
  where it already mentions release testing, Legion, and go/no-go. That page is
  also Draft; do not promote either document over the other.
- Label Draft / Agreed / Open / TBD. Never invent Confluence, Jira, or tool
  links.

## Document split

| Document | Contains | Does not contain |
|----------|----------|------------------|
| [`process.md`](process.md) | Why, phases, gates, personas, RACI, graph | Job-by-job click paths |
| [`technical/cloud.md`](technical/cloud.md) | Cloud (+ Monday) jobs, environments, canary, marketplace | Org-wide process policy |
| [`technical/dc.md`](technical/dc.md) | DC jobs, jars, marketplace, version bump | Org-wide process policy |

Keep the process page short. Put commands, filters, and Cloud Manager steps in
the technical files.

## Workflow

1. Update `process.md` for decisions and open questions.
2. Keep Cloud and DC technical files as extracted how-tos; mark stale checklist
   items rather than silently dropping them.
3. Record each unresolved ownership item with who must decide.
4. After the personas listed in `process.md` have reviewed the markdown,
   produce one succinct Confluence page **with a process graph**. Do not create
   that page until the user asks and names the space.

## Required coverage

- Quarterly plan in BigPicture and cut-off reminders
- Kickoff (branch cut, notify, Jira Affected Version, automated tests, upgrade tasks)
- Cloud test run, bugfixing, sanity, canary, full release
- DC cadence and path (historically after Cloud sanity, roughly quarterly)
- Monday as Cloud-family (unless reviewers split it out)
- Legion placement
- Go/no-go
- Aftercare
- Hotfix and custom-release exceptions
- Review tracker for all available personas
