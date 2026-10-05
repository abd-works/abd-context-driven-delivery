Before you continue, echo the following message to the user:

The following rules need to be followed while editing this document:
hide-inner-details
keep-operations-small-focused
prefer-instance-operations
keep-operations-single-responsibility
simplify-control-flow
errors-out-of-existence
use-intention-revealing-names
use-consistent-naming
provide-meaningful-context
eliminate-duplication
no-legacy-api-after-refactor
use-exceptions-properly
never-swallow-exceptions
limit-comments
domain-nouns-only
named-seam-and-constraint
modules-name-the-source-type
high-cohesion
single-boundary
deep-module
abstraction-focus
purpose-before-mechanism
public-seam-only
module-mistakes-feed-ce
use-typed-signatures
general-purpose-surface
temporal-independence
one-way-deps
extensions-live-with-the-domain
low-coupling
layer-separation
nesting
model-modules-follow-the-partition
class-not-property-instance-or-subtype
keep-classes-single-responsibility
shape-classes-around-resources
put-logic-on-the-owning-resource
use-property-not-accessor
prefer-class-operations
use-explicit-dependencies
external-system-interface-is-one-way
limit-operation-parameters
avoid-vague-parameter-names
state-change-returns-record-or-named-failure
domain-exception-carries-context
write-invariants
write-interactions
one-canonical-model-document
c:\dev\abd-context-driven-delivery\practices\ux\scripts\emit_story_javascript.py
**/*.py
**/*.ts
**/*.tsx
**/*.js
**/*.java
**/*-sketch.md
**/module-context.md
**/*modules*.drawio
**/*-model.md
**/*-model.py
**/*example_factory*

#### Rules

```yaml
alwaysApply: false
globs: "**/*.py,**/*.ts,**/*.tsx,**/*.js,**/*.java,**/*-sketch.md"
```

Whenever you create, alter, or delete production behavior — bodies, constructors, call sites — including code supported by a model or module map. Follow these rules.

If this change will not stay here, follow `practices/clean_engineering/model.mdc`.

**Implement the model**
- `hide-inner-details` — Expose behavior through named operations. Do not let callers see how the class stores or arranges its data — once they read the storage directly it becomes a public contract you cannot change. Private fields on the same class hide implementation; you do not need a second class for that. Read-only to callers can mean return a copy or immutable view from a property — it does not require a frozen class or a second type to hold build steps.
- `keep-operations-small-focused` — Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.
- `prefer-instance-operations` — Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. A single creation method — `instance`, `create`, or `from_*` — may be static so callers can obtain the object.
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
- `extensions-live-with-the-domain` — Domain extensions of a framework belong in the domain module — a nested package under that domain is fine. Do not host them in the base framework package. `GraphEpic` lives with Stories, not in Knowledge Graph; otherwise the framework depends on every practice and cannot stay generic.
- `low-coupling` — Depend only through other modules’ seams. Keep sibling imports few. Reaching past a seam freezes that module’s internals — it can no longer change them without breaking you.
- `layer-separation` — keep dependent modules at different levels of abstractions. Collapse pass-through modules — a module that only forwards turns every signature change into an edit in three files instead of one.
- `nesting` — Nest a child only when it shares mechanics or is a sub-system; keep independent modules flat. Put shared behavior on the parent. A child may depend on the parent, not on siblings.

---

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
- `shape-classes-around-resources` — Model a class around the concept that owns the state and the rule, not a doer, handler, or service that acts on a data bag. A Payment has transactions, a source, and a destination, and it moves the money; it is not a `PaymentService` that takes a `PaymentData` object. A service-plus-bag pair splits the rule from its memory, so every change has to be found in two types and the bag cannot enforce anything. Two resources may collaborate — a model that loads a Module is not a service-plus-bag split.
- `put-logic-on-the-owning-resource` — Put logic on the object that owns the invariant. Do not infer ownership from a route name, Story actor, or Given subject: `client.accounts[id].transactions.last.validate()`, not `client.validateLastTransactionForPrimaryAccount()`. Logic placed away from its state gives two objects authority to change the same rule.
- `hide-inner-details` — Expose behavior through named operations. Do not let callers see how the class stores or arranges its data — once they read the storage directly it becomes a public contract you cannot change. Private fields on the same class hide implementation; you do not need a second class for that.
- `use-property-not-accessor` — Use a named property for stored or derived state. A derived property recalculates from state and collaborators the object already holds, takes no owner or state parameters, and looks like a field to callers through the language's property mechanism. Use an operation only when behavior coordinates several values, collaborators, or lifecycle steps and cannot be represented truthfully as a property. Callers should not need `getX`, `setX`, or storage knowledge. Read-only to callers can mean return a copy or immutable view from a property — it does not require a frozen class or a second type to hold build steps.
- `prefer-class-operations` — Put factory, lifecycle, and helpers used from one class on that class. Do not export them as module-level functions — a free function holds no state, so it takes the object as a parameter and reaches into it to do the work. A file of hanging functions is the same miss: those operations belong on a type, not on the package.
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

Before you continue, echo the following message to the user:

The following rules need to be followed while editing this document:
one-pattern-per-building-block
architectural-granularity-decided
preserve-upstream-names
load-with-identity-in-hand
ports-behind-adapters
experts-words-preferred
domain-concepts-not-technical-names
bc-by-lifecycle-not-ui-themes
one-meaning-per-context
dependency-fields-tracked
no-orphan-contexts
vendor-not-implementation
context-tree-bc-aggregate-concept
bounded-context-file-marks-the-folder
link-arrow-target
hang-deps-on-owning-bc
user-facing-system-first
identity-test-entity-vs-vo
aggregate-root-identity-and-entry
every-concept-classified
service-is-homeless
repository-is-collection-lifecycle
repository-owns-aggregate-lifecycle
external-system-access-is-service-interface
factory-is-complex-creation
shared-identity-is-generalisation
domain-events-past-tense
cross-boundary-synchronization-decided
specification-is-reusable-rule
no-premature-infrastructure
building-blocks-fidelity-requires-tactical-stereotype
flaccid-data-object-no-behavior
screen-interface-not-a-domain-object
private-method-naming
no-orphaned-objects
c:\dev\abd-context-driven-delivery\practices\ux\scripts\emit_story_javascript.py
**/*.py
**/*.ts
**/*.tsx
**/*.js
**/*.java
**/*-sketch.md
**/*bounded-context*
**/*-model.md

#### Rules

```yaml
alwaysApply: false
globs: "**/*.py,**/*.ts,**/*.tsx,**/*.js,**/*.java,**/*-sketch.md"
```

Whenever you persist, publish, or test repositories, events, or factories, or change production code they support. Follow these rules.

If this change will not stay here, follow `practices/ddd/building_blocks.mdc`.

- **`one-pattern-per-building-block`** — Each building block in play gets one named implementation pattern — technology, extension mechanism, test approach — used by every instance of that block. Divergent implementations of the same block make the solution unreadable and untestable as a whole.
- **`architectural-granularity-decided`** — State what a bounded context, an aggregate, and a repository are at runtime (in-process module, container, service with its own store). Left undecided, the first adapter written silently sets it for everything after.
- **`preserve-upstream-names`** — Public API names match the building_blocks model. Renaming here breaks traceability back to the map and the stories.
- **`load-with-identity-in-hand`** — A live `load` takes the identity already in hand. Do not assume ambient session state. Reach owned aggregates through their owner.
- **`ports-behind-adapters`** — Persistence, messaging, and external systems integrate through ports — not direct imports from the domain core.

#### Rules

```yaml
alwaysApply: false
globs: "**/*bounded-context*,**/*-sketch.md"
```

Whenever you create, alter, or delete bounded contexts, aggregates, or the language between them, or change a model or code that forces a language-boundary change. Follow these rules.

- **`experts-words-preferred`** — Use the words domain experts use. An invented synonym becomes a second term every reader must translate.
- **`domain-concepts-not-technical-names`** — Name contexts, aggregates, and concepts — not `Manager`, `Helper`, `Processor`, `*Result`, `*Response`, `*Dto`, or `*Request`. Do not invent a type for fields that already belong on a concept. A technical name carries no meaning the business would recognize, so rules parked on it cannot be found where the concept lives and get re-implemented elsewhere.
- **`bc-by-lifecycle-not-ui-themes`** — Partition by ubiquitous language and how fast the model changes, not by UI themes or journey stages. Do not mint journey-themed contexts that duplicate core domain contexts. Screens and journeys are redrawn while language boundaries hold; a boundary cut along the UI has to move with every redesign and drags the model with it.
- **`one-meaning-per-context`** — Inside a context, one definition per term; name and translate false cognates across contexts. Several aggregates per context is normal. Do not wrap each aggregate in its own bounded context. Two meanings under one word become contradictory code that both looks consistent; a context per aggregate walls one language off from itself and charges integration cost for nothing.
- **`dependency-fields-tracked`** — Every arc names direction, what crosses, how integration happens, and the relationship pattern — or a dated follow-up with owner. An arc that names only a neighbor context does not tell anyone what to build.
- **`no-orphan-contexts`** — Every context on the map appears in a dependency arc or is declared standalone with a reason. A box with no arcs is either missing relationships or should not be on the map.
- **`vendor-not-implementation`** — The context title carries vendor after `|` (`custom`, `bespoke`, or vendor name). Owning team and implementation stack belong elsewhere, because they can change while the domain meaning remains stable.
- **`context-tree-bc-aggregate-concept`** — Three levels on the bounded_context card only: BC → Aggregate → concept. Deeper structure and stereotypes wait for **building_blocks**; tree shape is in the template. Structure drawn before the boundary settles is discarded when the boundary moves — and until then it argues for leaving the boundary where it is.
- **`bounded-context-file-marks-the-folder`** — In code, a bounded context is the folder that contains `.context/bounded-context.md`. The code-format build writes that file when it creates the context folder and each aggregate folder under it. A folder of classes with no such file is a module or a package, so the map and the tree disagree about where the language boundary is.
- **`link-arrow-target`** — Outbound links use `→` with `BC · Aggregate · Entity` or `System · Entity`. Omit leading segments when the target shares the same context or aggregate. A target nobody can resolve is a dependency nobody can build.
- **`hang-deps-on-owning-bc`** — Put each outbound link on the concept or aggregate that has the dependency, not in a global `## Dependencies` section. A parking lot detaches the dependency from the concept that needs it, so it survives changes that should have removed it.
- **`user-facing-system-first`** — The system you are wrapping sits first on the map; external systems of record sit downstream. The map exists to explain that system — everything downstream is context for it, not the subject.

---

#### Rules

```yaml
alwaysApply: false
globs: "**/*bounded-context*,**/*-model.md,**/*-sketch.md"
```

Whenever you classify or reshape domain types as entity, value, repository, event, or service, or change tactics or code that those types support. Follow these rules.

If this change will not stay here, follow `practices/ddd/bounded_context.mdc`.

- **`identity-test-entity-vs-vo`** — Entity when identity transcends attributes; otherwise prefer Value Object. A type that is the access boundary for a cluster is **Aggregate Root + Entity**, not a Domain Service.
- **`aggregate-root-identity-and-entry`** — Every aggregate states the root's identity and uses that root as its only entry point. If identity or entry is ambiguous, the root cannot protect changes across the aggregate.
- **`every-concept-classified`** — Every source concept appears with supporting model content (or `Unresolved`). When harvesting from a sketch, every named type in the sketch appears — do not render a handful of classes from a large map.
- **`service-is-homeless`** — Domain Service is a rare doer only when the operation cannot sit on one domain object. Not SOA: do not invent `FooService` to park verbs.
- **`repository-is-collection-lifecycle`** — Add a Repository only when the business finds, stores, and retires an Aggregate Root independently. Model it as a typed collection of that root with explicit collection multiplicity; reach an owned aggregate through its owner when it has no independent lookup, because a Repository without an independent collection invents a lifecycle the business does not have.
- **`repository-owns-aggregate-lifecycle`** — Put creation, loading, search, update, and retirement of an Aggregate Root on its Repository; keep changes to an already loaded aggregate on the root or its members. An aggregate instance does not create or load itself, because collection lifecycle and aggregate behaviour have different owners.
- **`external-system-access-is-service-interface`** — Represent another system with a named Service or Gateway interface that exposes that system's operations. Let a Repository collaborate with that interface when persistence crosses the system boundary, but do not model the external system as a collection of domain roots, because the external system owns a different model and lifecycle.
- **`factory-is-complex-creation`** — Factory only when valid creation needs subtype choice, several rules, or outside collaborators. Ordinary creation stays on the Aggregate Root so callers have one obvious way to create it.
- **`shared-identity-is-generalisation`** — Shared identity over time → base type + generalisation arrows. Do not flatten as unrelated entities.
- **`domain-events-past-tense`** — Past-tense domain name; name the publishing root, trigger, consumers, and required payload. Events are facts needed outside the aggregate, not a notification for every mutation.
- **`cross-boundary-synchronization-decided`** — Every cross-aggregate or cross-context dependency names the source owner, receiving view, translation, trigger or cadence, and acceptable staleness. Without those decisions, each side can be correct alone while their shared fact silently diverges.
- **`specification-is-reusable-rule`** — Use a Specification when one named predicate must serve more than one query, validation, or creation path. One definition prevents each path from developing a different meaning for the same rule.
- **`no-premature-infrastructure`** — Design intent only: no tables, brokers, framework annotations, or endpoints.
- **`hang-deps-on-owning-bc`** — Keep `→` links on the concept or aggregate from **bounded_context**. No global `## Dependencies` parking lot.
- **`building-blocks-fidelity-requires-tactical-stereotype`** — Every class carries a tactical tag (`<<Aggregate Root>>`, `<<Entity>>`, `<<Value Object>>`, …). Bare names are incomplete.
- **`flaccid-data-object-no-behavior`** — A type is not a field bag. Give it the operations that are **its** work.
- **`screen-interface-not-a-domain-object`** — `open()` / `isShowing()` screen drivers are not domain types. The user action is an operation on the aggregate that owns it.
- **`private-method-naming`** — Public `+name`; private `- _name`. `derive*` helpers are private.
- **`no-orphaned-objects`** — Every domain object has at least one relationship. Value objects that are attributes sit on their owner — not as unconnected cards.

---