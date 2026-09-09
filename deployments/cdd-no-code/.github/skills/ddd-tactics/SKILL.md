---
name: ddd-tactics
description: "Provide guidance for creating bounded contexts, building blocks, and tactics."
disable-model-invocation: true
---

# ddd-tactics

Use ddd guidance at `tactics` fidelity only.

Refer to these skills in order to fill in details from previous fidelities if not present:
@ddd-building_blocks
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

## tactics

**Default format:** Python

**Goal:** Decide one implementation pattern for each building block the model uses, then implement the domain against it — preserving every name and boundary from upstream.

**Produce:** Implementation under the project layout; call clean_engineering at **code**.

### Guidance

**Read the project's architecture before deciding anything.** Check project context (`.context/`, ADRs, stack). If none exists, ask. If nothing is available, default to a Node-shaped app with JSON file persistence (package TBD).

**Decide one implementation pattern per building block, then apply it everywhere that block appears.** Work through the blocks the model actually uses — not every solution uses all of them — and settle for each: what technology backs it, how you extend or wrap that technology, and how it is tested. With the pattern fixed, going from model to implementation is a mechanical translation — the model says `<<Repository>>` and the pattern says exactly what that becomes. Without it, every instance is a fresh design problem invented from scratch, and nothing about the model tells you what the code should look like.

**Settle the architectural granularity in the same pass.** Decide whether a bounded context is an in-process module, a deployed container, or a service, and decide whether an aggregate and Repository are in-process objects or sit behind a service and its own store. For example, a Repository backed by MongoDB and service calls has different runtime and test costs from an in-memory collection. Make the choice explicitly before implementation sets it by accident.

**Preserve names and boundaries from the map and model.** Tactics is where repositories persist, events publish, and factories run — not where you rename concepts to match a framework tutorial.

**Keep the domain free of UI and transport.** Persistence and messaging sit behind ports; the domain types do not import screens or HTTP clients.

**Load with the identity already in hand** when wrapping live code. Do not assume a browser session. Load once and reuse the variable. A cart has no identity outside its prospect — reach it through the owner, not `cartRepository().current()`.

### Rules

- **`one-pattern-per-building-block`** — Each building block in play gets one named implementation pattern — technology, extension mechanism, test approach — used by every instance of that block. Divergent implementations of the same block make the solution unreadable and untestable as a whole.
- **`architectural-granularity-decided`** — State what a bounded context, an aggregate, and a repository are at runtime (in-process module, container, service with its own store). Left undecided, the first adapter written silently sets it for everything after.
- **`preserve-upstream-names`** — Public API names match the building_blocks model. Renaming here breaks traceability back to the map and the stories.
- **`load-with-identity-in-hand`** — A live `load` takes the identity already in hand. Do not assume ambient session state. Reach owned aggregates through their owner.
- **`ports-behind-adapters`** — Persistence, messaging, and external systems integrate through ports — not direct imports from the domain core.

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