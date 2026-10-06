---
fidelity: [building_blocks]
artifact: [ce-domain-model]
format: md
extends: practices/clean_engineering/templates/class-model.md
---

# Bounded Context Model — {{project_name}}

**Sources / context:** `bounded-context-map.md` (read in full); story map and sketch for the aggregates in scope.

**Extends:** `practices/clean_engineering/templates/class-model.md` — same class notation (`+` constructor · `------` properties · `----` operations). At **building_blocks** every class carries a DDD tactical stereotype and the operations that stereotype needs to do its job.

---

## Stereotype operations

Give each building block the operations the guidelines assign to it — not a field bag, not another type's verbs parked on the wrong class.

| Stereotype | Operations on the class | Submit events |
|------------|-------------------------|---------------|
| **<<Aggregate Root>> <<Entity>>** | Domain behaviour that enforces invariants; only entry point for changes inside the aggregate | State-changing operations that other aggregates or contexts must hear about build a past-tense **<<Domain Event>>** and call `-> DomainEventPublisher.publish` (or `-> {{Root}}Repository.save` when persistence and publish move together) before returning |
| **<<Entity>>** (member) | Behaviour on owned state; reached through the root | Does not publish cross-aggregate events — the root submits |
| **<<Value Object>>** | Derive and compare without mutation: `equals`, `with{{Field}}`, predicates such as `isQualified()` | None — immutable facts |
| **<<Specification>>** | `isSatisfiedBy({{candidate}}): boolean` — one named rule reused across qualify · validate · create paths | None |
| **<<Repository>>** | `load({{identity}})`, `save({{root}})`, `search({{criteria}})`, `update({{root}})`, `remove({{identity}})` — collection lifecycle on the **aggregate root** only; no domain rules | None — repositories persist and retrieve; aggregates emit |
| **<<Entity>>** (inside a collection aggregate) | Behaviour on the member entity; lookup through the root: `catalog.findProduct(name)` not `ProductRepository.load` | None — the catalog root is the entry point |
| **<<Factory>>** | `create({{inputs}}): {{AggregateRoot}}` or `build({{inputs}}): {{AggregateRoot}}` when valid birth needs subtype choice, several rules, or outside collaborators | None — ordinary creation stays on the root when birth is simple |
| **<<Domain Event>>** | Past-tense name; payload properties only | Published by the aggregate operation that recorded the fact — not by a standalone emitter type |
| **<<Domain Service>>** | Rare homeless verb that genuinely spans aggregates: `{{transfer}}({{from}}, {{to}}, {{amount}})` | May `-> DomainEventPublisher.publish` when the coordinated act produces a fact consumers need |
| **<<Service>>** (external system / port) | `publish({{event}})` on **DomainEventPublisher**; `receive({{event}})` on downstream intake ports | Boundary only — domain types do not import transport |

**Repository** models a typed collection: declare `+ << aggregation >> {{roots}}: Collection<{{Root}}>` on the repository class.

**Event submission:** when an aggregate operation changes business state that crosses the consistency boundary, name the operation on the root, list the event in the **Event map**, and show `-> DomainEventPublisher.publish({{PastTenseEvent}})` on that operation line.

---

## {{ContextName}} | {{owner}}

**Module:** `{{context-folder}}`

> // seam: {{job a caller hires this context for}}
> // constraint: {{caller obligation}}

### {{Aggregate}}

{{Root Entity}} — {{one line}}

Integrations (from bounded-context map — keep on the aggregate):

```
Integrations:
  - → {{Target}} · {{Aggregate}} · {{Entity}}
    pattern: {{ACL | Customer/Supplier | …}}
    crosses: {{what crosses}}
    integration: {{concrete call site}}
```

consumes events:
  - {{EventName}}

emits events:
  - {{EventName}}

#### {{Root}} <<Aggregate Root>> <<Entity>>

+ {{Root}}({{dependencies including DomainEventPublisher when the root emits}})
------
+ {{identity}}: {{IdentityType}}
+ << association >> eventPublisher: DomainEventPublisher
----
+ {{domainOperation}}({{parameters}}): {{ReturnType}}
	-> {{Collaborator}}.{{operation}}
+ {{stateChange}}({{parameters}}): {{PastTenseEvent}}
	-> eventPublisher.publish({{PastTenseEvent}})
	-> {{Root}}Repository.save(this)
	// {{what changed and who must react}}

**Invariants**

- {{aggregate invariant}}

#### {{MemberEntity}} <<Entity>>

+ {{MemberEntity}}(...)
------
+ {{property}}: {{Type}}
----
+ {{memberBehaviour}}(): {{ReturnType}}

#### {{ValueName}} <<Value Object>>

+ {{ValueName}}(...)
------
+ {{field}}: {{Type}}
----
+ {{predicateOrTransform}}(): {{boolean | ValueName}}

#### {{RuleName}} <<Specification>>

+ {{RuleName}}(...)
------
----
+ isSatisfiedBy({{candidate}}): boolean

#### {{Root}}Repository <<Repository>>

+ {{Root}}Repository(...)
------
+ << aggregation >> {{roots}}: Collection<{{Root}}>
+ << association >> {{externalPort}}: {{ServiceType}}
----
+ load({{identity}}): {{Root}}
+ save({{root}}): void
+ search({{criteria}}): {{Root}}[]
+ update({{root}}): void
+ remove({{identity}}): void

#### {{PastTenseEvent}} <<Domain Event>>

+ {{PastTenseEvent}}({{payload fields}})
------
+ {{field}}: {{Type}}

#### {{FactoryName}} <<Factory>> (only when creation is complex)

+ {{FactoryName}}(...)
------
----
+ create({{inputs}}): {{Root}}

#### {{DomainCapability}} <<Domain Service>> (only when the verb is homeless)

+ {{DomainCapability}}(...)
------
----
+ {{coordinatedAct}}({{parameters}}): {{Result}}
	-> {{AggregateA}}.{{operation}}
	-> {{AggregateB}}.{{operation}}
	-> eventPublisher.publish({{PastTenseEvent}})

#### DomainEventPublisher <<Service>>

+ DomainEventPublisher(...)
------
----
+ publish({{PastTenseEvent}} | …): void

---

## {{AnotherContext}} | {{vendor}}

{{Repeat aggregate sections — every concept from the bounded-context map appears here or is marked `Unresolved`.}}

---

## Event map

| Event | Emitted by | Operation | Consumed by |
|-------|------------|-----------|-------------|
| {{PastTenseEvent}} | {{Aggregate Root}} | {{operation on root}} | {{Consumer aggregate or external intake}} |
