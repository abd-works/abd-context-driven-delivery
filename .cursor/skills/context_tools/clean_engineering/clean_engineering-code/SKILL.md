---
name: clean_engineering-code
description: "Provide guidance for creating OO modules, models, and code."
disable-model-invocation: true
---

# clean_engineering-code

Use clean_engineering guidance at `code` fidelity only.

Use higher-level fidelity guidance only when required information is missing. Reference these commands with `@`; do not inline their content:
@clean_engineering-model
@clean_engineering-modules

# Contexts

Deepen OO design from modules toward production code. Each fidelity **adds** artifacts — do not invent detail from a deeper level.

**Progression:** `partition` (action) → **scaffold** → **modules** → **model** → **code**.

| Fidelity | Default format | Produce |
|---|---|---|
| **modules** | markdown (+ drawio) | Independent modules, one-way deps, build order, thin seam terms |
| **model** | python | Empty public seam (on `Class` directly by default, or on a separate `I{Class}` contract **only when interfaces are explicitly requested**) + full module-context; stub example factories |
| **code** | python | Typed contracts (`Class(I{Class})` when an interface was requested, otherwise `Class` directly) → full production implementation |

**Interfaces (`I{Class}`) are optional, not automatic.** See `## model` § Interfaces for the trigger — ask for one, or a genuine multi-layer/multi-implementation seam.

---

## Language companion (not a fidelity)

**Language is not invocable** (`context.fidelity: language` is rejected). Natural-language identity is a **companion** that deepens at every stage through code.

- At each fidelity, refresh prose for terms/classes already named at that stage — definition, story bullets, invariants in plain English.
- Keep identity on the class (or `## ClassName` section); member bullets move onto members as model/code deepen.
- Do **not** invent types, method bodies, relationship kinds, or Public API ahead of the active fidelity.
- Prose lives under `{session}/{module}/` (markdown sections and/or class docstrings) and is updated in place — never a separate language-only generate run.

---

## code

**Default format:** Python

**Goal:** Two phases in one fidelity — first lock down the typed contracts (`Class(I{Class})` when an interface was requested at model, otherwise the `Class` stub already in place from model), then wire the full production implementation. When an `I{Class}` exists it stays as the stable seam throughout; when it does not, `Class` itself is the seam.

A vertical is not at **code** fidelity while it still depends on a mockup / Story Demo shell as the only UI, or on in-memory / fake factories as the only "backend." **Code** means real backend **and** real frontend (UX **code** fidelity) — not greybox + demo domain alone.

### Phase 1 — typed contracts

- **When an `I{Class}` interface was requested at model** (interfaces are optional — see `## model` § Interfaces): add `Class(I{Class})` (Java: `implements I{Class}`) in the **same file** as `I{Class}`. Do **not** fill out `I{Class}` or add private members to it.
- **When no interface was requested:** skip that step — the empty `Class` stub already exists from **model** fidelity in its own family file; continue directly onto it.
- On `Class`: implement public properties and operations; add private properties/operations as **empty interfaces** (`...` / `@abstractmethod`); add each relationship with its **kind** (composition / aggregation / association) and **cardinality** (e.g. `1..*`, `0..1`); invariants as **comments** (not methods) — formalizing any named at `## model` § Invariants, or newly introduced here.
- Interactions: `@interaction` abstract methods on `Class` (never on `I{Class}`, whether or not one exists) — formalizing any named at `## model` § Interactions, or newly introduced here.
- Complete `{Type}ExampleFactory` — fill in Fake, Isolated, and Production modes per the **Example factories** pattern in `## model`.
- Refresh `.context/module-context.md` still **public-seam-only**: ensure **Public API**, **Constraint**, and **Dependencies** match the implemented seam; add **Extend** / **Mechanism** only for public variation points. **Do not** add **Participants**, **Internal design**, **Domain separation**, or any other internals section — those stay in source and sketches, never in module-context.
- Edit the same `.context/module-context.md` — do not create parallel context files.
- Edit so remaining language-companion bullets sit on members; class-level docstring keeps only the opening definition.


State which side **navigates** to the other — direction is explicit.

### Phase 2 — production implementation

- Fill all remaining empty bodies on `Class` (no `...`, no `# TODO` on production ops/props).
- Wire **Production** collaborators — real persistence, services, and cross-module dependencies — not Fake-mode stubs as the shipping path.
- Drop `@interaction` methods — not needed once implemented.
- Keep invariants as **comments**.
- If an `I{Class}` exists, leave it in place for the public seam and for hand-written test fakes; if it does not, `Class` itself remains the seam.
- Add exceptions, named constants, private helpers as needed.
- Edit so language-companion prose stays as the class docstring — implementations sit beneath intent, they do not replace it.
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

## Templates

Call `load_template` directly with your active format and fidelity:

```python
from context_tools.clean_engineering.clean_engineering import CleanEngineering
CleanEngineering(fidelity="code").load_template(format="<your_format>", fidelity="code")
```

See examples in `context_tools/clean_engineering/examples/` if needed.