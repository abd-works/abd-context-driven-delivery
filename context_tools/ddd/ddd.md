# Instructions

Apply **DDD** — bounded contexts, aggregates, building blocks — on top of **clean_engineering**.

**`clean_engineering`** owns OO structure (modules → model → specification → code; language is a companion). Do not restate class/module analysis here. DDD starts at **bounded_context**: context maps, aggregates, then stereotypes and tactics.

Each fidelity below is the whole story for that level. Call clean_engineering at the mapped fidelity. Do not fill details from a more detailed fidelity.

| Fidelity | clean_engineering |
|---|---|
| **bounded_context** | **modules** |
| **building_blocks** | **model** |
| **tactics** | **code** |

---
# Contexts



## bounded_context

**Default format:** markdown

**Goal:** Draw context boundaries, dependency arcs, and the aggregates that protect invariants — naming everything in the experts' vocabulary.

### Scaffold

Rough bounded-context map for a **partition** pass or first cut — **names only**: context name + candidate aggregates + short ubiquitous-language note (`DomainMap` → `BoundedContext` → `Aggregate`). No building blocks, no tactics, no dependency arcs yet.

Key rules: `language-is-context-scoped` — a term's meaning is only valid inside the context that defines it; the same word in two contexts is two different concepts.

A **bounded context** is the boundary of **one model and one ubiquitous language**. Inside it, every term has one meaning. Across it, the same word may mean different things.

An **aggregate** is not a context. It is a **consistency** cluster *inside* a context: one root, a boundary, the invariants that boundary protects. Several aggregates that share the same language live in the **same** context (Catalog can hold Plan, Offer, …). Do **not** mint a bounded context per aggregate — that is a class with a fence around it, not a model boundary.

Failure modes: **duplicate concepts** (same real-world thing modeled twice); **false cognates** (same term, different meaning); **one-aggregate contexts** (every root wrapped as its own BC); **UI-theme contexts** (Onboarding vs Selfcare vs SignIn as BCs, with Customer/Catalog copied under each screen group); **ignoring change-frequency** (parking a fast-changing Subscription inside a slow Customer identity context).

**Context map:** identify contexts → name them → describe contact points with translation. Each context is a **peer card**, not a nested bullet inside another context's box. Shared Kernel is an **arc** between peers, not a parent card containing children.

**What gets tracked on a dependency:** direction (upstream/downstream/mutual, naming both sides); what crosses (concepts + translation); how they integrate — name the concrete mechanism and call site (e.g. synchronous call to `Catalog.Product.unit_price` at `add_item`, domain event `PriceChanged`, nightly batch extract). Categories like Events / Messaging / REST/API / Batch / Shared DB / File Transfer / Shared Kernel help, but "in-process" or "module seam" alone is not enough; relationship pattern from the catalogue below. Undecided items get owner + target date.

**Patterns:** Shared Kernel (shared subset, consult on change); Customer/Supplier (one-way, joint acceptance tests); Conformist (downstream adopts upstream); Anticorruption Layer (translate/isolate legacy); Open Host / Published Language (published protocol); Separate Ways (no integration). No ad hoc labels like "loose coupling."

**Boundary heuristics:** split a context when language, team, model, **or lifecycle change-frequency** actually diverges — not when you add another aggregate, and not when the UI grows another theme or page. Screens are not contexts. Things that change at different rates (stable identity vs line/service lifecycle vs catalog merchandising) are candidates for different contexts; things that change together stay together (cart, billing, and the subscription they pay for). Size ~ten people upper bound; external systems usually Separate Ways / Conformist / ACL; formalize informal internal sharing; transform boundaries with clear current/end state.

An **Aggregate** is decided **inside** the context already named. Cluster for **one transaction / one invariant set**, not relatedness; keep aggregates small.

**Links:** when a BC, aggregate, or concept depends on another, append `→ BC · Aggregate · Entity` or `→ System · Entity`. Drop leading segments when the target shares the same BC or aggregate (e.g. `→ · Voucher` inside Customer). Integration pattern and call site belong in notes or **building_blocks**, not on the bounded_context card.

**Input traps:** hidden coupling; ownership ambiguity; false cognates; missing unnamed contexts; unclear direction; a new BC for each aggregate.

**Produce:** one `bounded-context-map.md` in **tree format** — `## BC | vendor`, then `### Aggregate`, then bulleted **concepts**. Links on any level: `→ BC · Aggregate · Entity` (cross-context; omit leading segments when same BC/aggregate) or `→ System · Entity` (external vendor). Fill `templates/bounded-context-template.md`. Call clean_engineering at **modules**.

**Rules:**

- **`experts-words-preferred`** — Prefer the words domain experts use; do not invent technical synonyms when a domain word already exists. A ported telephone number is `TelephoneNumber` with `PortingInformation`, not `PortabilityRequest`; the operation is `port()`, not `requestPortability()`.
- **`domain-concepts-not-technical-names`** — Every class/module names a domain concept (or honest boundary collaborator). Reject `Manager`, `Helper`, `Processor`, `*Result`, `*Response`, `*Dto`, `*Request`. Do not invent a type for fields that already belong on a concept (`OrderResult` → fields on `Order`). Do not invent a concept the experts and the running system do not name.
- **`bc-by-lifecycle-not-ui-themes`** — Partition bounded contexts by ubiquitous language and by how fast the model changes, not by UI themes, pages, or journey stages. Do not mint Selfcare / Onboarding / Acquisition contexts that duplicate Customer, Catalog, and Subscription. Put purchase, cart, and billing with the faster-changing lifecycle they serve, not under slow-changing identity.
- **`one-meaning-per-context`** — Inside a context, one definition per term; false cognates across contexts are named and translated. The context is that language boundary. Aggregates are consistency clusters inside it — several per context is normal. Do not wrap each aggregate in its own bounded context. On the map, every context is a peer card — not a parent-box bullet.
- **`dependency-fields-tracked`** — Every arc states direction (named sides or mutual), what crosses, how they integrate (concrete mechanism), and catalogue relationship pattern — or a dated follow-up with owner.
- **`no-orphan-contexts`** — Every inventoried context appears in a dependency arc or is declared standalone with rationale.
- **`vendor-not-implementation`** — BC title carries vendor after `|` — `custom`, `bespoke`, or vendor name. No owning team or implementation stack on the card.
- **`context-tree-bc-aggregate-concept`** — Three levels only: BC → Aggregate → concept. No Root, Boundary members, Refs, Protected invariants, or #### Dependencies blocks on the bounded_context card.
- **`link-arrow-target`** — Outbound links use `→` with `BC · Aggregate · Entity` or `System · Entity`. Omit leading BC/Aggregate segments when the target is in the same context or aggregate.
- **`hang-deps-on-owning-bc`** — Put each outbound link on the **concept or aggregate that has the dependency**, not in a global `## Dependencies` section. External-system links sit on the aggregate that owns the integration (e.g. Inventory → Mavenir DEP).
- **`user-facing-system-first`** — On the context map, the system you are wrapping — the consumer app — sits first (left / upstream). External systems of record sit downstream. Do not start the layout at Mavenir / AWS / a vendor column.

---

## building_blocks

**Default format:** markdown

**Goal:** Deepen the same context map — under each owning context, add CE compact class detail with DDD stereotypes. Not a separate BB document; added detail on the aggregates already placed in the BC.

| Stereotype | Business question |
|---|---|

| **Entity** | An object defined by its unique identity rather than its attributes, maintaining continuity across state changes over time.|
| **Aggregate** | A cluster of associated domain objects (entities and value objects) grouped together to maintain consistent business rules as a single unit. |
| **Aggregate Root** | The main entity inside an aggregate that acts as the sole gateway, controlling all external access and enforcing consistency rules for the entire cluster. |
| **Value Object** | Fully described by values — interchangeable, replaceable, immutable? Prefer VO unless tracked identity is required. |
| **Repository** | A design pattern that hides database operations, allowing your code to load, save, and query entire aggregates as if they lived in a simple memory collection. How does the business find, store, and retire this aggregate? Collection-style seam only (`add` / `remove` / `update` / `find_by_*`). No repository if there is no independent collection lifecycle. |
| **Factory** | Complex birth / invariants at creation / subtype choice? |
| **Service** | Rare **doer** — only when the operation cannot sit cleanly on a single domain object. Not SOA / application `FooService`. `CheckoutService.placeOrder` is `Cart.checkout`. |
| **Domain Event** | Significant past-tense moment — trigger and consumers as invariants; payload as properties. Facts, not commands. |
| **Specification** | Named, reusable true/false business rule (query / validate / construct)? |

Honour aggregate boundaries from bounded_context; do not redraw by relatedness. Same class shape as clean_engineering — stereotypes layered on. Every source concept classified (or Unresolved) with supporting model content.

**Input traps:** identity by habit; aggregate redrawn by relatedness; VO as Entity; `*Service` as a verb bag (SOA); silent consistency.

**Produce:** Update `bounded-context-map.md` — CE compact blocks + stereotypes under each owning context (`templates/bounded-context-template.md`); keep `#### Dependencies` on each aggregate from bounded_context. Call clean_engineering at **specification**. No tables, brokers, frameworks, or REST endpoints here — infrastructure at **tactics**.

**Rules:**

- **`identity-test-entity-vs-vo`** — Entity vs VO by identity that transcends attributes; prefer Value Object. A type that holds collection state and is the access boundary for that cluster is **Aggregate Root + Entity**, not a Domain Service (`Catalog` is not `<<Service>>` because it "does" selection). Invoice you chase over time is an Entity; an immutable money amount is a Value Object.
- **`every-concept-classified`** — Every source concept classified with supporting model content (or Unresolved); multiple stereotypes per concept are fine. When harvesting from a sketch, every named type in the sketch appears in the model — do not render a handful of classes from a large map.
- **`service-is-homeless`** — DDD Service = a **doer**, and they are **rare**. Use one only when the operation cannot sit cleanly on a single domain object. Not SOA: do not invent `FooService` to park verbs. If `Customer` signs in, that is `Customer.signIn`. `CheckoutService.placeOrder` is `Cart.checkout` (or `Order` born from that). `AuthenticationService.fillEmail` is a screen driver (`screen-interface-not-a-domain-object`). Credentials does not grow `signIn`.
- **`repository-is-collection-lifecycle`** — A Repository exists only when the business finds, stores, and retires that aggregate independently. Do not mint `FooRepository` because every aggregate "should have one." Cart created by checkout and never retrieved as a collection has no CartRepository. Subscription that is an invariant of Subscriber is not a top-level SubscriptionRepository.
- **`shared-identity-is-generalisation`** — When two types share identity and the same core attributes over time (Prospect and Subscriber both *are* a Customer), model a base type and generalisation arrows. Do not flatten them as unrelated entities.
- **`domain-events-past-tense`** — Past-tense domain name; trigger and consumers as invariants; not commands or infra names.
- **`no-premature-infrastructure`** — Design intent only: no tables, brokers, framework annotations, or endpoints.
- **`hang-deps-on-owning-bc`** — Keep `→` links on the concept or aggregate from bounded_context when deepening **building_blocks**. No global `## Dependencies` parking lot.
- **`building-blocks-fidelity-requires-tactical-stereotype`** — Every class name at building_blocks carries a tactical tag (`<<Aggregate Root>>`, `<<Entity>>`, `<<Value Object>>`, `<<Repository>>`, `<<Factory>>`, `<<Service>>`, `<<Domain Event>>`, `<<Specification>>`). Bare names are incomplete.
- **`flaccid-data-object-no-behavior`** — A type is not a field bag. Give it the operations that are **its** work. Select / port / checkout live on the aggregate that does them, not on a repository. Do not hang someone else’s verbs on a value so it “has behavior” (credentials does not grow `signIn`).
- **`screen-interface-not-a-domain-object`** — `open()` / `isShowing()` screen drivers are not domain objects. The user action is an operation on the aggregate that owns it.
- **`private-method-naming`** — Public operations use `+` and no leading `_`. Private helpers use `-` and a `_` prefix (e.g. `- _deriveOnboardingStep`). `derive*` helpers are private.
- **`no-orphaned-objects`** — Every domain object has at least one relationship (dependency, composition, or association). Unconnected Credentials/Session-style boxes are incomplete. Value objects that are attributes (Money, Usage) sit on their owner — they are not unconnected cards. OnboardingStep connects to Prospect; Billing to the subscriber/subscription that pays.

---

## tactics

**Default format:** Python

**Goal:** Implement the domain and building-block seams (repos, events, factories, …) against a chosen architecture.

- Preserve names from the CE / building-blocks model.
- Implement repository persistence, event publication/handling, factories, services as decided upstream.
- **Architecture** — from project context (`.context/`, ADRs, stack). If none, **ask**. If none available, default: Node-shaped app + **JSON file persistence** (package TBD).
- Domain model free of UI/transport; persistence and messaging behind ports.
- **`load-with-identity-in-hand`** — When wrapping live, `load` takes the identity already in hand. Do not assume a browser session. Load once and reuse the variable. A cart has no identity outside its prospect — reach it through the owner, not `cartRepository().current()`.
- Call clean_engineering at **code**.

---

# Default folder

`default_workspace_folder` is `src/` for **generate**. `/document` calls `apply_document_workspace_default`: working area becomes `domain/` unless `path` was passed or `default_workspace_folder` was already overwritten. Clean Engineering does not choose this folder; `ce()` follows DDD's working path.

---

# Document

Take the persona of a **neutral observer** — describe what exists, do not prescribe what should exist.

When documenting an existing system, tactical wraps live under the DDD working area (`domain/` by default, overridable via `path` or `default_workspace_folder`) as `{bounded-context}/{aggregate}/` (`{class}.ts` + `{class}.{tier}.ts` + `stubs/{system}/`). Leave production `src/` alone. Generate / greenfield work may still use `src/`.

- **`load-with-identity-in-hand`** — A live wrap `load`s with the identity already in hand. Do not assume a browser session. Load once and reuse the variable. A cart has no identity outside its prospect — reach it through the owner, not `cartRepository().current()`.
- **`user-facing-system-first`** — same rule as **bounded_context**: the consumer app is first on the map; vendors sit downstream.

---

# Generate

1. Confirm fidelity (`bounded_context` → `building_blocks` → `tactics`) and format.
2. Read the active fidelity section above (including its Rules). Do not re-author CE OO theory.
3. Use peer actions when useful (`grill`, `sketch`, `iterate`; `templates/ddd-sketch.md`).
4. Fill / deepen `bounded-context-map.md`; at **tactics**, resolve architecture first.
5. Call clean_engineering at the mapped fidelity (`generate_output`).
6. Run **validate**.
