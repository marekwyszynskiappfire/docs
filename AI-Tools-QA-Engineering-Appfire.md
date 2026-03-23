# Using AI for test case creation (QA Engineering at Appfire)

*Workflow, prompts, review, and tooling—outline. Expand sections as the playbook matures.*

---

## Table of contents

1. [Purpose and scope](#purpose-and-scope)
2. [Principles](#principles)
3. [Inputs AI needs](#inputs-ai-needs)
4. [End-to-end workflow](#end-to-end-workflow)
5. [Prompting patterns](#prompting-patterns)
6. [Tooling map](#tooling-map)
7. [Worked examples](#worked-examples)
8. [Review criteria](#review-criteria)
9. [Anti-patterns](#anti-patterns)
10. [Metrics](#metrics)
11. [FAQ and troubleshooting](#faq-and-troubleshooting)
12. [Appendix](#appendix)

---

## Purpose and scope

- Audience: QA, QA leads, feature teams collaborating on coverage.
- Definition of “test case” for this document: *(TBD—manual, scripted, BDD, Zephyr/Jira fields, etc.)*
- Out of scope: *(TBD—e.g. full automation strategy; link to other docs.)*

---

## Principles

- Human-in-the-loop: AI produces drafts; humans approve and own quality.
- Quality over volume; traceability to requirements and risks.
- Data and privacy: what may and may not go into external tools. *(TBD—link to policy.)*

---

## Inputs AI needs

- Strong sources: user stories, acceptance criteria, designs, APIs, existing tests.
- How to package context for the model: copy-paste, exports, ticket links, file attachments.
- Minimum context checklist before prompting. *(TBD)*

---

## End-to-end workflow

1. Gather inputs (requirements, constraints, environments).
2. Generate drafts by layer: happy path, negative, edge cases, data variations, non-functional where relevant.
3. QA review using [review criteria](#review-criteria).
4. Publish to test management and link to requirements. *(TBD—tool names/fields.)*
5. Maintain when requirements change (diff-driven refresh prompts). *(TBD)*

---

## Prompting patterns

- Base template: “From this requirement, produce …” *(TBD—paste template.)*
- Variants: exploratory ideas, regression gaps, boundary/pairwise hints.
- Output formats: steps + expected results, Given/When/Then, data tables. *(TBD)*

---

## Tooling map

| Tool / channel | Role in test case creation |
|----------------|----------------------------|
| *(TBD)*        | *(TBD)*                    |

---

## Worked examples

- **Example A:** Story + AC → draft cases. *(TBD)*
- **Example B:** API spec → cases. *(TBD)*
- **Example C:** UI change → cases (including regression angles). *(TBD)*

---

## Review criteria

- Traceability to requirement / risk.
- Clarity, atomic steps, unambiguous expected results.
- Independence, suitable priority/severity, realistic data and environment notes.

---

## Anti-patterns

- Pasting secrets or customer-identifiable data into unapproved tools.
- Bulk-importing unreviewed AI output.
- Duplicating existing coverage without consolidation.
- Vague expected results or missing negative paths.

---

## Metrics

- Time to first useful draft; time in human review.
- Defects found from AI-assisted cases vs baseline (if measured). *(TBD—keep minimal.)*

---

## FAQ and troubleshooting

- Hallucinated steps or wrong product area—how to tighten prompts. *(TBD)*
- Wrong format for test tool—how to constrain output. *(TBD)*

---

## Appendix

### Glossary

- *(TBD)*

### Related documents

- AI usage policy, data handling, test process guidelines. *(TBD—links.)*

### Version history

| Version | Date       | Author        | Changes                    |
|---------|------------|---------------|----------------------------|
| 2.0     | *(TBD)*    | QA Engineering | Restructured as AI test-case playbook outline. |

---

*Maintained by QA Engineering at Appfire. Questions: QA leadership.*
