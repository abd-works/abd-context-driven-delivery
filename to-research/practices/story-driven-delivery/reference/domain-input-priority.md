# Story-Driven Delivery — Domain Input Priority (shared)

Read domain artifacts **before** writing acceptance criteria, specification scenarios, or acceptance tests. Use exact concept names from these sources — do not paraphrase, abbreviate, or rename.

---

## Priority order

1. **Domain specification** (`domain-specification.md`) — typed classes with invariants and typed relationships. Use first when present.
2. **Domain model** (`domain-model.md`) — concepts with responsibilities and collaborators. **Default source** when no domain specification exists.
3. **Domain language** (`domain-language.md`) — defined terms and key abstractions. Use for term verification and when no model file exists.

Check for `domain.json` in the workspace. If it does not exist and a domain model markdown file is present, produce `domain.json` before running scanners (specification skill).

---

## Per skill

| Skill | Domain use |
| --- | --- |
| `abd-story-acceptance-criteria` | **Domain terms** section per story — every term must exist in a domain source. If a term is missing, **stop — list every missing term and ask how to proceed**. **Never create `domain-terms.md` when domain sources already exist.** Only bootstrap `domain-terms.md` when the engagement has no domain sources at all. See rule **Domain terms must come from the domain model**. |
| `abd-story-specification` | Structural spine for scenarios — concept names in bold, relationships in step language, invariants exercised by scenarios. |
| `abd-story-acceptance-test` | Class names, helper names, and fixtures trace to domain vocabulary and spec Examples tables. |

---

## New vs existing system

Mode detection and evidence sources: [`new-vs-existing-system.md`](./new-vs-existing-system.md).
