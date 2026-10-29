---
description: "Whenever you add factories, specifications, domain services, or domain events; persist, publish, or test repositories, events, or factories; or change production code they support. Follow these rules."
paths:
  - "**/*.py"
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.java"
  - "**/*-sketch.md"
---

#### Rules



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
- **`load-with-identity-in-hand`** — A live `load` takes the identity already in hand. Do not find it in ambient state (session, request, cookie, signed-in user). A repository that holds one record may load it with no identity. Reach owned aggregates through their owner.
- **`ports-behind-adapters`** — Persistence, messaging, and external systems integrate through ports — not direct imports from the domain core.
- **`private-method-naming`** — Public `+name`; private `- _name`. `derive*` helpers are private.

---