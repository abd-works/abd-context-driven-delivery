---
name: ddd-bounded-context
description: "Provide guidance for creating bounded contexts, building blocks, and tactics."
disable-model-invocation: true
---

# ddd-bounded_context

Use ddd guidance at `bounded_context` fidelity only.

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

For sketch output at this fidelity, nest aggregates under each bounded context and show event ownership at the aggregate level: each aggregate lists `emits` and `consumes`. Then add a compact event map (`Event: emitted by X; consumed by Y`) so cross-context coordination remains explicit without jumping to tactics.

In a service-per-capability or event-driven design where you control the model, each bounded context will likely hold only a couple of aggregates, so that you can deliberately decouple them and orchestrate through event-oriented architecture. Use this approach when you are not working within boundaries already set by existing teams and systems, and keep those contexts aligned to where the language boundaries fall.

**Then describe how the contexts relate.** Contexts are peers — a Shared Kernel is two of them agreeing to consult each other on change, not one owning the other. For every pair that touches, decide what crosses the boundary, which direction it flows, how integration actually happens, and which relationship pattern applies. "We call their API" names no mechanism, so that decision gets made during implementation by whoever reaches it first. Where two contexts share a word with different meanings, name the translation on the relationship — that translation is what the code will have to do, and pretending the meanings match is how a false cognate reaches production.

**Then read the map back and look for what it is hiding.** The same real thing modeled twice, one word quietly meaning two things, or contexts that mirror UI journeys rather than vocabularies. Check the aggregates too: one holding concepts that never change together, or a rule the business relies on that nobody wrote down. These are cheap to fix while contexts and aggregates are still names; once building blocks, stories, and code hang off them, moving a boundary means moving all of that with it.

### Scaffold

**When scaffolding only** (`/partition` or a names-only first cut, not full generation at this fidelity), follow this subsection. Do not use Guidance or Rules below.

Rough bounded-context map for a **partition** pass or first cut — context names, candidate aggregates, short language notes only. Keep aggregates nested inside their owning context and include lightweight `emits`/`consumes` event ownership where known. No building blocks, no dependency arcs, no integration detail yet.

Key rules: `one-meaning-per-context` — a term's meaning is only valid inside the context that defines it; `bc-by-lifecycle-not-ui-themes` — split on language and change-rate, not on screens.

**Stop reading this skill when scaffolding.**

### Rules

- **`experts-words-preferred`** — Use the words domain experts use. A ported telephone number is `TelephoneNumber` with `PortingInformation`, not `PortabilityRequest`; the operation is `port()`, not `requestPortability()`. A invented synonym becomes a second term every reader must translate.
- **`domain-concepts-not-technical-names`** — Name contexts, aggregates, and concepts — not `Manager`, `Helper`, `Processor`, `*Result`, `*Response`, `*Dto`, or `*Request`. Do not invent a type for fields that already belong on a concept (`OrderResult` → fields on `Order`). A technical name carries no meaning the business would recognize, so rules parked on it cannot be found where the concept lives and get re-implemented elsewhere.
- **`bc-by-lifecycle-not-ui-themes`** — Partition by ubiquitous language and how fast the model changes, not by UI themes or journey stages. Do not mint Selfcare / Onboarding / Acquisition contexts that duplicate Customer, Catalog, and Subscription. Screens and journeys are redrawn while language boundaries hold; a boundary cut along the UI has to move with every redesign and drags the model with it.
- **`one-meaning-per-context`** — Inside a context, one definition per term; name and translate false cognates across contexts. Several aggregates per context is normal. Do not wrap each aggregate in its own bounded context. Two meanings under one word become contradictory code that both looks consistent; a context per aggregate walls one language off from itself and charges integration cost for nothing.
- **`dependency-fields-tracked`** — Every arc names direction, what crosses, how integration happens, and the relationship pattern — or a dated follow-up with owner. An arc with only "integrates with Catalog" does not tell anyone what to build.
- **`no-orphan-contexts`** — Every context on the map appears in a dependency arc or is declared standalone with a reason. A box with no arcs is either missing relationships or should not be on the map.
- **`vendor-not-implementation`** — The context title carries vendor after `|` (`custom`, `bespoke`, or vendor name). Owning team and implementation stack belong elsewhere, because they can change while the domain meaning remains stable.
- **`context-tree-bc-aggregate-concept`** — Three levels on the bounded_context card only: BC → Aggregate → concept. Deeper structure and stereotypes wait for **building_blocks**; tree shape is in the template. Structure drawn before the boundary settles is discarded when the boundary moves — and until then it argues for leaving the boundary where it is.
- **`link-arrow-target`** — Outbound links use `→` with `BC · Aggregate · Entity` or `System · Entity`. Omit leading segments when the target shares the same context or aggregate. A target nobody can resolve is a dependency nobody can build.
- **`hang-deps-on-owning-bc`** — Put each outbound link on the concept or aggregate that has the dependency, not in a global `## Dependencies` section. A parking lot detaches the dependency from the concept that needs it, so it survives changes that should have removed it.
- **`user-facing-system-first`** — The system you are wrapping sits first on the map; external systems of record sit downstream. The map exists to explain that system — everything downstream is context for it, not the subject.

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