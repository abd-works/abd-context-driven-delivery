# Contexts — Fidelity

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

**Goal:** Define **modules** in terms of **purpose, primary use case, rationale, and public seam / API** — what the module is for, how callers typically use it, why it is shaped that way, and the classes/operations callers depend on (plus the constraint on that surface). The public seam is an **`I{Class}`** contract; `.context/module-context.md` records that seam.

- Create **`I{Class}` only** for each Public API type — no production `Class` yet. Public properties and operations are **empty interfaces** (Python: `ABC` + `@abstractmethod` / `@property`+`@abstractmethod` + `...`; Java: `interface`; other channels: abstract/empty equivalent). No internals until specification.
- Name the contract `I{Class}` (e.g. `IShoppingCart`). Keep `I{Class}` and its later extender in the **same file** (`cohesive-file`).
- When the type will be used from Stories examples, also declare **`I{Type}ExampleFactory`** (empty) in a **sibling** `{type}_example_factory.{ext}` file — not in the production family file — with named methods that will load `examples[{example_key}]` multi-type bundles — see **Example factories** in `clean_engineering.md`.
- Add `.context/module-context.md` inside the module folder with **Purpose**, **Primary use case**, **Rationale**, **Seam**, **Public API**, **Dependencies**, optional **Mechanism stereotype**.
- Ensure code and context for a module belong only in that module's folder.
- Apply **`cohesive-file`**: one file per class family (primary type + subtypes + tightly connected peers such as element + collection); not one class per file by default. Example factories are **not** part of that cohesive production file (`example-factory-separate-file`).
- Edit to carry forward the language-fidelity identity into **Purpose**; expand primary use case and rationale at this fidelity.
- Edit class docstrings so member bullets move down onto those members; keep everything inside the module folder (`physical-folder`).

---

## specification

**Default format:** Python

**Goal:** Fully typed **contracts**. Keep `I{Class}` as the public/fakeable seam. Add production `Class(I{Class})` in the same file — public members get real bodies; internals stay empty interfaces on `Class` only.

- **Do not fill out `I{Class}`** and **do not add private members to it**. Spec **extends** the interface: `class Class(IClass)` (Java: `implements IClass`).
- On `Class`: implement public properties and operations; add private properties/operations as **empty interfaces** (`...` / `@abstractmethod`); relationship kind + cardinality; invariants as **comments** (not methods).
- Interactions: `@interaction` abstract methods on `Class` (not on `I{Class}`).
- **Example factory (when Stories will use the type):** keep production **`I{Type}`** + **`{Type}`** in the family file; put **`I{Type}ExampleFactory`** + **`{Type}ExampleFactory`** + `examples` in **`{type}_example_factory.{ext}`**. Do **not** generate `Fake{Type}` / `Isolated{Type}` / `Production{Type}` subclasses. Factory methods load **multi-type bundles** keyed by `{example_key}` and build `I{Type}` in one of three **modes**:
  - **Fake** — mocking/stub framework creates `I{Type}`; feed `examples[{example_key}]` (explore/spec default).
  - **Isolated** — `new {Type}(...mocks/stubs via constructor injection...)` for a story-test tier.
  - **Production** — `new {Type}(...real collaborators...)` for a story-test tier.
- Add context sections: **Participants**, **Public API (specification)**, **Internal design**, **Domain separation**, optional **Mechanism** (variation points / fixed parts).
- Edit the same `.context/module-context.md` seeded at modules fidelity — do not create parallel context files.
- Edit so remaining language bullets sit on members; class-level docstring keeps only the opening definition.
- Keep editing inside the existing module folder — do not relocate files.

---

## code

**Default format:** Python

**Goal:** Fully implemented **production** code on `Class` — real collaborators, persistence, and services behind the seam (not Fake/Isolated demo wiring alone). `I{Class}` stays as the separate contract (new production code extends it; existing code may satisfy it informally). Honour the seam with clean-code discipline.

A vertical is not at **code** fidelity while it still depends on a mockup / Story Demo shell as the only UI, or on in-memory / fake factories as the only “backend.” **Code** means real backend (this fidelity) **and** real frontend (UX **code** fidelity) — not greybox + demo domain alone.

- Fill remaining empty bodies on `Class` (no `...`, no `# TODO` on production ops/props).
- Wire **Production** collaborators — real persistence, services, and cross-module dependencies — not Fake-mode stubs as the shipping path.
- Drop `@interaction` methods — not needed in code.
- Keep invariants as **comments**.
- Leave `I{Class}` in place for the public seam and for hand-written test fakes.
- Add exceptions, named constants, private helpers as needed.
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
