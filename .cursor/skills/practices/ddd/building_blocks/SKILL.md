## Overview

Build the solution around how the business actually works, in the words the business already uses. When the software mirrors the business, it holds the business's logic and knowledge where that understanding actually lives; when it mirrors a database, a framework, or a screen layout, every business conversation has to be re-translated and what the business knows ends up scattered wherever the technology happened to put it.

**`clean_engineering`** owns OO structure, one skill per fidelity: **`clean_engineering-modules`** shapes the module boundaries and seams when **`bounded_context`** draws the map; **`clean_engineering-model`** types the classes, operations, and relationships when **`building_blocks`** classifies concepts with stereotypes; **`clean_engineering-code`** implements the seams when **`tactics`** wires repositories, events, and factories. Do not restate module or class analysis here. DDD adds the domain layer on top: where the language changes, which clusters protect which rules, and what each concept actually is.

---

When this DDD work is done, call guidance on the Clean Engineering companion and pass that companion to this action as a separate tools run. The action already knows what to do for every tool. Do not inline.

## Shared rules

Use these rules when defining domain logic in code, a model, or language.

- **`ubiquitous-language-everywhere`** — One term per concept, taken from the business, used identically on the map, in the model, in the code, and in the tests. A technical synonym makes every reader keep a translation in their head, and the two names drift until they mean different things.
- **`model-the-domain-not-the-implementation`** — Model what the business does, not what the current database, screens, or vendor API expose. A model shaped by an existing implementation locks in decisions nobody chose on purpose.
- **`vocabulary-traces-to-domain-source`** — Trace every term back to domain experts or an upstream artifact. Invent a word and each layer keeps its own glossary.
- **`read-all-source-context-in-full`** — Before locking a context boundary or aggregate, read every referenced segment, sketch, grill-answer, and handoff in full. Titles and indexes show words, not mechanics; a boundary drawn from headings alone misses coupling that shows up only in the prose.
- **`do-not-invent-concepts`** — Only model contexts, aggregates, and types the source describes or the user explicitly asks for. Invented contexts and DTO-shaped nouns become code nobody asked for and integrations nobody planned.

---

#### Overview


**Default format:** markdown
**Stage:** specification

**Goal:** Classify each concept on the map — entity, value, repository, event, service — and shape the classes that carry them.

**Produce:** Update `bounded-context-map.md` using `templates/bounded-context-template.md`. Call clean_engineering at **model**.

#### Guidance

**Work through one bounded context and one aggregate at a time.** Call clean_engineering at **model** fidelity and use its object-oriented analysis to deepen the Bounded Contexts and aggregates inside them: begin at the root, work inward through the objects it governs, then work outward through its dependencies. Classify each concept with one or more of the DDD **building blocks** below.

The building blocks look technical, but only the business can answer them. Fully defining each aggregate is how you flesh out the solution's seams from a *business* lens — boundaries that follow where the business actually changes, not where the technology happened to split.

**Start with the Aggregate Root.** Identify the root and make it the only entry point for the aggregate. Keep other members behind the root so one object protects changes across the whole consistency boundary.

Determine which concepts are **Entities**, including the root. State how the business distinguishes each Entity as its values change. A Customer remains the same Customer after changing an address; a ported number remains the same line; a Subscription remains the same Subscription after adding a family member. Identity determines what the business can find, update, replace, and retire.

Determine which concepts are **Value Objects**, whose meaning comes entirely from their values. Make them immutable and shareable rather than giving them independent identity or mutable lifecycle. Examples include a chosen color, an order's delivery address, and a Shopping Cart product line.

**Add a Factory** when creating a valid object is too much for a simple constructor — complex business rules, work that crosses aggregates, an intricate workflow, or a choice among several subtypes behind one interface. This keeps all of that creation logic in one obvious place instead of leaving every caller to figure it out for themselves.

**Use a Domain Service** when the business operation belongs to no single object — eg transferring funds from one bank account to another: neither account owns the transfer; debiting one and crediting the other is one piece of work that spans both.

As you define aggregates and bounded contexts, **decide synchronization for every cross-aggregate and cross-context dependency.** Record which side owns the source fact, what triggers synchronization, what the receiving side copies or derives, how terms are translated, and how much delay is acceptable. Use an immediate event when the consumer must react as the fact changes, a scheduled refresh when delay is acceptable, or an on-demand query when no local copy is needed. A dependency without timing and translation leaves two valid models with no agreed way to remain consistent.

**Define Domain Events** for business state changes that other aggregates or contexts must react to. Name each event in past tense, define it on the publishing Aggregate Root, identify its consumers, and state which facts cross the boundary. The consumer decides what it needs from the event, so the publisher does not depend on each subscriber's workflow.

**Use a Specification for a named rule that must mean the same thing in several operations.** A `PreferredCustomerSpecification` can define what makes a Customer preferred, support a query for preferred customers, validate an existing customer, and guide a Factory creating one. Keep the predicate in the Specification and let the Entity or Factory perform the state change; otherwise the same definition is copied into queries, validation, and creation and eventually disagrees with itself.

#### Rules

Use these rules when tagging types already on the map — entity vs value, repository, event, service — not inventing a parallel model.

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
