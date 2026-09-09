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

## bounded_context

**Default format:** markdown

**Goal:** Draw where language changes — context boundaries, the aggregates that protect invariants inside each context, and the dependency arcs between contexts — using the experts' words. Names and boundaries are cheap to change here; they are expensive once building blocks, stories, and code hang off them.

**Produce:** `bounded-context-map.md` from `templates/bounded-context-template.md`. Call clean_engineering at **modules**.

### Guidance

**Start from the language, not the structure.** Read the source context and watch the vocabulary. A **bounded context** is where one model and one ubiquitous language hold — inside it every term has exactly one meaning. So the first move is not drawing boxes; it is noticing where the vocabulary shifts. The same word carrying two meanings in two conversations, or two words describing what looks like one thing, is the signal that you are standing on a boundary. Boundaries drawn from screens, or existing services will cut straight through a single language and leave you translating inside what should have been one model.

**Then name the candidate contexts — a boundary comes from vocabulary and meaning that genuinely differs.** You cross a context boundary when you reach people or systems that call things by different names: another department with its own working vocabulary, or a vendor-managed or different team's system with its own model and terminology that are simply not yours to change. The boundary protects you from silently merging two vocabularies, in the language and in the code.

**For each context, list business concepts, and group which ones change together.** Each group is an **aggregate**. For each one, identify its anchor concept: the **root** (eg a `Customer` root holding `Demographics`, `Address`, and `NetWorth`). The root is the controlled access point for reading and changing that group's business state, so every change lands consistently and completely across the concepts that change together. `Customer`, `Subscription`, and `AvailablePlan` move as one: entitlements must match the plan at every instant, so a feature cannot be withdrawn while subscribers still hold it.

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

**Work through one bounded context and one aggregate at a time.** Call clean_engineering at **model** fidelity and use its object-oriented analysis to deepen the Bounded Contexts and aggregate inside them: begin at the root, work inward through the objects it governs, then work outward through its dependencies. Refine your object oriented analysis by implementing each concept theough one or more of the DDD **building blocks** mentioned below.

The building blocks look technical, but only the business can answer them. Fully defining each aggregate is how you flesh out the solution's seams from a *business* lens — boundaries that follow where the business actually changes, not where the technology happened to split.

**Start with the Aggregate Root.** allow access to the aggregate by identifying it's **root**, do not allow other members to be accessed directly- a single entry point based on business thinking avoids a fragmented calls surface that is too fine-grained or too coarse. 

**Give every Aggregate Root a Repository** — implement it as the collection seam for reaching a particular root; define search, access, and update menchanisms that match how the business gets at whole aggregates. This allow you to you reason about transactional proererties from the perspective of the business not technical jargon.

Determine which concepts are an **Entity** (the root at a minumum) — for each; Define how the the business keeps its identity distinct even as its values change. eg A customer can change their name, sex, or address. A ported number is still the same line. A subscription with an added family member is still the same subscription. - tells you how to maintain consistency and distinctness, what to search, update, replace and retire.

Define which concepts are instead **Value Objects** — primitives whose whole meaning comes from their values. Do not waste cycles giving identity and mutable state to concepts that do not need it; you bloat the solution and make change harder for no reason.  Instead implement Value Objects so they are shareable, immutable, and cheap. eg A chosen color in a painting system, the delivery address on an order, the product line on a shopping-cart. You will greatly simplify implementation.

**Add a Factory** when creating a valid object is too much for a simple constructor — complex business rules, work that crosses aggregates, an intricate workflow, or a choice among several subtypes behind one interface. This keeps all of that creation logic in one obvious place instead of leaving every caller to figure it out for themselves.

**Use a Domain Service** when the business operation belongs to no single object — eg transferring funds from one bank account to another: neither account owns the transfer; debiting one and crediting the other is one piece of work that spans both.

As you define nore and more aggregates and bounded contests, **decide synchronization for every cross agg/bc dependency .** Record which side owns the source fact, what triggers synchronization, what the receiving side copies or derives, how terms are translated, and critically how often.. Use an immediate event when the consumer must react to a fact as it happens; use a scheduled refresh, such as weekly, when that delay is acceptable; use an on-demand query when no local copy is needed. A dependency with no timing and translation decision leaves two valid models with no agreed way to remain consistent.

**Define Domain Events** when building your own system from scratch take advantage of Domain Events primarily for crosss agg/bc synchronization. Events are changes in business state that other parts of your domain need to react to — name them in past tense, define on the publisher, note onsumption on the consuer. define what parts of the aggregates(s) cross the boundary. This inverts the dependency of RPC-style integration: the consumer decides what it needs from the event rather than the producer needing to know what the subscriber wants. Each aggregate is then free to change internally as long as the events it publishes stay the same.

**Use a Specification for a named rule that must mean the same thing in several operations.** A `PreferredCustomerSpecification` can define what makes a Customer preferred, support a query for preferred customers, validate an existing customer, and guide a Factory creating one. Keep the predicate in the Specification and let the Entity or Factory perform the state change; otherwise the same definition is copied into queries, validation, and creation and eventually disagrees with itself.

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

**Goal:** Decide one implementation pattern for each building block the model uses, then implement the domain against it — preserving every name and boundary from upstream.

**Produce:** Implementation under the project layout; call clean_engineering at **code**.

### Guidance

**Read the project's architecture before deciding anything.** Check project context (`.context/`, ADRs, stack). If none exists, ask. If nothing is available, default to a Node-shaped app with JSON file persistence (package TBD).

**Decide one implementation pattern per building block, then apply it everywhere that block appears.** Work through the blocks the model actually uses — not every solution uses all of them — and settle for each: what technology backs it, how you extend or wrap that technology, and how it is tested. With the pattern fixed, going from model to implementation is a mechanical translation — the model says `<<Repository>>` and the pattern says exactly what that becomes. Without it, every instance is a fresh design problem invented from scratch, and nothing about the model tells you what the code should look like.

**Settle the architectural granularity in the same pass.** Decide what a bounded context is at runtime — are we using container technology and if So what kindand how do we deploy them, or a module inside a larger one — and what an aggregate and its repository are inside it: plain in-process objects, or their own service behind its own database. eg a repository backed by Mongo and micro service calls, the choice clarifies what every caller pays and what every test has to stand up. Make it deliberately, before AI settles it by accident.

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
