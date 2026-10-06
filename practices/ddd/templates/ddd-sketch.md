# DDD sketch



The questions to ask are in `ddd.md`, under **Sketch** for the active fidelity. The shell's level of detail is that fidelity's **Scaffold** section. This file is the notation for the `domain driven design:` section.



For how Clean Engineering folds into this section, see `ddd.md` under **Sketch** at the active fidelity.



Declare fidelity once at the top. Use only the sketch for that fidelity — do not fill later-fidelity detail early.



## Notation — headings carry the hierarchy



The map nests through markdown headings, so every context, aggregate, entity, and root folds on its own. `## domain driven design:` is the section heading; the map starts one level below it.



| Heading | Holds |

|---|---|

| `### {Context Name} \| {vendor}` | a bounded context |

| `#### {Module}/` | clean-engineering module inside the context — usually **one per context** when the context is small; several aggregates and entities nest inside it |
| `#### {Aggregate}/` | optional — consistency cluster inside a module when the sketch needs to show aggregate boundaries explicitly |

| `##### {Entity}` | an aggregate root or an entity the root owns — each entity that acts gets its own heading |

| `### event_map:` | the cross-context event map, last in the section |



Under an aggregate heading, a fenced block holds the **module seam** — `// seam:` and `// constraint:` — plus aggregate-level notes (`entry:`, `note:`). Under each **entity** heading, a fenced block uses clean-engineering class notation:



- **operations** first — verb phrases on the entity that owns the behavior (`resolve`, `confirm`, `qualify`)

- **properties** next — noun phrases the entity holds (no `members:` header; no bullet list)

- **owned entities** — indent one level, or give a sibling `#####` when the owned entity has its own operations

- **emits events:** / **consumes events:** — on the entity that publishes or reacts

- **Integrations:** — cross-context only (`→ OtherContext · Aggregate · Entity`). Same context or same aggregate: name the other type as a **property** on the entity that uses it — not an integration arc.



Do not float bare operations above the entity they belong to. Do not use `members:` — state belongs on the entity as properties. A verb names an operation; a noun names a property or an owned entity.



Prose that is not a context — false cognates, open questions, what is settled, build order — belongs in its own `##` section beside `## domain driven design:`, or in a closing fenced block before `event_map:`.



---



## bounded_context

Name each **bounded context** at the level of a **business area, department, or system collection** — the place where one ubiquitous language holds. Then nest the **aggregates** that live inside it (usually more than one). A bounded context sits **above** aggregates; one `###` heading per aggregate is noise. If a downstream record does not justify its own language boundary, leave it off the map and record it under **Integrations:** instead.

Good boundaries come from organizational and system reality: different departments, different business areas, different systems (or groups of systems that share one model). The solution's own unique views count too. Split when language or **change-frequency** genuinely diverges — not when the UI has another section, and not to give every aggregate its own box. If you cannot name the business area or system collection behind a candidate context, omit the `###` heading.

Use experts' words. List the solution's contexts first; downstream areas and systems of record follow. Each context carries its vendor after `|` (`custom`, `bespoke`, or vendor name). On each **aggregate** that depends on another context, list upstream dependencies under `depends:` or **Integrations:** — do not invent a Cross-Context Relationships dump.



Each **custom-owned context** is usually **one clean-engineering module** — not one module per aggregate or per class. Name the module with a trailing `/` (`#### single-client-view/`). Put the module **seam** and **constraint** on that module card. Nest aggregates only when the sketch must show consistency boundaries; otherwise list entities directly under the module. Give each entity that remembers state or performs work its own `#####` heading; put that entity's operations and properties in its fence. Split into multiple modules only when change rate, ownership, or coupling genuinely diverges.



For bounded_context sketches, include event flow on the entity that owns the transition:

- `emits events:` on the publishing entity

- `consumes events:` on the reacting entity



Then close the section with `### event_map:` (`{Event}: emitted by X; consumed by Y, Z`) to make ownership and integration explicit at scaffold/discovery depth. When custom aggregates depend on one another, add a `build order:` block before `event_map:`.



- **`bc-above-aggregate`** — Context names a business area, department, or system collection — not one aggregate. Several aggregates per context is normal; one context per aggregate is an anti-pattern.
- **`one-module-per-context-when-small`** — One module per context when types collaborate in a consolidated view; not one package per class (`no-module-per-class` in clean_engineering **modules**).
- **`aggregate-clusters-entities`** — One aggregate per consistency cluster with a chosen root; several entities under one `#### {Aggregate}/`. Not one aggregate heading per entity class.

- **`bc-by-lifecycle-not-ui-themes`** — Contexts follow language and change-frequency, not Onboarding/Selfcare/SignIn screen groups.

- **`user-facing-system-first`** — Solution contexts first; downstream areas and systems follow.

- **`vendor-not-implementation`** — vendor after `|` on each context heading; no owning team or implementation stack on the card.

- **`hang-deps-on-owning-bc`** — `depends:` on the **aggregate** that has the dependency; one upstream per entry. No global `## Dependencies` parking lot.
- **`integrations-cross-context-only`** — **Integrations:** arcs cross a bounded-context boundary. Collaborators inside the same context are properties on the entity that reads them.



~~~markdown

### {ContextName} | {vendor}



```

note: {why this context exists}

```



#### {Aggregate}/



```

// seam: {what a caller hires this aggregate to do — job first}

// constraint: {what callers must or must not do}

entry: {how the aggregate is reached, when that matters}

```



##### {Root}



```

{operationName}

{operationName}

{propertyName}

{ownedEntityName}

Integrations:

  - → {OtherContext} · {OtherRoot} (by {IdType})

    pattern: {Shared Kernel | Customer/Supplier | Conformist | ACL | Open Host | Separate Ways}

    crosses: {what crosses}

    integrate: {concrete call site}

// dep -> {OtherAggregate}/ — {why}

```



##### {OwnedEntity}



```

{operationName}

{propertyName}

emits events:

  - {EventName}

consumes events:

  - {EventName}

```



```

build order:

  {aggregate}/ → {aggregate}/ → {aggregate}/

```



### event_map:



```

- {EventName}: emitted by {Entity}; consumed by {Entity}, {Entity}

```

~~~



---



## building_blocks



Flesh out each aggregate under its context. Give each entity its stereotype; deepen operations into signatures and add `->` interactions per clean-engineering **model** fidelity. Keep aggregate-level module seam and constraint. At generate time use `templates/building-blocks.md` (extends `practices/clean_engineering/templates/class-model.md`) for stereotype operations — repositories load/save/search/update/remove; aggregate roots submit `-> DomainEventPublisher.publish` on state-changing operations that emit past-tense events.



- **`building-blocks-fidelity-requires-tactical-stereotype`** — Every class name carries a tag (`<<Aggregate Root>>`, `<<Entity>>`, `<<Value Object>>`, …). Bare names are incomplete.

- **`flaccid-data-object-no-behavior`** — A type is not a field bag; give it *its* operations. Not a repository dump, not someone else's verbs on a value.

- **`service-is-homeless`** — Domain Service = rare **doer**, only when the operation will not sit cleanly on one domain object. Not SOA `FooService`. `CheckoutService.placeOrder` is `Cart.checkout`.

- **`repository-is-collection-lifecycle`** — Repository only when the business finds/stores/retires that aggregate. Collection members: `add` / `remove` / `update` / `find_by_*`. No repo for a checkout-born Cart or a Subscription that is an invariant of Subscriber.

- **`shared-identity-is-generalisation`** — Shared identity over time (Prospect and Subscriber *are* a Customer) → base type + generalisation arrows.

- **`screen-interface-not-a-domain-object`** — `open()` / `isShowing()` screens are not domain types.

- **`private-method-naming`** — Public `+name`; private `- _name`.

- **`no-orphaned-objects`** — Every type has at least one relationship.



~~~markdown

### {ContextName} | {vendor}



#### {Aggregate}/



```

// seam: {job a caller hires this module for}

// constraint: {caller obligation}

```



##### {Root} <<Aggregate Root>> <<Entity>>



```

{operationName} {param}

   -> {Collaborator}.{operation}

{propertyName}

{ownedEntity} <<Entity|Value Object>>

Invariant: {what this root must keep true}

refs:

  - {OtherRoot} (by {IdType})

depends:

  → {UpstreamContext}:

      pattern: {catalogue pattern}

      crosses: {SyncObject}, …

      integrate: {concrete call site}

repo: {Root}Repository <<Repository>>

  load / save / search / update / remove

events: {SomethingHappened} — emitted by {operationOnRoot} -> DomainEventPublisher.publish — consumers: {who}

```

~~~



---



## tactics



Architecture + which seams get real adapters.



~~~markdown

### architecture:



```

runtime: {from context | asked | default node+json}

repos: {Root}Repository → {persistence}

events: {SomethingHappened} → {publish / handle}

sync across BC: {SyncObject} via {mechanism}

```

~~~


