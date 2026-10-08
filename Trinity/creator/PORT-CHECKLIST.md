# The Creator — port checklist (Part 2)

**Status:** Template — fill during ACTION-PLAN Phase 1  
**Sources:** `The Creator/Input/` only (Marek, Kacper, Karolina & Agata)  
**Rulings:** [`../reviewer/DECISIONS.md`](../reviewer/DECISIONS.md) → Creator resolutions — Part 2  
**Skill WIP:** [`SKILL.md`](SKILL.md)  

## How to use

For each rule or behaviour in the input skills, add one row:

| Source | Location | Rule summary | Disposition | DECISION id | Notes |
|--------|----------|--------------|-------------|-------------|-------|
| Marek | `test-case-creation/SKILL.md` §… | … | carry / generalize / conflict / drop | CR… | |

**Disposition:**

- **carry** — unchanged in merged skill  
- **generalize** — product-agnostic wording or config hook  
- **conflict** — resolved by explicit DECISIONS entry (cite D# / U#)  
- **drop** — out of v1 scope  

## Section checklist (headings to complete)

- [ ] Preconditions and gates (D20, review_ref, K&A scan dependency)  
- [ ] Output contract and identifiers (D21–D24, U-15)  
- [ ] Step and CSV shapes (D22–D23, U-9, U-17)  
- [ ] Prioritisation and quality (D25–D26, T-G3, U-12)  
- [ ] Preconditions placement (D27)  
- [ ] Grounding authority (D28–D29, U-11, A-38)  
- [ ] Effort and release gate (D30)  
- [ ] Duplicates and regeneration (D31, D38)  
- [ ] Automation handoff (D32, P4)  
- [ ] Epic / API scope (D33–D34, U-16)  
- [ ] Limits and roles (D35–D36)  
- [ ] Figma (D37)  
- [ ] Host / invocation (D40)  
- [ ] Import script and submission (T-G1–T-G2, **CR-IMPORTER-01** — Importer not Creator)  
- [ ] Golden library and catalog (T-G7–T-G8, **CR-GOLDEN-01**)  
- [ ] Boundary conditions **BC-01–BC-07** (no invention, minimal suite, YAML/JSONC config + snapshots, HTML Save→MD, MANUAL)  
- [ ] **HTML reports** — [`../shared/html-report-guidelines.md`](../shared/html-report-guidelines.md): suite = Profile A; triage/table = Profile B (`report/` folder, AND filters, dynamic facet counts); cite TC-6504 example  

**Phase 1 exit:** every row has a disposition; one Marek JSON appendix converts to `suite-payload.json` with no data loss.
