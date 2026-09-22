---
format: markdown
fidelity: modules
---
<!--
  clean_engineering markdown template — modules fidelity (`module-context.md`).

  Substitute {Root} / {Concept} / {module_path} / ... when generating.
  This file stops after Purpose, Seam, Dependencies, Constraint. Typed class
  blocks and I{ClassName} live in templates/clean_engineering.md at **model**.

  - `no-subtype-at-modules` — In `module-context.md`, every concept is its own
    heading. Do not write `*is a type of*` or `Child : Parent`. Generalisation
    waits for **model**. An is-a heading here freezes a type hierarchy before
    the object model exists, and the same split has to be rewritten when the
    model names it.
  - `modules-not-model-blocks` — At modules, do not write typed `+ ClassName()` /
    `------` / `+ operation()` dumps. Those wait for **model**. Modules stop at
    Purpose, Seam, Dependencies, Constraint. A dump here is a second object
    model in prose, and the markdown and the later class blocks will disagree.
  - `language-modules-one-section` — `module-context.md` is one `## Language`
    section: opening prose, `###` concepts, build order, then `# {path}` cards.
    Do not add `## Modules`. A second heading splits the same document into two
    fidelities.

  Write human-readable markdown only. Sit a module heading immediately above
  its `- **Purpose:**` block — no blank line between them.
-->

## Language

*{Root}* is {the job a caller hires it for — then what it holds and does.
This paragraph IS the definition. Identity and purpose. Not a decorator or merge.}

### {Concept}

- {why a caller uses this (the outcome), then the mark they type if there is one}
- {as many bullets as the concept warrants}
- **Invariant:** {rule that must always hold — only when one exists}

### {AnotherConcept}

- {why a caller uses this — same shape as any other concept}

Build order: `{first}` → `{second}`

---

# {module_path}
- **Purpose:** {the job a caller hires this module for — not how it is wired}
- **Seam (terms):** {Concept}, {AnotherConcept}, ...
- **Dependencies (one-way):** {other_module}, ...

## Constraint

{what callers must or must not do at this seam — the marks they type, not runtime names they never write}
