Guide this action so the output conforms to this schema.

[spec]

spec:
  fidelity: behavior
  id: dotPath
  name: string
  descriptions: [description]
  where:
    - id is this spec name slug
    - the outermost describe is the subject
    - order follows the usage story
  rules:
    - observable-behavior
    - domain-practice-alignment
    - usage-order-behaviors
    - shared-describe-subject
    - full-surface-coverage
    - framework-syntax

description:
  fidelity: behavior
  id: dotPath
  text: string
  order: number
  belongsTo: [spec | description]
  alignsWith?: class
  contexts?: [context]
  descriptions?: [description]
  observations?: [observation]
  where:
    - id is the text slugs from the spec through each parent description to this one, joined by dots
    - plain-English subject, state, or observable condition
    - sibling describes are mutually exclusive
    - reading this describe through each nested that and with to it should is one sentence
  rules:
    - describe-is-subject-not-internal
    - describe-is-plain-english
    - domain-practice-alignment

context:
  fidelity: behavior
  id: dotPath
  text: string
  order: number
  belongsTo: [description | context]
  kind: "that" | "with"
  contexts?: [context]
  observations?: [observation]
  examples?: [example]
  where:
    - id is the parent id, then this text slug, joined by dots
    - that names an enabling event or condition already true
    - with names a standing condition
    - a nested context is a precondition of the observations under it
    - setup under the label establishes the state the label names
    - examples are the shared arrange state for the observations here
  rules:
    - state-not-when
    - nest-by-enabling-events
    - context-setup-expresses-state
    - context-sharing

observation:
  fidelity: behavior
  id: dotPath
  text: string
  order: number
  belongsTo: [context | description]
  examples?: [example]
  demonstrates?: class
  invokes?: [operation | property]
  specifies?: scenario
  where:
    - id is the parent context or description id, then this text slug, joined by dots
    - one observable outcome a stakeholder can verify
    - behavior fidelity is a signature with no assertion body
    - examples are the concrete cases for this outcome
    - demonstrates is the class whose public effect this observation proves
    - invokes is the operation or property the call surface exercises
    - specifies is the story scenario this observation makes executable
  rules:
    - observable-behavior
    - full-surface-coverage
    - no-implementation
    - hierarchy-preservation
    - one-assertion-per-test
    - one-signature-at-a-time
    - red-then-green
    - minimum-green
    - code-minimalism
    - layer-isolation
    - oo-api-design
    - honors-documented-surface-contracts
    - scan-fixture-pair

## Overview

Behavior-driven development turns domain vocabulary into passing tests. Every BDD artifact is an indented hierarchy. Sketch that shape first (`templates/bdd-sketch.md`).

**Tooling & Idioms:** Refer to [`cdd_guidance/references/language-tools.md`](../../references/language-tools.md) for language-specific tool recommendations and idiomatic patterns.

## Guidance

Design the tree hierarchy by building a flowing sentence. Build every hierarchy so that reading from the outermost `describe` through every nested `that`/`with` down to the `it should` produces a clean, flowing English sentence — spoken aloud, it describes the behavior naturally. When it does not read as a sentence, the nesting is grouping tests for convenience instead of following the conditions the behavior depends on — and you can no longer reason about all the possible behaviors and alternate behaviors that require coverage. At development fidelity, scan production source for coverage gaps before filling signatures.

**Always start with the subject:** place the baseline entity type, class, or user mode at the outermost `describe` — everything below inherits it, so the wrong subject at the top misplaces every behavior under it. **Then nest layers in any order** — choose whichever sequence produces the most natural spoken sentence. Nesting means each condition is set up once and everything inside adds to it — easier to follow, and no rebuilding the same state in every test. Select from these three layer types and arrange them to flow: 

* **Structure:** the content configuration or data shape of that identity. `with items in the cart`, `with no billing address`, `with a linked payment method`
* **Event:** the static system state *after* an action has been finalized. `that has been submitted`, `that has been cancelled`, `that has been approved` — express lifecycle events as past-participle states only
* **Environmental Variance:** external factors, temporal rules, or inputs applied to that state. `during a flash sale weekend`, `outside of promotional periods`, `on a public holiday`

Arrange these in whatever sequence makes the sentence read naturally. `"with items in the cart, that has been submitted, during a flash sale"` flows. Always let the sentence guide the nesting order.

> *"a ShoppingCart, for a premium member account, with items in the cart, that has been submitted, during a flash sale weekend, it should apply an automatic double-points multiplier"*

**Branch** when the system behaves entirely differently based on a change. Make sibling `describe` blocks mutually exclusive.
```
describe a user
  that is authenticated
    [Behaviors exclusive to logged-in state]
  that is an anonymous visitor
    [Behaviors exclusive to logged-out state]
```

**Nest** when a sub-state inherits everything from its parent but introduces another behavior — a nested block only makes sense if the parent state has to hold for the behavior to happen.
```
describe an account
  that is premium
    with a linked payment method
      [Behaviors for fully active premium users]
      that belongs a minor
      [Behaviors for minors linked premium users account]
```

**Share** when multiple channels or implementations produce the same observable behavior but each has a few unique behaviors of its own. Define the shared behaviors once, include them per channel, add only the deltas.
```
shared_examples "onboarding a new mobile customer"
  that selects a plan
    it should display the selected plan details
    it should show the monthly cost
  that provides identity verification
    it should validate the customer's ID
    it should create a pending account
  that completes payment
    it should activate the mobile line
    it should send a welcome confirmation

describe onboarding through the web
  it_behaves_like "onboarding a new mobile customer"
  that uploads a selfie for verification
    it should match the selfie against the ID photo

describe onboarding through voice
  it_behaves_like "onboarding a new mobile customer"
  that speaks the verification code
    it should confirm identity via voice match

describe onboarding through the retail store
  it_behaves_like "onboarding a new mobile customer"
  that scans the physical ID at the counter
    it should verify the document in real time
```

**Promote** when a condition repeated inside many areas is actually a core state that other behaviors sit inside. Pull it to the outermost boundary and nest everything under it.
```
before:                                     after:
describe a Payment                          describe a Payment
  that is submitted                           with an expired token       *promoted
    with an expired token  ←repeated            that is submitted
    with a valid token                            it should reject
  that is refunded                              that is refunded
    with an expired token  ←repeated              it should reject
    with a valid token                          that is disputed
  that is disputed                                it should reject
    with an expired token  ←repeated            that checks balance
    with a valid token                            it should reject
  that checks balance                           that generates statement
    with an expired token  ←repeated              it should reject
    with a valid token                        with a valid token
  that generates statement                      that is submitted
    with an expired token  ←repeated              it should process
    with a valid token                          that is refunded
                                                  it should process
                                                ...
```

Start from an agreed sketch and deepen toward green tests and production code. Each level **adds** artifacts and **extends** the previous — do not fill in details from a more detailed fidelity.

| Fidelity | Output |
|---|---|
| **behavior** | describe/it hierarchy with `BDD: SIGNATURE` markers in each `it` |
| **realization** | Same hierarchy; each `it should` carries the domain call graph (`->` / `<-`) for Act and observable side effects |
| **development** | Implemented tests + production code |

#### Guidance

- Sketch nesting (subjects → `with`/`that`/events → `it should`) is agreed
- **Confirm framework** — ask if not stated. Default: Mamba/Python; Jest/TypeScript or JUnit 5/Java when the project uses those.
- Convert every sketch hierarchy line to its framework equivalent (see Framework syntax).
- Process in batches of ~18 describe blocks when the hierarchy is large.

Fill the **behavior** (SIGNATURE) section of `templates/bdd-templates.{ext}` (`.py` / `.java` / `.ts`).

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

## Shared rules

```yaml
alwaysApply: false
globs: "**/*spec.py,**/*_spec.py,**/*spec.ts,**/*Spec.java,**/*-sketch.md"
```

Whenever you write or reshape describe / that / with / it-should specs, or code that is supported by these specifications. Follow these rules.

- **`observable-behavior`** — Prove what a stakeholder can verify without reading code (return value, state, public effect). Never internals. Assertions on internals break when the code is refactored and still pass when the behavior is wrong.
- **`domain-practice-alignment`** — Describe names must match domain language / model exactly, so the business, the spec, and the code all use the same words.
- **`usage-order-behaviors`** — Order describes, contexts, and examples as a **usage story** or operational sequence (what happens first → next). Do not order by implementation layer, package, or internal type. In usage order a missing step is obvious; ordered by layer, nobody can tell what is not covered.
- **`describe-is-subject-not-internal`** — A `describe` is a domain subject, state, or observable condition — never a manager, hub, runner, service, or other internal (`SessionLog`, `ToolsetRunner`, …). A spec named after a class has to be rewritten when that class is replaced, even though the behavior did not change.
- **`describe-is-plain-english`** — Full English phrases (e.g. "an action that is annotated with log", "an action that is not annotated"). Never symbol/mechanism names (`"@log marker"`) as the subject.
- **`shared-describe-subject`** — Keep **one** outermost `describe` per domain subject. When two top-level describes share the same opening phrase and only diverge in a trailing qualifier (`registered for deploy` vs `with mcp-published operations`, `context guidance registered for` vs `context guidance with`, `a context tool module with fidelity sections` vs `with fidelities and assembly`), that divergence is a **branch** — promote the shared phrase to the single describe and nest each qualifier as a sibling `with` / `that` context. Do not repeat the shared setup string in a second top-level describe.
- **`state-not-when`** — Never name a nested state with `when`. Use `that …` for events/conditions on the subject and `with …` for standing conditions. Ask: what event or condition must already be true for this observation?
- **`nest-by-enabling-events`** — Each nested `that` / `with` must be a real precondition or event required for the nested `it should` — not a test-file grouping convenience.
- **`context-setup-expresses-state`** — Any `before.each`, `before.all`, or Arrange nested directly under a `that`/`with` must establish the state named in that label. Read label and setup together: if the label says the subject is annotated, configured, or classified a certain way, the setup must make that true — not merely boot the host, wire paths, or call a factory. Put host boot, browser launch, and construction plumbing in a parent context whose label says the host is started, loaded, or running (`that is hosted on…`, `that the server has started…`).
- **`full-surface-coverage`** — Full coverage means the behavior tree is complete — every observable outcome has an `it should` in the right branch. Walk the describe/`that`/`with` tree for missing subjects, states, and outcomes; do not add one `it` per public method just because the member exists.
- **`scan-fixture-pair`** — A mechanical mistake spec passes the fail file to `expect_scan_fails` and the pass file to `expect_scan_passes` (`cdd_guidance.practices.bdd.spec_helpers`). Do not invent a parallel eval spec harness.

"""
# Conceptual BDD Reference (Python/Mamba style)
# Refer to cdd_guidance/references/language-tools.md for tool recommendations.
# =============================================================================
# BEHAVIOR (SIGNATURE) — `signature-markers`
# Every `it` body is exactly `pass  # BDD: SIGNATURE` — nothing else. A bare comment is not a Python body.
#
# with description('{DomainEntity}'):
#     with context('that has been created'):
#         with it('should have {initial property} assigned'):
#             pass  # BDD: SIGNATURE
# =============================================================================
# REALIZATION — call graph per `it` (default after behavior unless user opts out)
# Replace `# BDD: SIGNATURE` with `# ->` / `# <-` lines only — same notation as CE model.
#
#         with it('should reject an expired token'):
#             # cart.checkout()
#             #   -> paymentGateway.charge(amount)
#             #   <- receipt
#             pass  # BDD: SIGNATURE
# =============================================================================
# DEVELOPMENT — `no-remaining-signatures`
# Replace each `# BDD: SIGNATURE` with Arrange / Act / Assert. Zero markers when done.
# Instructions:
#   1. Replace {DomainEntity} with the class or module under test.
#   2. Use Arrange / Act / Assert comments in test bodies.
#   3. One assertion per behavior.
# =============================================================================
"""
from mamba import description, context, it, before
from expects import equal, expect
from {domain_module} import {DomainEntity}

with description('{DomainEntity}'):
    with context('that has been created'):
        with it('should have {initial property} assigned'):
            # Arrange / Act
            entity = {DomainEntity}(**default_data())
            # Assert
            expect(entity.property).to(equal(expected_value))

    with context('that is {active state}'):
        with before.each:
            self.entity = {DomainEntity}(**default_{related_data}())

        with it('should {behavior description}'):
            # Act
            self.entity.{action}({input})
            # Assert
            expect(self.entity.{property}).to(equal({expected_value}))

        with it('should {second behavior}'):
            # Arrange
            {local_setup} = {value}
            # Act
            self.entity.{action}({local_setup})
            # Assert
            expect(self.entity.{property}).to(equal({expected_value}))


# Scan fixture pair — mechanical mistake specs use these helpers, not an eval harness.
from cdd_guidance.practices.bdd.spec_helpers import expect_scan_fails, expect_scan_passes

with description('a scan fixture pair'):
    with context('a file that violates the rule'):
        with it('should fail scan'):
            expect_scan_fails({scan}, '{FailFixturePath}', rule='{Rule}')

    with context('a file that satisfies the rule'):
        with it('should pass scan'):
            expect_scan_passes({scan}, '{PassFixturePath}', rule='{Rule}')

Guide this action so the output conforms to this schema.

[spec]

spec:
  fidelity: behavior
  id: dotPath
  name: string
  descriptions: [description]
  where:
    - id is this spec name slug
    - the outermost describe is the subject
    - order follows the usage story
  rules:
    - observable-behavior
    - domain-practice-alignment
    - usage-order-behaviors
    - shared-describe-subject
    - full-surface-coverage
    - framework-syntax

description:
  fidelity: behavior
  id: dotPath
  text: string
  order: number
  belongsTo: [spec | description]
  alignsWith?: class
  contexts?: [context]
  descriptions?: [description]
  observations?: [observation]
  where:
    - id is the text slugs from the spec through each parent description to this one, joined by dots
    - plain-English subject, state, or observable condition
    - sibling describes are mutually exclusive
    - reading this describe through each nested that and with to it should is one sentence
  rules:
    - describe-is-subject-not-internal
    - describe-is-plain-english
    - domain-practice-alignment

context:
  fidelity: behavior
  id: dotPath
  text: string
  order: number
  belongsTo: [description | context]
  kind: "that" | "with"
  contexts?: [context]
  observations?: [observation]
  examples?: [example]
  where:
    - id is the parent id, then this text slug, joined by dots
    - that names an enabling event or condition already true
    - with names a standing condition
    - a nested context is a precondition of the observations under it
    - setup under the label establishes the state the label names
    - examples are the shared arrange state for the observations here
  rules:
    - state-not-when
    - nest-by-enabling-events
    - context-setup-expresses-state
    - context-sharing

observation:
  fidelity: behavior
  id: dotPath
  text: string
  order: number
  belongsTo: [context | description]
  examples?: [example]
  demonstrates?: class
  invokes?: [operation | property]
  specifies?: scenario
  where:
    - id is the parent context or description id, then this text slug, joined by dots
    - one observable outcome a stakeholder can verify
    - behavior fidelity is a signature with no assertion body
    - examples are the concrete cases for this outcome
    - demonstrates is the class whose public effect this observation proves
    - invokes is the operation or property the call surface exercises
    - specifies is the story scenario this observation makes executable
  rules:
    - observable-behavior
    - full-surface-coverage
    - no-implementation
    - hierarchy-preservation
    - one-assertion-per-test
    - one-signature-at-a-time
    - red-then-green
    - minimum-green
    - code-minimalism
    - layer-isolation
    - oo-api-design
    - honors-documented-surface-contracts
    - scan-fixture-pair

## Overview

Behavior-driven development turns domain vocabulary into passing tests. Every BDD artifact is an indented hierarchy. Sketch that shape first (`templates/bdd-sketch.md`).

**Tooling & Idioms:** Refer to [`cdd_guidance/references/language-tools.md`](../../references/language-tools.md) for language-specific tool recommendations and idiomatic patterns.

## Guidance

Design the tree hierarchy by building a flowing sentence. Build every hierarchy so that reading from the outermost `describe` through every nested `that`/`with` down to the `it should` produces a clean, flowing English sentence — spoken aloud, it describes the behavior naturally. When it does not read as a sentence, the nesting is grouping tests for convenience instead of following the conditions the behavior depends on — and you can no longer reason about all the possible behaviors and alternate behaviors that require coverage. At development fidelity, scan production source for coverage gaps before filling signatures.

**Always start with the subject:** place the baseline entity type, class, or user mode at the outermost `describe` — everything below inherits it, so the wrong subject at the top misplaces every behavior under it. **Then nest layers in any order** — choose whichever sequence produces the most natural spoken sentence. Nesting means each condition is set up once and everything inside adds to it — easier to follow, and no rebuilding the same state in every test. Select from these three layer types and arrange them to flow: 

* **Structure:** the content configuration or data shape of that identity. `with items in the cart`, `with no billing address`, `with a linked payment method`
* **Event:** the static system state *after* an action has been finalized. `that has been submitted`, `that has been cancelled`, `that has been approved` — express lifecycle events as past-participle states only
* **Environmental Variance:** external factors, temporal rules, or inputs applied to that state. `during a flash sale weekend`, `outside of promotional periods`, `on a public holiday`

Arrange these in whatever sequence makes the sentence read naturally. `"with items in the cart, that has been submitted, during a flash sale"` flows. Always let the sentence guide the nesting order.

> *"a ShoppingCart, for a premium member account, with items in the cart, that has been submitted, during a flash sale weekend, it should apply an automatic double-points multiplier"*

**Branch** when the system behaves entirely differently based on a change. Make sibling `describe` blocks mutually exclusive.
```
describe a user
  that is authenticated
    [Behaviors exclusive to logged-in state]
  that is an anonymous visitor
    [Behaviors exclusive to logged-out state]
```

**Nest** when a sub-state inherits everything from its parent but introduces another behavior — a nested block only makes sense if the parent state has to hold for the behavior to happen.
```
describe an account
  that is premium
    with a linked payment method
      [Behaviors for fully active premium users]
      that belongs a minor
      [Behaviors for minors linked premium users account]
```

**Share** when multiple channels or implementations produce the same observable behavior but each has a few unique behaviors of its own. Define the shared behaviors once, include them per channel, add only the deltas.
```
shared_examples "onboarding a new mobile customer"
  that selects a plan
    it should display the selected plan details
    it should show the monthly cost
  that provides identity verification
    it should validate the customer's ID
    it should create a pending account
  that completes payment
    it should activate the mobile line
    it should send a welcome confirmation

describe onboarding through the web
  it_behaves_like "onboarding a new mobile customer"
  that uploads a selfie for verification
    it should match the selfie against the ID photo

describe onboarding through voice
  it_behaves_like "onboarding a new mobile customer"
  that speaks the verification code
    it should confirm identity via voice match

describe onboarding through the retail store
  it_behaves_like "onboarding a new mobile customer"
  that scans the physical ID at the counter
    it should verify the document in real time
```

**Promote** when a condition repeated inside many areas is actually a core state that other behaviors sit inside. Pull it to the outermost boundary and nest everything under it.
```
before:                                     after:
describe a Payment                          describe a Payment
  that is submitted                           with an expired token       *promoted
    with an expired token  ←repeated            that is submitted
    with a valid token                            it should reject
  that is refunded                              that is refunded
    with an expired token  ←repeated              it should reject
    with a valid token                          that is disputed
  that is disputed                                it should reject
    with an expired token  ←repeated            that checks balance
    with a valid token                            it should reject
  that checks balance                           that generates statement
    with an expired token  ←repeated              it should reject
    with a valid token                        with a valid token
  that generates statement                      that is submitted
    with an expired token  ←repeated              it should process
    with a valid token                          that is refunded
                                                  it should process
                                                ...
```

Start from an agreed sketch and deepen toward green tests and production code. Each level **adds** artifacts and **extends** the previous — do not fill in details from a more detailed fidelity.

| Fidelity | Output |
|---|---|
| **behavior** | describe/it hierarchy with `BDD: SIGNATURE` markers in each `it` |
| **realization** | Same hierarchy; each `it should` carries the domain call graph (`->` / `<-`) for Act and observable side effects |
| **development** | Implemented tests + production code |

## Shared rules

```yaml
alwaysApply: false
globs: "**/*spec.py,**/*_spec.py,**/*spec.ts,**/*Spec.java,**/*-sketch.md"
```

Whenever you write or reshape describe / that / with / it-should specs, or code that is supported by these specifications. Follow these rules.

- **`observable-behavior`** — Prove what a stakeholder can verify without reading code (return value, state, public effect). Never internals. Assertions on internals break when the code is refactored and still pass when the behavior is wrong.
- **`domain-practice-alignment`** — Describe names must match domain language / model exactly, so the business, the spec, and the code all use the same words.
- **`usage-order-behaviors`** — Order describes, contexts, and examples as a **usage story** or operational sequence (what happens first → next). Do not order by implementation layer, package, or internal type. In usage order a missing step is obvious; ordered by layer, nobody can tell what is not covered.
- **`describe-is-subject-not-internal`** — A `describe` is a domain subject, state, or observable condition — never a manager, hub, runner, service, or other internal (`SessionLog`, `ToolsetRunner`, …). A spec named after a class has to be rewritten when that class is replaced, even though the behavior did not change.
- **`describe-is-plain-english`** — Full English phrases (e.g. "an action that is annotated with log", "an action that is not annotated"). Never symbol/mechanism names (`"@log marker"`) as the subject.
- **`shared-describe-subject`** — Keep **one** outermost `describe` per domain subject. When two top-level describes share the same opening phrase and only diverge in a trailing qualifier (`registered for deploy` vs `with mcp-published operations`, `context guidance registered for` vs `context guidance with`, `a context tool module with fidelity sections` vs `with fidelities and assembly`), that divergence is a **branch** — promote the shared phrase to the single describe and nest each qualifier as a sibling `with` / `that` context. Do not repeat the shared setup string in a second top-level describe.
- **`state-not-when`** — Never name a nested state with `when`. Use `that …` for events/conditions on the subject and `with …` for standing conditions. Ask: what event or condition must already be true for this observation?
- **`nest-by-enabling-events`** — Each nested `that` / `with` must be a real precondition or event required for the nested `it should` — not a test-file grouping convenience.
- **`context-setup-expresses-state`** — Any `before.each`, `before.all`, or Arrange nested directly under a `that`/`with` must establish the state named in that label. Read label and setup together: if the label says the subject is annotated, configured, or classified a certain way, the setup must make that true — not merely boot the host, wire paths, or call a factory. Put host boot, browser launch, and construction plumbing in a parent context whose label says the host is started, loaded, or running (`that is hosted on…`, `that the server has started…`).
- **`full-surface-coverage`** — Full coverage means the behavior tree is complete — every observable outcome has an `it should` in the right branch. Walk the describe/`that`/`with` tree for missing subjects, states, and outcomes; do not add one `it` per public method just because the member exists.
- **`scan-fixture-pair`** — A mechanical mistake spec passes the fail file to `expect_scan_fails` and the pass file to `expect_scan_passes` (`cdd_guidance.practices.bdd.spec_helpers`). Do not invent a parallel eval spec harness.

#### Overview

Define BDD signatures — describe/it names for every observation, no test bodies.

#### Guidance

- Sketch nesting (subjects → `with`/`that`/events → `it should`) is agreed
- **Confirm framework** — ask if not stated. Default: Mamba/Python; Jest/TypeScript or JUnit 5/Java when the project uses those.
- Convert every sketch hierarchy line to its framework equivalent (see Framework syntax).
- Process in batches of ~18 describe blocks when the hierarchy is large.

Fill the **behavior** (SIGNATURE) section of `templates/bdd-templates.{ext}` (`.py` / `.java` / `.ts`).

#### Rules

```yaml
alwaysApply: false
globs: "**/*spec.py,**/*_spec.py,**/*spec.ts,**/*Spec.java,**/*-sketch.md"
```

Whenever you name or re-nest describe/it signatures, change code that relies on those signatures, or change specifications that need this kind of rename. Follow these rules.

If this change will not stay here, follow `practices/bdd.mdc`.

- **`state-not-when`** — Nest by the state or condition that enables an observation, never by a `when` trigger.
- **`nest-by-enabling-events`** — Sub-groupings are conditions that unlock further behavior, not implementation steps.
- **`context-setup-expresses-state`** — Setup under a label must establish that label's state, not unrelated host boot.
- **`shared-describe-subject`** — Same rule as shared rules (above); at behavior fidelity, scan the spec file for repeated top-level `describe` prefixes before adding another subject line.
- **`no-implementation`** — No assertions, mocks, production imports, helpers, or `beforeEach` / shared setup.
- **`framework-syntax`** — Refer to [`cdd_guidance/references/language-tools.md`](../../references/language-tools.md) for the target language's syntax. One confirmed framework throughout. Do not mix Jest and Mamba constructs.

**Pass:**
```typescript
it('should apply a percentage discount to eligible items', () => {
  // BDD: SIGNATURE
});
```

**Fail:** any assertion, mock, import of production code, or helper inside the body.

---

#### Template

"""
# Conceptual BDD Reference (Python/Mamba style)
# Refer to cdd_guidance/references/language-tools.md for tool recommendations.
# =============================================================================
# BEHAVIOR (SIGNATURE) — `signature-markers`
# Every `it` body is exactly `pass  # BDD: SIGNATURE` — nothing else. A bare comment is not a Python body.
#
# with description('{DomainEntity}'):
#     with context('that has been created'):
#         with it('should have {initial property} assigned'):
#             pass  # BDD: SIGNATURE
# =============================================================================
# REALIZATION — call graph per `it` (default after behavior unless user opts out)
# Replace `# BDD: SIGNATURE` with `# ->` / `# <-` lines only — same notation as CE model.
#
#         with it('should reject an expired token'):
#             # cart.checkout()
#             #   -> paymentGateway.charge(amount)
#             #   <- receipt
#             pass  # BDD: SIGNATURE
# =============================================================================
# DEVELOPMENT — `no-remaining-signatures`
# Replace each `# BDD: SIGNATURE` with Arrange / Act / Assert. Zero markers when done.
# Instructions:
#   1. Replace {DomainEntity} with the class or module under test.
#   2. Use Arrange / Act / Assert comments in test bodies.
#   3. One assertion per behavior.
# =============================================================================
"""
from mamba import description, context, it, before
from expects import equal, expect
from {domain_module} import {DomainEntity}

with description('{DomainEntity}'):
    with context('that has been created'):
        with it('should have {initial property} assigned'):
            # Arrange / Act
            entity = {DomainEntity}(**default_data())
            # Assert
            expect(entity.property).to(equal(expected_value))

    with context('that is {active state}'):
        with before.each:
            self.entity = {DomainEntity}(**default_{related_data}())

        with it('should {behavior description}'):
            # Act
            self.entity.{action}({input})
            # Assert
            expect(self.entity.{property}).to(equal({expected_value}))

        with it('should {second behavior}'):
            # Arrange
            {local_setup} = {value}
            # Act
            self.entity.{action}({local_setup})
            # Assert
            expect(self.entity.{property}).to(equal({expected_value}))


# Scan fixture pair — mechanical mistake specs use these helpers, not an eval harness.
from cdd_guidance.practices.bdd.spec_helpers import expect_scan_fails, expect_scan_passes

with description('a scan fixture pair'):
    with context('a file that violates the rule'):
        with it('should fail scan'):
            expect_scan_fails({scan}, '{FailFixturePath}', rule='{Rule}')

    with context('a file that satisfies the rule'):
        with it('should pass scan'):
            expect_scan_passes({scan}, '{PassFixturePath}', rule='{Rule}')

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

[spec]

spec:
  fidelity: behavior
  id: dotPath
  name: string
  descriptions: [description]
  where:
    - id is this spec name slug
    - the outermost describe is the subject
    - order follows the usage story
  rules:
    - observable-behavior
    - domain-practice-alignment
    - usage-order-behaviors
    - shared-describe-subject
    - full-surface-coverage
    - framework-syntax

description:
  fidelity: behavior
  id: dotPath
  text: string
  order: number
  belongsTo: [spec | description]
  alignsWith?: class
  contexts?: [context]
  descriptions?: [description]
  observations?: [observation]
  where:
    - id is the text slugs from the spec through each parent description to this one, joined by dots
    - plain-English subject, state, or observable condition
    - sibling describes are mutually exclusive
    - reading this describe through each nested that and with to it should is one sentence
  rules:
    - describe-is-subject-not-internal
    - describe-is-plain-english
    - domain-practice-alignment

context:
  fidelity: behavior
  id: dotPath
  text: string
  order: number
  belongsTo: [description | context]
  kind: "that" | "with"
  contexts?: [context]
  observations?: [observation]
  examples?: [example]
  where:
    - id is the parent id, then this text slug, joined by dots
    - that names an enabling event or condition already true
    - with names a standing condition
    - a nested context is a precondition of the observations under it
    - setup under the label establishes the state the label names
    - examples are the shared arrange state for the observations here
  rules:
    - state-not-when
    - nest-by-enabling-events
    - context-setup-expresses-state
    - context-sharing

observation:
  fidelity: behavior
  id: dotPath
  text: string
  order: number
  belongsTo: [context | description]
  examples?: [example]
  demonstrates?: class
  invokes?: [operation | property]
  specifies?: scenario
  where:
    - id is the parent context or description id, then this text slug, joined by dots
    - one observable outcome a stakeholder can verify
    - behavior fidelity is a signature with no assertion body
    - examples are the concrete cases for this outcome
    - demonstrates is the class whose public effect this observation proves
    - invokes is the operation or property the call surface exercises
    - specifies is the story scenario this observation makes executable
  rules:
    - observable-behavior
    - full-surface-coverage
    - no-implementation
    - hierarchy-preservation
    - one-assertion-per-test
    - one-signature-at-a-time
    - red-then-green
    - minimum-green
    - code-minimalism
    - layer-isolation
    - oo-api-design
    - honors-documented-surface-contracts
    - scan-fixture-pair

## Overview

Behavior-driven development turns domain vocabulary into passing tests. Every BDD artifact is an indented hierarchy. Sketch that shape first (`templates/bdd-sketch.md`).

**Tooling & Idioms:** Refer to [`cdd_guidance/references/language-tools.md`](../../references/language-tools.md) for language-specific tool recommendations and idiomatic patterns.

## Guidance

Design the tree hierarchy by building a flowing sentence. Build every hierarchy so that reading from the outermost `describe` through every nested `that`/`with` down to the `it should` produces a clean, flowing English sentence — spoken aloud, it describes the behavior naturally. When it does not read as a sentence, the nesting is grouping tests for convenience instead of following the conditions the behavior depends on — and you can no longer reason about all the possible behaviors and alternate behaviors that require coverage. At development fidelity, scan production source for coverage gaps before filling signatures.

**Always start with the subject:** place the baseline entity type, class, or user mode at the outermost `describe` — everything below inherits it, so the wrong subject at the top misplaces every behavior under it. **Then nest layers in any order** — choose whichever sequence produces the most natural spoken sentence. Nesting means each condition is set up once and everything inside adds to it — easier to follow, and no rebuilding the same state in every test. Select from these three layer types and arrange them to flow: 

* **Structure:** the content configuration or data shape of that identity. `with items in the cart`, `with no billing address`, `with a linked payment method`
* **Event:** the static system state *after* an action has been finalized. `that has been submitted`, `that has been cancelled`, `that has been approved` — express lifecycle events as past-participle states only
* **Environmental Variance:** external factors, temporal rules, or inputs applied to that state. `during a flash sale weekend`, `outside of promotional periods`, `on a public holiday`

Arrange these in whatever sequence makes the sentence read naturally. `"with items in the cart, that has been submitted, during a flash sale"` flows. Always let the sentence guide the nesting order.

> *"a ShoppingCart, for a premium member account, with items in the cart, that has been submitted, during a flash sale weekend, it should apply an automatic double-points multiplier"*

**Branch** when the system behaves entirely differently based on a change. Make sibling `describe` blocks mutually exclusive.
```
describe a user
  that is authenticated
    [Behaviors exclusive to logged-in state]
  that is an anonymous visitor
    [Behaviors exclusive to logged-out state]
```

**Nest** when a sub-state inherits everything from its parent but introduces another behavior — a nested block only makes sense if the parent state has to hold for the behavior to happen.
```
describe an account
  that is premium
    with a linked payment method
      [Behaviors for fully active premium users]
      that belongs a minor
      [Behaviors for minors linked premium users account]
```

**Share** when multiple channels or implementations produce the same observable behavior but each has a few unique behaviors of its own. Define the shared behaviors once, include them per channel, add only the deltas.
```
shared_examples "onboarding a new mobile customer"
  that selects a plan
    it should display the selected plan details
    it should show the monthly cost
  that provides identity verification
    it should validate the customer's ID
    it should create a pending account
  that completes payment
    it should activate the mobile line
    it should send a welcome confirmation

describe onboarding through the web
  it_behaves_like "onboarding a new mobile customer"
  that uploads a selfie for verification
    it should match the selfie against the ID photo

describe onboarding through voice
  it_behaves_like "onboarding a new mobile customer"
  that speaks the verification code
    it should confirm identity via voice match

describe onboarding through the retail store
  it_behaves_like "onboarding a new mobile customer"
  that scans the physical ID at the counter
    it should verify the document in real time
```

**Promote** when a condition repeated inside many areas is actually a core state that other behaviors sit inside. Pull it to the outermost boundary and nest everything under it.
```
before:                                     after:
describe a Payment                          describe a Payment
  that is submitted                           with an expired token       *promoted
    with an expired token  ←repeated            that is submitted
    with a valid token                            it should reject
  that is refunded                              that is refunded
    with an expired token  ←repeated              it should reject
    with a valid token                          that is disputed
  that is disputed                                it should reject
    with an expired token  ←repeated            that checks balance
    with a valid token                            it should reject
  that checks balance                           that generates statement
    with an expired token  ←repeated              it should reject
    with a valid token                        with a valid token
  that generates statement                      that is submitted
    with an expired token  ←repeated              it should process
    with a valid token                          that is refunded
                                                  it should process
                                                ...
```

Start from an agreed sketch and deepen toward green tests and production code. Each level **adds** artifacts and **extends** the previous — do not fill in details from a more detailed fidelity.

| Fidelity | Output |
|---|---|
| **behavior** | describe/it hierarchy with `BDD: SIGNATURE` markers in each `it` |
| **realization** | Same hierarchy; each `it should` carries the domain call graph (`->` / `<-`) for Act and observable side effects |
| **development** | Implemented tests + production code |

## Shared rules

```yaml
alwaysApply: false
globs: "**/*spec.py,**/*_spec.py,**/*spec.ts,**/*Spec.java,**/*-sketch.md"
```

Whenever you write or reshape describe / that / with / it-should specs, or code that is supported by these specifications. Follow these rules.

- **`observable-behavior`** — Prove what a stakeholder can verify without reading code (return value, state, public effect). Never internals. Assertions on internals break when the code is refactored and still pass when the behavior is wrong.
- **`domain-practice-alignment`** — Describe names must match domain language / model exactly, so the business, the spec, and the code all use the same words.
- **`usage-order-behaviors`** — Order describes, contexts, and examples as a **usage story** or operational sequence (what happens first → next). Do not order by implementation layer, package, or internal type. In usage order a missing step is obvious; ordered by layer, nobody can tell what is not covered.
- **`describe-is-subject-not-internal`** — A `describe` is a domain subject, state, or observable condition — never a manager, hub, runner, service, or other internal (`SessionLog`, `ToolsetRunner`, …). A spec named after a class has to be rewritten when that class is replaced, even though the behavior did not change.
- **`describe-is-plain-english`** — Full English phrases (e.g. "an action that is annotated with log", "an action that is not annotated"). Never symbol/mechanism names (`"@log marker"`) as the subject.
- **`shared-describe-subject`** — Keep **one** outermost `describe` per domain subject. When two top-level describes share the same opening phrase and only diverge in a trailing qualifier (`registered for deploy` vs `with mcp-published operations`, `context guidance registered for` vs `context guidance with`, `a context tool module with fidelity sections` vs `with fidelities and assembly`), that divergence is a **branch** — promote the shared phrase to the single describe and nest each qualifier as a sibling `with` / `that` context. Do not repeat the shared setup string in a second top-level describe.
- **`state-not-when`** — Never name a nested state with `when`. Use `that …` for events/conditions on the subject and `with …` for standing conditions. Ask: what event or condition must already be true for this observation?
- **`nest-by-enabling-events`** — Each nested `that` / `with` must be a real precondition or event required for the nested `it should` — not a test-file grouping convenience.
- **`context-setup-expresses-state`** — Any `before.each`, `before.all`, or Arrange nested directly under a `that`/`with` must establish the state named in that label. Read label and setup together: if the label says the subject is annotated, configured, or classified a certain way, the setup must make that true — not merely boot the host, wire paths, or call a factory. Put host boot, browser launch, and construction plumbing in a parent context whose label says the host is started, loaded, or running (`that is hosted on…`, `that the server has started…`).
- **`full-surface-coverage`** — Full coverage means the behavior tree is complete — every observable outcome has an `it should` in the right branch. Walk the describe/`that`/`with` tree for missing subjects, states, and outcomes; do not add one `it` per public method just because the member exists.
- **`scan-fixture-pair`** — A mechanical mistake spec passes the fail file to `expect_scan_fails` and the pass file to `expect_scan_passes` (`cdd_guidance.practices.bdd.spec_helpers`). Do not invent a parallel eval spec harness.

#### Overview

Expand each agreed `it should` into the domain call graph that executes that observation — sketch fidelity only (signatures and collaborator calls, no bodies). Notation matches `@clean_engineering` **model** interactions (`->` outbound, `<-` return). This fidelity does not restate GWT scenarios; it traces the describe/`that`/`with` tree already fixed at **behavior**.

#### Guidance

- **Default on** after **behavior** signatures exist, unless the user says **no realizations**.
- Walk implementation from the outermost domain entry for the observation; strip pass-through helpers and language-native noise; stop at external systems with `[ExternalSystem]` at the boundary (same rules as `@practices/stories/story-realizations`).
- Keep Arrange surface lines (`-> subject = new …`, property sets) separate from the nested call graph under the Act that the observation proves.
- Store graphs on observations in the BDD model: fenced blocks in `templates/bdd-sketch.md`, round-tripped through `practices/bdd/model` (same call-graph conversion as stories and clean engineering).

Fill the **realization** section of `templates/bdd-templates.{ext}` (`.py` / `.java` / `.ts`) — call-graph comments or structured `realization` data beside each `BDD: SIGNATURE` until **development** replaces them with real Arrange / Act / Assert.

#### Rules

```yaml
alwaysApply: false
globs: "**/*spec.py,**/*_spec.py,**/*spec.ts,**/*Spec.java,**/*-sketch.md,**/*-realization.md"
```

Whenever you add or change call graphs on BDD observations, or change production code those graphs describe. Follow these rules.

If this change will not stay here, follow `practices/bdd/bdd-behavior.mdc`.

- **`strip-helpers-to-domain-calls`** — Same rule as story realizations: show the domain call the helper delegates to.
- **`full-call-graph-per-observation`** — Follow every named domain or external-system collaborator from the entry operation through returns; do not stop at the first hop.
- **`external-systems-at-their-boundary`** — Label `[ExternalSystem]` at the seam; do not recurse inside vendor code.
- **`no-typescript-internals`** — Omit framework and language-native steps unless the observation is entirely infrastructure.
- **`sketch-fidelity`** — Signatures and interaction arrows only; no assertions, mocks, or production imports in the realization artifact.
- **`hierarchy-preservation`** — One graph per `it should`; do not add or remove observations when deepening to realization.

**Pass:** an `it` whose body is only call-graph comments (or `BDD: SIGNATURE` plus `# ->` lines) naming real domain operations.

**Fail:** assertions, mocks, or invented collaborators not traced to source.

---

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

[spec]

spec:
  fidelity: behavior
  id: dotPath
  name: string
  descriptions: [description]
  where:
    - id is this spec name slug
    - the outermost describe is the subject
    - order follows the usage story
  rules:
    - observable-behavior
    - domain-practice-alignment
    - usage-order-behaviors
    - shared-describe-subject
    - full-surface-coverage
    - framework-syntax

description:
  fidelity: behavior
  id: dotPath
  text: string
  order: number
  belongsTo: [spec | description]
  alignsWith?: class
  contexts?: [context]
  descriptions?: [description]
  observations?: [observation]
  where:
    - id is the text slugs from the spec through each parent description to this one, joined by dots
    - plain-English subject, state, or observable condition
    - sibling describes are mutually exclusive
    - reading this describe through each nested that and with to it should is one sentence
  rules:
    - describe-is-subject-not-internal
    - describe-is-plain-english
    - domain-practice-alignment

context:
  fidelity: behavior
  id: dotPath
  text: string
  order: number
  belongsTo: [description | context]
  kind: "that" | "with"
  contexts?: [context]
  observations?: [observation]
  examples?: [example]
  where:
    - id is the parent id, then this text slug, joined by dots
    - that names an enabling event or condition already true
    - with names a standing condition
    - a nested context is a precondition of the observations under it
    - setup under the label establishes the state the label names
    - examples are the shared arrange state for the observations here
  rules:
    - state-not-when
    - nest-by-enabling-events
    - context-setup-expresses-state
    - context-sharing

observation:
  fidelity: behavior
  id: dotPath
  text: string
  order: number
  belongsTo: [context | description]
  examples?: [example]
  demonstrates?: class
  invokes?: [operation | property]
  specifies?: scenario
  where:
    - id is the parent context or description id, then this text slug, joined by dots
    - one observable outcome a stakeholder can verify
    - behavior fidelity is a signature with no assertion body
    - examples are the concrete cases for this outcome
    - demonstrates is the class whose public effect this observation proves
    - invokes is the operation or property the call surface exercises
    - specifies is the story scenario this observation makes executable
  rules:
    - observable-behavior
    - full-surface-coverage
    - no-implementation
    - hierarchy-preservation
    - one-assertion-per-test
    - one-signature-at-a-time
    - red-then-green
    - minimum-green
    - code-minimalism
    - layer-isolation
    - oo-api-design
    - honors-documented-surface-contracts
    - scan-fixture-pair

## Overview

Behavior-driven development turns domain vocabulary into passing tests. Every BDD artifact is an indented hierarchy. Sketch that shape first (`templates/bdd-sketch.md`).

**Tooling & Idioms:** Refer to [`cdd_guidance/references/language-tools.md`](../../references/language-tools.md) for language-specific tool recommendations and idiomatic patterns.

## Guidance

Design the tree hierarchy by building a flowing sentence. Build every hierarchy so that reading from the outermost `describe` through every nested `that`/`with` down to the `it should` produces a clean, flowing English sentence — spoken aloud, it describes the behavior naturally. When it does not read as a sentence, the nesting is grouping tests for convenience instead of following the conditions the behavior depends on — and you can no longer reason about all the possible behaviors and alternate behaviors that require coverage. At development fidelity, scan production source for coverage gaps before filling signatures.

**Always start with the subject:** place the baseline entity type, class, or user mode at the outermost `describe` — everything below inherits it, so the wrong subject at the top misplaces every behavior under it. **Then nest layers in any order** — choose whichever sequence produces the most natural spoken sentence. Nesting means each condition is set up once and everything inside adds to it — easier to follow, and no rebuilding the same state in every test. Select from these three layer types and arrange them to flow: 

* **Structure:** the content configuration or data shape of that identity. `with items in the cart`, `with no billing address`, `with a linked payment method`
* **Event:** the static system state *after* an action has been finalized. `that has been submitted`, `that has been cancelled`, `that has been approved` — express lifecycle events as past-participle states only
* **Environmental Variance:** external factors, temporal rules, or inputs applied to that state. `during a flash sale weekend`, `outside of promotional periods`, `on a public holiday`

Arrange these in whatever sequence makes the sentence read naturally. `"with items in the cart, that has been submitted, during a flash sale"` flows. Always let the sentence guide the nesting order.

> *"a ShoppingCart, for a premium member account, with items in the cart, that has been submitted, during a flash sale weekend, it should apply an automatic double-points multiplier"*

**Branch** when the system behaves entirely differently based on a change. Make sibling `describe` blocks mutually exclusive.
```
describe a user
  that is authenticated
    [Behaviors exclusive to logged-in state]
  that is an anonymous visitor
    [Behaviors exclusive to logged-out state]
```

**Nest** when a sub-state inherits everything from its parent but introduces another behavior — a nested block only makes sense if the parent state has to hold for the behavior to happen.
```
describe an account
  that is premium
    with a linked payment method
      [Behaviors for fully active premium users]
      that belongs a minor
      [Behaviors for minors linked premium users account]
```

**Share** when multiple channels or implementations produce the same observable behavior but each has a few unique behaviors of its own. Define the shared behaviors once, include them per channel, add only the deltas.
```
shared_examples "onboarding a new mobile customer"
  that selects a plan
    it should display the selected plan details
    it should show the monthly cost
  that provides identity verification
    it should validate the customer's ID
    it should create a pending account
  that completes payment
    it should activate the mobile line
    it should send a welcome confirmation

describe onboarding through the web
  it_behaves_like "onboarding a new mobile customer"
  that uploads a selfie for verification
    it should match the selfie against the ID photo

describe onboarding through voice
  it_behaves_like "onboarding a new mobile customer"
  that speaks the verification code
    it should confirm identity via voice match

describe onboarding through the retail store
  it_behaves_like "onboarding a new mobile customer"
  that scans the physical ID at the counter
    it should verify the document in real time
```

**Promote** when a condition repeated inside many areas is actually a core state that other behaviors sit inside. Pull it to the outermost boundary and nest everything under it.
```
before:                                     after:
describe a Payment                          describe a Payment
  that is submitted                           with an expired token       *promoted
    with an expired token  ←repeated            that is submitted
    with a valid token                            it should reject
  that is refunded                              that is refunded
    with an expired token  ←repeated              it should reject
    with a valid token                          that is disputed
  that is disputed                                it should reject
    with an expired token  ←repeated            that checks balance
    with a valid token                            it should reject
  that checks balance                           that generates statement
    with an expired token  ←repeated              it should reject
    with a valid token                        with a valid token
  that generates statement                      that is submitted
    with an expired token  ←repeated              it should process
    with a valid token                          that is refunded
                                                  it should process
                                                ...
```

Start from an agreed sketch and deepen toward green tests and production code. Each level **adds** artifacts and **extends** the previous — do not fill in details from a more detailed fidelity.

| Fidelity | Output |
|---|---|
| **behavior** | describe/it hierarchy with `BDD: SIGNATURE` markers in each `it` |
| **realization** | Same hierarchy; each `it should` carries the domain call graph (`->` / `<-`) for Act and observable side effects |
| **development** | Implemented tests + production code |

## Shared rules

```yaml
alwaysApply: false
globs: "**/*spec.py,**/*_spec.py,**/*spec.ts,**/*Spec.java,**/*-sketch.md"
```

Whenever you write or reshape describe / that / with / it-should specs, or code that is supported by these specifications. Follow these rules.

- **`observable-behavior`** — Prove what a stakeholder can verify without reading code (return value, state, public effect). Never internals. Assertions on internals break when the code is refactored and still pass when the behavior is wrong.
- **`domain-practice-alignment`** — Describe names must match domain language / model exactly, so the business, the spec, and the code all use the same words.
- **`usage-order-behaviors`** — Order describes, contexts, and examples as a **usage story** or operational sequence (what happens first → next). Do not order by implementation layer, package, or internal type. In usage order a missing step is obvious; ordered by layer, nobody can tell what is not covered.
- **`describe-is-subject-not-internal`** — A `describe` is a domain subject, state, or observable condition — never a manager, hub, runner, service, or other internal (`SessionLog`, `ToolsetRunner`, …). A spec named after a class has to be rewritten when that class is replaced, even though the behavior did not change.
- **`describe-is-plain-english`** — Full English phrases (e.g. "an action that is annotated with log", "an action that is not annotated"). Never symbol/mechanism names (`"@log marker"`) as the subject.
- **`shared-describe-subject`** — Keep **one** outermost `describe` per domain subject. When two top-level describes share the same opening phrase and only diverge in a trailing qualifier (`registered for deploy` vs `with mcp-published operations`, `context guidance registered for` vs `context guidance with`, `a context tool module with fidelity sections` vs `with fidelities and assembly`), that divergence is a **branch** — promote the shared phrase to the single describe and nest each qualifier as a sibling `with` / `that` context. Do not repeat the shared setup string in a second top-level describe.
- **`state-not-when`** — Never name a nested state with `when`. Use `that …` for events/conditions on the subject and `with …` for standing conditions. Ask: what event or condition must already be true for this observation?
- **`nest-by-enabling-events`** — Each nested `that` / `with` must be a real precondition or event required for the nested `it should` — not a test-file grouping convenience.
- **`context-setup-expresses-state`** — Any `before.each`, `before.all`, or Arrange nested directly under a `that`/`with` must establish the state named in that label. Read label and setup together: if the label says the subject is annotated, configured, or classified a certain way, the setup must make that true — not merely boot the host, wire paths, or call a factory. Put host boot, browser launch, and construction plumbing in a parent context whose label says the host is started, loaded, or running (`that is hosted on…`, `that the server has started…`).
- **`full-surface-coverage`** — Full coverage means the behavior tree is complete — every observable outcome has an `it should` in the right branch. Walk the describe/`that`/`with` tree for missing subjects, states, and outcomes; do not add one `it` per public method just because the member exists.
- **`scan-fixture-pair`** — A mechanical mistake spec passes the fail file to `expect_scan_fails` and the pass file to `expect_scan_passes` (`cdd_guidance.practices.bdd.spec_helpers`). Do not invent a parallel eval spec harness.

#### Overview

Implement BDD tests with production code.

#### Guidance

**Procedure:** Follow the **Test shape ladder** in `@clean_engineering` `## code` § Procedure — real conditions first, then stub TDD, then e2e swap on request.

**Tooling & Idioms:** Refer to [`cdd_guidance/references/language-tools.md`](../../references/language-tools.md) for language-specific tool recommendations and idiomatic patterns for tests.

1. **Confirm framework** — inherit from the behavior file.
2. **Scan markers** — list all `it` blocks still containing `BDD: SIGNATURE`; report count.
3. **Identify shared setup** — extract to `beforeEach` / `with before.each:` or a factory when three or more siblings share arrangement.
4. Pick **one** marker. Use the **realization** call graph for Act when present; otherwise derive Act from the observation label and domain model. Fill Arrange-Act-Assert from the DEVELOPMENT TESTS section of `templates/bdd-templates.{ext}` (`.py` / `.java` / `.ts`).
5. Run the test — confirm RED for the right reason.
6. Write the **minimum** production code until GREEN (PRODUCTION CODE section of the same template).
7. Refactor only while green. Move to the next marker.
8. Repeat until zero markers remain, then run **validate**.

#### Rules

```yaml
alwaysApply: false
globs: "**/*spec.py,**/*_spec.py,**/*spec.ts,**/*Spec.java,**/*-sketch.md"
```

Whenever you create, alter, or delete production code supported by BDD specs, or the specs themselves. Follow these rules.

If this change will not stay here, follow `practices/bdd/bdd-behavior.mdc`.

- **`hierarchy-preservation`** — 1:1 from sketch nesting to code. Nothing added, removed, or flattened. Same depth, same `it` count. Changing the tree during implementation drops behaviors that were agreed on, or adds ones nobody specified.
- **`red-then-green`** — Fix code by writing the test first, then watching it fail, then making production code changes.
- **`minimum-green`** / **`code-minimalism`** — Least production code that makes this assertion pass. Refactor only while green.
- **`one-signature-at-a-time`** — Implement and test one `BDD: SIGNATURE` at a time — get it passing before moving to the next. Do not fill in every test body first and try to make them all pass together.
- **`one-assertion-per-test`** — One outcome per `it` — two outcomes in one test and a failure does not tell you which behavior broke.
- **`layer-isolation`** — Mock only at architecture boundaries; never the subject under test. Mocking the subject tests the mock, not your code.
- **`context-sharing`** — Shared construction in `beforeEach` / factory at three sibling dupes. Repeated setup in every test hides what actually differs between them.
- **`context-setup-expresses-state`** — Same rule as behavior (above). At development fidelity, `before.each` is Arrange: it must express the parent context's named state, not smuggle host boot under a domain classification branch.
- **`oo-api-design`** — Ask-don't-tell: construct fully; own state on the object; operations on the closest domain concept. Tests that assemble state through getters or pass setup bags couple to how you built it, not what it does.
- **`honors-documented-surface-contracts`** — Public API must match documented surface contracts; if a spec fights the contract, fix the spec.

---

#### Template

"""
# Conceptual BDD Reference (Python/Mamba style)
# Refer to cdd_guidance/references/language-tools.md for tool recommendations.
# =============================================================================
# BEHAVIOR (SIGNATURE) — `signature-markers`
# Every `it` body is exactly `pass  # BDD: SIGNATURE` — nothing else. A bare comment is not a Python body.
#
# with description('{DomainEntity}'):
#     with context('that has been created'):
#         with it('should have {initial property} assigned'):
#             pass  # BDD: SIGNATURE
# =============================================================================
# REALIZATION — call graph per `it` (default after behavior unless user opts out)
# Replace `# BDD: SIGNATURE` with `# ->` / `# <-` lines only — same notation as CE model.
#
#         with it('should reject an expired token'):
#             # cart.checkout()
#             #   -> paymentGateway.charge(amount)
#             #   <- receipt
#             pass  # BDD: SIGNATURE
# =============================================================================
# DEVELOPMENT — `no-remaining-signatures`
# Replace each `# BDD: SIGNATURE` with Arrange / Act / Assert. Zero markers when done.
# Instructions:
#   1. Replace {DomainEntity} with the class or module under test.
#   2. Use Arrange / Act / Assert comments in test bodies.
#   3. One assertion per behavior.
# =============================================================================
"""
from mamba import description, context, it, before
from expects import equal, expect
from {domain_module} import {DomainEntity}

with description('{DomainEntity}'):
    with context('that has been created'):
        with it('should have {initial property} assigned'):
            # Arrange / Act
            entity = {DomainEntity}(**default_data())
            # Assert
            expect(entity.property).to(equal(expected_value))

    with context('that is {active state}'):
        with before.each:
            self.entity = {DomainEntity}(**default_{related_data}())

        with it('should {behavior description}'):
            # Act
            self.entity.{action}({input})
            # Assert
            expect(self.entity.{property}).to(equal({expected_value}))

        with it('should {second behavior}'):
            # Arrange
            {local_setup} = {value}
            # Act
            self.entity.{action}({local_setup})
            # Assert
            expect(self.entity.{property}).to(equal({expected_value}))


# Scan fixture pair — mechanical mistake specs use these helpers, not an eval harness.
from cdd_guidance.practices.bdd.spec_helpers import expect_scan_fails, expect_scan_passes

with description('a scan fixture pair'):
    with context('a file that violates the rule'):
        with it('should fail scan'):
            expect_scan_fails({scan}, '{FailFixturePath}', rule='{Rule}')

    with context('a file that satisfies the rule'):
        with it('should pass scan'):
            expect_scan_passes({scan}, '{PassFixturePath}', rule='{Rule}')

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

Behavior-driven development turns domain vocabulary into passing tests. Every BDD artifact is an indented hierarchy. Sketch that shape first (`templates/bdd-sketch.md`).

**Tooling & Idioms:** Refer to [`cdd_guidance/references/language-tools.md`](../../references/language-tools.md) for language-specific tool recommendations and idiomatic patterns.

## Guidance

Design the tree hierarchy by building a flowing sentence. Build every hierarchy so that reading from the outermost `describe` through every nested `that`/`with` down to the `it should` produces a clean, flowing English sentence — spoken aloud, it describes the behavior naturally. When it does not read as a sentence, the nesting is grouping tests for convenience instead of following the conditions the behavior depends on — and you can no longer reason about all the possible behaviors and alternate behaviors that require coverage. At development fidelity, scan production source for coverage gaps before filling signatures.

**Always start with the subject:** place the baseline entity type, class, or user mode at the outermost `describe` — everything below inherits it, so the wrong subject at the top misplaces every behavior under it. **Then nest layers in any order** — choose whichever sequence produces the most natural spoken sentence. Nesting means each condition is set up once and everything inside adds to it — easier to follow, and no rebuilding the same state in every test. Select from these three layer types and arrange them to flow: 

* **Structure:** the content configuration or data shape of that identity. `with items in the cart`, `with no billing address`, `with a linked payment method`
* **Event:** the static system state *after* an action has been finalized. `that has been submitted`, `that has been cancelled`, `that has been approved` — express lifecycle events as past-participle states only
* **Environmental Variance:** external factors, temporal rules, or inputs applied to that state. `during a flash sale weekend`, `outside of promotional periods`, `on a public holiday`

Arrange these in whatever sequence makes the sentence read naturally. `"with items in the cart, that has been submitted, during a flash sale"` flows. Always let the sentence guide the nesting order.

> *"a ShoppingCart, for a premium member account, with items in the cart, that has been submitted, during a flash sale weekend, it should apply an automatic double-points multiplier"*

**Branch** when the system behaves entirely differently based on a change. Make sibling `describe` blocks mutually exclusive.
```
describe a user
  that is authenticated
    [Behaviors exclusive to logged-in state]
  that is an anonymous visitor
    [Behaviors exclusive to logged-out state]
```

**Nest** when a sub-state inherits everything from its parent but introduces another behavior — a nested block only makes sense if the parent state has to hold for the behavior to happen.
```
describe an account
  that is premium
    with a linked payment method
      [Behaviors for fully active premium users]
      that belongs a minor
      [Behaviors for minors linked premium users account]
```

**Share** when multiple channels or implementations produce the same observable behavior but each has a few unique behaviors of its own. Define the shared behaviors once, include them per channel, add only the deltas.
```
shared_examples "onboarding a new mobile customer"
  that selects a plan
    it should display the selected plan details
    it should show the monthly cost
  that provides identity verification
    it should validate the customer's ID
    it should create a pending account
  that completes payment
    it should activate the mobile line
    it should send a welcome confirmation

describe onboarding through the web
  it_behaves_like "onboarding a new mobile customer"
  that uploads a selfie for verification
    it should match the selfie against the ID photo

describe onboarding through voice
  it_behaves_like "onboarding a new mobile customer"
  that speaks the verification code
    it should confirm identity via voice match

describe onboarding through the retail store
  it_behaves_like "onboarding a new mobile customer"
  that scans the physical ID at the counter
    it should verify the document in real time
```

**Promote** when a condition repeated inside many areas is actually a core state that other behaviors sit inside. Pull it to the outermost boundary and nest everything under it.
```
before:                                     after:
describe a Payment                          describe a Payment
  that is submitted                           with an expired token       *promoted
    with an expired token  ←repeated            that is submitted
    with a valid token                            it should reject
  that is refunded                              that is refunded
    with an expired token  ←repeated              it should reject
    with a valid token                          that is disputed
  that is disputed                                it should reject
    with an expired token  ←repeated            that checks balance
    with a valid token                            it should reject
  that checks balance                           that generates statement
    with an expired token  ←repeated              it should reject
    with a valid token                        with a valid token
  that generates statement                      that is submitted
    with an expired token  ←repeated              it should process
    with a valid token                          that is refunded
                                                  it should process
                                                ...
```

Start from an agreed sketch and deepen toward green tests and production code. Each level **adds** artifacts and **extends** the previous — do not fill in details from a more detailed fidelity.

| Fidelity | Output |
|---|---|
| **behavior** | describe/it hierarchy with `BDD: SIGNATURE` markers in each `it` |
| **realization** | Same hierarchy; each `it should` carries the domain call graph (`->` / `<-`) for Act and observable side effects |
| **development** | Implemented tests + production code |

## Shared rules



Whenever you write or reshape describe / that / with / it-should specs, or code that is supported by these specifications. Follow these rules.

- **`observable-behavior`** — Prove what a stakeholder can verify without reading code (return value, state, public effect). Never internals. Assertions on internals break when the code is refactored and still pass when the behavior is wrong.
- **`domain-practice-alignment`** — Describe names must match domain language / model exactly, so the business, the spec, and the code all use the same words.
- **`usage-order-behaviors`** — Order describes, contexts, and examples as a **usage story** or operational sequence (what happens first → next). Do not order by implementation layer, package, or internal type. In usage order a missing step is obvious; ordered by layer, nobody can tell what is not covered.
- **`describe-is-subject-not-internal`** — A `describe` is a domain subject, state, or observable condition — never a manager, hub, runner, service, or other internal (`SessionLog`, `ToolsetRunner`, …). A spec named after a class has to be rewritten when that class is replaced, even though the behavior did not change.
- **`describe-is-plain-english`** — Full English phrases (e.g. "an action that is annotated with log", "an action that is not annotated"). Never symbol/mechanism names (`"@log marker"`) as the subject.
- **`shared-describe-subject`** — Keep **one** outermost `describe` per domain subject. When two top-level describes share the same opening phrase and only diverge in a trailing qualifier (`registered for deploy` vs `with mcp-published operations`, `context guidance registered for` vs `context guidance with`, `a context tool module with fidelity sections` vs `with fidelities and assembly`), that divergence is a **branch** — promote the shared phrase to the single describe and nest each qualifier as a sibling `with` / `that` context. Do not repeat the shared setup string in a second top-level describe.
- **`state-not-when`** — Never name a nested state with `when`. Use `that …` for events/conditions on the subject and `with …` for standing conditions. Ask: what event or condition must already be true for this observation?
- **`nest-by-enabling-events`** — Each nested `that` / `with` must be a real precondition or event required for the nested `it should` — not a test-file grouping convenience.
- **`context-setup-expresses-state`** — Any `before.each`, `before.all`, or Arrange nested directly under a `that`/`with` must establish the state named in that label. Read label and setup together: if the label says the subject is annotated, configured, or classified a certain way, the setup must make that true — not merely boot the host, wire paths, or call a factory. Put host boot, browser launch, and construction plumbing in a parent context whose label says the host is started, loaded, or running (`that is hosted on…`, `that the server has started…`).
- **`full-surface-coverage`** — Full coverage means the behavior tree is complete — every observable outcome has an `it should` in the right branch. Walk the describe/`that`/`with` tree for missing subjects, states, and outcomes; do not add one `it` per public method just because the member exists.
- **`scan-fixture-pair`** — A mechanical mistake spec passes the fail file to `expect_scan_fails` and the pass file to `expect_scan_passes` (`cdd_guidance.practices.bdd.spec_helpers`). Do not invent a parallel eval spec harness.

### behavior

```yaml
default_format: python
stage: specification
clean_engineering: model
```

#### Overview

Define BDD signatures — describe/it names for every observation, no test bodies.

#### Guidance

- Sketch nesting (subjects → `with`/`that`/events → `it should`) is agreed
- **Confirm framework** — ask if not stated. Default: Mamba/Python; Jest/TypeScript or JUnit 5/Java when the project uses those.
- Convert every sketch hierarchy line to its framework equivalent (see Framework syntax).
- Process in batches of ~18 describe blocks when the hierarchy is large.

Fill the **behavior** (SIGNATURE) section of `templates/bdd-templates.{ext}` (`.py` / `.java` / `.ts`).

#### Rules

```yaml
alwaysApply: false
globs: "**/*spec.py,**/*_spec.py,**/*spec.ts,**/*Spec.java,**/*-sketch.md"
```

Whenever you name or re-nest describe/it signatures, change code that relies on those signatures, or change specifications that need this kind of rename. Follow these rules.

If this change will not stay here, follow `practices/bdd.mdc`.

- **`state-not-when`** — Nest by the state or condition that enables an observation, never by a `when` trigger.
- **`nest-by-enabling-events`** — Sub-groupings are conditions that unlock further behavior, not implementation steps.
- **`context-setup-expresses-state`** — Setup under a label must establish that label's state, not unrelated host boot.
- **`shared-describe-subject`** — Same rule as shared rules (above); at behavior fidelity, scan the spec file for repeated top-level `describe` prefixes before adding another subject line.
- **`no-implementation`** — No assertions, mocks, production imports, helpers, or `beforeEach` / shared setup.
- **`framework-syntax`** — Refer to [`cdd_guidance/references/language-tools.md`](../../references/language-tools.md) for the target language's syntax. One confirmed framework throughout. Do not mix Jest and Mamba constructs.

**Pass:**
```typescript
it('should apply a percentage discount to eligible items', () => {
  // BDD: SIGNATURE
});
```

**Fail:** any assertion, mock, import of production code, or helper inside the body.

---