
# Contexts

## Modules

A **module** is a named structural boundary that groups closely related classes — and optionally smaller modules — into a single cohesive unit. Modules can be composed of other modules; a highly complex and nested module can be thought of as a sub-system.

### Module rules

- **`high-cohesion`** — Classes inside a module share a common purpose and operate on the same domain concept. Cross-class relationships within the module are strong and semantic, not incidental.
- **`low-coupling`** — Modules depend on each other only through well-defined interfaces. Cross-module dependencies are explicit and minimal — no module reaches into another's internals.
- **`single-boundary`** — Each module is the single source of truth for its domain concept. No other module holds, mutates, or duplicates that concept's state or rules.
- **`named-seam-and-constraint`** — Every module owns a *seam* — the public surface of classes and operations callers depend on — paired with a *constraint* stating what callers must do or must not do at that boundary. A module is described by what it requires of its callers, not only by what it holds.
- **`deep-module`** — The seam stays a short named list of classes and operations with substantial functionality behind it (Ousterhout: small interface, large hidden implementation). If internal helpers leak into the seam, encapsulation is overhead without benefit. Scanner heuristic: at most **40%** of top-level symbols may be public (leading underscore for the rest).
- **`physical-folder`** — Each module occupies its own folder; class files, markdown documents, and other module-level artifacts live in it. Generated code belongs in that folder — not beside the module, not in a flat dump outside it. Not every folder is a module — chapter or organisational folders may group several modules and must not be treated as one module unless they own `.context/module-context.md`.
- **`cohesive-file`** — Put a **class family** in one file: the primary type, its subtypes, and tightly connected peers that only make sense together (element + collection, small aggregate + its part). Name the file after the family concept (`abilities.py` for `Ability` + `Abilities`). Split into another file only when a type is independently reused across families or the file becomes a grab-bag of unrelated types. Do not default to one class per file. **Exception:** `{Type}ExampleFactory` (and its `I{Type}ExampleFactory` + `examples` data) always live in a **sibling file** — never in the production family file (see **Example factories**).
- **`abstraction-focus`** — Module description names *what* the module does at a higher level than the classes inside it; public verbs are caller-facing, not internal steps or storage layouts.
- **`layer-separation`** — Adjacent modules operate at different abstraction levels; collapse pass-through modules.
- **`complexity-absorption`** — Push configuration and edge-case handling into the module; callers pass intent, not setup flags.
- **`information-hiding`** — Volatile implementation choices must not appear in public signatures or return types.
- **`temporal-independence`** — Every public operation leaves the module in a valid state; avoid order-coupled APIs or document the constraint.
- **`general-purpose-surface`** — Public interface is not hardcoded to one caller's UI/workflow.
- **`errors-out-of-existence`** — Prefer total functions / empty states for routine edges; reserve exceptions for real failures.

Further module design rules are declared per fidelity — see `contexts.md` (Add / Extend / Rules for each fidelity).

### Vanilla module vs. mechanism

A module is either a **vanilla module** or a **mechanism**. Most modules are vanilla — they own one domain concept and are instantiated once.

A **mechanism** is a structural pattern the codebase instantiates more than once. It has:
- **Variation points** — what changes per instance (the parameters of the pattern).
- **Fixed parts** — what the pattern enforces across all instances (the constants of the pattern).

Whether a module is a mechanism is determined at modules fidelity (stereotyped with a brief note) and made precise at specification fidelity (variation points and fixed parts listed in the context file). Mechanism identification is optional and exploratory — pursue it when the pattern is genuinely recurring, not as a default.

At modules fidelity, `.context/module-context.md` uses **Purpose**, **Primary use case**, **Rationale**, **Seam**, **Public API**, and **Dependencies** (see `fidelities/modules/contexts.md`).

---

## What is a class

A class is a named idea that earns its own identity because it has at least one of: **distinct identity**, **state**, **behavior**, **structure**, or **interactions** that cannot be collapsed into a property, instance, or subtype of something else.

A class knows things (**state**), does things (**behavior**), interacts with other things (**interactions**), has (**relationships**) with other things, can be a sub type of other things (**inheritance**), and can implement (**interfaces**) — finally, it maintains the (**invariants**) that constrain it.

---

## Responsibilities

For each responsibility a class owns, ask: *hold something, do something, or both?* A responsibility may be a property, an operation, or **both** — the class holds state *and* exposes an action that works with it. 

---

## Properties

The class must remember something across calls. Named as a **noun phrase**: *remaining budget*, *active status*, *target character*. A **property** encapsulates information a class exposes to its callers together with the logic required to access or update it. A property may be **typed** — carries a concrete type like `Person`, `int`, or `Car` or can be untyped.

- **`use-property-not-accessor`** — Use `@property` (or the language equivalent) for read-only computed values; do not use `get_` / `set_` method prefixes.

## Operations

The class must do something on demand. Named as a **verb phrase**: *charge card*, *reserve seat*, *compute total*. An **operation** is an action a class performs or a result it computes on demand. Operations may be entirely stateless — depending only on their parameters — or work with the class's own state.

- **`keep-operations-single-responsibility`** — Each operation has one reason to change — pure calculation or orchestration, not both. An operation doing two things reveals either a missing operation or a missing class.
- **`separate-concerns`** — Pure calculation separate from I/O and mutation. Applies from modules through specification and code.
- **`use-clear-operation-parameters`** — Prefer 0–2 parameters. When more configuration is needed, the extra parameters reveal a missing value object — promote them to a new class and pass that instead.

---

## Relationships

A relationship describes how two classes depend on each other. Every relationship is one of three kinds, decided by a single question about lifecycle and independence:

1. **Composition** — *Does one class own the other's lifecycle?* The other cannot exist without the first. If the owning class is gone, so is the owned one. (`Order` composes `OrderLine`.)
2. **Aggregation** — *Does one class exist to collect or group the other?* The collecting class has no meaningful identity without its members, but the members can outlive it. Remove all members and the collector is empty of purpose. (`Playlist` aggregates `Song`.)
3. **Association** — *Are both sides independent?* Each can exist and be meaningful without the other; they simply know about or use each other. (`Customer` associates with `SupportAgent`.)

A relationship also has **direction**: the class that depends on, uses, or navigates to the other is the navigating end. Be explicit about which side initiates the dependency.

---

## Interfaces (`I{Class}`)

The public seam of a type is a separate **interface** named **`I{Class}`**, introduced at **modules** fidelity. Properties and operations on the interface are empty contracts — treated the same way (typed signatures with no body).

| Channel | `I{Class}` form |
|---------|-----------------|
| Python | `class IClass(ABC):` with `@abstractmethod` / `@property`+`@abstractmethod` |
| Java | `public interface IClass` |
| TypeScript / JavaScript | abstract or empty-method contract equivalent |
| Markdown | `### **I{Class}**` compact block (public members only) |

**Specification** adds `Class` that **extends / implements** `I{Class}` in the **same file**. Public members are filled on `Class`; private members are empty interfaces on `Class` only — never added to `I{Class}`. **Code** fills those remaining empties on `Class`, wires **real** collaborators / persistence / services (not Fake demo mode alone), and leaves `I{Class}` as the stable seam (including for hand-written test fakes). A product vertical at **code** also needs real frontend (UX **code**) — mockup / Story Demo alone is not enough. Existing production types may satisfy `I{Class}` informally without a formal extends clause.

Empty vs filled is inferred from the member body (`...` / empty vs real implementation) — no extra abstract flag on the model.

---

## Example factories (Fake / Isolated / Production **modes**)

When a type is used from **Stories** (helpers / scenario setup), generate:

| File | Contents |
|---|---|
| `{family}.{ext}` | **`I{Type}`** + production **`{Type}`** (+ subtypes / peers) — production family only |
| `{type}_example_factory.{ext}` | **`I{Type}ExampleFactory`** + **`{Type}ExampleFactory`** + `examples[{example_key}]` — Stories / fake / isolated / production **modes** |

Do **not** put the factory (or fake-mode wiring) in the production family file. Do **not** generate `Fake{Type}` / `Isolated{Type}` / `Production{Type}` subclasses — those are **usage modes**, not an inheritance tree.

**PATTERN** (see also `sketch-template.md` and templates):

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
| **Fake** | Stories exploration + specification | Mocking / stub framework creates an `I{Type}`; feed `examples[{example_key}]` data into it. No hand-written `Fake{Type}` class. |
| **Isolated** | Story-test tier | Construct production `{Type}` with **constructor injection** of mocks/stubs (from the mocking framework) for collaborators. |
| **Production** | Story-test tier | Construct production `{Type}` with **real** collaborators. |

**Rules**

- **`example-factory-separate-file`** — `{Type}ExampleFactory` (+ `I{Type}ExampleFactory` + `examples`) lives in `{type}_example_factory.{ext}` beside the production family file. Production file stays `I{Type}` + `{Type}` only.
- **`no-fake-isolated-production-subclasses`** — Do not emit `Fake{Type}` / `Isolated{Type}` / `Production{Type}` types that extend `I{Type}`. Modes are factory behavior + mocking framework, not inheritance.
- **`example-factory-by-pattern`** — Generate `{Type}ExampleFactory` as a plain class (no shared Loader base). Methods are shaped by `{example_key}` + mode (fake / isolated / production).
- **`examples-multi-type-bundle`** — Store data under `examples[{example_key}]` as a bundle of one or more `{IType}` payloads. Never `examples[{Type}][{example_key}]` alone when a method needs several types.
- **`fake-via-mocking-framework`** — Explore/spec fakes come from the project's mock/stub framework, fed example data.
- **`isolated-via-constructor-injection`** — Isolated tier builds `{Type}(...injected mocks/stubs...)`.
- **`stories-consume-via-factory`** — Callers obtain instances from factory methods (Stories helpers call the factory; they do not invent Fake objects or Fake subclasses).
- **`ensure_example_factory_family`** — Stub `I{Type}`, `{Type}`, and `{Type}ExampleFactory` onto a module before render/transform (not Fake/Isolated/Production classes); render factories into the sibling factory file.

Cart/Product names in sketches are **pattern examples only** — not a product under construction.

---

## Inheritance and subtypes

A **base class** defines the common identity, state, and behavior shared by a family of related things. It owns everything that is true of every member of that family — the responsibilities, rules, and collaborations that do not change regardless of which specific variant you are dealing with.

A **subtype** is a class that specialises the base by adding or overriding behavior that only applies to it. The subtype inherits everything the base defines and records **only the delta** — inherited responsibilities are not repeated in the subtype. Use a subtype when the distinction changes what the thing *does*, not just what data it carries.

### Liskov Substitution rule

**Anywhere the base is used, a subtype must work correctly in its place.** If swapping in a subtype breaks or weakens a rule the base guarantees, the subtype is not a true specialisation — it is a different thing that happens to share some behavior.

---

## Class design

Before promoting a term to its own class, check whether it fits as a **property** (see *Properties*), an **instance** (see *Instances*), or a **subtype** (see *Inheritance and subtypes*). Only when none of those three fit does something deserve its own class.

Follow these rules

- **`keep-classes-single-responsibility`** — Each class has **one reason to change**.
- **`hide-inner-details`** — Expose **behavior** through named methods; callers see what the class does, not how it stores or arranges its information.
- **`eliminate-duplication`** — Repeated logic gets one canonical function.
- **`use-explicit-dependencies`** — Pass every collaborator through the **constructor**; never reach for a global or construct a collaborator inside construction.
- **`use-intention-revealing-names`** — Every name — class, property, operation, parameter — answers "why does this exist?" No abbreviations, no single-letter identifiers outside trivial loop indices.
- **`use-consistent-naming`** — One word per concept across the model. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`).


