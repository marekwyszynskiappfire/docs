# Requirements testability specification

Normative input for The Reviewer. Read this before `checklist.md`.

The default review answers one question: **can QA design pass/fail tests from this requirement without inventing product behavior?** It does not score every documentation habit.

## Basis

The contract below is this team's reading of four public sources. It does not reproduce their text.

| Source | What we take from it |
|--------|----------------------|
| ISO/IEC/IEEE 29148 | A requirement states a needed outcome, is singular, feasible, and verifiable against an observable result. |
| IREB quality criteria | Necessary, unambiguous, consistent, complete enough for the decision at hand, and traceable to a source. |
| INVEST | A story is negotiable and testable; size and independence matter only when they hide the behavior. |
| EARS | When a trigger, an actor, and a response can be named, write the behavior that way. Do not force the syntax onto prose that is already testable. |

A locally reviewed Epic that met this contract named the user outcome, the behavior in scope, who could and could not do it, and an observable success result. Gaps that did not change the pass/fail checks stayed out of the question list. Do not copy customer requirement text into this file or into example findings.

## Minimum testable feature contract

A feature is testable when the gathered sources, taken together, give all of the following. "Not relevant" is allowed only when the requirement truly does not involve that topic; record that judgment in `context_loaded` or a one-line observation, not as a question.

1. **Intent.** Who benefits, and what outcome they get.
2. **Behavior in scope.** The primary flow, plus the boundaries that would make a test pass for the wrong reason.
3. **Actors.** Which roles see different behavior, when more than one role is involved.
4. **Observable success.** A result a tester can see, call, or measure. "Works correctly" is not an outcome.
5. **Material exceptions.** Failure, data, integrations, states, and rollout **only when the feature depends on them**. Do not demand a rollout plan for a change that has none.
6. **One authoritative story.** Sources agree, or the contradiction is named. Linked Confluence and Figma count only after they are read.
7. **No invented behavior.** A tester can write the expected result from the sources. If they would have to guess, the contract is not met.

## Verdict

Set `report.testability_verdict` to exactly one value.

| Verdict | Meaning | Creator |
|---------|---------|---------|
| `testable_now` | The contract holds. Remaining notes do not change expected results. | May draft after the operator approves the review. |
| `testable_with_clarifications` | The main flow is clear. One or more **blocker questions** would change a pass/fail check. | May draft only the flows that do not depend on those questions, after approval. Say which flows are safe in `report.testability_reasons`. |
| `not_testable_yet` | Intent, scope, or the success outcome is missing or contradicted. A suite would invent behavior. | Do not draft. Set `report.qa_planning_fit` to `not_fit`. |

Also set:

| Verdict | `qa_planning_fit` | `classifications.readiness.human_label` |
|---------|-------------------|------------------------------------------|
| `testable_now` | `fit` | Ready for test design |
| `testable_with_clarifications` | `provisional` | Needs clarification before test design |
| `not_testable_yet` | `not_fit` | Cannot plan tests yet |

`gate.status` stays the existing compatibility field. On an Epic, do not raise CRITICAL solely to express "not testable yet"; the verdict and `not_fit` carry that. `blocks_test_generation` remains true only when `severity` is CRITICAL.

Put one to three sentences in `report.testability_reasons`. Each sentence cites a source you read (issue key, page title, or comment). No percentages. No Reviewer voice words from the blocked-phrase list (`gate`, `blocked`, `not ready`).

## Blockers and observations

| Kind | `finding_role` | Becomes a question? | Default cap |
|------|----------------|---------------------|-------------|
| Testability blocker | `blocker` | Yes. One question may clear several blockers through `unblocks`. | No fixed cap. Merge questions that one answer would clear. High questions stay within the existing High cap. |
| Optional observation | `observation` | No. | At most **three**, rolled up. Drop the rest. |

A blocker is a contract miss that changes an expected result, a role, a scope boundary, or an authoritative source. An observation is real but would not change a test you can already write (wording, template shape, a missing out-of-scope line on a change that does not touch a shared system).

Every finding still has a `checklist_ref`. In the default review, cite the row that matches the contract miss. Do not walk the other rows and do not emit a finding per row.

## Default output

Lead the report with:

1. The verdict and `testability_reasons`.
2. Blocker questions, each naming what is missing, who answers, and which blocker it clears.
3. Suggested testing focus: the flows that are safe to draft now. Empty when the verdict is `not_testable_yet`.

Keep the source inventory, child status mix, and classification numbers. They are evidence, not the decision. The HTML renderer may place them after the verdict.

## Deep audit

`review_depth: deep_audit` (or the operator saying "deep audit") walks every row of `checklist.md` and may emit a finding per gap. Use it when the operator asks for a documentation audit, not as the default for "can we test this?".

Gathering does not change with depth. Children, comments, remote links, Confluence bodies plus the nested hop, and Figma or screenshots within the current limits are always read. A short verdict is not a shallow gather.
