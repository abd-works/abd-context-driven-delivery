Run the action on clean_engineering at code fidelity through the tools cli

Provide guidance for creating OO modules, models, and code.

Provide guidance from contexts, examples, and templates.

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

## modules

**Default format:** markdown  
**Diagram format:** `drawio` (modules view — blue boxes, seam-term bullets, one-way dependency arrows; template `templates/modules.drawio`). Language channels (python/java/…) are for **model** and later — not required here.

**Goal:** Refine **modules** purpose, primary use case, rationale, key terms, and relationship to other modules. Strive for **independent modules with one-way dependencies** and an explicit **build order**. Thin class/term identification only — enough to show independence.

A **module** is a named structural boundary that groups closely related classes — and optionally smaller modules — into a single cohesive unit. Modules can be composed of other modules; a highly complex and nested module can be thought of as a sub-system.

- Consume the existing `{session}/.context/{subject}-index.md` and partition chunks if they exist — **do not edit** or wipe partitions.
- Create module structure (`physical-folder` / `nested-physical-folder`) under `{session}/{module}/`.
- When nesting, the **parent module** owns shared base classes/terms (e.g. `powers` owns `Effect`). Specializing children use a path under the parent (`powers/attack`) and depend on the parent — not on siblings. Do **not** invent a `parent/base` submodule (e.g. no `powers/effect`) just to hold shared content; that content belongs on the parent. Diagram: path nesting = containment (children drawn inside the parent box).
- Seed `{session}/{module}/.context/module-context.md` — **public seam only** (see **`module-context.md` — public seam only** below). Thin: **Purpose**, **Seam** (public term/class names), **Dependencies**, optional **Extend** / **Mechanism** note. No full Public API / `I{Class}` yet. **Never** internals.
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
- **`public-seam-only`** — `.context/module-context.md` documents **only** the public seam: how to **use** the module, how to **extend** it, and what its **dependencies** are. Internals are banned (see dedicated section below). Scanner: `public-seam-only`.
- **`deep-module`** — The seam stays a short named list of classes and operations with substantial functionality behind it (Ousterhout: small interface, large hidden implementation). If internal helpers leak into the seam, encapsulation is overhead without benefit. Scanner heuristic: at most **40%** of top-level symbols may be public (leading underscore for the rest).
- **`physical-folder`** — Each module occupies its own folder; class files, markdown documents, and other module-level artifacts live in it. Generated code belongs in that folder — not beside the module, not in a flat dump outside it. Nested modules use child folders under the parent (`nested-physical-folder`). Not every folder is a module — chapter or organisational folders may group several modules and must not be treated as one module unless they own `.context/module-context.md`. **Do not stop at an arbitrary depth** — every folder that is a cohesive functional unit owns `.context/module-context.md`; folders that are only implementation detail (`assets/`, thin config/) are absorbed into the parent description. Stopping mid-tree at `pages/My` while leaving nested pages, hooks, and services undocumented is a defect. **`module-context.md` never lives under `.context/sessions/`** — the session folder is for sprint artifacts; the context file belongs beside the source it describes.
- **`output-format`** — Written markdown is human-readable only. Strip template markup (`<!-- Mu -->`, `<!-- Mv -->`, and similar) before writing. A module heading sits immediately above its `- **Purpose:**` block — no blank line between them.
- **`cohesive-file`** — Put a **class family** in one file: the primary type, its subtypes, and tightly connected peers that only make sense together (element + collection, small aggregate + its part). Name the file after the family concept (`abilities.py` for `Ability` + `Abilities`). Split into another file only when a type is independently reused across families or the file becomes a grab-bag of unrelated types. Do not default to one class per file. **Exception:** `{Type}ExampleFactory` (and its `examples` data, plus `I{Type}ExampleFactory` when one was requested) always live in a **sibling file** — never in the production family file (see **Example factories**).
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

At **modules** fidelity, `.context/module-context.md` is thin: Purpose, Seam (term list), Dependencies (one-way), optional Extend / Mechanism note — plus `{session}/.context/module-build-order.md`. At **model** fidelity it expands within the **same public-seam-only allowlist** (Purpose, Primary use case, Rationale, Seam, Public API, Constraint, Extend, Dependencies).

### `module-context.md` — public seam only

`.context/module-context.md` (and any `.module-context` synonym) is the **caller-facing contract**. It must contain **only**:

| Concern | Allowed headings / content |
|---|---|
| **Use** | **Purpose**, **Primary use case**, **Rationale**, **Seam**, **Public API** / **Public surface**, **Constraint** — what callers invoke and what they must / must not do |
| **Extend** | **Extend**, **Extension**, **How to extend**, optional **Mechanism** / **Mechanism stereotype** — variation points and fixed parts that are part of the *public* extension contract; authoring annotations that callers use to extend |
| **Dependencies** | **Dependencies** — one-way module / package names only |

**Allowed headings (exact, case-insensitive):** `Purpose`, `Primary use case`, `Rationale`, `Seam`, `Public API`, `Public surface`, `Constraint`, `Dependencies`, `Extend`, `Extension`, `How to extend`, `Mechanism`, `Mechanism stereotype`. Authoring tables that document the public annotation protocol (e.g. `@toolset` / `@agent_tool`) may sit under **Extend** or **Seam** — they are how to extend, not internals.

**Hard ban — never put these in module-context:**

- **Internal design**, **Internals**, **Participants** (private collaborators), **Domain separation**, **Pickup**, **Layout** (as an implementation dump), **Known scan notes**, **Implementation**, **Scan violations**, **Tests**, **Scanners** (as a private inventory), or any heading containing *internal*
- Underscore-prefixed **types**, **helpers**, or **methods** (`_CliAgentLog`, `_Pickup`, `_await_pickup`, `_ensure_work_session`, `_scanner_collection`, …) — leading underscore means private; keep them out of the seam list and out of prose
- Abstract bases, doers/judges, job-template stores, and other **private participants** that are not the public contract callers import
- Implementation notes, pickup/transcript heuristics, test inventories, scanner FP notes, private marker wiring beyond the public authoring annotations

**Exception:** public authoring markers of the form `_is_*` (e.g. `_is_toolset`) may appear in an **Extend** / annotation table when they *are* the published protocol. Every other `_…` name is banned.

**Do not** add **Internal design**, **Participants**, or **Domain separation** at **code** (or any) fidelity — those belong in source, sketches, or session notes, never in module-context. Edit the same `.context/module-context.md` in place; never create a parallel internals file beside it.

Scanner rule: **`public-seam-only`**.

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

## shopping-cart/examples.py

# @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
# invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
from __future__ import annotations
from abc import ABC, abstractmethod
from decimal import Decimal


class IShoppingCart(ABC):
    """Running tally of what a customer intends to buy in a single shopping session."""

    @property
    @abstractmethod
    def customer(self) -> Customer: ...

    @property
    @abstractmethod
    def items(self) -> list[CartItem]: ...

    @property
    @abstractmethod
    def discount(self) -> Discount | None: ...

    @property
    @abstractmethod
    def checked_out(self) -> bool: ...

    @abstractmethod
    def __init__(self, customer: Customer) -> None: ...

    @abstractmethod
    def add_item(self, product: str, quantity: int, unit_price: Decimal) -> None: ...

    @abstractmethod
    def remove_item(self, product: str) -> None: ...

    @abstractmethod
    def apply_discount(self, discount: Discount) -> None: ...

    @abstractmethod
    def compute_total(self) -> Decimal: ...

    @abstractmethod
    def checkout(self, inventory: Inventory) -> None: ...


class ShoppingCart(IShoppingCart):
    """Running tally of what a customer intends to buy in a single shopping session."""

    """@association - belongs to exactly one customer whose identity anchors the cart."""
    @property
    def customer(self) -> Customer:
        return self._customer

    """@composition - collects CartItems as the customer browses; keeps the total current."""
    @property
    def items(self) -> list[CartItem]:
        return self._items

    """@association - optional reduction rule applied before the total is computed."""
    @property
    def discount(self) -> Discount | None:
        return self._discount

    """Seals the cart permanently once the customer commits to checkout."""
    # Invariant: once true, never reverts to false.
    @property
    def checked_out(self) -> bool:
        return self._checked_out

    def __init__(self, customer: Customer) -> None:
        self._customer = customer
        self._items: list[CartItem] = []
        self._discount: Discount | None = None
        self._checked_out = False

    # region Public operations

    """Adds a line to the cart; merges quantity if the product is already present."""
    # Invariant: cart may not be modified after checkout.
    # Invariant: quantity must be at least 1.
    def add_item(self, product: str, quantity: int, unit_price: Decimal) -> None:
        ...

    def remove_item(self, product: str) -> None:
        ...

    """Attaches a reduction rule; replaces any previously applied discount."""
    def apply_discount(self, discount: Discount) -> None:
        ...

    """Sums line totals and applies the discount if one is present."""
    def compute_total(self) -> Decimal:
        ...

    """Verifies availability with Inventory, then seals the cart; raises if already checked out."""
    def checkout(self, inventory: Inventory) -> None:
        ...

    # endregion

    # region Private operations (empty until code)

    @abstractmethod
    def _find_item(self, product: str) -> CartItem | None: ...

    # endregion

    # region Interactions (specification only)

    @abstractmethod
    def adding_an_item_merges_if_product_already_present(self) -> None:
        """@interaction"""
        ...

    @abstractmethod
    def checkout_verifies_availability_before_sealing(self) -> None:
        """@interaction"""
        ...

    # endregion


class ICartItem(ABC):
    """A single product choice inside a ShoppingCart."""

    @property
    @abstractmethod
    def product(self) -> str: ...

    @property
    @abstractmethod
    def quantity(self) -> int: ...

    @property
    @abstractmethod
    def unit_price(self) -> Decimal: ...

    @abstractmethod
    def __init__(self, product: str, quantity: int, unit_price: Decimal) -> None: ...

    @abstractmethod
    def line_total(self) -> Decimal: ...

    @abstractmethod
    def update_quantity(self, quantity: int) -> None: ...


class CartItem(ICartItem):
    """A single product choice inside a ShoppingCart."""

    # Invariant: quantity is at least one.
    # Invariant: unit_price is non-negative.

    @property
    def product(self) -> str:
        return self._product

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def unit_price(self) -> Decimal:
        return self._unit_price

    def __init__(self, product: str, quantity: int, unit_price: Decimal) -> None:
        self._product = product
        self._quantity = quantity
        self._unit_price = unit_price

    def line_total(self) -> Decimal:
        ...

    def update_quantity(self, quantity: int) -> None:
        ...


class IDiscount(ABC):
    """A reduction rule a customer applies to a ShoppingCart."""

    @property
    @abstractmethod
    def code(self) -> str: ...

    @property
    @abstractmethod
    def reduction(self) -> Decimal: ...

    @abstractmethod
    def __init__(self, code: str, reduction: Decimal) -> None: ...

    @abstractmethod
    def is_valid(self, cart: IShoppingCart) -> bool: ...

    @abstractmethod
    def compute_reduction(self, subtotal: Decimal) -> Decimal: ...


class Discount(IDiscount):
    """A reduction rule a customer applies to a ShoppingCart."""

    # Invariant: discount cannot reduce total below zero.

    @property
    def code(self) -> str:
        return self._code

    @property
    def reduction(self) -> Decimal:
        return self._reduction

    def __init__(self, code: str, reduction: Decimal) -> None:
        self._code = code
        self._reduction = reduction

    def is_valid(self, cart: IShoppingCart) -> bool:
        ...

    def compute_reduction(self, subtotal: Decimal) -> Decimal:
        ...


"""
# @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
# invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering

CleanEngineering Python template - two files when Stories-bound:

    {family_slug}.py                 - (I{Class} +) {Class} (+ subtypes)   PRODUCTION
    {type_slug}_example_factory.py   - (I{Class}ExampleFactory +) factory  SEPARATE

INTERFACES ARE OPTIONAL (see clean_engineering.md SS Interfaces). I{Class} and
I{Class}ExampleFactory below are shown because this is the richer case to document -
default to OMITTING both and stubbing {Class} / {Class}ExampleFactory directly
(empty bodies at Md, filled at S/C, no ABC base needed) unless the user asked for an
interface, or the module genuinely has multiple layers/implementations behind one
seam. The two decisions (domain type vs. factory) are independent.

A production file holds the public seam (I{Class} when one exists), the production
Class that extends it (or stands alone when no interface exists), subtypes, and
tightly connected peers. Not one class per file. Example factories are NEVER in
that file (example-factory-separate-file).

Layout (physical-folder): write each file under the **module** folder
(e.g. {module_slug}/{family_slug}.py). Module context:
{module_slug}/.context/module-context.md.

Naming:
    File (production)  {family_slug}.py
    File (factory)     {type_slug}_example_factory.py
    Interface          I{Class}                (OPTIONAL - public seam only when requested; model fidelity)
    Class              {Class}(I{Class})       (production; drop "(I{Class})" when no interface exists)
    ExampleFactory     {Class}ExampleFactory   (plain class; no Loader base; Md+/S+)
    Modes              Fake | Isolated | Production  (factory behavior - not subclasses)
    Property           {owned_property}, ...     (snake_case slots)
    Operation          {operation_name}, ...     (snake_case slots)
    Params             {param}, {dep}
    Type slots         {Type}, {ReturnType}
    Invariant          comment                 (plain-English; not a method)
    Interaction        abstract method at S    (on Class only; dropped at code)

Fidelity tags:
    L  = language companion (prose; refined every stage - not a fidelity)
    Mu = modules       (thin terms, one-way deps, build order - markdown / module-context)
    Md = model         (empty public props/ops directly on Class by default; I{Class} - and
                       optional I{Class}ExampleFactory in factory file - only when requested)
    S  = specification (Class extends I{Class} when one exists, else stands alone; public
                       filled; privates empty on Class; {Class}ExampleFactory modes in
                       sibling factory file when Stories-bound)
    C  = code          (fill remaining empties on Class; drop interactions)
"""

from __future__ import annotations
from abc import ABC, abstractmethod


# =============================================================================
# FILE: {family_slug}.py - production family only (cohesive-file)
# =============================================================================


# OPTIONAL - omit this whole class by default. Only add I{ClassName} when the
# user requested an interface, or {ClassName} has multiple layers/implementations
# behind one seam. Otherwise skip straight to `class {ClassName}:` below with the
# same empty (# Md) bodies, and drop `(I{ClassName})` from its base list.
class I{ClassName}(ABC):                                                # Md
    """*{ClassName}* is - one sentence: what it is, its unique role.
    Identity only. No relationship or behavior sentences here."""     # L

    # -- Public properties (empty interfaces) --------------------------------

    @property                                                           # Md
    @abstractmethod                                                     # Md
    def {owned_property}(self) -> {Type}: ...                           # Md

    @property                                                           # Md
    @abstractmethod                                                     # Md
    def {plain_property}(self) -> {Type}: ...                           # Md

    # -- Public operations (empty interfaces) --------------------------------

    @abstractmethod                                                     # Md
    def __init__(self, {param}: {Type}) -> None: ...                    # Md

    @abstractmethod                                                     # Md
    def {operation_name}(self, {param}: {Type}) -> {ReturnType}: ...    # Md

    @abstractmethod                                                     # Md
    def {another_operation}(self) -> {ReturnType}: ...                  # Md


class {ClassName}(I{ClassName}):                                        # S
    # Drop "(I{ClassName})" above when no interface exists - {ClassName} then
    # carries the # Md empty-body members itself instead of inheriting them.
    """*{ClassName}* is - one sentence: what it is, its unique role."""  # L

    # -- Public properties (filled at specification) -------------------------

    """{sentence about this property - what it holds and why.}
    @composition"""                                                     # S
    @property                                                           # S
    def {owned_property}(self) -> {Type}:                               # S
        ...                                                             # S

    """{sentence about this plain property.}"""                         # L
    # Invariant: {constraint sentence - the rule in plain English.}    # S
    @property                                                           # S
    def {plain_property}(self) -> {Type}:                               # S
        ...                                                             # S

    # -- Constructor / public operations (filled at specification) -----------

    def __init__(self, {param}: {Type}) -> None:                        # S
        self._{plain_property} = {param}                                # S

    """{language bullet for this operation}"""                          # L
    # Invariant: {constraint sentence applicable to this operation.}   # S
    def {operation_name}(self, {param}: {Type}) -> {ReturnType}:        # S
        ...                                                             # S / C

    def {another_operation}(self) -> {ReturnType}:                      # S
        """{language bullet for this operation}"""                      # L
        ...                                                             # S / C

    # -- Private operations (empty interfaces at S; filled at C) -------------

    """{what this helper does}"""                                       # S
    @abstractmethod                                                     # S
    def _{private_helper}(self, {param}: {Type}) -> {ReturnType}: ...   # S

    def _{private_helper}(self, {param}: {Type}) -> {ReturnType}:       # C
        """{what this helper does}"""                                   # S
        ...                                                             # C

    # -- Interactions (specification only; omit at code) ---------------------

    @abstractmethod                                                     # S
    def {interaction_summary_as_a_method_name}(self) -> None:           # S
        """@interaction"""
        ...


# Subtype - delta only; parent members are inherited, not repeated     # Md/S
class I{ChildClass}(ABC):                                               # Md
    """{delta - what {ChildClass} adds}"""                              # L

    @abstractmethod                                                     # Md
    def {delta_operation}(self, {param}: {Type}) -> {ReturnType}: ...   # Md


class {ChildClass}({ClassName}, I{ChildClass}):                         # S
    """{delta - what {ChildClass} adds or overrides}"""                 # L

    def {delta_operation}(self, {param}: {Type}) -> {ReturnType}:       # S/C
        ...                                                             # S/C


# =============================================================================
# FILE: {type_slug}_example_factory.py - Stories factory (separate file)
# from .{family_slug} import {ClassName}, I{ClassName}
# Pattern only - no ExampleLoader base. examples[{example_key}] is a
# multi-type bundle (not examples[{Type}][...]).
# Fake / Isolated / Production are modes - not Fake{ClassName} subclasses.
# =============================================================================


# OPTIONAL - same opt-in rule as I{ClassName} above; omit by default and go
# straight to `class {ClassName}ExampleFactory:` below.
class I{ClassName}ExampleFactory(ABC):                                  # Md
    """Loads examples[{example_key}] as Fake | Isolated | Production modes."""  # L

    @abstractmethod                                                     # Md
    def load_{example_key}(self, *, mode: str = "fake") -> I{ClassName}: ...  # Md


class {ClassName}ExampleFactory(I{ClassName}ExampleFactory):            # S
    # Drop "(I{ClassName}ExampleFactory)" above when no interface exists.
    """Fake: mock framework + examples; Isolated: {ClassName}(injected mocks);
    Production: {ClassName}(real collaborators)."""                     # L

    def load_{example_key}(self, *, mode: str = "fake") -> I{ClassName}:  # S
        # examples[{example_key}] -> I{ClassName} (+ peer types if needed)  # S
        ...                                                             # S/C



Every tool call uses this shape - set `tool` and `arguments`, pipe to CLI:

```yaml
toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
context:
  fidelity: code
tool: <tool name>
arguments:
  <if needed>
```

Run: python -m tools run -

Suggested flow (repeat and reorder as the story needs):

Read `resources` from each response before choosing the next tool.

With a straight prompt passed, take the action from the prompt. If you took an action from the context versus being given a straight prompt, confirm the use of the context. AskQuestion constrained to these actions: car-inspect | createRule | document | generate | grill | iterate | partition | render | repair | satisfy | scan | sketch | travel-to | validate.
Then run:
Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
context:
  fidelity: code
action: generate
```
.\tools.ps1 run -
