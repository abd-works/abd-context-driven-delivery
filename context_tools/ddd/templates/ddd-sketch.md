# DDD sketch

Declare fidelity once at the top. Use only the sketch for that fidelity — do not fill later-fidelity detail early.

---

## bounded_context

Name each **bounded context** (language / team / model boundary — **not** a UI theme or page), then the **aggregates it holds** (consistency clusters — usually more than one). Split when language or **change-frequency** diverges (stable identity vs fast line/service lifecycle), not when the UI has another section. A context is not an aggregate; do not wrap each root in its own BC. Use experts' words. List the wrapping / user-facing system first; vendors and systems of record sit downstream. Hang each dependency as `Source → Target` — do not invent a Cross-Context Relationships dump.

- **`bc-by-lifecycle-not-ui-themes`** — Contexts follow language and change-frequency, not Onboarding/Selfcare/SignIn screen groups.
- **`user-facing-system-first`** — Consumer app first / left; externals downstream.
- **`hang-deps-on-owning-bc`** — `{{Source}} → {{Target}}` on the owning pair. No Cross-Context Relationships parking lot.

```
fidelity: bounded_context

{{ContextName}}
  aggregates: {{Root}}, {{Root}}
{{ContextName}}
  aggregates: {{Root}}, {{Root}}

{{Source}} → {{Target}}
  direction: {{upstream / downstream | mutual}}
  crosses: {{concepts}}
  integrate: {{concrete call site}}
  pattern: {{Shared Kernel | Customer/Supplier | Conformist | ACL | Open Host | Separate Ways}}
```

---

## building_blocks

Flesh out each aggregate under its BC. Root, invariants, cross-agg and cross-BC deps, sync objects. Stereotypes as you decide them.

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
    invariants: {{rule}}; {{rule}}
    members: {{Part}} <<Value Object|Entity>>; {{Part}}
    cross-agg:
      → {{OtherRoot}} (by {{IdType}}) — {{immediate | eventual | snapshot}}; {{rule}}
    cross-bc:
      → {{OtherContext}}.{{Root}} via {{SyncObject}} — {{how / when}}
    repo: {{Root}}Repository <<Repository>>
      add / remove / update / find_by_{{criteria}}
    events: {{SomethingHappened}} — consumers: {{who}}
  {{Root}}
    …

{{Source}} → {{Target}}
  sync objects: {{ProductId}}, {{unit_price snapshot}}, …
  integrate: {{concrete call site using those objects}}
  pattern: {{catalogue pattern}}
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
