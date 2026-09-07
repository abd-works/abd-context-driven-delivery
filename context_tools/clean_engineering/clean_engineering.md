# Contexts

Structure the problem into a solution of independent, decoupled modules behind small, simple public APIs that hide deep functionality, with explict one way dependencies named. Implement those modules using rigourous object oriiented and clean-code practice.

## Shared rules

- **`honor-every-rule-in-the-artifact`** — Honor every rule in the artifact you are writing. One-way dependencies, named seams, and localized behavior apply to language and markdown as well as to code. Do not create a dependency in prose that violates isolation. Treat prose with the same respect you treat the model and the code.
- **`vocabulary-traces-to-source`** — Take every term from the source. The English term and the code name are the same word: *shopping cart* is `ShoppingCart`.
- **`do-not-invent-terms`** — Do not invent a second noun or a parallel vocabulary. Keep `do-not-invent-parallel-object-models` on the model for wrappers and `*Model` / `*Entry` families.

---

## Language

When asked to express output using language, write the same names, definitions, and rules in a conversational format that we do in modules, model, and code. Shared rules `vocabulary-traces-to-source` and `do-not-invent-terms` apply here.

**Follow the object-oriented thinking in modules and model — write it in English.** Use the same ideas: a **root** to group terms, then **concept**, **subtype**, **property**, **instance**, and **invariant**. Do not restate those rules here; apply them as prose — short definitions, verb-led story bullets, italicized domain terms — not typed class blocks. Keep identity on the ; move member bullets onto members as the model and code deepen. Update prose in place under `{session}/{module}/`.
 If the user asks for language while generating **modules** or **model**, stop there and use the language template at `templates/clean_engineering-language.md` — do not continue reading the remaining templates.

---

## modules

**Default format:** markdown  
**Diagram format:** `drawio` (modules view — blue boxes, seam-term bullets, one-way dependency arrows; template `templates/modules.drawio`). Language channels (python/java/…) are for **model** and later — not required here.

**Goal:** Partition a problem or solution space into independently understandable units — each a deep module with a narrow public seam and substantial implementation behind it. Name the units, their seams, and the one-way dependencies between them. Thin class/term identification only — enough to show independence. Do not invent types, method bodies, or relationship kinds yet. Each **module** is a named structural boundary that groups closely related classes — and optionally smaller modules — into a single cohesive unit. Modules can be composed of other modules; a highly complex and nested module can be thought of as a sub-system.

### Language

**When the user asks for language** (not full generate at this fidelity): use the language template at `templates/clean_engineering-language.md`. Do not use ### Guidance, ### Scaffold, ### Module rules, ## Sketching, or ## Templates. **Stop reading this skill when writing language.**

### Guidance:

**Deep modules** Start by identifying the major structural boundaries — group closely related classes around a single domain concept. Each module should be **deep**: a narrow public interface with substantial implementation behind it. Create deep module to reduce both your and human user cognitive load so that you can focus on reading the interface versus reading the implementation. Build interfaces to be much simpler than their implementation, avoid shallow modules that adds overhead without encapsulation. Resist the urge to decompose into many small modules.

**Smart Dependencies** Arrange dependencies **one way only**, never back, never circular. Code that changes often depends on code that rarely changes — a feature screen may import a shared utility, but the shared utility never imports the feature screen. Break circular dependencies by extracting to a common module. Avoid dependency magnets — modules that accumulate dependencies from everywhere become rigid and expensive to change. Narrow the surface of dependency magnets by splitting it along domain lines.

Make every dependency **explicit**. Use direct, visible references over indirection. Avoid Implicit coupling ( globals, configuration magic ,side effects, shared mutable state, convention-based wiring), as it is harder to reason about, harder to test, and harder to change safely. 

Document only the **public seam** — how to use the module, how to extend it, and what it depends on. One name per concept on the seam (prefer the type name — `Ability`, not `Ability, Abilities`). Write language for the terms you name. Never document internals in module-context. The caller-facing contract is the only thing that should survive into documentation; implementation details live in source code and session notes. If someone needs to read the internals to use the module, the interface is too shallow.

### Scaffold

**When scaffolding only** (`/partition` or a names-only first cut — not full generate at this fidelity): follow this subsection. Do not use ### Rules below, ## Sketching, or ## Templates. 

Rough module index for a **partition** pass or first cut — module paths, chunk files, seam terms, and thin dependency notes only. Formal one-way graph and full `module-context.md` wait for **modules** generate.

Key rules: `one-way-deps` — dependencies flow one direction only; no cycles; `domain-nouns-only` — module names are domain nouns or paths, never action verbs or `*Model`/`*Runtime` suffixes. Use **abd-code-research** (not raw file scraping) when the corpus is code.

**Stop reading this skill when scaffolding.**

### Module rules

**Form the module**

- `named-seam-and-constraint` — Name the seam (public classes and operations) and the constraint (what callers must or must not do).
- `high-cohesion` — Group classes that share one purpose and the same domain concept.
- `single-boundary` — Do not let another module hold, mutate, or duplicate this module’s concept.

**Shape the seam**

- `deep-module` — Keep most top-level symbols private (at most **40%** public). Substantial work stays behind a short seam.
- `abstraction-focus` — Name *what* the module does for callers, not internal steps or storage.
- `public-seam-only` — Document only public seam and dependencies on other modules. Do not document internals, or tests.
- `use-typed-signatures` — Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them.
- `general-purpose-surface` — Do not shape the seam for one caller’s UI or workflow.
- `temporal-independence` — Leave the module valid after every public operation. Do not require a call order unless you document it.

**Define Dependebcues**

- `low-coupling` — Depend only through other modules’ seams. Keep sibling imports few.
- `layer-separation` — keep dependent modules at different levels of abstractions. Collapse pass-through modules.
- `nesting` — Nest a child only when it shares mechanics or is a sub-system; keep independent modules flat. Put shared behavior on the parent. A child may depend on the parent, not on siblings.

---
## model

**Default format:** Python

**Goal:** Analyze modules and design its object model — the classes, what they remember and do, and how they relate. Stub empty properties and operations. No production behavior yet.

### Language

**When the user asks for language** (not full generate at this fidelity): use the language template at `templates/clean_engineering-language.md`. Do not use ### Guidelines, ### Rules, ## Sketching, or ## Templates. **Stop reading this skill when writing language.**

### Guidelines

Analyze the source context to identify the concepts and operations the domain already names — do not invent terminology. Group concepts that have their own identity, state, and behavior into **classes**. Model them **behaviors first and data second** — **properties** (what they remember — noun phrases) and **operations** (what they do — verb phrases). An `Order` calculates its own total; a `Cart` checks itself out. Do not invent a `Manager`, `Service`, `Helper`, or `Processor` to do what the object itself should do.

**Localize behavior to the object that owns the state.** Each object accesses its own state and enforces its own invariants — do not write objects that manipulate another object's internal state. When deciding where an operation belongs, ask: which object has the data this operation needs? That is where the operation lives. `cart.checkout()`, not `CheckoutManager.processCheckout(cart)`. 

**Give each class one clear, focused responsibility.** When a class accumulates operations spanning different concerns, it reveals missing classes — split by the data each group of operations works with, this will reveal a hidden conceptthis will reveal a hidden concept. Keep the public surface narrow: a few well-named operations that express intent, not a long list of methods covering every concern the system touches.

**Find the operations.** Walk the source for the verbs this concept already performs — what a user or system asks it to do. An operation belongs on the class that owns the data it needs. Parameters are only what the object does not already hold; the return is what the caller must observe, not internals. Inside an operation, name **interactions** with other classes — specifically in other modules. Use the existing public seam named in those modules or create new ones that respect module boundaries. Add **invariants** — things that must stay true when the operation runs. How to write those notes is in the model template.

**Get typing right.** Write a **property** when variation is data — a `type` field, not a new class. Write a **base class** when two or more types share identity, state, and operations — put that shared behavior in one place. Write a **subtype** when a variant changes what the thing *does*; record only the delta. Anywhere the base is used, the subtype must work in its place. Write an **interface** when multiple implementations sit behind one seam.

**Make dependencies explicit.** Pass publicly accessible and swappable collaborators through the constructor — never reach for a global.

**Name the relationships.** Add kind and cardinality. Choose kind by **ownership** and **identity**. **Write composition** when the owner completely owns the part and the part has no identity outside it — an airplane is composed of its wings, cockpit, and engine; the cockpit has no identity outside the plane. **Write aggregation** when the collector has no meaning without its members, but members keep their own identity — a fleet is an aggregate of planes. **Write association** when both sides are independent — a plane is driven by a pilot; the pilot has complete independence from the plane.

Extend module level **public seam** documentation — what callers invoke, what they must or must not do, and how to extend — plus **dependencies**: every other-module class or operation this module calls. See `@clean_engineering-modules`. Refresh the language for new or uodated terms now on the public API. Do not document internal design, private participants, or implementation notes.


### Rules

**Shape classes**
- `class-not-property-instance-or-subtype` — Before you write a new class, check property, instance, then subtype. Write a class only when none of those three fit.
- `keep-classes-single-responsibility` — Give each class one reason to change.
- `put-logic-on-the-owning-resource` — Put the logic on the object that owns the resource first — `client.accounts[id].transactions.last.validate()`, not `client.validateLastTransactionForPrimaryAccount()`. A shorter public API may facade that later.
- `hide-inner-details` — Expose behavior through named operations. Do not let callers see how the class stores or arranges its data.
- `use-property-not-accessor` — Use `@property` (or the language equivalent) for read-only computed values. Hide the logic that updates state behind a setter — do not write an update opration. Do not prefix methods with `get_` or `set_`.
- `prefer-class-operations` — Put factory, lifecycle, and helpers used from one class on that class. Do not export them as module-level functions.
- `use-explicit-dependencies` — Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction.


**Define operations**
- `keep-operations-single-responsibility` — Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class.
- `use-clear-operation-parameters` — Have callers pass intent, not setup. Prefer 0–2 parameters; when you need more, promote paramters to a class. Do not use vague names (`data`, `options`, `info`).
- `errors-out-of-existence` — For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken.
- `limit-comments` — write comment in operations and properties only when the signature cannot say a constraint or explain why the code behaves the way it does. Do not narrate a line that already names what it does.

**Invariants, interactions, and comments**

- `write-invariants` — Name a rule the object itself must keep true whenever it acts — a must, never, always, before, or after about its own state. Write one a caller can break by using the object wrong. Do not restate a type, a name, or a single operation’s happy path.
- `write-interactions` — Collaborate when this object cannot finish its job from its own state — another object owns the data or the next act. Ask that object to do the work so each keeps its own invariants; do not reach into its internals or steal its job. Ask through a named public operation on a collaborator you hold or are given. Do not point at a type, and do not invent a third object to mediate a conversation two objects can have.

**Names and reuse**

- `use-intention-revealing-names` — Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.
- `use-consistent-naming` — Use one word per concept. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`).
- `eliminate-duplication` — Give repeated logic one canonical function.
- `do-not-invent-parallel-object-models` — Wrap or extend the live objects. Name a wrapper after the type it wraps. Do not invent a parallel domain noun, and do not scrape the same data into a second `*Model` / `*Entry` family.




## code

**Default format:** Python

**Goal:** Turn the model into working production code. Implement types and seams first, then real behavior behind them. Write real backend and real frontend — not a demo shell with stand-ins.

### Guidelines

Follow the idioms in `[context_tools/language-tools.md](/context_tools/language-tools.md)`.

Start by **Implenenting the public surface.** Where the model asked for an interface, the class implements it in the same file and the interface stays public-only. Where it did not, continue to impmlement the class. Implement public properties and operations first; write out private members next. Relationships keep the kind and cardinality already named. 

Make sure to **Implement real behavior.** Fill every empty body. Wire real persistence, services, and other-module seams — not stand-ins as the shipping path. Add helpers, named constants, and domain exceptions only when the implementation needs them. Keep an existing interface as the seam; otherwise treat the class as the seam. 

When writing out code take care to **Fill out all interactions with real code.** Turn `-> collaborator.operation` notes into actual calls — have the object ask its collaborators to do the work; do not reach into their internals. Drop the placeholder once the call is real.

**Honor invariants in the implementation.** Turn `// remaining budget never goes negative` comments into methods where you can; replace comments with explicit code.

**Keep the code clean.** Give each operation one thing to do; keep it short and at one level of abstraction — do not mix orchestration with raw I/O. Name things so they say why they exist. Handle the failing or empty cases first and return — then write the main path flat. Do not bury the real work inside nested ifs. Name exceptions after the failure; never swallow them. Give magic numbers names. Keep the public surface the seam already designed: short, caller-facing, with substantial implementation behind it, still in the module folder.

**Skip the model only for a very small change** — fill a body, rename, extract a helper, honor an invariant already named. The language is already there; keep it current. When you start needing to model — a new class, a new responsibility, a new relationship, a new public seam, or a new concept — stop and go to **model**. See `@clean_engineering-model`. Then return to code and implement what the model now names. Do not grow a shadow model only in the implementation.

**Refresh the language and the seam.** Keep class identity in the docstring; put member bullets on the members. Edit the same public-seam module-context — how to use it, what callers must honor, what it depends on. Never internals. Never a parallel file.



### Rules

**Implement the model**
- `hide-inner-details` — Expose behavior through named operations. Do not let callers see how the class stores or arranges its data.
- `keep-operations-small-focused` — Keep each operation short enough to read as one thought — under 20 lines. When it grows, extract a private helper whose name says why that slice exists.
- `keep-operations-single-responsibility` — Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class.
- `simplify-control-flow` — Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels.
- `errors-out-of-existence` — For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken.

**Names and reuse**
- `use-intention-revealing-names` — Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.
- `use-consistent-naming` — Use one word per concept. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`).
- `provide-meaningful-context` — Give a number or literal a name that says why it is there (`SECONDS_PER_DAY`, not `86400`). Do not number variables (`item1`).
- `eliminate-duplication` — Give repeated logic one canonical function.

**Errors / comments**
- `use-exceptions-properly` — Raise a domain exception that names the failure (`CartAlreadyCheckedOut`, not `Error` or a bare string). Catch the specific type you can handle. Do not use a bare `except`.
- `never-swallow-exceptions` — Do not catch and ignore. Log and re-raise, or convert to a domain exception that still names the failure. A `pass` in `except` hides a broken invariant.
- `limit-comments` — write comment in operations and properties only when the signature cannot say a constraint or explain why the code behaves the way it does. Do not narrate a line that already names what it does.


