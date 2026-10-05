# DDD sketch

The questions to ask are in `ddd.md`, under **Sketch** for the active fidelity. The shell's level of detail is that fidelity's **Scaffold** section. This file is the notation for the `domain driven design:` section.

Declare fidelity once at the top. Use only the sketch for that fidelity — do not fill later-fidelity detail early.

## Notation — headings carry the hierarchy

The map nests through markdown headings, so every context, aggregate, and root folds on its own. `## domain driven design:` is the section heading; the map starts one level below it.

| Heading | Holds |
|---|---|
| `### {Context Name} \| {vendor}` | a bounded context |
| `#### {Aggregate}` | one consistency cluster inside that context |
| `##### {Root}` | the aggregate root, with its tactical stereotypes at **building_blocks** |
| `### event_map:` | the cross-context event map, last in the section |

Under a root heading, a fenced block holds its keys — `emits events:`, `consumes events:`, `members:`, `Integrations:`, `refs:`, `depends:`, `repo:`, `events:`, `Invariant:`. Prose that is not a context — false cognates, open questions, what is settled — belongs in its own `##` section beside `## domain driven design:`, not under a context heading.

---

## bounded_context

Name each **bounded context** (language boundary — **not** a UI theme or page), then the **aggregates it holds** (consistency clusters — usually more than one). Split when language or **change-frequency** diverges (stable identity vs fast line/service lifecycle), not when the UI has another section. A context is not an aggregate; do not wrap each root in its own BC. Use experts' words. List the wrapping / user-facing system first; vendors and systems of record sit downstream. Each context carries its vendor after `|` (`custom`, `bespoke`, or vendor name). On each **aggregate** that depends on another context, list upstream dependencies under `depends:` — do not invent a Cross-Context Relationships dump.

For bounded_context sketches, include event flow on each root:
- `emits events:` event names this aggregate publishes
- `consumes events:` event names this aggregate reacts to

Then close the section with `### event_map:` (`{Event}: emitted by X; consumed by Y, Z`) to make ownership and integration explicit at scaffold/discovery depth.

- **`bc-by-lifecycle-not-ui-themes`** — Contexts follow language and change-frequency, not Onboarding/Selfcare/SignIn screen groups.
- **`user-facing-system-first`** — Consumer app first; externals downstream.
- **`vendor-not-implementation`** — vendor after `|` on each context heading; no owning team or implementation stack on the card.
- **`hang-deps-on-owning-bc`** — `depends:` on the **aggregate** that has the dependency; one upstream per entry. No global `## Dependencies` parking lot.

~~~markdown
### {ContextName} | {vendor}

#### {Aggregate}

##### {Root}

```
events produced:
  - {EventName}
events consumed:
  - {EventName}
members:
  - {member}
  - {member}
Integrations:
  - → {OtherContext} · {OtherRoot} (by {IdType})
    pattern: {Shared Kernel | Customer/Supplier | Conformist | ACL | Open Host | Separate Ways}
    crosses: {what crosses}
    integrate: {concrete call site}
```

#### {AnotherAggregate}

##### {Root}

### event_map:

```
- {EventName}: emitted by {Root}; consumed by {Root}, {Root}
```
~~~

---

## building_blocks

Flesh out each aggregate under its context. Root, members, refs, cross-BC deps, stereotypes. Business invariants belong here as `Invariant:` on classes — not on the bounded_context card.

- **`building-blocks-fidelity-requires-tactical-stereotype`** — Every class name carries a tag (`<<Aggregate Root>>`, `<<Entity>>`, `<<Value Object>>`, `<<Repository>>`, …). Bare names are incomplete.
- **`flaccid-data-object-no-behavior`** — A type is not a field bag; give it *its* operations. Not a repository dump, not someone else's verbs on a value.
- **`service-is-homeless`** — Domain Service = rare **doer**, only when the operation will not sit cleanly on one domain object. Not SOA `FooService`. `CheckoutService.placeOrder` is `Cart.checkout`.
- **`repository-is-collection-lifecycle`** — Repository only when the business finds/stores/retires that aggregate. Collection members: `add` / `remove` / `update` / `find_by_*`. No repo for a checkout-born Cart or a Subscription that is an invariant of Subscriber.
- **`shared-identity-is-generalisation`** — Shared identity over time (Prospect and Subscriber *are* a Customer) → base type + generalisation arrows.
- **`screen-interface-not-a-domain-object`** — `open()` / `isShowing()` screens are not domain types.
- **`private-method-naming`** — Public `+name`; private `- _name`.
- **`no-orphaned-objects`** — Every type has at least one relationship.

~~~markdown
### {ContextName} | {vendor}

#### {Aggregate}

##### {Root} <<Aggregate Root>> <<Entity>>

```
members: {Part} <<Value Object|Entity>>; {Part}
Invariant: {what this root must keep true}
refs:
  - {OtherRoot} (by {IdType})
depends:
  → {UpstreamContext}:
      pattern: {catalogue pattern}
      crosses: {SyncObject}, …
      integrate: {concrete call site}
repo: {Root}Repository <<Repository>>
  add / remove / update / find_by_{criteria}
events: {SomethingHappened} — consumers: {who}
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
