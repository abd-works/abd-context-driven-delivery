Guide this action so the output conforms to this schema.

[module | package]

module:
  fidelity: modules
  id: dotPath
  name: string
  stereotypes?: [string]
  participants: [module | package | class | operation]
  dependsOn?: [module]
  usedBy?: [epic]
  where:
    - id is the name slugs from the root module to this module, joined by dots
    - name is a domain noun or a path
    - a nested module shares a base seam or is a sub-system
    - at most 40% of classes are public
    - dependencies flow one way, with no cycle
    - seam terms are what a caller types
    - purpose opens with the job a caller hires it for
  rules:
    - vocabulary-traces-to-source
    - do-not-invent-terms
    - do-not-invent-parallel-object-models
    - domain-nouns-only
    - named-seam-and-constraint
    - high-cohesion
    - no-module-per-class
    - single-boundary
    - deep-module
    - abstraction-focus
    - purpose-before-mechanism
    - public-seam-only
    - use-typed-signatures
    - general-purpose-surface
    - temporal-independence
    - one-way-deps
    - extensions-live-with-the-domain
    - low-coupling
    - layer-separation
    - missing-module-context
    - language-modules-one-section
    - modules-not-model-blocks

package:
  fidelity: modules
  id: dotPath
  name: string
  belongsTo: module
  participants: [class | package | module]
  where:
    - id is the module id, then this package name, joined by dots
    - a package groups classes inside a module

class:
  fidelity: model
  id: dotPath
  name: string
  belongsTo: module
  stereotypes?: [string]
  baseClass?: class
  dependsOn?: [class]
  relationships?: [relationship]
  demonstratedThrough?: [example | observation]
  participants: [operation | property]
  where:
    - id is the module id, then this class name, joined by dots
    - a class exists when a property, an instance, and a subtype do not fit
    - a subtype works wherever the base is used
    - collaborators arrive through the constructor
    - behavior sits on the object that owns the invariant
    - one reason to change
  rules:
    - model-modules-follow-the-partition
    - class-not-property-instance-or-subtype
    - no-prototype-swapping
    - keep-classes-single-responsibility
    - shape-classes-around-resources
    - put-logic-on-the-owning-resource
    - hide-inner-details
    - use-explicit-dependencies
    - external-system-interface-is-one-way
    - use-intention-revealing-names
    - use-consistent-naming
    - eliminate-duplication
    - one-canonical-model-document
    - no-redundant-relationship-paths
    - missing-module-context
    - language-modules-one-section
    - modules-not-model-blocks

relationship:
  fidelity: model
  id: dotPath
  kind: "composition" | "aggregation" | "association"
  target: class
  cardinality?: string
  where:
    - id is the class id, then kind, then the target class name, joined by dots
    - composition when the part has no identity outside the owner
    - aggregation when members keep their own identity
    - association when both sides stay independent
    - one canonical link per participant

operation:
  fidelity: model
  id: dotPath
  name: string
  belongsTo: class
  parameters: [parameter]
  returnType: class | string
  body?: string
  invokes: [operation | property]
  invokedBy?: [step | observation]
  invariants?: [invariant]
  where:
    - id is the class id, then this operation name, joined by dots
    - 0..3 parameters on a domain operation (self not counted)
    - one job
    - body under 20 statements
    - a state change returns the record or a failure named after the rejected rule
    - interactions call a named public operation on a collaborator
  rules:
    - keep-operations-single-responsibility
    - limit-operation-parameters
    - avoid-vague-parameter-names
    - errors-out-of-existence
    - state-change-returns-record-or-named-failure
    - domain-exception-carries-context
    - write-invariants
    - write-interactions
    - prefer-class-operations
    - prefer-instance-operations
    - keep-operations-small-focused
    - simplify-control-flow
    - use-exceptions-properly
    - never-swallow-exceptions
    - limit-comments
    - provide-meaningful-context
    - no-legacy-api-after-refactor

property:
  fidelity: model
  id: dotPath
  name: string
  belongsTo: class
  type: string
  value?: string
  hasType?: class
  invokes?: [operation | property]
  invariants?: [invariant]
  where:
    - id is the class id, then this property name, joined by dots
    - a derived property takes no owner or state parameter
    - a relationship stereotype on the property copies onto relationship.kind
  rules:
    - use-property-not-accessor
    - hide-inner-details

parameter:
  fidelity: model
  id: dotPath
  name: string
  belongsTo: operation
  type: string
  where:
    - id is the operation id, then this parameter name, joined by dots
    - the name says what the caller supplies
  rules:
    - avoid-vague-parameter-names
    - use-typed-signatures
    - use-intention-revealing-names

invariant:
  fidelity: model
  id: dotPath
  text: string
  belongsTo: [operation | property]
  where:
    - id is the owner id, then this text slug, joined by dots
    - a must, never, always, before, or after about this object's own state
  rules:
    - write-invariants
    - limit-comments

## Overview

Structure the problem into independent modules with small public interfaces, substantial hidden functionality, and one-way dependencies. Implement those modules with rigorous object-oriented and clean-code practices. When boundaries hold, a change stays inside one module; when they blur, callers depend on internal decisions and must change with them.

## Guidance

Partition first, then type the objects, then implement. Keep the same names in language, modules, model, and code — in prose, diagrams, and source.

#### Guidance

Analyze the source context to identify the concepts and operations the domain already names. Group concepts with their own identity, state, and behavior into **classes**. Model them **behaviors first and data second**: **properties** are noun phrases describing what an object remembers or derives from the state it already owns, and **operations** are verb phrases describing what it does. A derived property recalculates internally when read but still looks like a field to its caller; it takes no owner or state parameters. An `Order` calculates its own total; a `Cart` checks itself out. Do not invent a `Manager`, `Service`, `Helper`, or `Processor` to perform behavior owned by another object. A Service or Gateway that names a real external system is different: it represents that system's operations rather than holding displaced domain logic.

**Localize behavior to the object that owns the invariant.** Each object accesses its own state and enforces its own rules; do not write objects that manipulate another object's internal state. A route name, the actor in a Story, or the object named in Given does not determine ownership. Ask which object has the state and rule needed to complete the behavior. A customer route may still call `cart.checkout()` when Cart owns checkout; moving that operation to Customer or a `CheckoutManager` separates the rule from its state.

**Give each class one clear, focused responsibility.** When a class accumulates operations spanning different concerns, it reveals missing classes — split by the data each group of operations works with; that split surfaces the concept you had not named yet. Keep the public surface narrow: a few well-named operations that express intent, not a long list of methods covering every concern the system touches. A class that does everything is a class that changes for every feature, and a long seam forces every caller to pick from methods that were not written for their job.

**Find the operations.** Walk the source for the verbs this concept already performs — what a user or system asks it to do. An operation belongs on the class that owns the data it needs. Parameters are only what the object does not already hold; the return is what the caller must observe, not internals — parameters that duplicate state mean callers assemble what the object should already know, and returns that expose internals let callers depend on how you store things. Inside an operation, name **interactions** with other classes — specifically in other modules. Use the existing public seam named in those modules or create new ones that respect module boundaries. Add **invariants** — things that must stay true when the operation runs; an invariant you do not name here is a bug you only find once the body is written. 

**Get typing right.** Write a **property** when variation is data: a `type` field, not a new class. Write a **base class** when two or more types share identity, state, and operations. Write a **subtype** when a variant changes what the thing does, and record only the difference. Anywhere the base is used, the subtype must work in its place. Write an **interface** when multiple implementations share one public contract or when a domain object must describe an external dependency without importing its implementation.

**Make dependencies explicit.** Pass publicly accessible and swappable collaborators through the constructor — never reach for a global. A dependency you cannot see in the constructor cannot be swapped for a test double, and a global hides what the class actually needs to run.

**Name the relationships.** Add kind and cardinality. Choose kind by **ownership** and **identity**. **Write composition** when the owner completely owns the part and the part has no identity outside it — an airplane is composed of its wings, cockpit, and engine; the cockpit has no identity outside the plane. **Write aggregation** when the collector has no meaning without its members, but members keep their own identity — a fleet is an aggregate of planes. **Write association** when both sides are independent — a plane is driven by a pilot; the pilot has complete independence from the plane. The kind you pick here becomes the lifecycle in code — composition deletes the part with the owner, association does not — so the wrong kind means rewriting constructors, delete paths, and every caller that assumed the wrong ownership.

Extend module level **public seam** documentation — what callers invoke, what they must or must not do, and how to extend — plus **dependencies**: every other-module class or operation this module calls. See `@clean_engineering-modules`. Refresh the language for new or updated terms now on the public API. Do not document internal design, private participants, or implementation notes — documented internals read as promises, and callers write against them.

## Shared rules

```yaml
alwaysApply: false
globs: "**/*-sketch.md"
```

Use these rules whenever you name a concept, draw a dependency, or write a public seam — in prose, a diagram, or source.

- **`vocabulary-traces-to-source`** — Take every term from the source. The English term and the code name are the same word: *shopping cart* is `ShoppingCart`. When the code says a different word than the domain, every reader keeps a translation in their head, and the two names drift until they mean different things.
- **`do-not-invent-terms`** — Do not invent a second noun or a parallel vocabulary. A second noun for the same thing becomes a second class, and then the same rule has to be written and fixed in both.
- **`do-not-invent-parallel-object-models`** — Keep one object model. Follow the nouns and verbs the rest of the graph already uses for that concept. A class that joins types the rest of the graph keeps apart is a second model — a big ball of mud — and every rule then has to be written and fixed in both. Wrap or extend the live objects and name a wrapper after the type it represents; do not scrape the same data into a second `*Model` or `*Entry` family.

---

---
format: markdown
fidelity: all
---
<!--
  clean_engineering markdown template — unified across all fidelities.

  I{ClassName} is not the default. When generated, it lives in the same file /
  same module H1 as {ClassName} — public members only on I{ClassName}; private
  members stay on {ClassName}. Omit ## I{ClassName} unless the user asked or
  multiple implementations sit behind one seam.

  Fidelity tags on section headings (as HTML comments — informational only):
    L  = language (prose identity; refined at every stage — not a fidelity)
    Mu = modules        (thin terms, one-way deps, build order; no I{Class} yet)
    Md = model          (I{ClassName} — typed compact block — ONLY when an interface is
                         requested; otherwise model is the empty `## {ClassName}` block)
    C  = code           (fill {ClassName}; public filled, privates filled; drop interactions)

  Class member format (model):
    ------  (six dashes)   constructor / properties separator
    ----    (four dashes)  properties / operations separator
    -       (dash prefix)  private operation
    +       (plus prefix)  public — code fidelity only

  Invariants, interactions, comments (model):
    Write each invariant as `//` on the class (or under the property / operation
    it constrains): a must / never / always / before / after that stays true
    when the object acts.
    Write each interaction as `-> {collaborator}.{operation}` nested under the
    calling operation. `-> ClassName` alone is not an interaction.
    State an invariant or a sequence with `//`. Leave every other line
    uncommented.

  Put a class family in one file: the primary type, its subtypes, and
  tightly connected peers that only make sense together (element +
  collection, small aggregate + its part). Name the file after the family
  concept (`abilities.py` for Ability + Abilities). Split into another
  file only when a type is independently reused across families or the
  file becomes a grab-bag of unrelated types. Do not default to one class
  per file. Put `{Type}ExampleFactory` (and its examples data, plus
  `I{Type}ExampleFactory` when one was requested) in a sibling file —
  never in the production family file.

  Give each module its own folder. Put class files, markdown, and other
  module-level artifacts in that folder — not beside it, not in a flat
  dump. Not every folder is a module: treat a folder as a module only
  when it owns `.context/module-context.md`. Do not stop at an arbitrary
  depth — every folder that is a cohesive functional unit owns
  `module-context.md`. Absorb implementation-only folders (`assets/`,
  thin `config/`) into the parent description. Never put
  `module-context.md` under `.context/sessions/`.

  Document structure: H1 = module, H2 = class within that module.
  Interface (I{ClassName}) and implementation ({ClassName}) both sit under the
  same module H1 — interface first, then implementation. No fidelity section
  headers (## Model fidelity / ## Code fidelity) in the output.
  At modules, language is the first lines under each `# {path}` card.
  Do not emit `## Language` or `## Modules` above those cards.
  At modules fidelity, stop after Purpose / Seam / Dependencies / Constraint.
  Do not emit ## {ClassName} typed compact blocks, *is a type of*,
  Child : Parent, Sources/context of this folder's own files, scan dumps,
  or runtime names nobody types (expand, invoke, install_to).
  Those wait for model, or they are internals — omit them.

  Write human-readable markdown only. Strip template markup (`<!-- Mu -->`,
  `<!-- Mv -->`, `<!-- L -->`, `<!-- Md -->`, `<!-- C -->`, and similar)
  before writing. At modules, sit the language immediately under `# {path}`,
  then the `- **Purpose:**` block.

  Subtypes use ## {ChildClass} : {ClassName} notation; deltas only.
  Substitute {ClassName} / {owned_property} / {param} / {Type} / ... when generating.
-->

## Language                                                       <!-- L, Mu — one section; do not add ## Modules -->

*{ClassName}* is {the job a caller hires it for — then what it holds and does.
This paragraph IS the class definition. Identity and purpose. Not a decorator or merge.} <!-- L -->

### {class_name_as_a_concept}                                     <!-- L, Mu -->

- {bullet: why a caller uses this (the outcome), then the mechanic if needed, then how it relates to *another class*} <!-- L -->
- {as many bullets as the concept warrants}                       <!-- L -->
- **Invariant:** {rule that must always hold — only when one exists} <!-- L -->

### {ChildClass}                                                  <!-- L, Mu — own heading; no *is a type of* at modules -->

- {why a caller uses this — same shape as any other concept}      <!-- L, Mu -->

<!-- omit from module-context.md: *is a type of* is model language -->

Build order: `{first}` → `{second}` → `{third}`                   <!-- Mu -->

---

# {module_path}                                                   <!-- Mu -->

- **Purpose:** {the job a caller hires this module for — not how it is wired} <!-- Mu -->
- **Seam (terms):** {ClassName}, {ChildClass}, ...                <!-- Mu -->
- **Dependencies (one-way):** {other_module}, ...                 <!-- Mu -->

## Constraint                                                    <!-- Mu -->

{what callers must or must not do at this seam — the marks they type, not runtime names they never write}

<!-- MODULES STOPS HERE. Do not copy the typed blocks below into module-context.md. -->

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
	// {must / never / always / before / after that stays true of the object}
------
+ << composition >> {owned_property}: {Type}
	// {must / never / always / before / after about this property}
+ << aggregation >> {collected_property}: list[{Type}]
+ << association >> {referenced_property}: {Type}
----
+ {operation_name}({param}: {Type}): {ReturnType}
	// {must / never / always / before / after when this operation runs}
	-> {collaborator}.{operation}
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
	// {must / never / always / before / after about this property}
----
+ {delta_operation}({param}: {Type}): {ReturnType}

---

# {next_module_path}                                              <!-- Mu -->

- **Purpose:** {the job a caller hires this module for}
- **Seam (terms):** {ClassName}, ...
- **Dependencies (one-way):** *(none)*

## Constraint                                                    <!-- Mu -->

{what callers must or must not do}

<!-- MODULES STOPS HERE. -->

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

Guide this action so the output conforms to this schema.

[module | package]

module:
  fidelity: modules
  id: dotPath
  name: string
  stereotypes?: [string]
  participants: [module | package | class | operation]
  dependsOn?: [module]
  usedBy?: [epic]
  where:
    - id is the name slugs from the root module to this module, joined by dots
    - name is a domain noun or a path
    - a nested module shares a base seam or is a sub-system
    - at most 40% of classes are public
    - dependencies flow one way, with no cycle
    - seam terms are what a caller types
    - purpose opens with the job a caller hires it for
  rules:
    - vocabulary-traces-to-source
    - do-not-invent-terms
    - do-not-invent-parallel-object-models
    - domain-nouns-only
    - named-seam-and-constraint
    - high-cohesion
    - no-module-per-class
    - single-boundary
    - deep-module
    - abstraction-focus
    - purpose-before-mechanism
    - public-seam-only
    - use-typed-signatures
    - general-purpose-surface
    - temporal-independence
    - one-way-deps
    - extensions-live-with-the-domain
    - low-coupling
    - layer-separation
    - missing-module-context
    - language-modules-one-section
    - modules-not-model-blocks

package:
  fidelity: modules
  id: dotPath
  name: string
  belongsTo: module
  participants: [class | package | module]
  where:
    - id is the module id, then this package name, joined by dots
    - a package groups classes inside a module

class:
  fidelity: model
  id: dotPath
  name: string
  belongsTo: module
  stereotypes?: [string]
  baseClass?: class
  dependsOn?: [class]
  relationships?: [relationship]
  demonstratedThrough?: [example | observation]
  participants: [operation | property]
  where:
    - id is the module id, then this class name, joined by dots
    - a class exists when a property, an instance, and a subtype do not fit
    - a subtype works wherever the base is used
    - collaborators arrive through the constructor
    - behavior sits on the object that owns the invariant
    - one reason to change
  rules:
    - model-modules-follow-the-partition
    - class-not-property-instance-or-subtype
    - no-prototype-swapping
    - keep-classes-single-responsibility
    - shape-classes-around-resources
    - put-logic-on-the-owning-resource
    - hide-inner-details
    - use-explicit-dependencies
    - external-system-interface-is-one-way
    - use-intention-revealing-names
    - use-consistent-naming
    - eliminate-duplication
    - one-canonical-model-document
    - no-redundant-relationship-paths
    - missing-module-context
    - language-modules-one-section
    - modules-not-model-blocks

relationship:
  fidelity: model
  id: dotPath
  kind: "composition" | "aggregation" | "association"
  target: class
  cardinality?: string
  where:
    - id is the class id, then kind, then the target class name, joined by dots
    - composition when the part has no identity outside the owner
    - aggregation when members keep their own identity
    - association when both sides stay independent
    - one canonical link per participant

operation:
  fidelity: model
  id: dotPath
  name: string
  belongsTo: class
  parameters: [parameter]
  returnType: class | string
  body?: string
  invokes: [operation | property]
  invokedBy?: [step | observation]
  invariants?: [invariant]
  where:
    - id is the class id, then this operation name, joined by dots
    - 0..3 parameters on a domain operation (self not counted)
    - one job
    - body under 20 statements
    - a state change returns the record or a failure named after the rejected rule
    - interactions call a named public operation on a collaborator
  rules:
    - keep-operations-single-responsibility
    - limit-operation-parameters
    - avoid-vague-parameter-names
    - errors-out-of-existence
    - state-change-returns-record-or-named-failure
    - domain-exception-carries-context
    - write-invariants
    - write-interactions
    - prefer-class-operations
    - prefer-instance-operations
    - keep-operations-small-focused
    - simplify-control-flow
    - use-exceptions-properly
    - never-swallow-exceptions
    - limit-comments
    - provide-meaningful-context
    - no-legacy-api-after-refactor

property:
  fidelity: model
  id: dotPath
  name: string
  belongsTo: class
  type: string
  value?: string
  hasType?: class
  invokes?: [operation | property]
  invariants?: [invariant]
  where:
    - id is the class id, then this property name, joined by dots
    - a derived property takes no owner or state parameter
    - a relationship stereotype on the property copies onto relationship.kind
  rules:
    - use-property-not-accessor
    - hide-inner-details

parameter:
  fidelity: model
  id: dotPath
  name: string
  belongsTo: operation
  type: string
  where:
    - id is the operation id, then this parameter name, joined by dots
    - the name says what the caller supplies
  rules:
    - avoid-vague-parameter-names
    - use-typed-signatures
    - use-intention-revealing-names

invariant:
  fidelity: model
  id: dotPath
  text: string
  belongsTo: [operation | property]
  where:
    - id is the owner id, then this text slug, joined by dots
    - a must, never, always, before, or after about this object's own state
  rules:
    - write-invariants
    - limit-comments

## Overview

Structure the problem into independent modules with small public interfaces, substantial hidden functionality, and one-way dependencies. Implement those modules with rigorous object-oriented and clean-code practices. When boundaries hold, a change stays inside one module; when they blur, callers depend on internal decisions and must change with them.

## Guidance

Partition first, then type the objects, then implement. Keep the same names in language, modules, model, and code — in prose, diagrams, and source.

## Shared rules

```yaml
alwaysApply: false
globs: "**/*-sketch.md"
```

Use these rules whenever you name a concept, draw a dependency, or write a public seam — in prose, a diagram, or source.

- **`vocabulary-traces-to-source`** — Take every term from the source. The English term and the code name are the same word: *shopping cart* is `ShoppingCart`. When the code says a different word than the domain, every reader keeps a translation in their head, and the two names drift until they mean different things.
- **`do-not-invent-terms`** — Do not invent a second noun or a parallel vocabulary. A second noun for the same thing becomes a second class, and then the same rule has to be written and fixed in both.
- **`do-not-invent-parallel-object-models`** — Keep one object model. Follow the nouns and verbs the rest of the graph already uses for that concept. A class that joins types the rest of the graph keeps apart is a second model — a big ball of mud — and every rule then has to be written and fixed in both. Wrap or extend the live objects and name a wrapper after the type it represents; do not scrape the same data into a second `*Model` or `*Entry` family.

---

#### Overview

Partition a problem into independently understandable units — name each unit, its public seam, and its one-way dependencies.

Each **module** is a named structural boundary that groups closely related classes — and optionally smaller modules — into a single cohesive unit. Modules can be composed of other modules; a highly complex and nested module can be thought of as a sub-system.

#### Guidance

**Create deep modules.** Group closely related classes around one domain concept. Give each module a narrow public interface with substantial implementation behind it so callers can understand the interface without reading the implementation. Avoid shallow modules that add another call without hiding a decision.

**Do not mint a module per class.** One package per class is the same mistake as one bounded context per aggregate — folder noise without a real seam. When a bounded context (especially a new consolidated view) has only a handful of collaborating types, keep **one module** for the whole context and place the classes inside it. Split into separate modules only when change rate, team ownership, or coupling genuinely diverges; several public classes in one module is normal.

**Arrange dependencies one way.** Code that changes often may depend on code that changes rarely, but the stable module must not import its volatile caller. Break a cycle by moving the genuinely shared concept to a module both sides may depend on. Split a module that attracts unrelated callers along domain lines.

**Make every dependency explicit.** Use direct, visible references rather than globals, configuration magic, side effects, shared mutable state, or convention-based wiring. An implicit dependency is difficult to identify, replace in a test, or change safely.

Document only the **public seam** — why a caller would use it, how to use it, what they must honor, how to extend it, and what it depends on. Write like you are introducing a new concept: succinct, explanatory, job first. **Purpose** is the outcome a caller hires the module for, not that the folder has an empty `__init__.py` or that a decorator merges a class. One name per concept on the seam (prefer the type name — `Ability`, not `Ability, Abilities`). Write language for the terms you name. Follow `templates/modules.md` for the `module-context.md` headings and cards. Do not emit scan reports, session notes, or `_private` names.

The seam is what a caller **types** (`@agent_toolset`, `@agent_tool`, `@agent_instructions`, `@mcp`, `@markdown`, `tools(...)`). A runtime name nobody writes (`expand`, `invoke`, `install_to`, `destinations`, `extract`) is an internal — leave it out. Destination is the annotation (`@mcp`, `@skill`, `@hook`), not a property list. `@agent_instructions` *is* the **instructions** the agent follows at the end, not an `expand` call. `@markdown` is a **file** named after the property or a **section** titled after the property — say those two cases; do not say “extract by label.”

Do not inventory names with no job (“Live instance: operations, instructions…”). If you cannot say what a term *is* for a caller, omit it. Do not put **Sources / context** that only lists files inside this module folder — those are the subject, not a source. Cite **Sources / context** only for upstream evidence outside the folder (stories, grill, another module).

Never document internals in module-context. The caller-facing contract is the only thing that should survive into documentation; implementation details live in source code and session notes. If someone needs to read the internals to use the module, the interface is too shallow.

**When you correct `module-context.md`.** Every mistake found in that file — this pass or a later one — is a gap in this fidelity. Name the prohibition in modules Guidance or Rules in the **same turn** as the file fix. Do not patch only the artifact.

#### Rules

```yaml
alwaysApply: false
globs: "**/module-context.md,**/*modules*.drawio,**/*-sketch.md"
```

Whenever you create, alter, or delete object-oriented boundaries and public seams across modules. Follow these rules.

**Form the module**

- `domain-nouns-only` — Name modules after domain concepts or paths, never action verbs or generic `*Model` and `*Runtime` suffixes. A technical container name does not tell callers which business knowledge it owns.
- `named-seam-and-constraint` — Name **Seam (terms)** and **Constraint** (what callers must or must not do). At modules do not require a Public API heading — that member dump is **model**.
- `high-cohesion` — Group classes that share one purpose and the same domain concept, or else unrelated work will keep landing in the same module and every feature ends up editing it.
- `no-module-per-class` — A module groups multiple cohesive classes. One folder or package per class is an anti-pattern unless each class is a genuinely independent subsystem. When sketching with DDD, a small bounded context is usually **one module** with several entities inside — not one module per aggregate root.
- `single-boundary` — Do not let another module hold, mutate, or duplicate this module’s concept. The two modules will drift, and every rule change has to be found and made in both.

**Shape the seam**

- `deep-module` — Keep most classes private (at most **40%** public) in each first-class module. A first-class module is a folder that owns `.context/module-context.md`. Nested folders that also own that file are separate modules — respect them. Nested folders that do not own it roll up to the nearest enclosing module-context folder, or to the folder you are querying if none sits in between. Count classes, not operations: a public method on a hidden class is not a second seam. Every public class is a signature you cannot change without editing every caller, so public classes are much harder to refactor than private ones.
- `abstraction-focus` — Name *what* the module does for callers, not internal steps or storage. A seam named after its implementation has to be renamed, with every caller updated, whenever the implementation changes.
- `language-opens-the-card` — Language is the first lines under `# {path}`. Do not add `## Language` or `## Modules`. A section above the cards splits the words from the module they name.
- `purpose-before-mechanism` — Open each concept, Purpose, and seam term with the job a caller hires it for. A decorator, merge, mark, or storage choice is how — it never leads. Either say what the caller uses each concept for, or omit them.
- `public-seam-only` — Document only the public seam and dependencies on other modules. The seam is what a caller types (`@agent_instructions`, `tools(...)`). A runtime name nobody writes (`expand`, `invoke`, `install_to`) is an internal — leave it out. Do not document tests, scan reports, or session dumps. Do not put **Sources / context** that only lists files inside the module folder — those are the subject, not a source. Documented internals are misunderstood as public promises, and callers start writing code against them.
- `use-typed-signatures` — Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.
- `general-purpose-surface` — Do not shape the seam for one caller’s UI or workflow. The second caller then either needs a near-duplicate operation or has to reshape its data to look like the first caller’s.
- `temporal-independence` — Leave the module valid after every public operation. Do not require a call order unless you document it, because an undocumented order fails on the first untested path.

**Define dependencies**

- `one-way-deps` — Make dependencies flow in one direction without cycles. A cycle prevents either module from changing or being tested independently.
- `extensions-live-with-the-domain` — Domain extensions of a framework belong in the domain module — a nested package under that domain is fine. Do not host them in the base framework package. `GraphEpic` lives with Stories, not in Knowledge Graph; otherwise the framework depends on every practice and cannot stay generic.
- `low-coupling` — Depend only through other modules’ seams. Keep sibling imports few. Reaching past a seam freezes that module’s internals — it can no longer change them without breaking you.
- `layer-separation` — keep dependent modules at different levels of abstractions. Collapse pass-through modules — a module that only forwards turns every signature change into an edit in three files instead of one.

---

#### Template

---
format: markdown
fidelity: modules
---
<!--
  clean_engineering markdown template — modules fidelity (`module-context.md`).

  Substitute {Root} / {Concept} / {module_path} / ... when generating.
  This file stops after Purpose, Seam, Dependencies, Constraint. Typed class
  blocks and I{ClassName} live in templates/clean_engineering.md at **model**.

  - `no-subtype-at-modules` — In `module-context.md`, every concept is its own
    heading. Do not write `*is a type of*` or `Child : Parent`. Generalisation
    waits for **model**. An is-a heading here freezes a type hierarchy before
    the object model exists, and the same split has to be rewritten when the
    model names it.
  - `modules-not-model-blocks` — At modules, do not write typed `+ ClassName()` /
    `------` / `+ operation()` dumps. Those wait for **model**. Modules stop at
    Purpose, Seam, Dependencies, Constraint. A dump here is a second object
    model in prose, and the markdown and the later class blocks will disagree.
  - `language-opens-the-card` — Language is the first lines under `# {path}`.
    Do not add `## Language` or `## Modules`. A section above the cards splits
    the words from the module they name.

  Write human-readable markdown only. Sit the language immediately under the
  module heading — no blank line — then the Purpose block.
-->

# {module_path}
*{Concept}* is {the job a caller hires it for — then what it holds and does.
These lines ARE the definition. Identity and purpose. Not a decorator or merge.}

{Another sentence naming the next term a caller uses, and the mark they type.}

- **Purpose:** {the job a caller hires this module for — not how it is wired}
- **Seam (terms):** {Concept}, {AnotherConcept}, ...
- **Dependencies (one-way):** {other_module}, ...

## Constraint

{what callers must or must not do at this seam — the marks they type, not runtime names they never write}

Guide this action so the output conforms to this schema.

[module | package]

module:
  fidelity: modules
  id: dotPath
  name: string
  stereotypes?: [string]
  participants: [module | package | class | operation]
  dependsOn?: [module]
  usedBy?: [epic]
  where:
    - id is the name slugs from the root module to this module, joined by dots
    - name is a domain noun or a path
    - a nested module shares a base seam or is a sub-system
    - at most 40% of classes are public
    - dependencies flow one way, with no cycle
    - seam terms are what a caller types
    - purpose opens with the job a caller hires it for
  rules:
    - vocabulary-traces-to-source
    - do-not-invent-terms
    - do-not-invent-parallel-object-models
    - domain-nouns-only
    - named-seam-and-constraint
    - high-cohesion
    - no-module-per-class
    - single-boundary
    - deep-module
    - abstraction-focus
    - purpose-before-mechanism
    - public-seam-only
    - use-typed-signatures
    - general-purpose-surface
    - temporal-independence
    - one-way-deps
    - extensions-live-with-the-domain
    - low-coupling
    - layer-separation
    - missing-module-context
    - language-modules-one-section
    - modules-not-model-blocks

package:
  fidelity: modules
  id: dotPath
  name: string
  belongsTo: module
  participants: [class | package | module]
  where:
    - id is the module id, then this package name, joined by dots
    - a package groups classes inside a module

class:
  fidelity: model
  id: dotPath
  name: string
  belongsTo: module
  stereotypes?: [string]
  baseClass?: class
  dependsOn?: [class]
  relationships?: [relationship]
  demonstratedThrough?: [example | observation]
  participants: [operation | property]
  where:
    - id is the module id, then this class name, joined by dots
    - a class exists when a property, an instance, and a subtype do not fit
    - a subtype works wherever the base is used
    - collaborators arrive through the constructor
    - behavior sits on the object that owns the invariant
    - one reason to change
  rules:
    - model-modules-follow-the-partition
    - class-not-property-instance-or-subtype
    - no-prototype-swapping
    - keep-classes-single-responsibility
    - shape-classes-around-resources
    - put-logic-on-the-owning-resource
    - hide-inner-details
    - use-explicit-dependencies
    - external-system-interface-is-one-way
    - use-intention-revealing-names
    - use-consistent-naming
    - eliminate-duplication
    - one-canonical-model-document
    - no-redundant-relationship-paths
    - missing-module-context
    - language-modules-one-section
    - modules-not-model-blocks

relationship:
  fidelity: model
  id: dotPath
  kind: "composition" | "aggregation" | "association"
  target: class
  cardinality?: string
  where:
    - id is the class id, then kind, then the target class name, joined by dots
    - composition when the part has no identity outside the owner
    - aggregation when members keep their own identity
    - association when both sides stay independent
    - one canonical link per participant

operation:
  fidelity: model
  id: dotPath
  name: string
  belongsTo: class
  parameters: [parameter]
  returnType: class | string
  body?: string
  invokes: [operation | property]
  invokedBy?: [step | observation]
  invariants?: [invariant]
  where:
    - id is the class id, then this operation name, joined by dots
    - 0..3 parameters on a domain operation (self not counted)
    - one job
    - body under 20 statements
    - a state change returns the record or a failure named after the rejected rule
    - interactions call a named public operation on a collaborator
  rules:
    - keep-operations-single-responsibility
    - limit-operation-parameters
    - avoid-vague-parameter-names
    - errors-out-of-existence
    - state-change-returns-record-or-named-failure
    - domain-exception-carries-context
    - write-invariants
    - write-interactions
    - prefer-class-operations
    - prefer-instance-operations
    - keep-operations-small-focused
    - simplify-control-flow
    - use-exceptions-properly
    - never-swallow-exceptions
    - limit-comments
    - provide-meaningful-context
    - no-legacy-api-after-refactor

property:
  fidelity: model
  id: dotPath
  name: string
  belongsTo: class
  type: string
  value?: string
  hasType?: class
  invokes?: [operation | property]
  invariants?: [invariant]
  where:
    - id is the class id, then this property name, joined by dots
    - a derived property takes no owner or state parameter
    - a relationship stereotype on the property copies onto relationship.kind
  rules:
    - use-property-not-accessor
    - hide-inner-details

parameter:
  fidelity: model
  id: dotPath
  name: string
  belongsTo: operation
  type: string
  where:
    - id is the operation id, then this parameter name, joined by dots
    - the name says what the caller supplies
  rules:
    - avoid-vague-parameter-names
    - use-typed-signatures
    - use-intention-revealing-names

invariant:
  fidelity: model
  id: dotPath
  text: string
  belongsTo: [operation | property]
  where:
    - id is the owner id, then this text slug, joined by dots
    - a must, never, always, before, or after about this object's own state
  rules:
    - write-invariants
    - limit-comments

## Overview

Structure the problem into independent modules with small public interfaces, substantial hidden functionality, and one-way dependencies. Implement those modules with rigorous object-oriented and clean-code practices. When boundaries hold, a change stays inside one module; when they blur, callers depend on internal decisions and must change with them.

## Guidance

Partition first, then type the objects, then implement. Keep the same names in language, modules, model, and code — in prose, diagrams, and source.

## Shared rules

```yaml
alwaysApply: false
globs: "**/*-sketch.md"
```

Use these rules whenever you name a concept, draw a dependency, or write a public seam — in prose, a diagram, or source.

- **`vocabulary-traces-to-source`** — Take every term from the source. The English term and the code name are the same word: *shopping cart* is `ShoppingCart`. When the code says a different word than the domain, every reader keeps a translation in their head, and the two names drift until they mean different things.
- **`do-not-invent-terms`** — Do not invent a second noun or a parallel vocabulary. A second noun for the same thing becomes a second class, and then the same rule has to be written and fixed in both.
- **`do-not-invent-parallel-object-models`** — Keep one object model. Follow the nouns and verbs the rest of the graph already uses for that concept. A class that joins types the rest of the graph keeps apart is a second model — a big ball of mud — and every rule then has to be written and fixed in both. Wrap or extend the live objects and name a wrapper after the type it represents; do not scrape the same data into a second `*Model` or `*Entry` family.

---

#### Overview

**Other formats:** markdown for a language model and `drawio` through `model/drawio` for a class diagram. The same classes, operations, and relationships must appear in every selected representation.

Design the object model — the classes, what they remember and do, and how they relate.

#### Guidance

Analyze the source context to identify the concepts and operations the domain already names. Group concepts with their own identity, state, and behavior into **classes**. Model them **behaviors first and data second**: **properties** are noun phrases describing what an object remembers or derives from the state it already owns, and **operations** are verb phrases describing what it does. A derived property recalculates internally when read but still looks like a field to its caller; it takes no owner or state parameters. An `Order` calculates its own total; a `Cart` checks itself out. Do not invent a `Manager`, `Service`, `Helper`, or `Processor` to perform behavior owned by another object. A Service or Gateway that names a real external system is different: it represents that system's operations rather than holding displaced domain logic.

**Localize behavior to the object that owns the invariant.** Each object accesses its own state and enforces its own rules; do not write objects that manipulate another object's internal state. A route name, the actor in a Story, or the object named in Given does not determine ownership. Ask which object has the state and rule needed to complete the behavior. A customer route may still call `cart.checkout()` when Cart owns checkout; moving that operation to Customer or a `CheckoutManager` separates the rule from its state.

**Give each class one clear, focused responsibility.** When a class accumulates operations spanning different concerns, it reveals missing classes — split by the data each group of operations works with; that split surfaces the concept you had not named yet. Keep the public surface narrow: a few well-named operations that express intent, not a long list of methods covering every concern the system touches. A class that does everything is a class that changes for every feature, and a long seam forces every caller to pick from methods that were not written for their job.

**Find the operations.** Walk the source for the verbs this concept already performs — what a user or system asks it to do. An operation belongs on the class that owns the data it needs. Parameters are only what the object does not already hold; the return is what the caller must observe, not internals — parameters that duplicate state mean callers assemble what the object should already know, and returns that expose internals let callers depend on how you store things. Inside an operation, name **interactions** with other classes — specifically in other modules. Use the existing public seam named in those modules or create new ones that respect module boundaries. Add **invariants** — things that must stay true when the operation runs; an invariant you do not name here is a bug you only find once the body is written. 

**Get typing right.** Write a **property** when variation is data: a `type` field, not a new class. Write a **base class** when two or more types share identity, state, and operations. Write a **subtype** when a variant changes what the thing does, and record only the difference. Anywhere the base is used, the subtype must work in its place. Write an **interface** when multiple implementations share one public contract or when a domain object must describe an external dependency without importing its implementation.

**Make dependencies explicit.** Pass publicly accessible and swappable collaborators through the constructor — never reach for a global. A dependency you cannot see in the constructor cannot be swapped for a test double, and a global hides what the class actually needs to run.

**Name the relationships.** Add kind and cardinality. Choose kind by **ownership** and **identity**. **Write composition** when the owner completely owns the part and the part has no identity outside it — an airplane is composed of its wings, cockpit, and engine; the cockpit has no identity outside the plane. **Write aggregation** when the collector has no meaning without its members, but members keep their own identity — a fleet is an aggregate of planes. **Write association** when both sides are independent — a plane is driven by a pilot; the pilot has complete independence from the plane. The kind you pick here becomes the lifecycle in code — composition deletes the part with the owner, association does not — so the wrong kind means rewriting constructors, delete paths, and every caller that assumed the wrong ownership.

Extend module level **public seam** documentation — what callers invoke, what they must or must not do, and how to extend — plus **dependencies**: every other-module class or operation this module calls. See `@clean_engineering-modules`. Refresh the language for new or updated terms now on the public API. Do not document internal design, private participants, or implementation notes — documented internals read as promises, and callers write against them.

#### Rules

```yaml
alwaysApply: false
globs: "**/*-model.md,**/*-model.py,**/*example_factory*,**/*-sketch.md"
```

Whenever you create, alter, or delete types and how they relate, or change production code that those types support. Follow these rules.

If this change will not stay here, follow `practices/clean-engineering/clean-engineering-modules.mdc`.

**Shape classes**
- `model-modules-follow-the-partition` — Use the module names and boundaries established by the partition artifact as the model's top-level modules. Change the partition before moving a model boundary, because otherwise the two artifacts describe different designs.
- `class-not-property-instance-or-subtype` — Before you write a new class, check property, instance, then subtype. Write a class only when none of those three fit. Multi-step work inside one operation usually belongs in private fields on the class that owns the operation, not in another class. Every new class is another type to construct, pass around, and keep in step with the rest; a property or subtype reuses one that already works.
- `keep-classes-single-responsibility` — Give each class one reason to change.
- `shape-classes-around-resources` — Model a class around the concept that owns the state and the rule, not a doer, handler, or service that acts on a data bag. A Payment has transactions, a source, and a destination, and it moves the money; it is not a `PaymentService` that takes a `PaymentData` object. A service-plus-bag pair splits the rule from its memory, so every change has to be found in two types and the bag cannot enforce anything. Two resources may collaborate — a model that loads a Module is not a service-plus-bag split.
- `put-logic-on-the-owning-resource` — Put logic on the object that owns the invariant. Do not infer ownership from a route name, Story actor, or Given subject: `client.accounts[id].transactions.last.validate()`, not `client.validateLastTransactionForPrimaryAccount()`. Logic placed away from its state gives two objects authority to change the same rule.
- `hide-inner-details` — Expose behavior through named operations. Do not let callers see how the class stores or arranges its data — once they read the storage directly it becomes a public contract you cannot change. Private fields on the same class hide implementation; you do not need a second class for that.
- `use-property-not-accessor` — Use a named property for stored or derived state. A derived property recalculates from state and collaborators the object already holds, takes no owner or state parameters, and looks like a field to callers through the language's property mechanism. Use an operation only when behavior coordinates several values, collaborators, or lifecycle steps and cannot be represented truthfully as a property. Callers should not need `getX`, `setX`, or storage knowledge. Read-only to callers can mean return a copy or immutable view from a property — it does not require a frozen class or a second type to hold build steps.
- `prefer-class-operations` — Put factory, lifecycle, and helpers used from one class on that class. Do not export them as module-level functions — a free function holds no state, so it takes the object as a parameter and reaches into it to do the work. A file of hanging functions is the same miss: those operations belong on a type, not on the package.
- `use-explicit-dependencies` — Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation.
- `external-system-interface-is-one-way` — Let a domain wrapper or collaborator depend on the named external-system contract. Keep the external type independent of domain wrappers and domain types, because a reverse dependency makes the external boundary depend on one caller's model.


**Define operations**
- `keep-operations-single-responsibility` — Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.
- `limit-operation-parameters` — Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.
- `avoid-vague-parameter-names` — Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.
- `errors-out-of-existence` — For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.
- `state-change-returns-record-or-named-failure` — When an operation coordinates a state change that cannot be one property assignment, return the resulting record or a failure named after the rejected rule. Decide at code fidelity whether that failure is a result type or domain exception, because callers need one explicit outcome contract.
- `domain-exception-carries-context` — Use a typed exception for a broken aggregate or repository operation. One exception type may cover that aggregate's operations when it carries the failed operation, the domain object or input already in hand, the user-facing message, and the underlying cause; do not return bare strings or untyped error objects because callers cannot handle them safely..
- `limit-comments` — write comment in operations and properties only when the signature cannot say a constraint or explain why the code behaves the way it does. Do not narrate a line that already names what it does.

**Invariants, interactions, and comments**

- `write-invariants` — Name a rule the object itself must keep true whenever it acts — a must, never, always, before, or after about its own state. Write one a caller can break by using the object wrong. Do not restate a type, a name, or a single operation’s happy path.
- `write-interactions` — Collaborate when this object cannot finish its job from its own state — another object owns the data or the next act. Ask that object to do the work so each keeps its own invariants; do not reach into its internals or steal its job. Ask through a named public operation on a collaborator you hold or are given. Do not point at a type, and do not invent a third object to mediate a conversation two objects can have.
- `no-redundant-relationship-paths` — Before you add an association, walk the paths already in the cluster. Each real participant gets one canonical link — not parallel wires through types that collapse to the same thing (`Client` and `ClientIdentity`, or `OfferChannel` on **Offer** and again on an event the offer just emitted). In-process payloads reach a participant through the aggregate that owns the act; outbound events carry the identity or routing fact downstream systems need, not a duplicate of context the publisher already holds.

**Names and reuse**

- `use-intention-revealing-names` — Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.
- `use-consistent-naming` — Use one word per concept. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`). Two words for one concept is how the same logic gets written twice — nobody searching for `fetch_` finds the `retrieve_` that already does the job.
- `eliminate-duplication` — Give repeated logic one canonical function. Every copy is another place the fix has to be repeated, and the copy you miss is the bug.
- `one-canonical-model-document` — Keep all modules for one model artifact in one canonical model document. Link diagrams and code to it rather than restating its classes in another design document, because parallel models become inconsistent.

#### Template

"""
# Conceptual Clean Engineering Reference (Python style)
# Refer to cdd_guidance/references/language-tools.md for tool recommendations.
# =============================================================================
# Put a class family in one file: the primary type, its subtypes, and
# tightly connected peers that only make sense together (element +
# collection, small aggregate + its part). Name the file after the family
# concept (`abilities.py` for Ability + Abilities). Split into another
# file only when a type is independently reused across families or the
# file becomes a grab-bag. Do not default to one class per file.
# Default: Class is the seam. I{ClassName} is not the default — add it in
# this same file when multiple implementations sit behind one seam, or when
# the user asks. Public members only on I{ClassName}; private members stay
# on {ClassName}. Put `{Type}ExampleFactory` in a sibling file — never in
# the production family file. Write each file under the module folder
# (`{module}/{family_slug}.py`), not beside the module.
# Invariants, interactions, comments (model):
#   Write each invariant as `#` on the class (or above the property /
#   operation it constrains): a must / never / always / before / after
#   that stays true when the object acts.
#   Write each interaction as `-> {collaborator}.{operation}` nested
#   under the calling operation. `-> ClassName` alone is not an interaction.
#   State an invariant or a sequence with `#`. Leave every other line
#   uncommented.
# =============================================================================
"""
from __future__ import annotations
from abc import ABC, abstractmethod

# FILE: {family_slug}.py
# Optional — omit unless generating an interface:
class I{ClassName}(ABC):
    @property
    @abstractmethod
    def {property}(self) -> {Type}:
        ...

    @abstractmethod
    def {operation}(self, {param}: {Type}) -> {ReturnType}:
        ...

class {ClassName}:  # or class {ClassName}(I{ClassName}):
    """*{ClassName}* unique role."""
    # {must / never / always / before / after that stays true of the object}

    @property
    def {property}(self) -> {Type}:
        # {must / never / always / before / after about this property}
        ...

    def {operation}(self, {param}: {Type}) -> {ReturnType}:
        # {must / never / always / before / after when this operation runs}
        # -> {collaborator}.{operation}
        ...

    def _{private_helper}(self, {param}: {Type}) -> {Type}:
        ...

# FILE: {type_slug}_example_factory.py
class {ClassName}ExampleFactory:
    def load_{example_key}(self, *, mode: str = "fake") -> {ClassName}:
        ...

Guide this action so the output conforms to this schema.

[module | package]

module:
  fidelity: modules
  id: dotPath
  name: string
  stereotypes?: [string]
  participants: [module | package | class | operation]
  dependsOn?: [module]
  usedBy?: [epic]
  where:
    - id is the name slugs from the root module to this module, joined by dots
    - name is a domain noun or a path
    - a nested module shares a base seam or is a sub-system
    - at most 40% of classes are public
    - dependencies flow one way, with no cycle
    - seam terms are what a caller types
    - purpose opens with the job a caller hires it for
  rules:
    - vocabulary-traces-to-source
    - do-not-invent-terms
    - do-not-invent-parallel-object-models
    - domain-nouns-only
    - named-seam-and-constraint
    - high-cohesion
    - no-module-per-class
    - single-boundary
    - deep-module
    - abstraction-focus
    - purpose-before-mechanism
    - public-seam-only
    - use-typed-signatures
    - general-purpose-surface
    - temporal-independence
    - one-way-deps
    - extensions-live-with-the-domain
    - low-coupling
    - layer-separation
    - missing-module-context
    - language-modules-one-section
    - modules-not-model-blocks

package:
  fidelity: modules
  id: dotPath
  name: string
  belongsTo: module
  participants: [class | package | module]
  where:
    - id is the module id, then this package name, joined by dots
    - a package groups classes inside a module

class:
  fidelity: model
  id: dotPath
  name: string
  belongsTo: module
  stereotypes?: [string]
  baseClass?: class
  dependsOn?: [class]
  relationships?: [relationship]
  demonstratedThrough?: [example | observation]
  participants: [operation | property]
  where:
    - id is the module id, then this class name, joined by dots
    - a class exists when a property, an instance, and a subtype do not fit
    - a subtype works wherever the base is used
    - collaborators arrive through the constructor
    - behavior sits on the object that owns the invariant
    - one reason to change
  rules:
    - model-modules-follow-the-partition
    - class-not-property-instance-or-subtype
    - no-prototype-swapping
    - keep-classes-single-responsibility
    - shape-classes-around-resources
    - put-logic-on-the-owning-resource
    - hide-inner-details
    - use-explicit-dependencies
    - external-system-interface-is-one-way
    - use-intention-revealing-names
    - use-consistent-naming
    - eliminate-duplication
    - one-canonical-model-document
    - no-redundant-relationship-paths
    - missing-module-context
    - language-modules-one-section
    - modules-not-model-blocks

relationship:
  fidelity: model
  id: dotPath
  kind: "composition" | "aggregation" | "association"
  target: class
  cardinality?: string
  where:
    - id is the class id, then kind, then the target class name, joined by dots
    - composition when the part has no identity outside the owner
    - aggregation when members keep their own identity
    - association when both sides stay independent
    - one canonical link per participant

operation:
  fidelity: model
  id: dotPath
  name: string
  belongsTo: class
  parameters: [parameter]
  returnType: class | string
  body?: string
  invokes: [operation | property]
  invokedBy?: [step | observation]
  invariants?: [invariant]
  where:
    - id is the class id, then this operation name, joined by dots
    - 0..3 parameters on a domain operation (self not counted)
    - one job
    - body under 20 statements
    - a state change returns the record or a failure named after the rejected rule
    - interactions call a named public operation on a collaborator
  rules:
    - keep-operations-single-responsibility
    - limit-operation-parameters
    - avoid-vague-parameter-names
    - errors-out-of-existence
    - state-change-returns-record-or-named-failure
    - domain-exception-carries-context
    - write-invariants
    - write-interactions
    - prefer-class-operations
    - prefer-instance-operations
    - keep-operations-small-focused
    - simplify-control-flow
    - use-exceptions-properly
    - never-swallow-exceptions
    - limit-comments
    - provide-meaningful-context
    - no-legacy-api-after-refactor

property:
  fidelity: model
  id: dotPath
  name: string
  belongsTo: class
  type: string
  value?: string
  hasType?: class
  invokes?: [operation | property]
  invariants?: [invariant]
  where:
    - id is the class id, then this property name, joined by dots
    - a derived property takes no owner or state parameter
    - a relationship stereotype on the property copies onto relationship.kind
  rules:
    - use-property-not-accessor
    - hide-inner-details

parameter:
  fidelity: model
  id: dotPath
  name: string
  belongsTo: operation
  type: string
  where:
    - id is the operation id, then this parameter name, joined by dots
    - the name says what the caller supplies
  rules:
    - avoid-vague-parameter-names
    - use-typed-signatures
    - use-intention-revealing-names

invariant:
  fidelity: model
  id: dotPath
  text: string
  belongsTo: [operation | property]
  where:
    - id is the owner id, then this text slug, joined by dots
    - a must, never, always, before, or after about this object's own state
  rules:
    - write-invariants
    - limit-comments

## Overview

Structure the problem into independent modules with small public interfaces, substantial hidden functionality, and one-way dependencies. Implement those modules with rigorous object-oriented and clean-code practices. When boundaries hold, a change stays inside one module; when they blur, callers depend on internal decisions and must change with them.

## Guidance

Partition first, then type the objects, then implement. Keep the same names in language, modules, model, and code — in prose, diagrams, and source.

## Shared rules

```yaml
alwaysApply: false
globs: "**/*-sketch.md"
```

Use these rules whenever you name a concept, draw a dependency, or write a public seam — in prose, a diagram, or source.

- **`vocabulary-traces-to-source`** — Take every term from the source. The English term and the code name are the same word: *shopping cart* is `ShoppingCart`. When the code says a different word than the domain, every reader keeps a translation in their head, and the two names drift until they mean different things.
- **`do-not-invent-terms`** — Do not invent a second noun or a parallel vocabulary. A second noun for the same thing becomes a second class, and then the same rule has to be written and fixed in both.
- **`do-not-invent-parallel-object-models`** — Keep one object model. Follow the nouns and verbs the rest of the graph already uses for that concept. A class that joins types the rest of the graph keeps apart is a second model — a big ball of mud — and every rule then has to be written and fixed in both. Wrap or extend the live objects and name a wrapper after the type it represents; do not scrape the same data into a second `*Model` or `*Entry` family.

---

#### Overview

Write working production code — real persistence, services, and UI behind the public seams.

#### Guidance

Follow the idioms in [`cdd_guidance/references/language-tools.md`](../../references/language-tools.md).

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

If this change will not stay here, follow `practices/clean-engineering/clean-engineering-model.mdc`.

**Implement the model**
- `hide-inner-details` — Expose behavior through named operations. Do not let callers see how the class stores or arranges its data — once they read the storage directly it becomes a public contract you cannot change. Private fields on the same class hide implementation; you do not need a second class for that. Read-only to callers can mean return a copy or immutable view from a property — it does not require a frozen class or a second type to hold build steps.
- `keep-operations-small-focused` — Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.
- `prefer-instance-operations` — Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.
- `keep-operations-single-responsibility` — Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.
- `simplify-control-flow` — Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.
- `errors-out-of-existence` — For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.
- `no-prototype-swapping` — An object keeps the class it was built as. Do not change it afterwards with `Object.setPrototypeOf`, `__proto__ =`, or `__class__ =`. When a subclass needs to make its own instances, give the base an overridable factory (`blank()`) or build the right class directly. A swapped object skips its constructor, so fields the subclass sets up are missing and nothing tells you.

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

---

#### Template

"""
# Conceptual Clean Engineering Reference (Python style)
# Refer to cdd_guidance/references/language-tools.md for tool recommendations.
# =============================================================================
# Put a class family in one file: the primary type, its subtypes, and
# tightly connected peers that only make sense together (element +
# collection, small aggregate + its part). Name the file after the family
# concept (`abilities.py` for Ability + Abilities). Split into another
# file only when a type is independently reused across families or the
# file becomes a grab-bag. Do not default to one class per file.
# Default: Class is the seam. I{ClassName} is not the default — add it in
# this same file when multiple implementations sit behind one seam, or when
# the user asks. Public members only on I{ClassName}; private members stay
# on {ClassName}. Put `{Type}ExampleFactory` in a sibling file — never in
# the production family file. Write each file under the module folder
# (`{module}/{family_slug}.py`), not beside the module.
# Invariants, interactions, comments (model):
#   Write each invariant as `#` on the class (or above the property /
#   operation it constrains): a must / never / always / before / after
#   that stays true when the object acts.
#   Write each interaction as `-> {collaborator}.{operation}` nested
#   under the calling operation. `-> ClassName` alone is not an interaction.
#   State an invariant or a sequence with `#`. Leave every other line
#   uncommented.
# =============================================================================
"""
from __future__ import annotations
from abc import ABC, abstractmethod

# FILE: {family_slug}.py
# Optional — omit unless generating an interface:
class I{ClassName}(ABC):
    @property
    @abstractmethod
    def {property}(self) -> {Type}:
        ...

    @abstractmethod
    def {operation}(self, {param}: {Type}) -> {ReturnType}:
        ...

class {ClassName}:  # or class {ClassName}(I{ClassName}):
    """*{ClassName}* unique role."""
    # {must / never / always / before / after that stays true of the object}

    @property
    def {property}(self) -> {Type}:
        # {must / never / always / before / after about this property}
        ...

    def {operation}(self, {param}: {Type}) -> {ReturnType}:
        # {must / never / always / before / after when this operation runs}
        # -> {collaborator}.{operation}
        ...

    def _{private_helper}(self, {param}: {Type}) -> {Type}:
        ...

# FILE: {type_slug}_example_factory.py
class {ClassName}ExampleFactory:
    def load_{example_key}(self, *, mode: str = "fake") -> {ClassName}:
        ...

## Overview

Structure the problem into independent modules with small public interfaces, substantial hidden functionality, and one-way dependencies. Implement those modules with rigorous object-oriented and clean-code practices. When boundaries hold, a change stays inside one module; when they blur, callers depend on internal decisions and must change with them.

## Guidance

Partition first, then type the objects, then implement. Keep the same names in language, modules, model, and code — in prose, diagrams, and source.

## Shared rules



Use these rules whenever you name a concept, draw a dependency, or write a public seam — in prose, a diagram, or source.

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

### model

```yaml
default_format: python
stage: specification
```

#### Overview

**Other formats:** markdown for a language model and `drawio` through `model/drawio` for a class diagram. The same classes, operations, and relationships must appear in every selected representation.

Design the object model — the classes, what they remember and do, and how they relate.

#### Sketch

- Verify with the user what the major concepts are from a business lens, and how they are currently implemented from a systems perspective.
- Ask what the major subsystems of the solution are, how users in other parts of the system interact with each, which states, transitions, and operations are visible to them, and the most important concepts in each.
- Ask about the valid states, the operations that cause transitions into those states, and the invariants that must stay true in each state.
- Ask who is allowed to act, and what they look at before they act.
- Ask when two things are really the same thing because they share behavior or share state.
- From those answers write what the class remembers, what it does, and whether it owns, collects, or only knows the other thing.
- Do not ask the user to pick class, property, or subtype.

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

If this change will not stay here, follow `practices/clean-engineering/clean-engineering-modules.mdc`.

**Shape classes**
- `model-modules-follow-the-partition` — Use the module names and boundaries established by the partition artifact as the model's top-level modules. Change the partition before moving a model boundary, because otherwise the two artifacts describe different designs.
- `class-not-property-instance-or-subtype` — Before you write a new class, check property, instance, then subtype. Write a class only when none of those three fit. Multi-step work inside one operation usually belongs in private fields on the class that owns the operation, not in another class. Every new class is another type to construct, pass around, and keep in step with the rest; a property or subtype reuses one that already works.
- `keep-classes-single-responsibility` — Give each class one reason to change.
- `shape-classes-around-resources` — Model a class around the concept that owns the state and the rule, not a doer, handler, or service that acts on a data bag. A Payment has transactions, a source, and a destination, and it moves the money; it is not a `PaymentService` that takes a `PaymentData` object. A service-plus-bag pair splits the rule from its memory, so every change has to be found in two types and the bag cannot enforce anything. Two resources may collaborate — a model that loads a Module is not a service-plus-bag split.
- `put-logic-on-the-owning-resource` — Put logic on the object that owns the invariant. Do not infer ownership from a route name, Story actor, or Given subject: `client.accounts[id].transactions.last.validate()`, not `client.validateLastTransactionForPrimaryAccount()`. Logic placed away from its state gives two objects authority to change the same rule.
- `hide-inner-details` — Expose behavior through named operations. Do not let callers see how the class stores or arranges its data — once they read the storage directly it becomes a public contract you cannot change. Private fields on the same class hide implementation; you do not need a second class for that.
- `use-property-not-accessor` — Use a named property for stored or derived state. A derived property recalculates from state and collaborators the object already holds, takes no owner or state parameters, and looks like a field to callers through the language's property mechanism. Use an operation only when behavior coordinates several values, collaborators, or lifecycle steps and cannot be represented truthfully as a property. Callers should not need `getX`, `setX`, or storage knowledge. Read-only to callers can mean return a copy or immutable view from a property — it does not require a frozen class or a second type to hold build steps.
- `prefer-class-operations` — Put factory, lifecycle, and helpers used from one class on that class. Do not export them as module-level functions — a free function holds no state, so it takes the object as a parameter and reaches into it to do the work. A file of hanging functions is the same miss: those operations belong on a type, not on the package.
- `use-explicit-dependencies` — Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation.
- `external-system-interface-is-one-way` — Let a domain wrapper or collaborator depend on the named external-system contract. Keep the external type independent of domain wrappers and domain types, because a reverse dependency makes the external boundary depend on one caller's model.


**Define operations**
- `keep-operations-single-responsibility` — Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.
- `limit-operation-parameters` — Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.
- `avoid-vague-parameter-names` — Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.
- `errors-out-of-existence` — For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.
- `state-change-returns-record-or-named-failure` — When an operation coordinates a state change that cannot be one property assignment, return the resulting record or a failure named after the rejected rule. Decide at code fidelity whether that failure is a result type or domain exception, because callers need one explicit outcome contract.
- `domain-exception-carries-context` — Use a typed exception for a broken aggregate or repository operation. One exception type may cover that aggregate's operations when it carries the failed operation, the domain object or input already in hand, the user-facing message, and the underlying cause; do not return bare strings or untyped error objects because callers cannot handle them safely..
- `limit-comments` — write comment in operations and properties only when the signature cannot say a constraint or explain why the code behaves the way it does. Do not narrate a line that already names what it does.

**Invariants, interactions, and comments**

- `write-invariants` — Name a rule the object itself must keep true whenever it acts — a must, never, always, before, or after about its own state. Write one a caller can break by using the object wrong. Do not restate a type, a name, or a single operation’s happy path.
- `write-interactions` — Collaborate when this object cannot finish its job from its own state — another object owns the data or the next act. Ask that object to do the work so each keeps its own invariants; do not reach into its internals or steal its job. Ask through a named public operation on a collaborator you hold or are given. Do not point at a type, and do not invent a third object to mediate a conversation two objects can have.
- `no-redundant-relationship-paths` — Before you add an association, walk the paths already in the cluster. Each real participant gets one canonical link — not parallel wires through types that collapse to the same thing (`Client` and `ClientIdentity`, or `OfferChannel` on **Offer** and again on an event the offer just emitted). In-process payloads reach a participant through the aggregate that owns the act; outbound events carry the identity or routing fact downstream systems need, not a duplicate of context the publisher already holds.

**Names and reuse**

- `use-intention-revealing-names` — Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.
- `use-consistent-naming` — Use one word per concept. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`). Two words for one concept is how the same logic gets written twice — nobody searching for `fetch_` finds the `retrieve_` that already does the job.
- `eliminate-duplication` — Give repeated logic one canonical function. Every copy is another place the fix has to be repeated, and the copy you miss is the bug.
- `one-canonical-model-document` — Keep all modules for one model artifact in one canonical model document. Link diagrams and code to it rather than restating its classes in another design document, because parallel models become inconsistent.