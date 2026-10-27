## Overview

Build the solution around how the business actually works, in the words the business already uses. When the software mirrors the business, it holds the business's logic and knowledge where that understanding actually lives; when it mirrors a database, a framework, or a screen layout, every business conversation has to be re-translated and what the business knows ends up scattered wherever the technology happened to put it.

**`clean_engineering`** owns OO structure, one skill per fidelity: **`clean_engineering-modules`** shapes the module boundaries and seams when **`bounded_context`** draws the map; **`clean_engineering-model`** types the classes, operations, and relationships when **`model`** draws the core aggregates — root, members, repository, and the operations that cross aggregates and contexts; **`clean_engineering-code`** implements the seams when **`tactics`** classifies the remaining building blocks (factories, specifications, domain services, events) and wires repositories, events, and factories. Do not restate module or class analysis here. DDD adds the domain layer on top: where the language changes, which clusters protect which rules, and how those clusters work with one another.

---

## Guidance

**Mine the source context.** Read every referenced segment, sketch, grill-answer, and handoff in full. Extract domain language, business rules, and expertise from that material — do not infer structure from legacy schemas, screens, or vendor APIs without first translating what they mean in domain terms. Those artifacts show how someone once implemented the business, not what the business is; model from the domain meaning or you preserve accidents of an old implementation as if they were rules.

**Speak one language everywhere.** The term in the source context is the term on the map, in the model, in the code, in the tests, and in the documentation. A *shopping cart* is `ShoppingCart`; a ported telephone number is `TelephoneNumber` carrying `PortingInformation`, not a `PortabilityRequest`. Anywhere a reader has to translate is somewhere two parts of the context can hold different understandings and both look consistent.

**Let conflicting meaning do its job.** When source context disagrees about what a term means — or uses different words for what appears to be the same thing — you have found a real modelling question: a distinction nobody named, or two concepts sharing one word. Resolve it by naming both things and stating how they relate — subtype, association, instance of a type, specification, the same word in two different bounded contexts. Vague terms pass review because nothing pins down the distinction, and the ambiguity turns into contradictory code later.

**Model behaviour, not just data.** Ask what each concept *does* in the business, not only what it holds. A cart checks itself out; an order calculates its own total; a subscription suspends itself. Concepts that only hold fields push the business rules out into managers and services, and then business logic and business state get scattered.

**Treat the model as the design, not documentation of it.** Reason through the model and the language before implementing — the map and the aggregate model are the primary organizing design for the software, not a summary you write after the code exists.

**Spend the deep thinking where the context is distinctive.** The part of the domain that makes this business different from a generic one deserves careful modelling; billing formats, address lookup, and sign-in usually do not. Modelling everything to the same depth spends effort on problems the source context never asked you to solve.

**Keep the language alive.** As understanding deepens, rename and restructure — in the model and in the code together. A glossary that no longer matches the code is worse than none, because readers trust it and it is wrong.

### Default folder

`default_workspace_folder` is `src/` for **generate**. Documenting an existing system uses the DDD working area (`domain/` by default) as `{bounded-context}/{aggregate}/`. A bounded context folder contains `.context/bounded-context.md`. The code-format build writes that file when it creates the context folder and the aggregate folders under it. A folder of classes with no such file is a module or a package. Leave production `src/` alone unless the user directs otherwise.

### Document

Take the persona of a **neutral observer** — describe what exists, do not prescribe what should exist.

When documenting an existing system, tactical wraps live under the DDD working area (`domain/` by default) as `{bounded-context}/{aggregate}/`. Leave production `src/` alone unless the user directs otherwise. Generate / greenfield work may still use `src/`.

- **`load-with-identity-in-hand`** — same rule as **tactics**.
- **`user-facing-system-first`** — same rule as **bounded_context**.

### Generate

1. Confirm fidelity (`bounded_context` → `model` → `tactics`) and format.
2. Read the active fidelity section above (including its Rules). Do not re-author CE OO theory.
3. Use peer actions when useful (`grill`, `sketch`, `iterate`; `templates/ddd-sketch.md`).
4. Fill / deepen `bounded-context-map.md`; at **model**, draw each aggregate's root, members, repository, and cross-aggregate operations; at **tactics**, resolve architecture first.
5. Call clean_engineering at the mapped fidelity (`generate_output`).
6. Run **validate**.

---

## Shared rules

```yaml
alwaysApply: false
globs: "**/*-sketch.md"
```

Use these rules when defining domain logic in code, a model, or language.

- **`ubiquitous-language-everywhere`** — One term per concept, taken from the business, used identically on the map, in the model, in the code, and in the tests. A technical synonym makes every reader keep a translation in their head, and the two names drift until they mean different things.
- **`model-the-domain-not-the-implementation`** — Model what the business does, not what the current database, screens, or vendor API expose. A model shaped by an existing implementation locks in decisions nobody chose on purpose.
- **`vocabulary-traces-to-domain-source`** — Trace every term back to domain experts or an upstream artifact. Invent a word and each layer keeps its own glossary.
- **`read-all-source-context-in-full`** — Before locking a context boundary or aggregate, read every referenced segment, sketch, grill-answer, and handoff in full. Titles and indexes show words, not mechanics; a boundary drawn from headings alone misses coupling that shows up only in the prose.
- **`do-not-invent-concepts`** — Only model contexts, aggregates, and types the source describes or the user explicitly asks for. Invented contexts and DTO-shaped nouns become code nobody asked for and integrations nobody planned.

---

## Fidelities

### bounded_context

```yaml
default_format: markdown
stage: discovery
clean_engineering: modules
```

#### Overview

Draw where language changes — at the level of **business areas, organizational departments, and systems** (or collections of systems that share one model) — then the aggregates that protect invariants inside each context, and the dependency arcs between contexts. A bounded context sits **above** aggregates; it is not one box per aggregate. Names and boundaries are cheap to change here; they are expensive once the model, stories, and code hang off them.

**Produce:** `bounded-context-map.md` from `templates/bounded-context.md`. Call clean_engineering at **modules**.

#### Sketch

When **Domain Driven Design** is active, module seams and aggregate-root operations live in `domain driven design:` — not in a separate `clean engineering:` section. Each custom-owned aggregate is also a clean-engineering module: `// seam:` and `// constraint:` on the aggregate card; each entity's operations and properties in that entity's fence. Ask the DDD questions below; read Clean Engineering's **Guidance** and **Rules** for the mapped fidelity (`modules` at **bounded_context**, `model` at **model**) in `practices/clean_engineering/clean_engineering.md` while you sketch; do not ask Clean Engineering Sketch questions. Use `practices/ddd/templates/ddd-sketch.md` for notation. When **Clean Engineering** is active **without** Domain Driven Design, use `clean engineering:` and `practices/clean_engineering/templates/clean_engineering-sketch.md` instead.

- Ask what different **areas of the business** — departments, organizations, and/or **systems** — hold a **different and unique view** of the domain in question. Ask what **unique views the solution itself will create**. Those are your bounded contexts.
- Ask which business areas or system collections share one ubiquitous language and can live in one context together — several aggregates under one boundary is normal.
- In each context, ask which concepts have to change together so the business stays consistent.
- Ask what the key facts are inside each of those groups.
- Ask where one context and another are different views of the same real thing: what each side cares about, and how those facts connect and stay in step.
- Ask where one context relies on another for something that is not that same shared fact.
- From those answers, write each context at business/system level, nest the aggregates that belong inside it, and record how contexts relate. If a downstream system does not warrant its own language boundary, record it under **Integrations:** on the owning aggregate instead of minting a `###` heading that merely repeats one aggregate.
- Ask what each entity does and what it holds. Give each entity that acts its own `#####` heading; write operations and properties in that entity's fence using clean-engineering class notation — verbs for operations, nouns for properties; no `members:` block and no bare operations floating outside an entity.
- Do not ask the user to name a bounded context or an aggregate.

#### Guidance

**Find bounded contexts from the business and from systems — not from aggregates.** Good boundaries come from areas of the business, organizational departments, and systems — or **collections of systems** that share one model and one team vocabulary. The solution's own unique views count too: a cross-bank client view the enterprise does not yet have is a bounded context even when no vendor product owns that language yet. A bounded context names that higher-level place where one ubiquitous language holds; aggregates nest **inside** it. One bounded context per aggregate is noise — it adds headings without naming a real language shift. If you cannot name a business area, department, or system collection behind a candidate context, **omit the bounded-context heading** and carry that knowledge as an integration on the aggregate that needs it.

**Keep modules inside the context — not one package per class.** Clean-engineering modules partition code; they follow the same rule as bounded contexts at a finer grain. One module per aggregate root, or one package per class, is folder noise when the types collaborate in one consolidated view. A small custom context is usually **one module** holding its entities together — split only when change rate, ownership, or coupling genuinely diverges. Read `no-module-per-class` in clean_engineering **modules** when sketching.

**Start from the language, not the structure.** Read the source context and watch the vocabulary. A **bounded context** is where one model and one ubiquitous language hold — inside it every term has exactly one meaning. The first move is not drawing boxes; it is noticing where the vocabulary shifts. The same word carrying two meanings in two conversations, or two words describing what looks like one thing, is the signal that you are standing on a boundary. Boundaries drawn from screens or existing services cut straight through a single language and leave you translating inside what should have been one model.

**Name contexts where vocabulary and ownership genuinely differ.** You cross a context boundary when you reach a department, business area, or system collection that calls things by different names: another department with its own working vocabulary, or vendor-managed systems whose model and terminology are not yours to change. Group systems that share one language under one context — e.g. several product lines on the same core banking tenant, or origination and servicing on the same lending platform when they speak one language to integrators. The boundary protects you from silently merging two vocabularies, in the language and in the code.

**For each context, list business concepts, and group which ones change together.** Each group is an **aggregate**. For each one, identify its anchor concept: the **root** (eg a `Customer` root holding `Demographics`, `Address`, and `NetWorth`). The root is the controlled access point for reading and changing that group's business state, so every change lands consistently and completely across the concepts that change together. `Customer`, `Subscription`, and `AvailablePlan` move as one: entitlements must match the plan at every instant, so a feature cannot be withdrawn while subscribers still hold it.

**Keep entities inside the aggregate — not one aggregate per entity.** A deposit account, a registered plan, and a term deposit that share one customer file belong in one aggregate with **Customer** as root — not five `####` headings that each hold a single entity. Split only when lifecycle, ownership, or invariants genuinely diverge.

**Then determine how concepts shared across aggregates and bounded contexts are synchronized.** Where the same real thing appears on both sides, decide what triggers the update and what each side holds. `ProductPlan` is separate from `AvailablePlan` — the inventory spans past, present, and future plans, and only on reaching `active` does one publish across, where it is kept as a copy. Left unnamed, the two drift with no agreed moment at which they should match. Most of the modelling value at this fidelity lives here — in the aggregates, the concepts they hold, and how those concepts synchronize across the map.

For sketch output at this fidelity, nest aggregates under each bounded context and show event ownership at the aggregate level: each aggregate lists `emits` and `consumes`. Then add a compact event map (`Event: emitted by X; consumed by Y`) so cross-context coordination remains explicit without jumping to tactics.

In a service-per-capability or event-driven design where you control the model, each bounded context will likely hold only a couple of aggregates, so that you can deliberately decouple them and orchestrate through event-oriented architecture. Use this approach when you are not working within boundaries already set by existing teams and systems, and keep those contexts aligned to where the language boundaries fall.

**Then describe how the contexts relate.** Contexts are peers — a Shared Kernel is two of them agreeing to consult each other on change, not one owning the other. For every pair that touches, decide what crosses the boundary, which direction it flows, how integration actually happens, and which relationship pattern applies. "We call their API" names no mechanism, so that decision gets made during implementation by whoever reaches it first. Where two contexts share a word with different meanings, name the translation on the relationship — that translation is what the code will have to do, and pretending the meanings match is how a false cognate reaches production.

**Then read the map back and look for what it is hiding.** The same real thing modeled twice, one word quietly meaning two things, contexts that mirror UI journeys rather than vocabularies, or a `###` heading per aggregate that names no business area or system collection. Check the aggregates too: one holding concepts that never change together, or a rule the business relies on that nobody wrote down. These are cheap to fix while contexts and aggregates are still names; once the model, stories, and code hang off them, moving a boundary means moving all of that with it.

#### Scaffold

**When scaffolding only** (`/partition` or a names-only first cut, not full generation at this fidelity), follow this subsection. Do not use Guidance or Rules below.

Rough bounded-context map for a **partition** pass or first cut — context names, candidate aggregates, short language notes only. Keep aggregates nested inside their owning context and include lightweight `emits`/`consumes` event ownership where known. No classes, no dependency arcs, no integration detail yet.

Key rules: `one-meaning-per-context` — a term's meaning is only valid inside the context that defines it; `bc-by-lifecycle-not-ui-themes` — split on language and change-rate, not on screens.

**Stop reading this skill when scaffolding.**

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
- **`bc-above-aggregate`** — A bounded context names a business area, department, or system collection with its own ubiquitous language — not a single aggregate. If the only candidate context is one aggregate, nest it under a broader context or record it as an **Integrations:** arc; omit the `###` heading. No real language boundary is better than a heading that merely duplicates an aggregate name.
- **`one-module-per-context-when-small`** — A consolidated custom context with only a handful of collaborating types is one clean-engineering module, not one package per aggregate or per class. Several entities under one `#### {module}/` is normal; four modules for four classes in the same context is the packaging version of `bc-above-aggregate`.
- **`aggregate-clusters-entities`** — An aggregate is a consistency cluster with a chosen root and the entities inside it — not one `####` heading per entity class. Several `#####` entities under one aggregate is normal; five aggregates for five account types that share one customer file is the same mistake at a finer grain.
- **`integrations-cross-context-only`** — **Integrations:** arcs cross a bounded-context boundary only. Another entity or aggregate in the same context is a property on the type that uses it — not an integration.
- **`dependency-fields-tracked`** — Every arc names direction, what crosses, how integration happens, and the relationship pattern — or a dated follow-up with owner. An arc that names only a neighbor context does not tell anyone what to build.
- **`no-orphan-contexts`** — Every context on the map appears in a dependency arc or is declared standalone with a reason. A box with no arcs is either missing relationships or should not be on the map.
- **`vendor-not-implementation`** — The context title carries vendor after `|` (`custom`, `bespoke`, or vendor name). Owning team and implementation stack belong elsewhere, because they can change while the domain meaning remains stable.
- **`context-tree-bc-aggregate-concept`** — Three levels on the bounded_context card only: BC → Aggregate → concept. Classes, stereotypes, and repositories wait for **model**; tree shape is in the template. Structure drawn before the boundary settles is discarded when the boundary moves — and until then it argues for leaving the boundary where it is.
- **`bounded-context-file-marks-the-folder`** — In code, a bounded context is the folder that contains `.context/bounded-context.md`. The code-format build writes that file when it creates the context folder and each aggregate folder under it. A folder of classes with no such file is a module or a package, so the map and the tree disagree about where the language boundary is.
- **`link-arrow-target`** — Outbound links use `→` with `BC · Aggregate · Entity` or `System · Entity`. Omit leading segments when the target shares the same context or aggregate. A target nobody can resolve is a dependency nobody can build.
- **`hang-deps-on-owning-bc`** — Put each outbound link on the concept or aggregate that has the dependency, not in a global `## Dependencies` section. A parking lot detaches the dependency from the concept that needs it, so it survives changes that should have removed it.
- **`user-facing-system-first`** — The system you are wrapping sits first on the map; external systems of record sit downstream. The map exists to explain that system — everything downstream is context for it, not the subject.

---

### model

```yaml
default_format: markdown
stage: specification
clean_engineering: model
```

#### Overview

Draw the core domain and nothing else: each aggregate's root, the entities and values it owns, the repository that keeps it, the domain operations the business performs on it, and how aggregates depend on one another inside a context and across contexts. Strip out everything technical, so the domain can be discussed, modelled, and simplified as far as it will go before any implementation detail lands on it.

The notation is Clean Engineering's class model. DDD adds three things to it: bounded contexts and aggregates drawn as containers, a stereotype on each class, and the root's repository drawn **in the root's card** below its domain operations.

**Produce:** `domain-model.md` (artifact `ce-domain-model`) from `templates/model.md`, which extends `practices/clean_engineering/templates/class-model.md`; render to `drawio` for the aggregate view. Keep `bounded-context-map.md` contexts, aggregates, and integrations in step. Call clean_engineering at **model**.

#### Sketch

Start from the aggregates already named at **bounded_context**. Read Clean Engineering's **Guidance** and **Rules** for **model** while you sketch; do not ask Clean Engineering Sketch questions.

- Ask what the business does to each aggregate — the verbs in the stories, scenarios, and screens. Each one is an operation on the root or on the member that owns the state.
- Ask what the root has to hold to do those things, and which of those holdings are things in their own right (entities) and which are only values.
- Ask how the business creates, finds again, changes, and retires the aggregate. Those are the repository's operations; everything else is a domain operation.
- Ask which operation needs something another aggregate or another context holds, what it needs, and by which identity it reaches it.
- Ask which operations, holdings, and classes can be merged or dropped without losing a business rule.
- Do not ask the user to name a class, a stereotype, or a repository operation.

#### Guidance

**One view, the domain operations, nothing else.** The model is the place to argue about the domain, so it holds only what the business would recognise: aggregate roots, the entities and values they own, repositories, domain operations, and the dependencies between aggregates. Leave out constructors, private helpers, ports, publishers, DTOs, request and response shapes, framework types, persistence, and transport. Leave out factories, specifications, domain services, and domain-event classes too — those are **tactics**. Each one you add before the domain is settled is one more thing to move when it changes.

**Simplify relentlessly before adding detail.** Read each aggregate back and ask whether two operations are one, whether a member entity is really a value, whether a class exists only to hold another class's fields, whether an aggregate is really part of another. Every merge here is a whole layer of code, tests, and screens that never gets written. Detail is cheap to add later and expensive to remove.

**Lay each aggregate out the same way.** Inside its bounded context, each aggregate is a container. The root card sits first and carries, top to bottom: its stereotypes (`<<Aggregate Root>> <<Entity>>`), its properties, its domain operations, and then its repository — `<<Repository>> {Root}Repository` and the collection operations. Owned entities and values sit beside or below the root and are composed by it. A reader finds the same things in the same place in every aggregate, so differences mean something.

**The repository is CRUD in the business's words.** Its operations create, load, update, and — when the business does it — search for and retire the aggregate. Nothing else. Every rule, state change, and calculation is a domain operation on the root or a member, because the repository keeps the aggregate and the aggregate keeps its rules.

**Every core operation is on the model.** Walk the stories and scenarios; each verb the business performs on this aggregate appears as a public operation on the class that owns the state it changes, named with the scenario's verb. An operation the stories need but the model lacks is a rule that will end up in a route, a view, or a manager.

**Draw how aggregates work together — that is the point of the view.** For every operation that needs another aggregate, draw an arrow from the class that depends to the root it depends on, hold the other aggregate by its identity, and name the call (`-> Plans.load(planId)`). Within a context it is an association; across contexts it is the integration from the map, with its pattern. Decide where each shared fact lives, what triggers the other side to catch up, and how stale it may be. Most of the design value at this fidelity is in these arrows: they are the seams the code, the tests, and the screens will follow.

**The code mirrors the model.** Each aggregate is a folder, each root a class with these operations, each repository the collection the model shows — the same names and the same operations. Until **tactics** do not break an aggregate into factories, specifications, services, or event classes. When existing code already splits an aggregate into those pieces, show the pieces as they are, so the model still matches the code it describes. In code, each class's doc comment opens with its stereotypes and place — `<<Aggregate Root>> <<Entity>> Customer | custom · Customer Profile` — and the root's carries its integrations, so the aggregate model renders to code and reads back from it.

**Work one bounded context and one aggregate at a time.** Begin at the root, work inward through the members it owns, then outward through its dependencies. Classify every class: `<<Aggregate Root>> <<Entity>>` for the root, `<<Entity>>` for an owned thing with its own identity, `<<Value Object>>` for a thing that is only its values, `<<Repository>>` for the collection.

#### Rules

```yaml
alwaysApply: false
globs: "**/*bounded-context*,**/*-model.md,**/*-model.drawio,**/*-sketch.md"
```

Whenever you add, change, or remove an aggregate's root, members, repository, domain operations, or its dependencies on other aggregates, or change code those aggregates support. Follow these rules.

If this change will not stay here, follow `practices/ddd/bounded_context.mdc`.

- **`aggregate-view-only`** — The model shows aggregate roots, member entities, value objects, repositories, domain operations, and dependencies between aggregates. No constructors, private helpers, ports, publishers, DTOs, framework types, factories, specifications, domain services, or event classes — unless the code being described already has them. Anything else in the view buries the domain under detail that is not decided yet.
- **`every-class-carries-ddd-stereotype`** — Every class carries its stereotype: `<<Aggregate Root>> <<Entity>>`, `<<Entity>>`, `<<Value Object>>`, or `<<Repository>>`. A bare name leaves the reader guessing whether it has identity or a lifecycle.
- **`root-card-carries-repository`** — Draw the root's repository inside the root's card, below the domain operations: stereotypes, properties, operations, then `<<Repository>> {Root}Repository` and its operations. One card per aggregate entry point keeps lifecycle and behaviour readable together without a second box per aggregate.
- **`repository-is-crud`** — Repository operations create, load, update, and — only when the business does it — search and retire the root. Every rule and state change is a domain operation on the root or a member. A rule on the repository cannot be found where the aggregate lives and runs only when the aggregate is saved.
- **`repository-is-collection-lifecycle`** — Add a Repository only when the business finds, stores, and retires an Aggregate Root independently. Reach an owned aggregate through its owner when it has no independent lookup, because a Repository without an independent collection invents a lifecycle the business does not have.
- **`core-operations-on-the-model`** — Each verb the stories and scenarios perform on an aggregate appears as a public operation on the class that owns the state, named with the scenario's verb. A missing operation becomes logic in a route, a view, or a manager.
- **`members-composed-by-root`** — Owned entities and values are composed by the root (or by the member that owns them) and reached through it. A member drawn loose or reached directly lets callers change part of the aggregate without the root's rules.
- **`identity-test-entity-vs-vo`** — Entity when identity transcends attributes; otherwise prefer Value Object. A type that is the access boundary for a cluster is **Aggregate Root + Entity**.
- **`aggregate-root-identity-and-entry`** — Every aggregate states the root's identity and uses that root as its only entry point. If identity or entry is ambiguous, the root cannot protect changes across the aggregate.
- **`cross-aggregate-dependency-drawn`** — Every operation that needs another aggregate draws an arrow from the dependent class to the target root, holds the target by identity, and names the call. An undrawn dependency is decided by whoever writes the code first.
- **`cross-boundary-synchronization-decided`** — Every cross-aggregate or cross-context dependency names the source owner, receiving view, translation, trigger or cadence, and acceptable staleness. Without those decisions, each side can be correct alone while their shared fact silently diverges.
- **`simplest-model-that-holds-the-rules`** — Merge operations, members, and aggregates until removing one more would lose a business rule. Each class or operation kept here becomes code, tests, and screens.
- **`model-mirrors-code`** — Aggregate, class, and operation names in the model match the code; the code adds no aggregate pieces the model does not show. When the two disagree, one of them is wrong and readers cannot tell which.
- **`shared-identity-is-generalisation`** — Shared identity over time → base type + generalisation arrows. Do not flatten as unrelated entities.
- **`flaccid-data-object-no-behavior`** — A type is not a field bag. Give it the operations that are **its** work.
- **`screen-interface-not-a-domain-object`** — `open()` / `isShowing()` screen drivers are not domain types. The user action is an operation on the aggregate that owns it.
- **`no-orphaned-objects`** — Every domain object has at least one relationship. Value objects that are attributes sit on their owner — not as unconnected cards.
- **`hang-deps-on-owning-bc`** — Keep `→` links on the concept or aggregate from **bounded_context**. No global `## Dependencies` parking lot.
- **`no-premature-infrastructure`** — Design intent only: no tables, brokers, framework annotations, or endpoints.

---

### tactics

```yaml
default_format: python
stage: implementation
clean_engineering: code
```

#### Overview

Classify the remaining DDD building blocks the model needs — factories, specifications, domain services, domain events, interfaces to other systems — decide one implementation pattern for each block, then implement the domain against it, preserving every name and boundary from the map and the model.

**Produce:** Implementation under the project layout, using `templates/tactics.md` for the building-block operations; call clean_engineering at **code**. When that build creates folders for bounded contexts and aggregates, write `.context/bounded-context.md` in each context folder.

#### Sketch

Ask whether creating this thing needs more than the root can do alone, which rule must mean the same thing in several places, which act belongs to no single aggregate, which facts other parts of the business need to hear, how the business finds this thing again later, and which outside system must be told. Write the building block and the way it is kept and told from those answers.

#### Guidance

**Start from the model, not from the pattern catalogue.** The aggregates, roots, repositories, and operations are settled at **model**. Add a building block only where the model shows a need for it: a creation the root cannot do alone, a rule several operations share, a verb no aggregate owns, a fact another aggregate must react to.

**Add a Factory** when creating a valid object is too much for a simple constructor — complex business rules, work that crosses aggregates, an intricate workflow, or a choice among several subtypes behind one interface. Ordinary creation stays on the repository's `create` so callers have one obvious way in.

**Use a Domain Service** when the business operation belongs to no single object — eg transferring funds from one bank account to another: neither account owns the transfer; debiting one and crediting the other is one piece of work that spans both. Try the verb on every object involved first; if it fits on one, it is not a service.

**Define Domain Events** for business state changes that other aggregates or contexts must react to. Name each event in past tense, publish it from the root operation that records the fact, identify its consumers, and state which facts cross the boundary. The consumer decides what it needs from the event, so the publisher does not depend on each subscriber's workflow.

**Use a Specification for a named rule that must mean the same thing in several operations.** A `PreferredCustomerSpecification` can define what makes a Customer preferred, support a query for preferred customers, validate an existing customer, and guide a Factory creating one. Keep the predicate in the Specification and let the Entity or Factory perform the state change.

**Represent another system with a named interface.** A Service or Gateway exposes that system's operations; a Repository may collaborate with it when persistence crosses the system boundary.

**Read the project's architecture before deciding anything.** Check project context (`.context/`, ADRs, stack). If none exists, ask. If nothing is available, default to a Node-shaped app with JSON file persistence (package TBD).

**Decide one implementation pattern per building block, then apply it everywhere that block appears.** Work through the blocks the model and this fidelity actually use and settle for each: what technology backs it, how you extend or wrap that technology, and how it is tested. With the pattern fixed, going from model to implementation is a mechanical translation — the model says `<<Repository>>` and the pattern says exactly what that becomes.

**Settle the architectural granularity in the same pass.** Decide whether a bounded context is an in-process module, a deployed container, or a service, and whether an aggregate and Repository are in-process objects or sit behind a service and its own store. Make the choice explicitly before implementation sets it by accident.

**Preserve names and boundaries from the map and model.** Tactics is where repositories persist, events publish, and factories run — not where you rename concepts to match a framework tutorial.

**Keep the domain free of UI and transport.** Persistence and messaging sit behind ports; the domain types do not import screens or HTTP clients.

**Load with the identity already in hand** when wrapping live code. Do not assume a browser session. Load once and reuse the variable. A cart has no identity outside its prospect — reach it through the owner, not `cartRepository().current()`.

#### Rules

```yaml
alwaysApply: false
globs: "**/*.py,**/*.ts,**/*.tsx,**/*.js,**/*.java,**/*-sketch.md"
```

Whenever you add factories, specifications, domain services, or domain events; persist, publish, or test repositories, events, or factories; or change production code they support. Follow these rules.

If this change will not stay here, follow `practices/ddd/model.mdc`.

- **`every-class-carries-ddd-stereotype`** — Every domain class carries its stereotype (`<<Factory>>`, `<<Specification>>`, `<<Domain Service>>`, `<<Domain Event>>`, plus the model's). In code a decorator or naming convention carries it. A bare class leaves the reader guessing which pattern applies.
- **`factory-is-complex-creation`** — Factory only when valid creation needs subtype choice, several rules, or outside collaborators. Ordinary creation stays on the repository's `create` so callers have one obvious way to create it.
- **`service-is-homeless`** — Domain Service is a rare doer only when the operation cannot sit on one domain object. Not SOA: do not invent `FooService` to park verbs.
- **`domain-events-past-tense`** — Past-tense domain name; name the publishing root, trigger, consumers, and required payload. Events are facts needed outside the aggregate, not a notification for every mutation.
- **`specification-is-reusable-rule`** — Use a Specification when one named predicate must serve more than one query, validation, or creation path. One definition prevents each path from developing a different meaning for the same rule.
- **`external-system-access-is-service-interface`** — Represent another system with a named Service or Gateway interface that exposes that system's operations. Do not model the external system as a collection of domain roots, because it owns a different model and lifecycle.
- **`repository-owns-aggregate-lifecycle`** — Put creation, loading, search, update, and retirement of an Aggregate Root on its Repository; keep changes to an already loaded aggregate on the root or its members. An aggregate instance does not create or load itself.
- **`one-pattern-per-building-block`** — Each building block in play gets one named implementation pattern — technology, extension mechanism, test approach — used by every instance of that block. Divergent implementations of the same block make the solution unreadable and untestable as a whole.
- **`architectural-granularity-decided`** — State what a bounded context, an aggregate, and a repository are at runtime (in-process module, container, service with its own store). Left undecided, the first adapter written silently sets it for everything after.
- **`preserve-upstream-names`** — Public API names match the **model**. Renaming here breaks traceability back to the map and the stories.
- **`load-with-identity-in-hand`** — A live `load` takes the identity already in hand. Do not assume ambient session state. Reach owned aggregates through their owner.
- **`ports-behind-adapters`** — Persistence, messaging, and external systems integrate through ports — not direct imports from the domain core.
- **`private-method-naming`** — Public `+name`; private `- _name`. `derive*` helpers are private.

---

## Common mistakes still being made

Scratch pad — mistakes people still make against this practice. Each entry: the mistake, an example, what should have happened instead. (Disposition TBD.)

_No entries yet._

---
