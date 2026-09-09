---
name: ddd-building-blocks
description: "Provide guidance for creating bounded contexts, building blocks, and tactics."
disable-model-invocation: true
---

# ddd-building_blocks

Use ddd guidance at `building_blocks` fidelity only.

Refer to these skills in order to fill in details from previous fidelities if not present:
@ddd-bounded_context

# Contexts

Build the solution around how the business actually works, in the words the business already uses. When the software mirrors the business, it holds the business's logic and knowledge where that understanding actually lives; when it mirrors a database, a framework, or a screen layout, every business conversation has to be re-translated and what the business knows ends up scattered wherever the technology happened to put it.

**`clean_engineering`** owns OO structure, one skill per fidelity: **`clean_engineering-modules`** shapes the module boundaries and seams when **`bounded_context`** draws the map; **`clean_engineering-model`** types the classes, operations, and relationships when **`building_blocks`** classifies concepts with stereotypes; **`clean_engineering-code`** implements the seams when **`tactics`** wires repositories, events, and factories. Do not restate module or class analysis here. DDD adds the domain layer on top: where the language changes, which clusters protect which rules, and what each concept actually is.

---

## Guidance

**Mine the source context.** Read every referenced segment, sketch, grill-answer, and handoff in full. Extract domain language, business rules, and expertise from that material — do not infer structure from legacy schemas, screens, or vendor APIs without first translating what they mean in domain terms. Those artifacts show how someone once implemented the business, not what the business is; model from the domain meaning or you preserve accidents of an old implementation as if they were rules.

**Speak one language everywhere.** The term in the source context is the term on the map, in the model, in the code, in the tests, and in the documentation. A *shopping cart* is `ShoppingCart`; a ported telephone number is `TelephoneNumber` carrying `PortingInformation`, not a `PortabilityRequest`. Anywhere a reader has to translate is somewhere two parts of the context can hold different understandings and both look consistent.

**Let conflicting meaning do its job.** When source context disagrees about what a term means — or uses different words for what appears to be the same thing — you have found a real modelling question: a distinction nobody named, or two concepts sharing one word. Resolve it by naming both things and stating how they relate — subtype, association, instance of a type, specification, the same word in two different bounded contexts. Vague terms pass review because nothing pins down the distinction, and the ambiguity turns into contradictory code later.

**Model behaviour, not just data.** Ask what each concept *does* in the business, not only what it holds. A cart checks itself out; an order calculates its own total; a subscription suspends itself. Concepts that only hold fields push the business rules out into managers and services, and then business logic and business state get scattered.

**Treat the model as the design, not documentation of it.** Reason through the model and the language before implementing — the map and the building blocks are the primary organizing design for the software, not a summary you write after the code exists.

**Spend the deep thinking where the context is distinctive.** The part of the domain that makes this business different from a generic one deserves careful modelling; billing formats, address lookup, and sign-in usually do not. Modelling everything to the same depth spends effort on problems the source context never asked you to solve.

**Keep the language alive.** As understanding deepens, rename and restructure — in the model and in the code together. A glossary that no longer matches the code is worse than none, because readers trust it and it is wrong.

---

## Shared rules

- **`ubiquitous-language-everywhere`** — One term per concept, taken from the business, used identically on the map, in the model, in the code, and in the tests. A technical synonym makes every reader keep a translation in their head, and the two names drift until they mean different things.
- **`model-the-domain-not-the-implementation`** — Model what the business does, not what the current database, screens, or vendor API expose. A model shaped by an existing implementation locks in decisions nobody chose on purpose.
- **`vocabulary-traces-to-domain-source`** — Trace every term back to domain experts or an upstream artifact. Invent a word and each layer keeps its own glossary.
- **`read-all-source-context-in-full`** — Before locking a context boundary or aggregate, read every referenced segment, sketch, grill-answer, and handoff in full. Titles and indexes show words, not mechanics; a boundary drawn from headings alone misses coupling that shows up only in the prose.
- **`do-not-invent-concepts`** — Only model contexts, aggregates, and types the source describes or the user explicitly asks for. Invented contexts and DTO-shaped nouns become code nobody asked for and integrations nobody planned.

---

## building_blocks

**Default format:** markdown

**Goal:** Deepen the same context map — under each aggregate already placed at **bounded_context**, add clean_engineering compact class detail and DDD stereotypes. You are classifying and shaping what is already on the map, not inventing a parallel model.

**Produce:** Update `bounded-context-map.md` using `templates/bounded-context-template.md`. Call clean_engineering at **model**.

### Guidance

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

### Rules

- **`identity-test-entity-vs-vo`** — Entity when identity transcends attributes; otherwise prefer Value Object. A type that is the access boundary for a cluster is **Aggregate Root + Entity**, not a Domain Service (`Catalog` is not `<<Service>>` because it "does" selection).
- **`aggregate-root-identity-and-entry`** — Every aggregate states the root's identity and uses that root as its only entry point. If identity or entry is ambiguous, the root cannot protect changes across the aggregate.
- **`every-concept-classified`** — Every source concept appears with supporting model content (or `Unresolved`). When harvesting from a sketch, every named type in the sketch appears — do not render a handful of classes from a large map.
- **`service-is-homeless`** — Domain Service is a rare doer only when the operation cannot sit on one domain object. Not SOA: do not invent `FooService` to park verbs. `CheckoutService.placeOrder` is `Cart.checkout`.
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
- **`flaccid-data-object-no-behavior`** — A type is not a field bag. Give it the operations that are **its** work. Credentials does not grow `signIn`.
- **`screen-interface-not-a-domain-object`** — `open()` / `isShowing()` screen drivers are not domain types. The user action is an operation on the aggregate that owns it.
- **`private-method-naming`** — Public `+name`; private `- _name`. `derive*` helpers are private.
- **`no-orphaned-objects`** — Every domain object has at least one relationship. Value objects that are attributes sit on their owner — not as unconnected cards.

---

## Sketching

When sketching, use the sketch template at `ddd/templates/ddd-sketch.md`. Do not use the produce templates below — stop reading this skill when sketching.

## Templates

### markdown

## bounded-context-template.md

<!--

  Bounded Context Map — tree format



  BC → Aggregate → concept. Links on any level:

  → BC · Aggregate · Entity   (another context; omit leading segments when same BC/aggregate)

  → System · Entity           (external vendor / system of record)



  building_blocks fidelity adds CE compact classes under each aggregate (not shown here).

-->



# Bounded Context Map — {{project_name}}



## Map format

Three levels on the **bounded_context** card: **BC** → **Aggregate** → **concept**.

No `Root`, boundary-member lists, protected-invariant blocks, or `#### Dependencies` sections at this fidelity — those deepen at **building_blocks**.

### Layout

Every context is a top-level `##` section — peers, never nested inside one another. A Shared Kernel is a dependency arc between two contexts, not a section that contains them.

Order the contexts with the system you are building first, then systems of record and vendor systems after it.

### Links

`→ BC · Aggregate · Entity` — cross-context (omit leading `BC` / `Aggregate` when the target shares the same context or aggregate; e.g. `→ · Voucher` inside Customer).

`→ System · Entity` — external system (e.g. `→ Mavenir DEP · engagedParty`).

Put each link on the **concept or aggregate that has the dependency** — not in a global `## Dependencies` section.

### Dependency arcs

For every arc between contexts, record:

| Field | Content |
|---|---|
| **Direction** | Upstream / downstream / mutual — name both sides |
| **What crosses** | Concepts and how they translate at the boundary |
| **Integration** | Concrete mechanism and call site (e.g. synchronous call to `Catalog.Product.unit_price` at `add_item`, domain event `PriceChanged`, nightly batch extract). "In-process" or "module seam" alone is not enough. |
| **Pattern** | One from the catalogue below — or owner + target date if undecided |

**Relationship patterns (use these names — no ad hoc labels like "loose coupling"):**

- **Shared Kernel** — shared subset; both sides consult on change
- **Customer/Supplier** — one-way; joint acceptance tests at the boundary
- **Conformist** — downstream adopts upstream model
- **Anticorruption Layer** — translate / isolate legacy or foreign model
- **Open Host / Published Language** — published protocol for many consumers
- **Separate Ways** — no integration

External systems of record usually **Separate Ways**, **Conformist**, or **ACL**. Formalize informal internal sharing instead of leaving it unnamed.

---



## {{ContextName}} | {{custom | bespoke | vendor name}}



{{One-line scope.}}



### {{AggregateRoot}}



- {{concept}}

- {{concept}} → {{BC | System}} · {{Aggregate}} · {{Entity}}

→ {{BC | System}} · {{Aggregate}} · {{Entity}}



### {{AnotherAggregate}}



- {{concept}}

→ {{upstream}}



---



## {{AnotherContext}} | {{vendor}}



{{Scope note.}}



### {{AggregateRoot}}



- {{concept}}

→ {{System}} · {{Entity}}



<!-- building_blocks: under each ### aggregate, add #### CE compact + stereotypes per bounded-context-template-building-blocks.md -->



See examples in `context_tools/ddd/examples/` if needed.