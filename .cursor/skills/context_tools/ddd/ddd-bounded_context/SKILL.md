---
name: ddd-bounded_context
description: "Provide guidance for creating bounded contexts, building blocks, and tactics."
disable-model-invocation: true
---

# ddd-bounded_context

Use ddd guidance at `bounded_context` fidelity only.

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

## Sketching

When sketching, use the following sketch template. Do not use the produce templates below — stop reading this skill when sketching.

# DDD sketch



Declare fidelity once at the top. Use only the sketch for that fidelity — do not fill later-fidelity detail early.



---



## bounded_context



Name each **bounded context** (language boundary — **not** a UI theme or page), then the **aggregates it holds** (consistency clusters — usually more than one). Split when language or **change-frequency** diverges (stable identity vs fast line/service lifecycle), not when the UI has another section. A context is not an aggregate; do not wrap each root in its own BC. Use experts' words. List the wrapping / user-facing system first; vendors and systems of record sit downstream. Each context gets **vendor:** (`custom`, `bespoke`, or vendor name). On each **aggregate** that depends on another context, list upstream dependencies under `depends:` — do not invent a Cross-Context Relationships dump.



- **`bc-by-lifecycle-not-ui-themes`** — Contexts follow language and change-frequency, not Onboarding/Selfcare/SignIn screen groups.

- **`user-facing-system-first`** — Consumer app first / left; externals downstream.

- **`vendor-not-implementation`** — `vendor:` on each context; no owning team or implementation stack on the card.

- **`hang-deps-on-owning-bc`** — `depends:` on the **aggregate** that has the dependency; one upstream per entry. No global `## Dependencies` parking lot.



```



fidelity: bounded_context



{{ContextName}}

  vendor: {{custom | bespoke | vendor name}}

  aggregates:

    {{Root}}:

      members:

        - {{member}}

        - {{member}}

      refs:

        - {{OtherRoot}} (by {{IdType}})

      depends:

        {{UpstreamContext}}:

          pattern: {{Shared Kernel | Customer/Supplier | Conformist | ACL | Open Host | Separate Ways}}

          crosses: {{concepts}}

          integrate: {{concrete call site}}

    {{Root}}:

      …

```



---



## building_blocks



Flesh out each aggregate under its BC. Root, members, refs, cross-BC deps, stereotypes. Business invariants belong here as `Invariant:` on classes — not on the bounded_context card.



- **`building-blocks-fidelity-requires-tactical-stereotype`** — Every class name carries a tag (`<<Aggregate Root>>`, `<<Entity>>`, `<<Value Object>>`, `<<Repository>>`, …). Bare names are incomplete.

- **`flaccid-data-object-no-behavior`** — A type is not a field bag; give it *its* operations. Not a repository dump, not someone else’s verbs on a value.

- **`service-is-homeless`** — Domain Service = rare **doer**, only when the operation will not sit cleanly on one domain object. Not SOA `FooService`. `CheckoutService.placeOrder` is `Cart.checkout`.

- **`repository-is-collection-lifecycle`** — Repository only when the business finds/stores/retires that aggregate. Collection members: `add` / `remove` / `update` / `find_by_*`. No repo for a checkout-born Cart or a Subscription that is an invariant of Subscriber.

- **`shared-identity-is-generalisation`** — Shared identity over time (Prospect and Subscriber *are* a Customer) → base type + generalisation arrows.

- **`screen-interface-not-a-domain-object`** — `open()` / `isShowing()` screens are not domain types.

- **`private-method-naming`** — Public `+name`; private `- _name`.

- **`no-orphaned-objects`** — Every type has at least one relationship.



```



fidelity: building_blocks



{{ContextName}}

  {{Root}} <<Aggregate Root>> <<Entity>>

    members: {{Part}} <<Value Object|Entity>>; {{Part}}

    refs:

      - {{OtherRoot}} (by {{IdType}})

    depends:

      → {{UpstreamContext}}:

          pattern: {{catalogue pattern}}

          crosses: {{SyncObject}}, …

          integrate: {{concrete call site}}

    repo: {{Root}}Repository <<Repository>>

      add / remove / update / find_by_{{criteria}}

    events: {{SomethingHappened}} — consumers: {{who}}

  {{Root}}

    …

```



---



## tactics



Architecture + which seams get real adapters.



```



fidelity: tactics



architecture: {{from context | asked | default node+json}}

  repos: {{Root}}Repository → {{persistence}}

  events: {{SomethingHappened}} → {{publish / handle}}

  sync across BC: {{SyncObject}} via {{mechanism}}

```

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



Three levels: **BC** → **Aggregate** → **concept**.



`→ BC · Aggregate · Entity` — cross-context (drop segments when same BC or aggregate).



`→ System · Entity` — external system (e.g. `→ Mavenir DEP · engagedParty`).



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