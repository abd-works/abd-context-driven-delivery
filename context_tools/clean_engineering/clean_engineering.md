# Contexts

Deepen OO design from modules toward production code. Each fidelity **adds** artifacts — do not invent detail from a deeper level.

**Progression:** `partition` (action) → **scaffold** → **modules** → **model** → **code**.

| Fidelity | Default format | Produce |
|---|---|---|
| **modules** | markdown (+ drawio) | Independent modules, one-way deps, build order, thin seam terms |
| **model** | python | Empty `I{Class}` contracts + full module-context; stub example factories |
| **code** | python | `Class(I{Class})` typed contracts → full production implementation |

---

## Language companion (not a fidelity)

**Language is not invocable** (`context.fidelity: language` is rejected). Natural-language identity is a **companion** that deepens at every stage through code.

- At each fidelity, refresh prose for terms/classes already named at that stage — definition, story bullets, invariants in plain English.
- Keep identity on the class (or `## ClassName` section); member bullets move onto members as model/code deepen.
- Do **not** invent types, method bodies, relationship kinds, or Public API ahead of the active fidelity.
- Prose lives under `{session}/{module}/` (markdown sections and/or class docstrings) and is updated in place — never a separate language-only generate run.

---

## modules

**Default format:** markdown  
**Diagram format:** `drawio` (modules view — blue boxes, seam-term bullets, one-way dependency arrows; template `templates/modules.drawio`). Language channels (python/java/…) are for **model** and later — not required here.

**Goal:** Refine **modules** purpose, primary use case, rationale, key terms, and relationship to other modules. Strive for **independent modules with one-way dependencies** and an explicit **build order**. Thin class/term identification only — enough to show independence.

A **module** is a named structural boundary that groups closely related classes — and optionally smaller modules — into a single cohesive unit. Modules can be composed of other modules; a highly complex and nested module can be thought of as a sub-system.

- Consume the existing `{session}/.context/{subject}-index.md` and partition chunks if they exist — **do not edit** or wipe partitions.
- Create module structure (`physical-folder` / `nested-physical-folder`) under `{session}/{module}/`.
- When nesting, the **parent module** owns shared base classes/terms (e.g. `powers` owns `Effect`). Specializing children use a path under the parent (`powers/attack`) and depend on the parent — not on siblings. Do **not** invent a `parent/base` submodule (e.g. no `powers/effect`) just to hold shared content; that content belongs on the parent. Diagram: path nesting = containment (children drawn inside the parent box).
- Seed `{session}/{module}/.context/module-context.md` — thin only: **Purpose** (one paragraph), **Seam** (term/class name list), **Dependencies** (one-way module names), optional **Mechanism** note. No full Public API / `I{Class}` yet.
- Write `{session}/.context/module-build-order.md` (or a **Build order** section on the subject index): topological order from one-way deps. **Cycles are a hard fail** — grill until deps are one-way.
- Name terms/classes only enough to show independence. Seed **language companion** prose for those names.
- Seam terms: **one name per concept** (prefer the type name). Do not list singular and plural of the same term (e.g. `Ability` — not `Ability, Abilities`).
- Do not add types, method bodies, or relationship kinds (composition / aggregation / association).

**Dependency rules**

- Dependencies are **one-way** (A → B means B is built before A).
- Children → parent base; never sibling → sibling.
- Partition's thin Deps column is a hint; **modules** owns the formal graph and build order.

### Nested modules

When several independently implementable modules share a **real common seam** (shared types, cost rules, activation protocol), nest them under a **parent module** rather than flattening siblings or duplicating the base into every child.

| Kind | Owns | Example |
|------|------|---------|
| **Parent** | Shared base types/mechanics + optional parent seam; folder that contains children | `powers/` owns shared **Effect** (rank, duration, descriptors, activate protocol) |
| **Child** | One independently implementable specialization | `powers/attack`, `powers/movement`, `powers/extras` |
| **Organisational folder only** | No seam — **not** a module | Do not invent empty parents |

**Rules**

- **`nested-physical-folder`** — Child module path is `{parent}/{child}/` (e.g. `powers/attack/`). Each module that is a real seam owns its own folder and `.context/module-context.md`. Parent shared code lives in the **parent** folder (e.g. types at `powers/`), not copy-pasted into every child — do not invent a `powers/effect` submodule for shared base.
- **`shared-base-before-siblings`** — If children would duplicate the same mechanics, extract **parent-owned base** types first; children depend on that base through a thin interface.
- **`nest-when-shared-else-flat`** — Nest under a parent only when there is shared mechanics or a clear sub-system boundary. Independent top-level concepts (`checks`, `character`) stay flat.
- **`independent-child`** — A child must still pass "implement with siblings stubbed"; it may depend on the **parent base**, not on sibling children.
- **Naming** — Domain nouns; path form `parent/child` in indexes and sketches (`powers/general`, `conflicts/turns`).

Examples: `powers` (owns Effect) + `powers/attack|control|defense|movement|sensory|general` + `powers/extras|flaws`; `conflicts/turns|actions|conditions`; `gear/equipment|headquarters|vehicles`.

### Module rules

- **`high-cohesion`** — Classes inside a module share a common purpose and operate on the same domain concept. Cross-class relationships within the module are strong and semantic, not incidental.
- **`low-coupling`** — Modules depend on each other only through well-defined interfaces. Cross-module dependencies are explicit and minimal — no module reaches into another's internals.
- **`single-boundary`** — Each module is the single source of truth for its domain concept. No other module holds, mutates, or duplicates that concept's state or rules.
- **`named-seam-and-constraint`** — Every module owns a *seam* — the public surface of classes and operations callers depend on — paired with a *constraint* stating what callers must do or must not do at that boundary. A module is described by what it requires of its callers, not only by what it holds.
- **`deep-module`** — The seam stays a short named list of classes and operations with substantial functionality behind it (Ousterhout: small interface, large hidden implementation). If internal helpers leak into the seam, encapsulation is overhead without benefit. Scanner heuristic: at most **40%** of top-level symbols may be public (leading underscore for the rest).
- **`physical-folder`** — Each module occupies its own folder; class files, markdown documents, and other module-level artifacts live in it. Generated code belongs in that folder — not beside the module, not in a flat dump outside it. Nested modules use child folders under the parent (`nested-physical-folder`). Not every folder is a module — chapter or organisational folders may group several modules and must not be treated as one module unless they own `.context/module-context.md`.
- **`cohesive-file`** — Put a **class family** in one file: the primary type, its subtypes, and tightly connected peers that only make sense together (element + collection, small aggregate + its part). Name the file after the family concept (`abilities.py` for `Ability` + `Abilities`). Split into another file only when a type is independently reused across families or the file becomes a grab-bag of unrelated types. Do not default to one class per file. **Exception:** `{Type}ExampleFactory` (and its `I{Type}ExampleFactory` + `examples` data) always live in a **sibling file** — never in the production family file (see **Example factories**).
- **`abstraction-focus`** — Module description names *what* the module does at a higher level than the classes inside it; public verbs are caller-facing, not internal steps or storage layouts.
- **`layer-separation`** — Adjacent modules operate at different abstraction levels; collapse pass-through modules.
- **`complexity-absorption`** — Push configuration and edge-case handling into the module; callers pass intent, not setup flags.
- **`information-hiding`** — Volatile implementation choices must not appear in public signatures or return types.
- **`temporal-independence`** — Every public operation leaves the module in a valid state; avoid order-coupled APIs or document the constraint.
- **`general-purpose-surface`** — Public interface is not hardcoded to one caller's UI/workflow.
- **`errors-out-of-existence`** — Prefer total functions / empty states for routine edges; reserve exceptions for real failures.

### Vanilla module vs. mechanism

A module is either a **vanilla module** or a **mechanism**. Most modules are vanilla — they own one domain concept and are instantiated once.

A **mechanism** is a structural pattern the codebase instantiates more than once. It has:
- **Variation points** — what changes per instance (the parameters of the pattern).
- **Fixed parts** — what the pattern enforces across all instances (the constants of the pattern).

Whether a module is a mechanism is stereotyped lightly at **modules** fidelity and made precise at **model** / **code** (variation points and fixed parts listed in the context file). Mechanism identification is optional and exploratory — pursue it when the pattern is genuinely recurring, not as a default.

At **modules** fidelity, `.context/module-context.md` is thin: Purpose, Seam (term list), Dependencies (one-way), optional Mechanism note — plus `{session}/.context/module-build-order.md`. At **model** fidelity it expands to **Purpose**, **Primary use case**, **Rationale**, **Seam**, **Public API**, and **Dependencies**.

---

## model

**Default format:** Python

**Goal:** Define the public seam as an **`I{Class}`** contract — what the module exposes, why it is shaped that way, and what callers depend on. No production `Class` yet. Expand `module-context.md` fully. Stub example factories.

- Create **`I{Class}` only** for each Public API type — no production `Class` yet. Public properties and operations are **empty interfaces** (Python: `ABC` + `@abstractmethod` / `@property`+`@abstractmethod` + `...`; Java: `interface`; other channels: abstract/empty equivalent). No internals until code.
- Name the contract `I{Class}` (e.g. `IShoppingCart`). Keep `I{Class}` and its later extender in the **same file** (`cohesive-file`).
- When the type will be used from Stories examples, stub **`I{Type}ExampleFactory`** (empty) in a **sibling** `{type}_example_factory.{ext}` file with named methods — see **Example factories** below. Complete the factory at **code** fidelity.
- Expand `.context/module-context.md` (seeded at modules) with **Purpose**, **Primary use case**, **Rationale**, **Seam**, **Public API**, **Dependencies**, optional **Mechanism stereotype**. Nested children list the **parent base** under Dependencies; parents list children as nested modules (not as a flat dump of sibling APIs).
- Ensure code and context for a module belong only in that module's folder (parent owns shared base; child owns specialization).
- Apply **`cohesive-file`**: one file per class family; example factories live in a sibling file (`example-factory-separate-file`).
- Edit to carry forward language-companion identity into **Purpose**; expand primary use case and rationale at this fidelity.
- Edit class docstrings so member bullets move down onto those members; keep everything inside the module folder (`physical-folder`).
- Refresh the **language companion** for terms now on the Public API — still no typed signatures in prose ahead of code.

### What is a class

A class is a named idea that earns its own identity because it has at least one of: **distinct identity**, **state**, **behavior**, **structure**, or **interactions** that cannot be collapsed into a property, instance, or subtype of something else.

A class knows things (**state**), does things (**behavior**), interacts with other things (**interactions**), has (**relationships**) with other things, can be a sub type of other things (**inheritance**), and can implement (**interfaces**) — finally, it maintains the (**invariants**) that constrain it.

### Responsibilities

For each responsibility a class owns, ask: *hold something, do something, or both?* A responsibility may be a property, an operation, or **both** — the class holds state *and* exposes an action that works with it.

### Properties

The class must remember something across calls. Named as a **noun phrase**: *remaining budget*, *active status*, *target character*. A **property** encapsulates information a class exposes to its callers together with the logic required to access or update it. A property may be **typed** — carries a concrete type like `Person`, `int`, or `Car` or can be untyped.

- **`use-property-not-accessor`** — Use `@property` (or the language equivalent) for read-only computed values; do not use `get_` / `set_` method prefixes.

### Operations

The class must do something on demand. Named as a **verb phrase**: *charge card*, *reserve seat*, *compute total*. An **operation** is an action a class performs or a result it computes on demand. Operations may be entirely stateless — depending only on their parameters — or work with the class's own state.

- **`keep-operations-single-responsibility`** — Each operation has one reason to change — pure calculation or orchestration, not both. An operation doing two things reveals either a missing operation or a missing class.
- **`separate-concerns`** — Pure calculation separate from I/O and mutation.
- **`use-clear-operation-parameters`** — Prefer 0–2 parameters. When more configuration is needed, the extra parameters reveal a missing value object — promote them to a new class and pass that instead.

### Interfaces (`I{Class}`)

The public seam of a type is a separate **interface** named **`I{Class}`**, introduced at **model** fidelity. Properties and operations on the interface are empty contracts — typed signatures with no body.

| Channel | `I{Class}` form |
|---------|-----------------|
| Python | `class IClass(ABC):` with `@abstractmethod` / `@property`+`@abstractmethod` |
| Java | `public interface IClass` |
| TypeScript / JavaScript | abstract or empty-method contract equivalent |
| Markdown | `### **I{Class}**` compact block (public members only) |

**Code** adds `Class` that **extends / implements** `I{Class}` in the **same file**. Public members are filled on `Class`; private members are empty interfaces on `Class` only — never added to `I{Class}`. `I{Class}` stays as the stable seam throughout (including for hand-written test fakes). Existing production types may satisfy `I{Class}` informally without a formal extends clause.

Empty vs filled is inferred from the member body (`...` / empty vs real implementation) — no extra abstract flag on the model.


### Inheritance and subtypes

A **base class** defines the common identity, state, and behavior shared by a family of related things. It owns everything that is true of every member of that family — the responsibilities, rules, and collaborations that do not change regardless of which specific variant you are dealing with.

A **subtype** is a class that specialises the base by adding or overriding behavior that only applies to it. The subtype inherits everything the base defines and records **only the delta** — inherited responsibilities are not repeated in the subtype. Use a subtype when the distinction changes what the thing *does*, not just what data it carries.

#### Liskov Substitution rule

**Anywhere the base is used, a subtype must work correctly in its place.** If swapping in a subtype breaks or weakens a rule the base guarantees, the subtype is not a true specialisation — it is a different thing that happens to share some behavior.

### Relationships

Relationship kind and cardinality are added  here. Three kinds, chosen by lifecycle:

1. **Composition** — owner controls the other's lifecycle. (`Order` composes `OrderLine`.)
2. **Aggregation** — collector groups members that can outlive it. (`Playlist` aggregates `Song`.)
3. **Association** — both sides are independent; they simply use each other. (`Customer` associates with `SupportAgent`.)

### Interactions (optional at this fidelity)

An **interaction** is one class's operation calling another class's operation — who talks to whom, and about what. You **may** name interactions at **model** fidelity to capture collaboration/sequencing intent early; naming none is equally valid — this is optional, not a required artifact for reaching model.

Reuse the exact notation from `templates/{tool}-sketch.md`'s **Notation**/**Interaction rules** — do not invent a parallel bullet convention:

Do **not** invent `- **Interaction:** calls {Other}.{operation}` or use `- **Invariant:** …` as the sketch/model collaboration marker — that is a parallel symbol set. Sketch/`## model` interactions and notes use `->` / `//` only. Language companion's `- **Invariant:** … <!-- L -->` and Spec's indented `Interaction:` / `Invariant:` labels are different surfaces; neither replaces the sketch notation.

- Nest `-> {collaborator}.{operation}` directly under the calling operation — a real call on a held property, peer, or `super`. No parameters, no body, just the receiver and the operation (or `x = {collaborator}.{attribute}` for a field read).
- Nest `// …` under the same operation for any invariant or sequencing note — including looping/conditionals around the call (e.g. `// once per {item} in {collection}`). Control flow is a `//` note, never folded into the `->` line.
- `-> ClassName` alone (pointing at a type, not an operation) is not an interaction.
- Naming an interaction here does **not** add a method to `I{Class}` or `Class` — it stays prose (or class-docstring bullet) until **code**.
- At **code** fidelity, any interaction named here becomes a real `@interaction` abstract stub method on `Class` (not on `I{Class}`) — see `## code` Phase 1 — and is dropped once implemented in Phase 2.

### Invariants (optional at this fidelity)

An **invariant** is a rule that must hold for every valid instance of the class, regardless of which operation last ran. You **may** state invariants at **model** fidelity in plain English; leaving them unstated is equally valid — this is optional, not a required artifact for reaching model.

- State a class-level invariant (one that holds regardless of which operation ran, not tied to one call) the same way: a `// …` line, on the class rather than nested under one operation (e.g. `// remaining budget never goes negative`).
- An invariant named here is prose only — it does not gate any method body until **code**.
- At **code** fidelity, any invariant named here gets pinned down as a **comment** (not an enforcement method) on `Class` — see `## code` Phase 1 and Phase 2.

### Class Rules

Before promoting a term to its own class, check whether it fits as a **property** (see *Properties*), an **instance** (see *Instances*), or a **subtype** (see *Inheritance and subtypes*). Only when none of those three fit does something deserve its own class.

- **`keep-classes-single-responsibility`** — Each class has **one reason to change**.
- **`hide-inner-details`** — Expose **behavior** through named methods; callers see what the class does, not how it stores or arranges its information.
- **`eliminate-duplication`** — Repeated logic gets one canonical function.
- **`use-explicit-dependencies`** — Pass every collaborator through the **constructor**; never reach for a global or construct a collaborator inside construction.
- **`use-intention-revealing-names`** — Every name — class, property, operation, parameter — answers "why does this exist?" No abbreviations, no single-letter identifiers outside trivial loop indices.
- **`use-consistent-naming`** — One word per concept across the model. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`).
- **`reuse-existing-not-invent-parallel`** — When a class wraps or renders an existing type, name it after that type (`CatalogContextTool` wraps `BaseContextTool`; `CatalogAction` wraps `Action`). Do not invent a parallel domain noun for the same concept — especially not a retired synonym the project has already replaced (Foundry **Practice** → CDD **context tool**). Explicit old→new mapping rows (and overview lines that *state* the replacement) are allowed; live class names, constructor args, and row/registry/toolset labels are not.
- **`reuse-established-notation-not-a-parallel-one`** — Interactions/invariants at sketch and `## model` reuse `->` / `//`; never invent a bold-bullet parallel (`- **Interaction:**` / `- **Invariant:**` as collaboration markers). Language companion `- **Invariant:** <!-- L -->` and Spec indented labels are different surfaces.
- **`do-not-invent-parallel-object-models`** — Do not invent a parallel object model when existing objects already carry the data a new requirement needs. Wrap or extend the live hierarchy instead; do not scrape the same information into a second `*Model` / `*Entry` (or similar) family.

### Example factories (Fake / Isolated / Production **modes**)

When a type is used from **Stories** (helpers / scenario setup), the factory lives in a sibling file, separate from the production family:

| File | Contents |
|---|---|
| `{family}.{ext}` | **`I{Type}`** + production **`{Type}`** (+ subtypes / peers) — production family only |
| `{type}_example_factory.{ext}` | **`I{Type}ExampleFactory`** + **`{Type}ExampleFactory`** + `examples[{example_key}]` |

Do **not** put factory wiring in the production family file. Do **not** generate `Fake{Type}` / `Isolated{Type}` / `Production{Type}` subclasses — those are **usage modes**, not an inheritance tree.

**PATTERN** (see also `templates/clean_engineering-sketch.md` and templates):

```
# {family}.{ext}                          // production cohesive-file
I{Type}                                   // public seam
{Type}                                    // production — implements I{Type}

# {type}_example_factory.{ext}            // separate file — always
I{Type}ExampleFactory
{Type}ExampleFactory
  {example_method}(mode)
    // loads examples[{example_key}] -> I{Type} (+ peers)
    // Fake | Isolated | Production are modes of how the factory builds I{Type}
```

| Mode | When used | How it is built |
|---|---|---|
| **Fake** | Stories exploration + early code | Mocking / stub framework creates an `I{Type}`; feed `examples[{example_key}]` data into it. No hand-written `Fake{Type}` class. |
| **Isolated** | Story-test tier | Construct production `{Type}` with **constructor injection** of mocks/stubs for collaborators. |
| **Production** | Story-test tier | Construct production `{Type}` with **real** collaborators. |

**At model fidelity:** stub `I{Type}ExampleFactory` (empty, named methods only). **At code fidelity:** complete `{Type}ExampleFactory` with all three modes.

**Rules**

- **`example-factory-separate-file`** — `{Type}ExampleFactory` (+ `I{Type}ExampleFactory` + `examples`) lives in `{type}_example_factory.{ext}`. Production file stays `I{Type}` + `{Type}` only.
- **`no-fake-isolated-production-subclasses`** — Do not emit `Fake{Type}` / `Isolated{Type}` / `Production{Type}` types that extend `I{Type}`. Modes are factory behavior + mocking framework, not inheritance.
- **`example-factory-by-pattern`** — Generate `{Type}ExampleFactory` as a plain class (no shared Loader base). Methods are shaped by `{example_key}` + mode.
- **`examples-multi-type-bundle`** — Store data under `examples[{example_key}]` as a bundle of one or more `{IType}` payloads. Never `examples[{Type}][{example_key}]` alone when a method needs several types.
- **`fake-via-mocking-framework`** — Fakes come from the project's mock/stub framework, fed example data.
- **`isolated-via-constructor-injection`** — Isolated tier builds `{Type}(...injected mocks/stubs...)`.
- **`stories-consume-via-factory`** — Callers obtain instances from factory methods; they do not invent Fake objects or Fake subclasses.
- **`ensure_example_factory_family`** — Stub `I{Type}`, `{Type}`, and `{Type}ExampleFactory` before render/transform; render factories into the sibling factory file.

Cart/Product names in sketches are **pattern examples only** — not a product under construction.

---

## code

**Default format:** Python

**Goal:** Two phases in one fidelity — first lock down the typed contracts (`Class(I{Class})`), then wire the full production implementation. `I{Class}` stays as the stable seam throughout.

A vertical is not at **code** fidelity while it still depends on a mockup / Story Demo shell as the only UI, or on in-memory / fake factories as the only "backend." **Code** means real backend **and** real frontend (UX **code** fidelity) — not greybox + demo domain alone.

### Phase 1 — typed contracts

- Add `Class(I{Class})` (Java: `implements I{Class}`) in the **same file** as `I{Class}`. Do **not** fill out `I{Class}` or add private members to it.
- On `Class`: implement public properties and operations; add private properties/operations as **empty interfaces** (`...` / `@abstractmethod`); add each relationship with its **kind** (composition / aggregation / association) and **cardinality** (e.g. `1..*`, `0..1`); invariants as **comments** (not methods) — formalizing any named at `## model` § Invariants, or newly introduced here.
- Interactions: `@interaction` abstract methods on `Class` (not on `I{Class}`) — formalizing any named at `## model` § Interactions, or newly introduced here.
- Complete `{Type}ExampleFactory` — fill in Fake, Isolated, and Production modes per the **Example factories** pattern in `## model`.
- Add context sections: **Participants**, **Public API**, **Internal design**, **Domain separation**, optional **Mechanism** (variation points / fixed parts).
- Edit the same `.context/module-context.md` — do not create parallel context files.
- Edit so remaining language-companion bullets sit on members; class-level docstring keeps only the opening definition.


State which side **navigates** to the other — direction is explicit.

### Phase 2 — production implementation

- Fill all remaining empty bodies on `Class` (no `...`, no `# TODO` on production ops/props).
- Wire **Production** collaborators — real persistence, services, and cross-module dependencies — not Fake-mode stubs as the shipping path.
- Drop `@interaction` methods — not needed once implemented.
- Keep invariants as **comments**.
- Leave `I{Class}` in place for the public seam and for hand-written test fakes.
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

# Scaffold

A scaffold produces a thin module index — rough public API; obvious mechanisms and their role — including nested modules when a shared base exists (§ Nested modules). Thin dependency notes only; formal one-way graph waits for **modules** generate.

Key rules: `one-way-deps` — dependencies flow one direction only; no cycles; `domain-nouns-only` — module names are domain nouns or paths, never action verbs or `*Model`/`*Runtime` suffixes.

Use **abd-code-research** (not raw file scraping) when the corpus is code.
