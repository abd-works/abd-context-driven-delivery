---
description: "Whenever you add, change, or remove an aggregate's root, members, repository, domain operations, or its dependencies on other aggregates, or change code those aggregates support. Follow these rules."
paths:
  - "**/*bounded-context*"
  - "**/*-model.md"
  - "**/*-model.drawio"
  - "**/*-sketch.md"
---

#### Rules



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