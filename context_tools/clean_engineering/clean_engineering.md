# Contexts

Deepen OO design from modules toward production code. Each fidelity **adds** artifacts — do not invent detail from a deeper level.

---



## Language 
- At each fidelity, refresh prose for terms/classes already named at that stage — definition, story bullets, invariants in plain English.
- Keep identity on the class (or `## ClassName` section); member bullets move onto members as model/code deepen.
- Do **not** invent types, method bodies, relationship kinds, or Public API ahead of the active fidelity.
- Prose lives under `{session}/{module}/` (markdown sections and/or class docstrings) and is updated in place — never a separate language-only generate run.

---



## modules

**Default format:** markdown  
**Diagram format:** `drawio` (modules view — blue boxes, seam-term bullets, one-way dependency arrows; template `templates/modules.drawio`). Language channels (python/java/…) are for **model** and later — not required here.

**Goal:** Partition a problem or solution space into independently understandable units — each a deep module with a narrow public seam and substantial implementation behind it. Name the units, their seams, and the one-way dependencies between them. Thin class/term identification only — enough to show independence. Do not invent types, method bodies, or relationship kinds yet. Each **module** is a named structural boundary that groups closely related classes — and optionally smaller modules — into a single cohesive unit. Modules can be composed of other modules; a highly complex and nested module can be thought of as a sub-system.

### Guidance:

**Deep modules** Start by identifying the major structural boundaries — group closely related classes around a single domain concept. Each module should be **deep**: a narrow public interface with substantial implementation behind it. Create deep module to reduce both your and human user cognitive load so that you can focus on reading the interface versus reading the implementation. Build interfaces to be much simpler than their implementation, avoid shallow modules that adds overhead without encapsulation. Resist the urge to decompose into many small modules.

**Smart Dependencies** Arrange dependencies **one way only**, never back, never circular. Code that changes often depends on code that rarely changes — a feature screen may import a shared utility, but the shared utility never imports the feature screen. Break circular dependencies by extracting to a common module. Avoid dependency magnets — modules that accumulate dependencies from everywhere become rigid and expensive to change. Narrow the surface of dependency magnets by splitting it along domain lines.

Make every dependency **explicit**. Use direct, visible references over indirection. Avoid Implicit coupling ( globals, configuration magic ,side effects, shared mutable state, convention-based wiring), as it is harder to reason about, harder to test, and harder to change safely. 

Document only the **public seam** — how to use the module, how to extend it, and what it depends on. One name per concept on the seam (prefer the type name — `Ability`, not `Ability, Abilities`). Write language-companion prose for the terms you name. Never document internals in module-context. The caller-facing contract is the only thing that should survive into documentation; implementation details live in source code and session notes. If someone needs to read the internals to use the module, the interface is too shallow.

### Scaffold

**When scaffolding only** (`/partition` or a names-only first cut — not full generate at this fidelity): follow this subsection. Do not use ### Rules below, ## Sketching, or ## Templates. **Stop reading this skill when scaffolding.**

Rough module index for a **partition** pass or first cut — module paths, chunk files, seam terms, and thin dependency notes only. Formal one-way graph and full `module-context.md` wait for **modules** generate.

Key rules: `one-way-deps` — dependencies flow one direction only; no cycles; `domain-nouns-only` — module names are domain nouns or paths, never action verbs or `*Model`/`*Runtime` suffixes. Use **abd-code-research** (not raw file scraping) when the corpus is code.

### Module rules

- `high-cohesion` — Classes inside a module share a common purpose and operate on the same domain concept. Cross-class relationships within the module are strong and semantic, not incidental.
- `low-coupling` — Modules depend on each other only through well-defined interfaces. Cross-module dependencies are explicit and minimal — no module reaches into another's internals.
- `single-boundary` — Each module is the single source of truth for its domain concept. No other module holds, mutates, or duplicates that concept's state or rules.
- `named-seam-and-constraint` — Every module owns a *seam* — the public surface of classes and operations callers depend on — paired with a *constraint* stating what callers must do or must not do at that boundary. A module is described by what it requires of its callers, not only by what it holds.
- `public-seam-only` — `.context/module-context.md` documents **only** the public seam. Never internals, participants, implementation, layout dumps, tests, scanners, scan notes, or any heading containing *internal*. Never underscore-prefixed types, helpers, or methods. Never private participants (abstract bases, doers, judges, stores) that callers do not import. Scanner: `public-seam-only`.
- `deep-module` — The seam stays a short named list of classes and operations with substantial functionality behind it (Ousterhout: small interface, large hidden implementation). If internal helpers leak into the seam, encapsulation is overhead without benefit. Scanner heuristic: at most **40%** of top-level symbols may be public (leading underscore for the rest).
- `physical-folder` — Each module occupies its own folder; class files, markdown documents, and other module-level artifacts live in it. Generated code belongs in that folder — not beside the module, not in a flat dump outside it. Not every folder is a module — chapter or organisational folders may group several modules and must not be treated as one module unless they own `.context/module-context.md`. **Do not stop at an arbitrary depth** — every folder that is a cohesive functional unit owns `.context/module-context.md`; folders that are only implementation detail (`assets/`, thin config/) are absorbed into the parent description. `module-context.md` **never lives under** `.context/sessions/` — the session folder is for sprint artifacts; the context file belongs beside the source it describes.
- `nesting` — Nest under a parent only when children share mechanics or form a clear sub-system boundary; independent concepts stay flat. Child path is `{parent}/{child}/` (e.g. `powers/attack/`). Parent-shared code lives in the **parent** folder — do not invent a submodule for shared base. If children would duplicate mechanics, extract parent-owned base types first. Each child must be independently implementable (siblings stubbed); it may depend on the parent base, not on sibling children.
- `output-format` — Written markdown is human-readable only. Strip template markup (`<!-- Mu -->`, `<!-- Mv -->`, and similar) before writing. A module heading sits immediately above its `- **Purpose:**` block — no blank line between them.
- `cohesive-file` — Put a **class family** in one file: the primary type, its subtypes, and tightly connected peers that only make sense together (element + collection, small aggregate + its part). Name the file after the family concept (`abilities.py` for `Ability` + `Abilities`). Split into another file only when a type is independently reused across families or the file becomes a grab-bag of unrelated types. Do not default to one class per file. **Exception:** `{Type}ExampleFactory` (and its `examples` data, plus `I{Type}ExampleFactory` when one was requested) always live in a **sibling file** — never in the production family file (see **Example factories**).
- `abstraction-focus` — Module description names *what* the module does at a higher level than the classes inside it; public verbs are caller-facing, not internal steps or storage layouts.
- `layer-separation` — Adjacent modules operate at different abstraction levels; collapse pass-through modules.
- `complexity-absorption` — Push configuration and edge-case handling into the module; callers pass intent, not setup flags.
- `information-hiding` — Volatile implementation choices must not appear in public signatures or return types.
- `temporal-independence` — Every public operation leaves the module in a valid state; avoid order-coupled APIs or document the constraint.
- `general-purpose-surface` — Public interface is not hardcoded to one caller's UI/workflow.
- `errors-out-of-existence` — Prefer total functions / empty states for routine edges; reserve exceptions for real failures.


---
## model

**Default format:** Python

**Goal:** Analyze the module and design its object model — the classes, what they remember and do, and how they relate. Stub empty properties and operations. No production behavior yet.

### Guidelines

Analyze the source context to identify the concepts and operations the domain already names — do not invent terminology. Group concepts that have their own identity, state, and behavior into **classes**. Model them **behaviors first and data second** — **properties** (what they remember — noun phrases) and **operations** (what they do — verb phrases). An `Order` calculates its own total; a `Cart` checks itself out. Do not invent a `Manager`, `Service`, `Helper`, or `Processor` to do what the object itself should do.

**Localize behavior to the object that owns the state.** Each object accesses its own state and enforces its own invariants — do not write objects that manipulate another object's internal state. When deciding where an operation belongs, ask: which object has the data this operation needs? That is where the operation lives. `cart.checkout()`, not `CheckoutManager.processCheckout(cart)`. 

**Give each class one clear, focused responsibility.** When a class accumulates operations spanning different concerns, it reveals missing classes — split by the data each group of operations works with, this will reveal a hidden conceptthis will reveal a hidden concept. Keep the public surface narrow: a few well-named operations that express intent, not a long list of methods covering every concern the system touches.

**Find the operations.** Walk the source for the verbs this concept already performs — what a user or system asks it to do. An operation belongs on the class that owns the data it needs. Parameters are only what the object does not already hold; the return is what the caller must observe, not internals. Inside an operation, name **interactions** with other classes — specifically in other modules (`-> {collaborator}.{operation}`). Use exsisting public seam named in those modules or create new ones that respect module boundaries. Add **invariants** thins that must stay true (`// remaining budget never goes negative`) when the operation runs.

**Get typing right.** Write a **property** when variation is data — a `type` field, not a new class. Write a **base class** when two or more types share identity, state, and operations — put that shared behavior in one place. Write a **subtype** when a variant changes what the thing *does*; record only the delta. Anywhere the base is used, the subtype must work in its place. Write an **interface** when multiple implementations sit behind one seam.

**Make dependencies explicit.** Pass publicly accessible and swappable collaborators through the constructor — never reach for a global. When modelling relationships, choose by lifecycle: composition when the owner controls the other's lifecycle, aggregation when the collector has no meaning without its members, association when both sides are independent.

Extend module level **public seam** documentation — what callers invoke, what they must or must not do, and how to extend — plus **dependencies**: every other-module class or operation this module calls. See `@clean_engineering-modules`. Refresh the language companion for new or uodated terms now on the public API. Do not document internal design, private participants, or implementation notes.

### Relationships

Relationship kind and cardinality are added  here. Three kinds, chosen by lifecycle:

1. **Composition** — owner controls the other's lifecycle. (`Order` composes `OrderLine`.)
2. **Aggregation** — collector groups members that can outlive it. (`Playlist` aggregates `Song`. A **Repository** aggregates the aggregate it collects — hollow diamond.)
3. **Association** — both sides are independent; they simply use each other. (`Customer` associates with `SupportAgent`.)

Value objects that merely describe (`Money` on a Transaction, `PortingInfo` on a number) are **association** or a property — not composition diamonds. Composition is for parts whose lifecycle the owner controls.


### Rules

- `class-not-property-instance-or-subtype` — Before promoting a term to its own class, check whether it fits as a property, an instance, or a subtype. Only when none of those three fit does it deserve its own class.
- `use-property-not-accessor` — Use `@property` (or the language equivalent) for read-only computed values; do not use `get_` / `set_` method prefixes.
- `keep-operations-single-responsibility` — Each operation has one reason to change — pure calculation or orchestration, not both. An operation doing two things reveals either a missing operation or a missing class.
- `separate-concerns` — Pure calculation separate from I/O and mutation.
- `use-clear-operation-parameters` — Prefer 0–2 parameters. When more configuration is needed, the extra parameters reveal a missing value object — promote them to a new class and pass that instead.
- `interactions-are-operation-calls` — Nest `-> {collaborator}.{operation}` under the calling operation. `-> ClassName` alone is not an interaction. Do not invent `- **Interaction:**` bullets.
- `invariants-are-class-level-notes` — Class-level invariants sit as `//` on the class, not under one operation. They do not become methods.
- `keep-classes-single-responsibility` — Each class has **one reason to change**.
- `hide-inner-details` — Expose **behavior** through named methods; callers see what the class does, not how it stores or arranges its information.
- `eliminate-duplication` — Repeated logic gets one canonical function.
- `prefer-class-operations` — Factory and lifecycle operations are **static methods on the class**, not module-level exported functions (`ParadiseMobile.initialize(config)`, not `export async function open()`). Private helpers used from one class belong on that class.
- `use-explicit-dependencies` — Pass every collaborator through the **constructor**; never reach for a global or construct a collaborator inside construction.
- `use-intention-revealing-names` — Every name — class, property, operation, parameter — answers "why does this exist?" No abbreviations, no single-letter identifiers outside trivial loop indices.
- `use-consistent-naming` — One word per concept across the model. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`).
- `reuse-existing-not-invent-parallel` — When a class wraps or renders an existing type, name it after that type (`CatalogContextTool` wraps `BaseContextTool`; `CatalogAction` wraps `Action`). Do not invent a parallel domain noun for the same concept — especially not a retired synonym the project has already replaced (Foundry **Practice** → CDD **context tool**). Explicit old→new mapping rows (and overview lines that *state* the replacement) are allowed; live class names, constructor args, and row/registry/toolset labels are not.
- `reuse-established-notation-not-a-parallel-one` — Interactions/invariants at sketch and `## model` reuse `->` / `//`; never invent a bold-bullet parallel (`- **Interaction:**` / `- **Invariant:**` as collaboration markers). Language companion `- **Invariant:** <!-- L -->` and Spec indented labels are different surfaces.
- `ce-comments-are-for-invariants-and-sequencing-notes-only` — `//` comments are must/never/always/before/after notes only. Not narrative, not “transient value object”, not cross-references between atoms.
- `do-not-invent-parallel-object-models` — Do not invent a parallel object model when existing objects already carry the data a new requirement needs. Wrap or extend the live hierarchy instead; do not scrape the same information into a second `*Model` / `*Entry` (or similar) family.




## code

**Default format:** Python

**Goal:** Two phases in one fidelity — first lock down the typed contracts (`Class(I{Class})` when an interface was requested at model, otherwise the `Class` stub already in place from model), then wire the full production implementation. When an `I{Class}` exists it stays as the stable seam throughout; when it does not, `Class` itself is the seam.

A vertical is not at **code** fidelity while it still depends on a mockup / Story Demo shell as the only UI, or on in-memory / fake factories as the only "backend." **Code** means real backend **and** real frontend (UX **code** fidelity) — not greybox + demo domain alone.

### Phase 1 — typed contracts

- **Tooling & Idioms:** Refer to `[context_tools/language-tools.md](/context_tools/language-tools.md)` for language-specific recommendations for coding.
- **When an** `I{Class}` **interface was requested at model** (interfaces are optional — see `## model` § Interfaces): add `Class(I{Class})` (Java: `implements I{Class}`) in the **same file** as `I{Class}`. Do **not** fill out `I{Class}` or add private members to it.
- **When no interface was requested:** skip that step — the empty `Class` stub already exists from **model** fidelity in its own family file; continue directly onto it.
- On `Class`: implement public properties and operations; add private properties/operations as **empty interfaces** (`...` / `@abstractmethod`); add each relationship with its **kind** (composition / aggregation / association) and **cardinality** (e.g. `1..`*, `0..1`); invariants as **comments** (not methods) — formalizing any named at `## model` § Invariants, or newly introduced here.
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

- `keep-operations-small-focused` — Under **20 lines**; extract named helpers.
- `simplify-control-flow` — Guard clauses; max nesting depth as enforced by scanners.
- `maintain-abstraction-levels` — One level at a time; no raw I/O mixed into orchestration names.

**Naming / context**

- `provide-meaningful-context` — Named constants for magic numbers and unexplained literals.

**Errors / comments**

- `use-exceptions-properly` — Domain exceptions that name the failure.
- `never-swallow-exceptions` — Log and re-raise or convert; never bare swallow.
- `stop-writing-useless-comments` — Comments explain **why**, not **what**.


