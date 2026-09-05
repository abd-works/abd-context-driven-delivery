---
name: clean_engineering-model
description: "Provide guidance for creating OO modules, models, and code."
disable-model-invocation: true
---

# clean_engineering-model

Use clean_engineering guidance at `model` fidelity only.

Refer to these skills in order to fill in details from previous fidelities if not present:
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

## model

**Default format:** Python

**Goal:** Define the public seam — what the module exposes, why it is shaped that way, and what callers depend on. **By default the seam is stubbed directly on `Class` itself** — no production behavior yet, no separate interface either, unless one is asked for. Expand `module-context.md` fully. Stub example factories.

- **Default (no interface):** stub the Public API **directly on `Class`** — no production `Class` yet in the sense of behavior, but the type itself already exists as an empty contract. Public properties and operations are **empty interfaces** (Python: `...` / `@property`+empty body; Java: stub methods; other channels: abstract/empty equivalent). No internals until code.
- **Opt-in (interface requested):** create a separate **`I{Class}`** contract instead — only when the user explicitly asks for one at this fidelity, or the module genuinely has multiple layers/implementations that need abstracting apart (see **Interfaces** below for the full trigger). Name it `I{Class}` (e.g. `IShoppingCart`) and keep it and its later extender in the **same file** (`cohesive-file`); there is no production `Class` yet in this case.
- Do not default to `I{Class}` just because this is model fidelity — interfaces are the exception, not the rule.
- When the type will be used from Stories examples, stub **`{Type}ExampleFactory`** (empty, named methods only — plus `I{Type}ExampleFactory` only if that interface was also requested) in a **sibling** `{type}_example_factory.{ext}` file — see **Example factories** below. Complete the factory at **code** fidelity.
- Expand `.context/module-context.md` (seeded at modules) within the **public-seam-only** allowlist: **Purpose**, **Primary use case**, **Rationale**, **Seam**, **Public API**, **Constraint**, **Dependencies**, optional **Extend** / **Mechanism stereotype**. Nested children list the **parent base** under Dependencies; parents list children as nested modules (not as a flat dump of sibling APIs). **Never** add Internal design, Participants, Domain separation, underscore types, or private participants.
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

### Interfaces (`I{Class}`) — optional

A separate interface is **not generated by default.** A type's public seam lives directly on `Class` itself unless a distinct `I{Class}` contract is explicitly introduced. Add `I{Class}` only when:

- **the user asks for it** — at **model** or **code** fidelity, or
- **the module genuinely has multiple layers/implementations behind one seam** that need abstracting apart — e.g. swappable backends, more than one concrete adapter, or a boundary hand-written test fakes must satisfy independently of the production class.

A single concrete implementation with no swapping need does not warrant a separate interface — `Class` itself **is** the seam. Do not add `I{Class}` "for consistency" with a sibling module, and do not default to it just because a fidelity table mentions it.

**Default (no interface):** the public seam is the empty `Class` stub introduced at **model** fidelity (properties/operations as empty contracts directly on `Class`, in its own family file) and filled in at **code** fidelity. The `## code` Phase 1 step of adding `Class(I{Class})` is skipped — there is no interface to implement.

**Opt-in (interface requested):** the public seam is a separate interface named **`I{Class}`**, introduced at **model** fidelity. Properties and operations on the interface are empty contracts — typed signatures with no body.

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
2. **Aggregation** — collector groups members that can outlive it. (`Playlist` aggregates `Song`. A **Repository** aggregates the aggregate it collects — hollow diamond.)
3. **Association** — both sides are independent; they simply use each other. (`Customer` associates with `SupportAgent`.)

Value objects that merely describe (`Money` on a Transaction, `PortingInfo` on a number) are **association** or a property — not composition diamonds. Composition is for parts whose lifecycle the owner controls.

### Interactions (optional at this fidelity)

An **interaction** is one class's operation calling another class's operation — who talks to whom, and about what. You **may** name interactions at **model** fidelity to capture collaboration/sequencing intent early; naming none is equally valid — this is optional, not a required artifact for reaching model.

Reuse the exact notation from `templates/{tool}-sketch.md`'s **Notation**/**Interaction rules** — do not invent a parallel bullet convention:

Do **not** invent `- **Interaction:** calls {Other}.{operation}` or use `- **Invariant:** …` as the sketch/model collaboration marker — that is a parallel symbol set. Sketch/`## model` interactions and notes use `->` / `//` only. Language companion's `- **Invariant:** … <!-- L -->` and Spec's indented `Interaction:` / `Invariant:` labels are different surfaces; neither replaces the sketch notation.

- Nest `-> {collaborator}.{operation}` directly under the calling operation — a real call on a held property, peer, or `super`. No parameters, no body, just the receiver and the operation (or `x = {collaborator}.{attribute}` for a field read).
- Nest `// …` under the same operation for any invariant or sequencing note — including looping/conditionals around the call (e.g. `// once per {item} in {collection}`). Control flow is a `//` note, never folded into the `->` line.
- **`ce-comments-are-for-invariants-and-sequencing-notes-only`** — `//` is must/never/always/before/after notes only. Do not use `//` for descriptive prose, implementation asides, or cross-references.
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
- **`prefer-class-operations`** — Factory and lifecycle operations are **static methods on the class**, not module-level exported functions (`ParadiseMobile.initialize(config)`, not `export async function open()`). Private helpers used from one class belong on that class.
- **`use-explicit-dependencies`** — Pass every collaborator through the **constructor**; never reach for a global or construct a collaborator inside construction.
- **`use-intention-revealing-names`** — Every name — class, property, operation, parameter — answers "why does this exist?" No abbreviations, no single-letter identifiers outside trivial loop indices.
- **`use-consistent-naming`** — One word per concept across the model. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`).
- **`reuse-existing-not-invent-parallel`** — When a class wraps or renders an existing type, name it after that type (`CatalogContextTool` wraps `BaseContextTool`; `CatalogAction` wraps `Action`). Do not invent a parallel domain noun for the same concept — especially not a retired synonym the project has already replaced (Foundry **Practice** → CDD **context tool**). Explicit old→new mapping rows (and overview lines that *state* the replacement) are allowed; live class names, constructor args, and row/registry/toolset labels are not.
- **`reuse-established-notation-not-a-parallel-one`** — Interactions/invariants at sketch and `## model` reuse `->` / `//`; never invent a bold-bullet parallel (`- **Interaction:**` / `- **Invariant:**` as collaboration markers). Language companion `- **Invariant:** <!-- L -->` and Spec indented labels are different surfaces.
- **`ce-comments-are-for-invariants-and-sequencing-notes-only`** — `//` comments are must/never/always/before/after notes only. Not narrative, not “transient value object”, not cross-references between atoms.
- **`do-not-invent-parallel-object-models`** — Do not invent a parallel object model when existing objects already carry the data a new requirement needs. Wrap or extend the live hierarchy instead; do not scrape the same information into a second `*Model` / `*Entry` (or similar) family.

### Example factories (Fake / Isolated / Production **modes**)

When a type is used from **Stories** (helpers / scenario setup), the factory lives in a sibling file, separate from the production family:

| File | Contents |
|---|---|
| `{family}.{ext}` | (optionally **`I{Type}`** +) production **`{Type}`** (+ subtypes / peers) — production family only |
| `{type}_example_factory.{ext}` | (optionally **`I{Type}ExampleFactory`** +) **`{Type}ExampleFactory`** + `examples[{example_key}]` |

`I{Type}` and `I{Type}ExampleFactory` follow the same **opt-in** rule as any other interface (see § Interfaces) — default to the concrete `{Type}` / `{Type}ExampleFactory` directly; only introduce the interface pair when requested or genuinely needed for abstraction. The two decisions are independent: a domain type can skip its interface while its factory keeps one (or vice versa).

Do **not** put factory wiring in the production family file. Do **not** generate `Fake{Type}` / `Isolated{Type}` / `Production{Type}` subclasses — those are **usage modes**, not an inheritance tree.

**PATTERN** (see also `templates/clean_engineering-sketch.md` and templates):

```
# {family}.{ext}                          // production cohesive-file
(I{Type})                                 // public seam — optional, only if requested/needed
{Type}                                    // production — implements I{Type} when one exists

# {type}_example_factory.{ext}            // separate file — always
(I{Type}ExampleFactory)                   // optional, same opt-in rule
{Type}ExampleFactory
  {example_method}(mode)
    // loads examples[{example_key}] -> {Type} (or I{Type} when one exists) (+ peers)
    // Fake | Isolated | Production are modes of how the factory builds the instance
```

| Mode | When used | How it is built |
|---|---|---|
| **Fake** | Stories exploration + early code | Mocking / stub framework creates a fake instance — of `I{Type}` when one exists, otherwise mocking/stubbing `{Type}` directly; feed `examples[{example_key}]` data into it. No hand-written `Fake{Type}` class. |
| **Isolated** | Story-test tier | Construct production `{Type}` with **constructor injection** of mocks/stubs for collaborators. |
| **Production** | Story-test tier | Construct production `{Type}` with **real** collaborators. |

**At model fidelity:** stub `{Type}ExampleFactory` (empty, named methods only), plus `I{Type}ExampleFactory` only if an interface was requested for it. **At code fidelity:** complete `{Type}ExampleFactory` with all three modes.

**Rules**

- **`example-factory-separate-file`** — `{Type}ExampleFactory` (+ `I{Type}ExampleFactory` when one was requested + `examples`) lives in `{type}_example_factory.{ext}`. Production file stays `{Type}` (+ `I{Type}` only when requested) only.
- **`no-fake-isolated-production-subclasses`** — Do not emit `Fake{Type}` / `Isolated{Type}` / `Production{Type}` types that extend `I{Type}` (or `{Type}` when no interface exists). Modes are factory behavior + mocking framework, not inheritance.
- **`example-factory-by-pattern`** — Generate `{Type}ExampleFactory` as a plain class (no shared Loader base). Methods are shaped by `{example_key}` + mode.
- **`examples-multi-type-bundle`** — Store data under `examples[{example_key}]` as a bundle of one or more `{Type}` (or `{IType}` when interfaces exist) payloads. Never `examples[{Type}][{example_key}]` alone when a method needs several types.
- **`fake-via-mocking-framework`** — Fakes come from the project's mock/stub framework, fed example data.
- **`isolated-via-constructor-injection`** — Isolated tier builds `{Type}(...injected mocks/stubs...)`.
- **`stories-consume-via-factory`** — Callers obtain instances from factory methods; they do not invent Fake objects or Fake subclasses.
- **`ensure_example_factory_family`** — Stub `{Type}` and `{Type}ExampleFactory` (plus `I{Type}` / `I{Type}ExampleFactory` only when an interface was requested) before render/transform; render factories into the sibling factory file.

Cart/Product names in sketches are **pattern examples only** — not a product under construction.

---

## Templates

### markdown

---
format: markdown
fidelity: all
---
<!--
  clean_engineering markdown template — unified across all fidelities.

  INTERFACES ARE OPTIONAL (see clean_engineering.md § Interfaces). This template shows
  the `I{ClassName}` form because it is the richer case to document. Default to
  skipping `## I{ClassName}` entirely and starting straight at `## {ClassName}` (empty,
  untagged Md members at model) unless the user asked for an interface, or the module
  genuinely has multiple layers/implementations behind one seam.

  Fidelity tags on section headings (as HTML comments — informational only):
    L  = language companion (prose identity; refined at every stage — not a fidelity)
    Mu = modules        (thin terms, one-way deps, build order; no I{Class} yet)
    Md = model          (I{ClassName} — typed compact block — ONLY when an interface is
                         requested; otherwise model is the empty `## {ClassName}` block)
    C  = code           (fill {ClassName}; public filled, privates filled; drop interactions)

  Class member format (model):
    ------  (six dashes)   constructor / properties separator
    ----    (four dashes)  properties / operations separator
    -       (dash prefix)  private operation
    +       (plus prefix)  public — code fidelity only

  Document structure: H1 = module, H2 = class within that module.
  Interface (I{ClassName}) and implementation ({ClassName}) both sit under the
  same module H1 — interface first, then implementation. No fidelity section
  headers (## Model fidelity / ## Code fidelity) in the output.
  Language companion and modules overview go as prose BEFORE the first H1.

  Subtypes use ## {ChildClass} : {ClassName} notation; deltas only.
  Substitute {ClassName} / {owned_property} / {param} / {Type} / ... when generating.
-->

**Sources / context:** {source_files}                             <!-- L -->

## Language companion                                             <!-- L -->

*{ClassName}* is {intent — what role it plays, what it holds, what it does.
This paragraph IS the class definition. Identity only.}           <!-- L -->

### {class_name_as_a_concept}                                     <!-- L -->

- {bullet: what it holds, what it does, how it relates to *another class*} <!-- L -->
- {as many bullets as the concept warrants}                       <!-- L -->
- **Invariant:** {rule that must always hold — only when one exists} <!-- L -->

### {ChildClass} *is a type of* {ClassName}                       <!-- L -->

- {delta behavior only — what this subtype adds or overrides}     <!-- L -->

## Modules                                                        <!-- Mu -->

Build order: `{first}` → `{second}` → `{third}`

---

# {module_path}                                                   <!-- Mu -->

- **Purpose:** {one paragraph}                                    <!-- Mu -->
- **Seam (terms):** {ClassName}, {ChildClass}, ...                <!-- Mu -->
- **Dependencies (one-way):** {other_module}, ...                 <!-- Mu -->

## I{ClassName}                                                   <!-- Md, optional -->
<!-- Omit this section entirely by default — see note at top of file.
     Include it only when an interface was requested, or the module has
     multiple layers/implementations that need abstracting apart. -->

I{ClassName}({param}: {Type})
------
{owned_property}: {Type}
{plain_property}: {Type}
----
{operation_name}({param}: {Type}): {ReturnType}
{another_operation}(): {ReturnType}

## {ClassName}                                                    <!-- Md -->

+ {ClassName}({param}: {Type})
------
+ << composition >> {owned_property}: {Type}
	Invariant: {constraint sentence.}
+ << aggregation >> {collected_property}: list[{Type}]
+ << association >> {referenced_property}: {Type}
----
+ {operation_name}({param}: {Type}): {ReturnType}
	Invariant: {constraint sentence applicable to this operation.}
	Interaction:
		{variable}: {Type} = {other}.{call}({args})
		return {variable}
- _{private_helper}({param}: {Type}): {Type}

## I{ChildClass}                                                  <!-- Md, optional -->

I{ChildClass}({param}: {Type})
------
----
{delta_operation}({param}: {Type}): {ReturnType}

## {ChildClass}                                                   <!-- Md -->

+ {ChildClass}({param}: {Type})
------
+ {child_specific_property}: {Type}
	Invariant: {constraint sentence.}
----
+ {delta_operation}({param}: {Type}): {ReturnType}

---

# {next_module_path}                                              <!-- Mu -->

- **Purpose:** {one paragraph}
- **Seam (terms):** {ClassName}, ...
- **Dependencies (one-way):** *(none)*

## I{NextClassName}                                               <!-- Md, optional -->

I{NextClassName}({param}: {Type})
------
{property}: {Type}
----
{operation_name}({param}: {Type}): {ReturnType}

## {NextClassName}                                                <!-- Md -->

+ {NextClassName}({param}: {Type})
------
+ {property}: {Type}
----
+ {operation_name}({param}: {Type}): {ReturnType}

---

### Example factory (when Stories-bound) — separate file           <!-- Md -->

Write factories in `{type_slug}_example_factory.md` (or code sibling), **not** in the production family file.
Do not sketch Fake{ClassName} / Isolated{ClassName} / Production{ClassName} types.

## I{ClassName}ExampleFactory                                     <!-- Md, optional — same opt-in rule -->

I{ClassName}ExampleFactory()
------
----
load_{example_key}(mode): I{ClassName}

## {ClassName}ExampleFactory                                      <!-- Md -->

+ {ClassName}ExampleFactory()
------
----
+ load_{example_key}(mode): I{ClassName}
	// examples[{example_key}] multi-type bundle
	// Fake: mock/stub framework + feed examples
	// Isolated: new {ClassName}(ctor-injected mocks/stubs)
	// Production: new {ClassName}(real collaborators)

See examples in `context_tools/clean_engineering/examples/` if needed.