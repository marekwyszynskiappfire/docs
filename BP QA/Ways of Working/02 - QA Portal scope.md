# QA Portal scope

**Audience:** requesters, managers, and the functions QA depends on
**Maintained by:** the QA Team · **Contact:** Marek Wyszyński · **Version:** 2.1 (draft for review) · **Last reviewed:** 2026-09-22
**Reviewed with:** Product Management `[date TBC]` · Engineering `[date TBC]` · Support `[date TBC]`

---

## The rule

> The QA Portal covers **testing the product, and maintaining the assets used to test it**.
>
> It does not cover infrastructure and tooling operations, customer support, or decisions about how the product should behave.
>
> Reactive work enters the portal only under three exceptions: **release-critical testing**, **security findings**, and **verification of absolutely Critical production issues**.

Everything below is an application of that rule. Where a new kind of request is not listed, apply the rule rather than assuming it is excluded — and tell QA, so the list can be extended.

**Why a rule and not just a list:** a list of in-scope items is out of date the moment something new appears, and every gap becomes an argument. The rule settles the cases nobody has thought of yet.

---

## Everything QA does is a portal ticket

Including the work QA raises for itself. The portal is not an inbox for other teams — it is where all of the team's requestable work is visible, whoever put it there.

| Who raises it | Examples |
|---------------|----------|
| **Anyone** | The ten requestable categories below |
| **QA** | Regression after initiative delivery; BugCrowd findings |
| **Engineering or Support** | Verification during an absolutely Critical production incident |

Two exceptions in form, not in principle: **release work** is represented by a single Release ticket, with the detail in linked Jira issues; and **scheduled work** — training, enablement — is tracked outside the queue, because a multi-week commitment does not behave like a ticket.

**All of it, including both exceptions, is visible in the [QA work Jira project](LINK-TBC)** `[LINK TBC]` — automation, BugCrowd, training preparation, release activity and portal counterparts in one place.

### Requestable by anyone

| Category | What it covers |
|----------|----------------|
| **Feature testing** | Validation of a complete feature |
| **Test automation** | Automation for a particular feature |
| **Performance testing** | Manual and automated performance tests after development |
| **Test design** | New test cases needed after a feature is delivered |
| **Shift-left requirement review** | Asynchronous review of requirements before build |
| **JCMA / migration testing** | Data Center to Cloud migration testing |
| **Azure DevOps testing** | Integration testing |
| **Event Manager testing** | Sanity and regression testing for Event Manager |
| **Documentation testing** | Testing of documentation |
| **Training and enablement** | Courses and training for developers and others. **Request it any time** — it is scheduled rather than queued, so it is planned into the next cycle rather than picked up from the queue |

### Raised by QA

| Category | Trigger |
|----------|---------|
| **Regression after initiative delivery** | The **quarterly release schedule** for full regression; the **target date in the epic** for feature-level regression |
| **BugCrowd findings** | Standing intake from the external security platform. Volume is outside anyone's control |

### Release-process work — not requestable

Release blocker testing, the **RUM review**, **Test Regression** and **Sanity** happen because a release is happening. You cannot request them, and while they run no portal requests are worked. They are described on **[How the QA team works](03%20-%20How%20the%20QA%20team%20works.md)**.

### Scheduled work

Training and enablement can be requested at any time, and is normally agreed at **quarter start**. It is tracked **outside the queue** — a three-week course does not occupy a WIP slot. It does consume capacity, so while it runs the team has fewer engineers available to pull tickets, and that is declared at triage.

---

## The three reactive exceptions

The rule excludes reactive work by default. Three things are in anyway, each with a boundary that matters more than the inclusion.

### Release-critical testing

A **release blocker** is a bug of **severity ≥ Medium raised during the Release Testing activity**. Severity alone does not make something a blocker — the activity it came from does.

Severity is assigned under **[rules that already exist](LINK-TBC)** `[LINK TBC]` and are owned outside QA. Those rules define what blocks a release, and **a release does not go out with a blocker open. There is no waiver.**

### Security — BugCrowd

BugCrowd findings stay with the QA team, and QA raises the resulting portal tickets. This is reactive work, and it is in scope deliberately.

### Production issues — verification only

QA does **not** handle production issues, with one exception: **absolutely Critical** issues where QA verification is needed.

**Absolutely Critical** means the **system is down and cannot be used**, or there has been a **major data loss incident**. This is an **incident condition, not the Jira severity field** — a bug marked Critical in Jira is not automatically this. Support assesses it from the customer's report; QA does not argue the label.

**The path is ordered, and QA is third in line:**

1. Support identifies the issue from the customer report.
2. Support contacts Engineering, who provide **L3 support**.
3. If QA verification is needed, **Support or Engineering — usually Engineering — raises a QA Portal ticket**.

**Verification is the only help provided.** QA does not investigate, reproduce on request, triage, or own resolution. Severity labels drift upward under pressure; that activity limit does not.

---

## Out of scope — and why that list is the price

| Not in the portal | Where it goes |
|-------------------|---------------|
| Support tickets | Support |
| DevOps and infrastructure requests | DevOps |
| **CI troubleshooting and CI-related requests** | DevOps. QA triggers release builds and does nothing else on CI |
| Filing bugs on behalf of Engineering, Product Management or Support | The person who found it files it |
| Routine bug verification | The feature team |
| Reproducing a bug for a developer | The developer. A conversation is fine; a reproduction effort is not QA work |
| Support ticket review | Support. QA has **stopped** doing this |
| Creating QA instances for other people | Self-service instructions in Confluence |
| Business and product questions — "how should this work?" | Product Owner or Product Manager |
| Vague environment reports — "something is broken on develop, please check" | Not actionable. Needs a reproducible report against a named environment |
| Kibana, DataStudio, Grafana, dashboards and reporting assets | Engineering |

**This list is not a statement of preference. It is the cost of running QA at four engineers, itemised.**

It is what had to stop for the rest of the model to work. Each entry is work that either ceases or is absorbed by another team, and the page says which. It is meant to be reviewed item by item — see [Service levels and measures](04%20-%20Service%20levels%20and%20measures.md) for the capacity it buys.

### Three of these need explaining

**Bugs.** The line is *on whose behalf*, not whether bugs get filed. QA files every bug it finds, and keeps doing so. QA does not file bugs for other people, does not verify routine fixes, and does not reproduce bugs on request — that stays with the feature team that made the change.

**CI.** QA's only CI activity is **triggering the software builds as part of a release**. Broken agents, pipeline configuration and build infrastructure are DevOps work, and CI requests are not portal requests. **The one thing QA does keep is its own failing automated tests** — that is QA's test code, and fixing it is part of the automation half of the week. The distinction is ownership of the code, not of the tool.

**Observability.** These assets were **built and maintained jointly with Engineering**, and Engineering **continues as sole owner**. QA is withdrawing from shared ownership rather than handing over something unfamiliar. Kibana, DataStudio, Grafana dashboards, BigQuery maintenance and RUM rollout all sit with Engineering, along with any new work. There is little maintenance involved and practically no development.

QA will provide **training or documentation** on these if Engineering needs it — requested through the portal like anything else, which is the clearest example of what the enablement category is for.

**The one exception is the RUM review.** QA still reviews RUM event dashboards before a release to judge whether performance has regressed. That is a release-process activity, not a portal request, and it is described on [How the QA team works](03%20-%20How%20the%20QA%20team%20works.md).

---

## Environments

QA **creates instances for its own work** — the release process, and testing or verifying features. Environment preparation is real effort and it is absorbed into the work it serves, not quoted separately.

QA does **not run an instance-creation service** for other teams. If you need an instance of your own, the self-service instructions are in Confluence.

---

## What QA depends on

The model on these pages relies on work done by three other functions. It is collected here so the dependencies are in one place rather than scattered through pages written for other audiences.

### Product Management

| QA relies on | What happens without it |
|--------------|-------------------------|
| **Every epic defined and in Jira at the start of the quarter** | QA cannot prepare test scenarios or automation placeholders, and the work arrives cold |
| **Clear acceptance criteria**, as part of Definition of Ready | The epic is incomplete against the SDLC definition, and requests against it are deprioritised |
| **A target shipping date in the epic** | QA cannot plan regression, and has no documented basis for prioritising the work |
| **Performance thresholds for RUM**, jointly with Engineering | The module is recorded **not assessable** at the release gate — never as a pass |

### Engineering

| QA relies on | What happens without it |
|--------------|-------------------------|
| **Performance thresholds for RUM**, jointly with Product Management, and the RUM Events portal | As above — the gate cannot be assessed |
| **Fixing regressions** found at the release gate | The gate blocks and the release does not proceed |
| **Ownership of the observability assets**, including any new work | These sit with Engineering; QA has withdrawn and does not pick them back up |
| **Ownership of CI** beyond release build triggering | CI issues have no owner in QA and are routed to DevOps |
| **Requesting incident assistance through the QA Portal** | The work is invisible to the queue and to the capacity model |

### Support

| QA relies on | What happens without it |
|--------------|-------------------------|
| **Assessing incident severity** from the customer report | QA has no basis for the Critical carve-out and would have to judge it, which it will not do |
| **Routing through Engineering L3 first**, then the QA Portal if verification is needed | Work arrives outside the portal and is redirected, costing time during an incident |

---

## Definition of Ready and Definition of Done

These are **epic-level standards shared with Engineering**, not QA Portal rules, and QA does not own them. They are referenced here because QA depends on them; the authoritative version is the **[SDLC definition of a complete epic](LINK-TBC)** `[LINK TBC]`.

**Definition of Ready** — before Engineering and QA can start on an epic:

- a clear description of the functionality
- very clearly defined acceptance criteria
- a statement of what is out of scope of the implementation
- relevant Figma designs

**Definition of Done** — Engineering and QA work is complete *and* the issue has been officially signed off by Product Management.

**QA's part ends before the sign-off.** QA provides the results of testing the implementation, and that is the whole of its contribution. QA does not approve, accept, or gate the epic.

> These words also appear in the portal process, meaning different things. A portal request is **complete** when it has the information on [Requesting QA work](01%20-%20Requesting%20QA%20work.md); a portal ticket is **closed** when testing is finished and the result is recorded. Neither is DoR or DoD.

---

## Standard response when something is out of scope

> This request falls outside QA Portal scope. Redirected to [DevOps / Product Owner / Product Manager / Support].
>
> The scope rule is here: [QA Portal scope]. If you think this is wrong, comment on the ticket or talk to Marek Wyszyński.

The link matters. A redirect that cites a published rule is a team decision; one that does not is one engineer's opinion.

**If you think the rule itself is wrong,** submit it through the QA Portal. Changes are made at the monthly QA Team Retrospective and published with a new version. If it cannot be resolved with QA, it goes to the **Senior QA Manager** and then the **SW Director for BigPicture**.
