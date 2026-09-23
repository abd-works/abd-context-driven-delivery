## Overview

Structure the problem into independent modules with small public interfaces, substantial hidden functionality, and one-way dependencies. Implement those modules with rigorous object-oriented and clean-code practices. When boundaries hold, a change stays inside one module; when they blur, callers depend on internal decisions and must change with them.

## Guidance

Partition first, then type the objects, then implement. Keep the same names in language, modules, model, and code. Honour every rule in the artifact you are writing — prose, diagrams, and source.

## Shared rules

```yaml
alwaysApply: false
globs: "**/*-sketch.md"
```

Use these rules whenever you name a concept, draw a dependency, or write a public seam — in prose, a diagram, or source.

- **`honor-every-rule-in-the-artifact`** — Honor every rule in the artifact you are writing. One-way dependencies, named seams, and localized behavior apply to language and markdown as well as to code. Do not create a dependency in prose that violates isolation. Treat prose with the same respect you treat the model and the code.
- **`vocabulary-traces-to-source`** — Take every term from the source. The English term and the code name are the same word: *shopping cart* is `ShoppingCart`. When the code says a different word than the domain, every reader keeps a translation in their head, and the two names drift until they mean different things.
- **`do-not-invent-terms`** — Do not invent a second noun or a parallel vocabulary. A second noun for the same thing becomes a second class, and then the same rule has to be written and fixed in both.
- **`do-not-invent-parallel-object-models`** — Keep one object model. Follow the nouns and verbs the rest of the graph already uses for that concept. A class that joins types the rest of the graph keeps apart is a second model — a big ball of mud — and every rule then has to be written and fixed in both. Wrap or extend the live objects and name a wrapper after the type it represents; do not scrape the same data into a second `*Model` or `*Entry` family.

---

## Language

When asked to express output using language, write the same names, definitions, and rules in a conversational format that we do in modules, model, and code. Shared rules `vocabulary-traces-to-source` and `do-not-invent-terms` apply here.

**Follow the object-oriented thinking in modules and model, then write it in English.** Use a **root** to group terms, then **concept**, **property**, **instance**, and **invariant**. At **model**, add **subtype** (`*is a type of*` / `Child : Parent`). At **modules**, every concept is `### {Name}` with no is-a heading. Express them as short definitions, verb-led behaviour bullets, and italicized domain terms rather than typed class blocks. Keep identity on the concept and move member details onto the members as the model and code deepen. Update the existing prose under `{session}/{module}/` rather than creating a parallel description.

**Lead with why a caller would use it.** The opening sentence of a concept, Purpose, or seam term is the job it does for someone — what they get that they did not have before. A decorator, merge, mark, flag, or storage choice is *how*; it never opens the definition. `@agent_toolset` is not the definition of *AgentToolSet*; the definition is that an ordinary class becomes a set of operations an agent can list, run as Python, or follow as **instructions**. If the first line only says “decorate / merge / mark,” the reader still does not know why they would.

If the user asks for language while generating **modules** or **model**, use this Language section and stop before the fidelity Guidance and Rules.

---

## Fidelities

### modules

```yaml
default_format: markdown
stage: discovery
```

**Diagram format:** `drawio` (modules view with blue boxes, public-interface bullets, and one-way dependency arrows; template `templates/modules.drawio`). **Markdown:** `module-context.md` uses template `templates/modules.md`. Programming-language channels are for **model** and later.

#### Overview

Partition a problem into independently understandable units — name each unit, its public seam, and its one-way dependencies.

Each **module** is a named structural boundary that groups closely related classes — and optionally smaller modules — into a single cohesive unit. Modules can be composed of other modules; a highly complex and nested module can be thought of as a sub-system.

#### Language

When language sits in `module-context.md`, use the top-level Language section **and** follow `templates/modules.md`. Do not skip this subsection.

Lead with the job a caller hires it for; then the mark they type (`@markdown`, `@agent_toolset`). Name the cases they hit (file vs section), not an internal verb (`extract`, `expand`, `invoke`).

**Pass**

- `@markdown` on a property loads prose from a matching document: **file** `{name}.md` beside the class, or **section** `## Name` in `{slug}.md`.

**Fail**

- Keep the prose next to the class; **extract** by label (folder, file, or section).
- `@agent_toolset` merges *AgentToolSet* onto the class.
- Live instance: **operations**, **instructions**, **tools**.

#### Guidance

**Create deep modules.** Group closely related classes around one domain concept. Give each module a narrow public interface with substantial implementation behind it so callers can understand the interface without reading the implementation. Avoid shallow modules that add another call without hiding a decision.

**Arrange dependencies one way.** Code that changes often may depend on code that changes rarely, but the stable module must not import its volatile caller. Break a cycle by moving the genuinely shared concept to a module both sides may depend on. Split a module that attracts unrelated callers along domain lines.

**Make every dependency explicit.** Use direct, visible references rather than globals, configuration magic, side effects, shared mutable state, or convention-based wiring. An implicit dependency is difficult to identify, replace in a test, or change safely.

Document only the **public seam** — why a caller would use it, how to use it, what they must honor, how to extend it, and what it depends on. Write like you are introducing a new concept: succinct, explanatory, job first. **Purpose** is the outcome a caller hires the module for, not that the folder has an empty `__init__.py` or that a decorator merges a class. One name per concept on the seam (prefer the type name — `Ability`, not `Ability, Abilities`). Write language for the terms you name. Follow `templates/modules.md` for the `module-context.md` headings and cards. Do not emit scan reports, session notes, or `_private` names.

The seam is what a caller **types** (`@agent_toolset`, `@agent_tool`, `@agent_instructions`, `@mcp`, `@markdown`, `tools(...)`). A runtime name nobody writes (`expand`, `invoke`, `install_to`, `destinations`, `extract`) is an internal — leave it out. Destination is the annotation (`@mcp`, `@skill`, `@hook`), not a property list. `@agent_instructions` *is* the **instructions** the agent follows at the end, not an `expand` call. `@markdown` is a **file** named after the property or a **section** titled after the property — say those two cases; do not say “extract by label.”

Do not inventory names with no job (“Live instance: operations, instructions…”). If you cannot say what a term *is* for a caller, omit it. Do not put **Sources / context** that only lists files inside this module folder — those are the subject, not a source. Cite **Sources / context** only for upstream evidence outside the folder (stories, grill, another module).

Never document internals in module-context. The caller-facing contract is the only thing that should survive into documentation; implementation details live in source code and session notes. If someone needs to read the internals to use the module, the interface is too shallow.

**When you correct `module-context.md`.** Every mistake found in that file — this pass or a later one — is a gap in this fidelity. Name the prohibition in modules Guidance or Rules in the **same turn** as the file fix. Do not patch only the artifact.

#### Scaffold

**When scaffolding only** (`/partition` or a names-only first cut, not full generation at this fidelity), follow this subsection. Do not use Guidance or Module rules below.

Rough module index for a **partition** pass or first cut — module paths, chunk files, seam terms, and thin dependency notes only. Formal one-way graph and full `module-context.md` wait for **modules** generate.

Key rules: `one-way-deps` — dependencies flow one direction only; no cycles; `domain-nouns-only` — module names are domain nouns or paths, never action verbs or `*Model`/`*Runtime` suffixes. Use **abd-code-research** (not raw file scraping) when the corpus is code.

**Stop reading this skill when scaffolding.**

#### Rules

```yaml
alwaysApply: false
globs: "**/module-context.md,**/*modules*.drawio,**/*-sketch.md"
```

Whenever you create, alter, or delete object-oriented boundaries and public seams across modules. Follow these rules.

**Form the module**

- `domain-nouns-only` — Name modules after domain concepts or paths, never action verbs or generic `*Model` and `*Runtime` suffixes. A technical container name does not tell callers which business knowledge it owns.
- `named-seam-and-constraint` — Name **Seam (terms)** and **Constraint** (what callers must or must not do). At modules do not require a Public API heading — that member dump is **model**.
- `modules-name-the-source-type` — Seam terms and Language headings use the type or annotation in source (`Hook`, `@Hook`). Do not rename a Destination to `*Mark`, invent an import path, or copy a Public API of operations into `module-context.md`. That dump belongs in the sibling `*-model.md`. A second name or a copied member list is a parallel model, and it will disagree with the code.
- `high-cohesion` — Group classes that share one purpose and the same domain concept, or else unrelated work will keep landing in the same module and every feature ends up editing it.
- `single-boundary` — Do not let another module hold, mutate, or duplicate this module’s concept. The two modules will drift, and every rule change has to be found and made in both.

**Shape the seam**

- `deep-module` — Keep most classes private (at most **40%** public) in each first-class module. A first-class module is a folder that owns `.context/module-context.md`. Nested folders that also own that file are separate modules — respect them. Nested folders that do not own it roll up to the nearest enclosing module-context folder, or to the folder you are querying if none sits in between. Count classes, not operations: a public method on a hidden class is not a second seam. Every public class is a signature you cannot change without editing every caller, so public classes are much harder to refactor than private ones.
- `abstraction-focus` — Name *what* the module does for callers, not internal steps or storage. A seam named after its implementation has to be renamed, with every caller updated, whenever the implementation changes.
- `purpose-before-mechanism` — Open each concept, Purpose, and seam term with the job a caller hires it for. A decorator, merge, mark, or storage choice is how — it never leads. Either say what the caller uses each concept for, or omit them.
- `public-seam-only` — Document only the public seam and dependencies on other modules. The seam is what a caller types (`@agent_instructions`, `tools(...)`). A runtime name nobody writes (`expand`, `invoke`, `install_to`) is an internal — leave it out. Do not document tests, scan reports, or session dumps. Do not put **Sources / context** that only lists files inside the module folder — those are the subject, not a source. Documented internals are misunderstood as public promises, and callers start writing code against them.
- `module-mistakes-feed-ce` — A mistake found in `module-context.md` is a gap in this fidelity. Write the prohibition into modules Guidance or Rules in the same pass as the file fix. Do not patch only the artifact.
- `use-typed-signatures` — Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.
- `general-purpose-surface` — Do not shape the seam for one caller’s UI or workflow. The second caller then either needs a near-duplicate operation or has to reshape its data to look like the first caller’s.
- `temporal-independence` — Leave the module valid after every public operation. Do not require a call order unless you document it, because an undocumented order fails on the first untested path.

**Define dependencies**

- `one-way-deps` — Make dependencies flow in one direction without cycles. A cycle prevents either module from changing or being tested independently.
- `low-coupling` — Depend only through other modules’ seams. Keep sibling imports few. Reaching past a seam freezes that module’s internals — it can no longer change them without breaking you.
- `layer-separation` — keep dependent modules at different levels of abstractions. Collapse pass-through modules — a module that only forwards turns every signature change into an edit in three files instead of one.
- `nesting` — Nest a child only when it shares mechanics or is a sub-system; keep independent modules flat. Put shared behavior on the parent. A child may depend on the parent, not on siblings.

---
### model

```yaml
default_format: python
stage: specification
```

#### Overview

**Other formats:** markdown for a language model and `drawio` through `model/drawio` for a class diagram. The same classes, operations, and relationships must appear in every selected representation.

Design the object model — the classes, what they remember and do, and how they relate.

#### Language

**When the user asks for language** rather than full generation at this fidelity, apply the top-level Language section. Do not use Guidance or Rules. **Stop reading this skill when writing language.**

#### Guidance

Analyze the source context to identify the concepts and operations the domain already names. Group concepts with their own identity, state, and behavior into **classes**. Model them **behaviors first and data second**: **properties** are noun phrases describing what an object remembers or derives from the state it already owns, and **operations** are verb phrases describing what it does. A derived property recalculates internally when read but still looks like a field to its caller; it takes no owner or state parameters. An `Order` calculates its own total; a `Cart` checks itself out. Do not invent a `Manager`, `Service`, `Helper`, or `Processor` to perform behavior owned by another object. A Service or Gateway that names a real external system is different: it represents that system's operations rather than holding displaced domain logic.

**Localize behavior to the object that owns the invariant.** Each object accesses its own state and enforces its own rules; do not write objects that manipulate another object's internal state. A route name, the actor in a Story, or the object named in Given does not determine ownership. Ask which object has the state and rule needed to complete the behavior. A customer route may still call `cart.checkout()` when Cart owns checkout; moving that operation to Customer or a `CheckoutManager` separates the rule from its state.

**Give each class one clear, focused responsibility.** When a class accumulates operations spanning different concerns, it reveals missing classes — split by the data each group of operations works with; that split surfaces the concept you had not named yet. Keep the public surface narrow: a few well-named operations that express intent, not a long list of methods covering every concern the system touches. A class that does everything is a class that changes for every feature, and a long seam forces every caller to pick from methods that were not written for their job.

**Find the operations.** Walk the source for the verbs this concept already performs — what a user or system asks it to do. An operation belongs on the class that owns the data it needs. Parameters are only what the object does not already hold; the return is what the caller must observe, not internals — parameters that duplicate state mean callers assemble what the object should already know, and returns that expose internals let callers depend on how you store things. Inside an operation, name **interactions** with other classes — specifically in other modules. Use the existing public seam named in those modules or create new ones that respect module boundaries. Add **invariants** — things that must stay true when the operation runs; an invariant you do not name here is a bug you only find once the body is written. 

**Get typing right.** Write a **property** when variation is data: a `type` field, not a new class. Write a **base class** when two or more types share identity, state, and operations. Write a **subtype** when a variant changes what the thing does, and record only the difference. Anywhere the base is used, the subtype must work in its place. Write an **interface** when multiple implementations share one public contract or when a domain object must describe an external dependency without importing its implementation.

**Make dependencies explicit.** Pass publicly accessible and swappable collaborators through the constructor — never reach for a global. A dependency you cannot see in the constructor cannot be swapped for a test double, and a global hides what the class actually needs to run.

**Name the relationships.** Add kind and cardinality. Choose kind by **ownership** and **identity**. **Write composition** when the owner completely owns the part and the part has no identity outside it — an airplane is composed of its wings, cockpit, and engine; the cockpit has no identity outside the plane. **Write aggregation** when the collector has no meaning without its members, but members keep their own identity — a fleet is an aggregate of planes. **Write association** when both sides are independent — a plane is driven by a pilot; the pilot has complete independence from the plane. The kind you pick here becomes the lifecycle in code — composition deletes the part with the owner, association does not — so the wrong kind means rewriting constructors, delete paths, and every caller that assumed the wrong ownership.

Extend module level **public seam** documentation — what callers invoke, what they must or must not do, and how to extend — plus **dependencies**: every other-module class or operation this module calls. See `@clean_engineering-modules`. Refresh the language for new or updated terms now on the public API. Do not document internal design, private participants, or implementation notes — documented internals read as promises, and callers write against them.

#### Interfaces

Use an interface when the model requires more than one implementation, when a caller must depend on a stable contract owned by another module, or when the domain describes access to an external system. Default to the concrete class when none of these conditions exists. A domain wrapper may name and represent the external type it wraps, but the external-system type must not import the domain wrapper or expose domain types; knowledge points from the domain toward the external contract, not back into the domain.


#### Rules

```yaml
alwaysApply: false
globs: "**/*-model.md,**/*-model.py,**/*example_factory*,**/*-sketch.md"
```

Whenever you create, alter, or delete types and how they relate, or change production code that those types support. Follow these rules.

If this change will not stay here, follow `practices/clean_engineering/modules.mdc`.

**Shape classes**
- `model-modules-follow-the-partition` — Use the module names and boundaries established by the partition artifact as the model's top-level modules. Change the partition before moving a model boundary, because otherwise the two artifacts describe different designs.
- `class-not-property-instance-or-subtype` — Before you write a new class, check property, instance, then subtype. Write a class only when none of those three fit. Multi-step work inside one operation usually belongs in private fields on the class that owns the operation, not in another class. Every new class is another type to construct, pass around, and keep in step with the rest; a property or subtype reuses one that already works.
- `keep-classes-single-responsibility` — Give each class one reason to change.
- `shape-classes-around-resources` — Model a class around the concept that owns the state and the rule, not a doer, handler, or service that acts on a data bag. A Payment has transactions, a source, and a destination, and it moves the money; it is not a `PaymentService` that takes a `PaymentData` object. A service-plus-bag pair splits the rule from its memory, so every change has to be found in two types and the bag cannot enforce anything.
- `put-logic-on-the-owning-resource` — Put logic on the object that owns the invariant. Do not infer ownership from a route name, Story actor, or Given subject: `client.accounts[id].transactions.last.validate()`, not `client.validateLastTransactionForPrimaryAccount()`. Logic placed away from its state gives two objects authority to change the same rule.
- `hide-inner-details` — Expose behavior through named operations. Do not let callers see how the class stores or arranges its data — once they read the storage directly it becomes a public contract you cannot change. Private fields on the same class hide implementation; you do not need a second class for that.
- `use-property-not-accessor` — Use a named property for stored or derived state. A derived property recalculates from state and collaborators the object already holds, takes no owner or state parameters, and looks like a field to callers through the language's property mechanism. Use an operation only when behavior coordinates several values, collaborators, or lifecycle steps and cannot be represented truthfully as a property. Callers should not need `getX`, `setX`, or storage knowledge. Read-only to callers can mean return a copy or immutable view from a property — it does not require a frozen class or a second type to hold build steps.
- `prefer-class-operations` — Put factory, lifecycle, and helpers used from one class on that class. Do not export them as module-level functions — a free function holds no state, so it takes the object as a parameter and reaches into it to do the work.
- `use-explicit-dependencies` — Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation.
- `external-system-interface-is-one-way` — Let a domain wrapper or collaborator depend on the named external-system contract. Keep the external type independent of domain wrappers and domain types, because a reverse dependency makes the external boundary depend on one caller's model.


**Define operations**
- `keep-operations-single-responsibility` — Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.
- `limit-operation-parameters` — Have callers pass intent, not setup. Prefer 0-2 parameters for domain operations; when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract.
- `avoid-vague-parameter-names` — Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.
- `errors-out-of-existence` — For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.
- `state-change-returns-record-or-named-failure` — When an operation coordinates a state change that cannot be one property assignment, return the resulting record or a failure named after the rejected rule. Decide at code fidelity whether that failure is a result type or domain exception, because callers need one explicit outcome contract.
- `domain-exception-carries-context` — Use a typed exception for a broken aggregate or repository operation. One exception type may cover that aggregate's operations when it carries the failed operation, the domain object or input already in hand, the user-facing message, and the underlying cause; do not return bare strings or untyped error objects because callers cannot handle them safely..
- `limit-comments` — write comment in operations and properties only when the signature cannot say a constraint or explain why the code behaves the way it does. Do not narrate a line that already names what it does.

**Invariants, interactions, and comments**

- `write-invariants` — Name a rule the object itself must keep true whenever it acts — a must, never, always, before, or after about its own state. Write one a caller can break by using the object wrong. Do not restate a type, a name, or a single operation’s happy path.
- `write-interactions` — Collaborate when this object cannot finish its job from its own state — another object owns the data or the next act. Ask that object to do the work so each keeps its own invariants; do not reach into its internals or steal its job. Ask through a named public operation on a collaborator you hold or are given. Do not point at a type, and do not invent a third object to mediate a conversation two objects can have.

**Names and reuse**

- `use-intention-revealing-names` — Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.
- `use-consistent-naming` — Use one word per concept. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`). Two words for one concept is how the same logic gets written twice — nobody searching for `fetch_` finds the `retrieve_` that already does the job.
- `eliminate-duplication` — Give repeated logic one canonical function. Every copy is another place the fix has to be repeated, and the copy you miss is the bug.
- `one-canonical-model-document` — Keep all modules for one model artifact in one canonical model document. Link diagrams and code to it rather than restating its classes in another design document, because parallel models become inconsistent.




### code

```yaml
default_format: python
stage: implementation
```

#### Overview

Write working production code — real persistence, services, and UI behind the public seams.

#### Guidance

Follow the idioms in [`../language-tools.md`](../language-tools.md).

Start by **Implementing the public surface.** Where the model asked for an interface, the class implements it in the same file and the interface stays public-only. Where it did not, continue to implement the class. Implement public properties and operations first; write out private members next — the seam the model named is the contract, and privates follow from what those operations need, not the other way around. Relationships keep the kind and cardinality already named. 

Make sure to **Implement real behavior.** Fill every empty body — a stub ships as a silent no-op and hides that the seam was never finished. Wire real persistence, services, and other-module seams — not stand-ins as the shipping path. Add helpers, named constants, and domain exceptions only when the implementation needs them; speculative helpers become APIs nobody asked for. Keep an existing interface as the seam; otherwise treat the class as the seam. 

When writing out code take care to **Fill out all interactions with real code.** Turn `-> collaborator.operation` notes into actual calls — have the object ask its collaborators to do the work; do not reach into their internals. A placeholder left in place means the module boundary was never exercised; reaching past the seam couples you to another module's internals. Drop the placeholder once the call is real.

**Honor invariants in the implementation.** Turn `// remaining budget never goes negative` comments into methods where you can; replace comments with explicit code. A comment-only invariant runs only if someone read it — explicit code runs on every path.

**Keep the code clean.** Give each operation one thing to do; keep it short and at one level of abstraction — do not mix orchestration with raw I/O, or a storage change drags through business logic. Name things so they say why they exist. Handle the failing or empty cases first and return — then write the main path flat. Do not bury the real work inside nested ifs. Name exceptions after the failure; never swallow them. Give magic numbers names. Keep the public surface the seam already designed: short, caller-facing, with substantial implementation behind it, still in the module folder.

**Skip the model only for a very small change** — fill a body, rename, extract a helper, honor an invariant already named. The language is already there; keep it current. When you start needing to model — a new class, a new responsibility, a new relationship, a new public seam, or a new concept — stop and go to **model**. See `@clean_engineering-model`. Then return to code and implement what the model now names. Do not grow a shadow model only in the implementation — code-only design drifts from the language and module-context, and the next reader cannot find what you decided.

**Refresh the language and the seam.** Keep class identity in the docstring; put member bullets on the members. Edit the same public-seam module-context — how to use it, what callers must honor, what it depends on. Never internals. Never a parallel file — two documents drift, and documented internals read as promises callers build against.



#### Rules

```yaml
alwaysApply: false
globs: "**/*.py,**/*.ts,**/*.tsx,**/*.js,**/*.java,**/*-sketch.md"
```

Whenever you create, alter, or delete production behavior — bodies, constructors, call sites — including code supported by a model or module map. Follow these rules.

If this change will not stay here, follow `practices/clean_engineering/model.mdc`.

**Implement the model**
- `hide-inner-details` — Expose behavior through named operations. Do not let callers see how the class stores or arranges its data — once they read the storage directly it becomes a public contract you cannot change. Private fields on the same class hide implementation; you do not need a second class for that. Read-only to callers can mean return a copy or immutable view from a property — it does not require a frozen class or a second type to hold build steps.
- `keep-operations-small-focused` — Keep each operation short enough to read as one thought — under 20 lines. When it grows, extract a private helper whose name says why that slice exists.
- `keep-operations-single-responsibility` — Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.
- `simplify-control-flow` — Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.
- `errors-out-of-existence` — For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.

**Names and reuse**
- `use-intention-revealing-names` — Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.
- `use-consistent-naming` — Use one word per concept. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`). Two words for one concept is how the same logic gets written twice — nobody searching for `fetch_` finds the `retrieve_` that already does the job.
- `provide-meaningful-context` — Give a number or literal a name that says why it is there (`SECONDS_PER_DAY`, not `86400`). Do not number variables (`item1`).
- `eliminate-duplication` — Give repeated logic one canonical function. Every copy is another place the fix has to be repeated, and the copy you miss is the bug.
- `no-legacy-api-after-refactor` — When you rename or reshape a public seam, update every caller — tests, dependencies, and adjacent modules — to the new API. Do not keep compatibility aliases, re-exports, or thin wrappers that preserve the old name.

**Errors / comments**
- `use-exceptions-properly` — Raise a domain exception that names the failure (`CartAlreadyCheckedOut`, not `Error` or a bare string). Catch the specific type you can handle. Do not use a bare `except`. A generic exception cannot be caught selectively, so the caller has to handle everything or nothing.
- `never-swallow-exceptions` — Do not catch and ignore. Log and re-raise, or convert to a domain exception that still names the failure. A `pass` in `except` hides a broken invariant.
- `limit-comments` — write comment in operations and properties only when the signature cannot say a constraint or explain why the code behaves the way it does. Do not narrate a line that already names what it does.


