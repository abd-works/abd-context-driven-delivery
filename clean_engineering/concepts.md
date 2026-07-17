# Concepts — Fidelity

This skill can operate at **multiple levels of fidelity**. Starting coarse and deepening toward production code. Each level **adds** new artifacts and **extends** what the previous level already produced.
When working at a fidelity level do no fill in details from a more detailed level of fidelity. They are presented in order of least detail to most detailed below.

---

## language

**Default format:** markdown

**Goal:** Modules, classes and behavior described using natural language.

- Create module structure (`physical-folder`): one folder per module; organisational parents are not modules.
- Add module description: role, boundary, collaborators, seam, constraint.
- Create class identity: one class-level docstring (or `## ClassName` section) with definition, story bullets, invariants in plain English.
- Edit so the class docstring holds **identity** only; sentences about a property, operation, or relationship belong on that member later.
- Do not add types, method bodies, or relationship kinds (composition / aggregation / association).

---

## modules

**Default format:** Python

**Goal:** Define **modules** in terms of their **public seam / API** — the classes, operations, and properties callers depend on (plus the constraint on how they may use that surface). Class stubs and `.context/module-context.md` record that seam.
- Create class stubs for Public API classes,: typed properties, operation signatures with `...` bodies, relationship targets (no kinds yet). No internals until specification
- Add `.context/module-context.md` inside the module folder with 1–2 paragraphs defining **Seam**, **Public API**, **Dependencies**, optional **Mechanism stereotype**.
- Ensure code and context for a module belong only in that module's folder.
- Apply **`cohesive-file`**: one file per class family (primary type + subtypes + tightly connected peers such as element + collection); not one class per file by default.
- Edit to carry forward the language-fidelity opening paragraph as the module identity statement.
- Edit class docstrings so member bullets move down onto those members; keep everything inside the module folder (`physical-folder`).

---

## specification

**Default format:** Python

**Goal:** Fully typed **contracts**. Module internals become explicit alongside the seam. Bodies of classes operations defined, internal functions are left blank `...`.

- Add full typed signatures (public and private), relationship kind + cardinality, invariants.
- Add context sections: **Participants**, **Public API (specification)**, **Internal design**, **Domain separation**, optional **Mechanism** (variation points / fixed parts).
- Define interactions of public operations — what each calls (external vs internal). Internal methods and helper objects are identified that way but not implemented. 
- Edit the same `.context/module-context.md` seeded at modules fidelity — do not create parallel context files.
- Edit so remaining language bullets sit on members; class-level docstring keeps only the opening definition.
- Keep editing inside the existing module folder — do not relocate files.
---

## code

**Default format:** Python

**Goal:** Fully implemented production code. Every body filled; honour specification contracts with clean-code discipline.

- Create real implementations (no `...`, no `# TODO`).
- Add  exceptions, named constants, private helpers as needed.
- Edit so language prose stays as the class docstring — implementations sit beneath intent, they do not replace it.
- Edit so the implemented public surface matches the seam already designed — a short caller-facing API with real behaviour behind it, still living in the module folder.

### Rules

**Operations**

- **`keep-operations-small-focused`** — Under **20 lines**; extract named helpers.
- **`simplify-control-flow`** — Guard clauses; max nesting depth as enforced by scanners.
- **`maintain-abstraction-levels`** — One level at a time; no raw I/O mixed into orchestration names.

**Naming / context**

- **`provide-meaningful-context`** — Named constants for magic numbers and unexplained literals.

**Errors / comments**

- **`use-exceptions-properly`** — Domain exceptions that name the failure.
- **`never-swallow-exceptions`** — Log and re-raise or convert; never bare swallow.
- **`stop-writing-useless-comments`** — Comments explain **why**, not **what**.
