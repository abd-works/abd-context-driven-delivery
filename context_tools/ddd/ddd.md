# Contexts

Build a solution that is organized and structured around how the business actually works, described in the words the business already uses. The concepts, structure, and rules in the model and in the code are the same ones the people who do the work would recognise — so there is nothing to translate between a conversation about the business and the code that runs it. When the software mirrors the business, a rule change lands where that rule lives and the code reads as an explanation of the business; when it mirrors a database, a framework, or a screen layout instead, every business conversation has to be re-translated and the rules end up scattered wherever the technology happened to put them.

Start from the business, not from the database or the screens. Listen to the people who do the work and use their words. When the same term means different things between two parts of the organization — or two teams use different words for what sounds like the same thing — you have found a boundary. Hold one consistent picture inside each area so later conversation, model, and code speaks a consistent language.

Inside each area, find what must stay true together. A price, the offer it belongs to, and the plan behind it may all need to change in one breath; a customer's address may change while their subscription rules stay put. Put a single entry point on each aggregate to control how business state is accessed and changed.

Then detail each aggregate — structure, behaviour, invariants, and integrations — with DDD's tactical building blocks. They look technical, but only the business can answer them: what makes one thing the same thing over time, what state counts as valid, how information is stored and synchronized between clusters, and which parts of the system publish events others must react to. You reach for a common set of blocks because each one is designed to hold the answer to a very specific business question in a structured, consistent way.

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

## bounded_context

**Default format:** markdown

**Goal:** Draw where language changes — context boundaries, the aggregates that protect invariants inside each context, and the dependency arcs between contexts — using the experts' words. Names and boundaries are cheap to change here; they are expensive once building blocks, stories, and code hang off them.

**Produce:** `bounded-context-map.md` from `templates/bounded-context-template.md`. Call clean_engineering at **modules**.

### Guidance

**Start from the language, not the structure.** Read the source context and watch the vocabulary. A **bounded context** is where one model and one ubiquitous language hold — inside it every term has exactly one meaning. So the first move is not drawing boxes; it is noticing where the vocabulary shifts. The same word carrying two meanings in two conversations, or two words describing what looks like one thing, is the signal that you are standing on a boundary. Boundaries drawn from screens, or existing services will cut straight through a single language and leave you translating inside what should have been one model.

**Then name the candidate contexts — a boundary comes from vocabulary and meaning that genuinely differs.** You cross a context boundary when you reach people or systems that call things by different names: another department with its own working vocabulary, or a vendor-managed or different team's system with its own model and terminology that are simply not yours to change. The boundary protects you from silently merging two vocabularies, in the language and in the code.

**Then name the business concepts, and group which ones change together.** Each group is an **aggregate**. For each one, identify its anchor concept: the **root** (eg a `Customer` root holding `Demographics`, `Address`, and `NetWorth`). The root is the controlled access point for reading and changing that group's business state, so every change lands consistently and completely across the concepts that change together. `Customer`, `Subscription`, and `AvailablePlan` move as one: entitlements must match the plan at every instant, so a feature cannot be withdrawn while subscribers still hold it.

**Then determine how concepts shared across aggregates and bounded contexts are synchronized.** Where the same real thing appears on both sides, decide what triggers the update and what each side holds. `ProductPlan` is separate from `AvailablePlan` — the inventory spans past, present, and future plans, and only on reaching `active` does one publish across, where it is kept as a copy. Left unnamed, the two drift with no agreed moment at which they should match. Most of the modelling value at this fidelity lives here — in the aggregates, the concepts they hold, and how those concepts synchronize across the map.

In a service-per-capability or event-driven design where you control the model, each bounded context will likely hold only a couple of aggregates, so that you can deliberately decouple them and orchestrate through event-oriented architecture. Use this approach when you are not working within boundaries already set by existing teams and systems, and keep those contexts aligned to where the language boundaries fall.

**Then describe how the contexts relate.** Contexts are peers — a Shared Kernel is two of them agreeing to consult each other on change, not one owning the other. For every pair that touches, decide what crosses the boundary, which direction it flows, how integration actually happens, and which relationship pattern applies. "We call their API" names no mechanism, so that decision gets made during implementation by whoever reaches it first. Where two contexts share a word with different meanings, name the translation on the relationship — that translation is what the code will have to do, and pretending the meanings match is how a false cognate reaches production.

**Then read the map back and look for what it is hiding.** The same real thing modeled twice, one word quietly meaning two things, or contexts that mirror UI journeys rather than vocabularies. Check the aggregates too: one holding concepts that never change together, or a rule the business relies on that nobody wrote down. These are cheap to fix while contexts and aggregates are still names; once building blocks, stories, and code hang off them, moving a boundary means moving all of that with it.

### Scaffold

**When scaffolding only** (`/partition` or a names-only first cut — not full generate at this fidelity): follow this subsection. Do not use ### Rules below, ## Sketching, or ## Templates.

Rough bounded-context map for a **partition** pass or first cut — context names, candidate aggregates, short language notes only. No building blocks, no dependency arcs, no integration detail yet.

Key rules: `one-meaning-per-context` — a term's meaning is only valid inside the context that defines it; `bc-by-lifecycle-not-ui-themes` — split on language and change-rate, not on screens.

**Stop reading this skill when scaffolding.**

### Rules

- **`experts-words-preferred`** — Use the words domain experts use. A ported telephone number is `TelephoneNumber` with `PortingInformation`, not `PortabilityRequest`; the operation is `port()`, not `requestPortability()`. A invented synonym becomes a second term every reader must translate.
- **`domain-concepts-not-technical-names`** — Name contexts, aggregates, and concepts — not `Manager`, `Helper`, `Processor`, `*Result`, `*Response`, `*Dto`, or `*Request`. Do not invent a type for fields that already belong on a concept (`OrderResult` → fields on `Order`). A technical name carries no meaning the business would recognize, so rules parked on it cannot be found where the concept lives and get re-implemented elsewhere.
- **`bc-by-lifecycle-not-ui-themes`** — Partition by ubiquitous language and how fast the model changes, not by UI themes or journey stages. Do not mint Selfcare / Onboarding / Acquisition contexts that duplicate Customer, Catalog, and Subscription. Screens and journeys are redrawn while language boundaries hold; a boundary cut along the UI has to move with every redesign and drags the model with it.
- **`one-meaning-per-context`** — Inside a context, one definition per term; name and translate false cognates across contexts. Several aggregates per context is normal. Do not wrap each aggregate in its own bounded context. Two meanings under one word become contradictory code that both looks consistent; a context per aggregate walls one language off from itself and charges integration cost for nothing.
- **`dependency-fields-tracked`** — Every arc names direction, what crosses, how integration happens, and the relationship pattern — or a dated follow-up with owner. An arc with only "integrates with Catalog" does not tell anyone what to build.
- **`no-orphan-contexts`** — Every context on the map appears in a dependency arc or is declared standalone with a reason. A box with no arcs is either missing relationships or should not be on the map.
- **`vendor-not-implementation`** — The context title carries vendor after `|` (`custom`, `bespoke`, or vendor name). Owning team and implementation stack belong elsewhere — they change while the language boundary does not.
- **`context-tree-bc-aggregate-concept`** — Three levels on the bounded_context card only: BC → Aggregate → concept. Deeper structure and stereotypes wait for **building_blocks**; tree shape is in the template. Structure drawn before the boundary settles is discarded when the boundary moves — and until then it argues for leaving the boundary where it is.
- **`link-arrow-target`** — Outbound links use `→` with `BC · Aggregate · Entity` or `System · Entity`. Omit leading segments when the target shares the same context or aggregate. A target nobody can resolve is a dependency nobody can build.
- **`hang-deps-on-owning-bc`** — Put each outbound link on the concept or aggregate that has the dependency, not in a global `## Dependencies` section. A parking lot detaches the dependency from the concept that needs it, so it survives changes that should have removed it.
- **`user-facing-system-first`** — The system you are wrapping sits first on the map; external systems of record sit downstream. The map exists to explain that system — everything downstream is context for it, not the subject.

---

## building_blocks

**Default format:** markdown

**Goal:** Deepen the same context map — under each aggregate already placed at **bounded_context**, add clean_engineering compact class detail and DDD stereotypes. You are classifying and shaping what is already on the map, not inventing a parallel model.

**Produce:** Update `bounded-context-map.md` using `templates/bounded-context-template.md`. Call clean_engineering at **model**.

### Guidance

**Work through one bounded context and one aggregate at a time.** Honor the boundaries already drawn at **bounded_context** unless the source or the user changes them. Call clean_engineering at **model** and use its object-oriented analysis to deepen the aggregate in place: begin at the root, work inward through the objects it governs, then work outward through its dependencies. A loose list of stereotypes does not show why an object belongs in this aggregate or how the aggregate stays valid.

**Validate the Aggregate Root first.** The root is both an **Entity** and the only entry point for changing the aggregate. State what gives it identity, where that identity is valid, and why it remains the same entity when its values change. If the only answer is equality of all its fields, it may be a Value Object rather than an Entity; if callers must enter through several objects, the proposed aggregate boundary is incomplete. Name the business invariants the root keeps true across its members. The members are the objects participating in an invariant; the invariant is the condition the root must preserve whenever any of them changes.

**Walk inward through every member and classify it by identity, ownership, and lifecycle.** Use clean_engineering's class model to name its properties, operations, relationships, and cardinality, then apply the DDD stereotype:

| Stereotype | Ask |
|---|---|
| **Entity** | Does this object keep the same identity while its values change, and how is that identity defined? |
| **Value Object** | Is it defined only by its values, immutable, and replaceable by an equal value? |
| **Aggregate Root** | Is it an Entity and the only gateway that can keep this aggregate's invariants true? |
| **Repository** | Is this Aggregate Root found, added, saved, and retired as an independent collection? |
| **Factory** | Is valid creation too complex for the root's constructor or named creation operation? |
| **Service** | Is this domain operation genuinely homeless because no one Entity or Value Object owns the state it needs? |
| **Domain Event** | Did a domain fact occur that a named consumer outside this aggregate needs to know? |
| **Specification** | Is this a named rule reused to select, validate, or guide the construction of domain objects? |

Choose the relationship at the same time. Use composition when the member belongs to the root's lifecycle and has no identity outside it; use association when the other object remains independent. A `Customer` can hold an `Address` Value Object and replace it when the customer moves. The `Address` type is reusable anywhere an address is needed, but each owner holds a value rather than sharing mutable identity. If an address must itself be tracked, shared, and updated independently, it is an Entity reached by association and may belong to another aggregate.

**Put behavior on the object that owns the state and let the root protect the whole aggregate.** Selection, porting, and checkout live on the object that can perform them while preserving its own invariants. Use `Cart.checkout`, not `CheckoutService.placeOrder`; use `Customer.signIn`, not `AuthenticationService.fillEmail`. When two types share identity over time, such as Prospect and Subscriber both being a Customer, model a base type and generalisation rather than duplicating the same entity.

**Add a Repository only for an Aggregate Root with an independent collection lifecycle.** Ask how the application finds it by identity or business criteria, adds a newly created root, saves changes, and removes or retires it. Child Entities and Value Objects are persisted through their root rather than receiving repositories of their own. Creation belongs on the root or a Factory; the Repository stores and reconstitutes what was created. A cart reached only through its customer does not need a `CartRepository`.

**Add a Factory only when construction is genuinely complex.** Prefer a constructor or named operation on the Aggregate Root for ordinary creation. A Factory earns its place when valid creation chooses subtypes, applies several rules, or needs information obtained through other aggregates' public operations. It may coordinate those inputs, but the object it returns still belongs to one aggregate; creation must not erase the boundaries already drawn.

**Use a Domain Service only for a domain operation with no natural owner.** First test every Entity and Value Object involved: if one owns the state needed to perform the operation, put the operation there. A Domain Service may coordinate behavior spanning independent domain objects, but it is not an application `FooService`, an SOA endpoint, or a place to collect verbs. Services with no domain meaning separate behavior from state and leave the aggregate unable to protect its own rules.

**Define Domain Events from facts that named consumers need, not from every state change.** Name the fact in past tense, the Aggregate Root that publishes it, the exact condition that triggers it, each consumer, and the smallest domain payload those consumers require. Inventory can publish `InventoryBecameUnavailable` without knowing anything about Shopping Cart. Shopping Cart subscribes because it owns a local availability view and ignores inventory events that do not affect that view. This keeps both aggregates independent: Inventory owns stock calculations; Shopping Cart owns how availability affects a cart.

**Decide synchronization wherever an object model crosses an aggregate or bounded context.** Record which side owns the source fact, what the receiving side copies or derives, how terms are translated, what triggers synchronization, and how stale the receiving view may be. Use an immediate event when the consumer must react to a fact as it happens; use a scheduled refresh, such as weekly, when that delay is acceptable; use an on-demand query when no local copy is needed. A dependency with no timing and translation decision leaves two valid models with no agreed way to remain consistent.

**Use a Specification for a named rule that must mean the same thing in several operations.** A `PreferredCustomerSpecification` can define what makes a Customer preferred, support a query for preferred customers, validate an existing customer, and guide a Factory creating one. Keep the predicate in the Specification and let the Entity or Factory perform the state change; otherwise the same definition is copied into queries, validation, and creation and eventually disagrees with itself.

**Keep design intent here.** Name domain objects, operations, invariants, relationships, collection seams, events, synchronization decisions, and translations. Database tables, message brokers, framework annotations, and REST endpoints belong at **tactics**, after the domain decisions they implement are visible.

### Rules

- **`identity-test-entity-vs-vo`** — Entity when identity transcends attributes; otherwise prefer Value Object. A type that is the access boundary for a cluster is **Aggregate Root + Entity**, not a Domain Service (`Catalog` is not `<<Service>>` because it "does" selection).
- **`aggregate-root-identity-and-entry`** — Every aggregate states the root's identity and uses that root as its only entry point. If identity or entry is ambiguous, the root cannot protect changes across the aggregate.
- **`every-concept-classified`** — Every source concept appears with supporting model content (or `Unresolved`). When harvesting from a sketch, every named type in the sketch appears — do not render a handful of classes from a large map.
- **`service-is-homeless`** — Domain Service is a rare doer only when the operation cannot sit on one domain object. Not SOA: do not invent `FooService` to park verbs. `CheckoutService.placeOrder` is `Cart.checkout`.
- **`repository-is-collection-lifecycle`** — Repository only when the business finds, stores, and retires that aggregate independently. Collection seam: `add` / `remove` / `update` / `find_by_*`.
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

## tactics

**Default format:** Python

**Goal:** Implement the domain and the building-block seams (repositories, events, factories, services) against a chosen architecture — preserving every name and boundary from upstream.

**Produce:** Implementation under the project layout; call clean_engineering at **code**.

### Guidance

**Preserve names and boundaries from the map and model.** Tactics is where repositories persist, events publish, and factories run — not where you rename concepts to match a framework tutorial.

**Ask for architecture before wiring adapters.** Read project context (`.context/`, ADRs, stack). If none exists, ask. If nothing is available, default to a Node-shaped app with JSON file persistence (package TBD).

**Keep the domain free of UI and transport.** Persistence and messaging sit behind ports; the domain types do not import screens or HTTP clients.

**Load with the identity already in hand** when wrapping live code. Do not assume a browser session. Load once and reuse the variable. A cart has no identity outside its prospect — reach it through the owner, not `cartRepository().current()`.

### Rules

- **`preserve-upstream-names`** — Public API names match the building_blocks model. Renaming here breaks traceability back to the map and the stories.
- **`load-with-identity-in-hand`** — A live `load` takes the identity already in hand. Do not assume ambient session state. Reach owned aggregates through their owner.
- **`ports-behind-adapters`** — Persistence, messaging, and external systems integrate through ports — not direct imports from the domain core.

---

# Default folder

`default_workspace_folder` is `src/` for **generate**. `/document` calls `apply_document_workspace_default`: working area becomes `domain/` unless `path` was passed or `default_workspace_folder` was already overwritten. Clean Engineering does not choose this folder; `ce()` follows DDD's working path.

---

# Document

Take the persona of a **neutral observer** — describe what exists, do not prescribe what should exist.

When documenting an existing system, tactical wraps live under the DDD working area (`domain/` by default) as `{bounded-context}/{aggregate}/`. Leave production `src/` alone unless the user directs otherwise. Generate / greenfield work may still use `src/`.

- **`load-with-identity-in-hand`** — same rule as **tactics**.
- **`user-facing-system-first`** — same rule as **bounded_context**.

---

# Generate

1. Confirm fidelity (`bounded_context` → `building_blocks` → `tactics`) and format.
2. Read the active fidelity section above (including its Rules). Do not re-author CE OO theory.
3. Use peer actions when useful (`grill`, `sketch`, `iterate`; `templates/ddd-sketch.md`).
4. Fill / deepen `bounded-context-map.md`; at **tactics**, resolve architecture first.
5. Call clean_engineering at the mapped fidelity (`generate_output`).
6. Run **validate**.
