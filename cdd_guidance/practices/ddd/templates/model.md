---
fidelity: [model]
artifact: [ce-domain-model]
format: md
extends: practices/clean_engineering/templates/class-model.md
---

# Domain Model — {{project_name}}

**Sources / context:** `bounded-context-map.md` (read in full); story map, scenarios, and sketch for the aggregates in scope.

**Extends:** `practices/clean_engineering/templates/class-model.md` — same class notation (`------` properties · `----` operations). At **model** the view holds the core domain only: each aggregate's root, the entities and values it owns, its repository, its domain operations, and the arrows to other aggregates. No constructors, ports, publishers, DTOs, factories, specifications, domain services, or event classes — those wait for **tactics** unless the code already has them.

---

## Layout

`##` is a bounded context, `###` an aggregate inside it, `####` a class inside the aggregate. Every aggregate is written in the same order:

1. **Root** — `#### {{Root}} <<Aggregate Root>> <<Entity>>`: identity and properties, then domain operations.
2. **Repository** — `#### {{Root}}Repository <<Repository>>` directly under the root. Rendered views draw it **inside the root's card**, below the domain operations. Collection operations only: `create`, `load`, `update`, plus `search` / `retire` when the business does them.
3. **Members** — `#### {{Member}} <<Entity>>` or `#### {{Value}} <<Value Object>>`, composed by the root (or by the member that owns them).

Dependencies on other aggregates are properties held by identity, `<< association >>` to the target root, with the call on the operation that uses it (`-> {{OtherRoot}}Repository.load({{otherId}})` or `-> {{OtherRoot}}.{{operation}}`). Across contexts, keep the arc from the bounded-context map under **Integrations:** on the aggregate.

---

## {{ContextName}} | {{owner}}

### {{Aggregate}}

{{One line: the rule this aggregate keeps true.}}

#### {{Root}} <<Aggregate Root>> <<Entity>>

------
+ {{identity}}: {{IdentityType}}
+ {{property}}: {{Type}}
+ << composition >> {{member}}: {{Member}}
+ << association >> {{otherRootId}}: {{IdentityType}}
	// held by identity — {{OtherRoot}} lives in {{OtherAggregate}}
----
+ {{domainOperation}}({{parameters}}): {{ReturnType}}
	-> {{Member}}.{{operation}}
+ {{operationNeedingAnotherAggregate}}({{parameters}}): {{ReturnType}}
	-> {{OtherRoot}}Repository.load({{otherRootId}})
	// {{what crosses and why}}

**Invariants**

- {{what the root keeps true across its members}}

#### {{Root}}Repository <<Repository>>

------
+ << aggregation >> {{roots}}: Collection<{{Root}}>
----
+ create({{what the business supplies}}): {{Root}}
+ load({{identity}}): {{Root}}
+ update({{root}}): void
+ search({{criteria}}): {{Root}}[]
	// only when the business finds this aggregate by something other than identity
+ retire({{identity}}): void
	// only when the business retires this aggregate

#### {{Member}} <<Entity>>

------
+ {{identity}}: {{Type}}
+ {{property}}: {{Type}}
----
+ {{memberOperation}}({{parameters}}): {{ReturnType}}

#### {{Value}} <<Value Object>>

------
+ {{field}}: {{Type}}

Integrations:
  - → {{OtherContext}} · {{OtherAggregate}} · {{OtherRoot}} (by {{IdType}})
    pattern: {{Shared Kernel | Customer/Supplier | Conformist | Anticorruption Layer | Open Host / Published Language | Separate Ways}}
    crosses: {{what crosses}}
    integration: {{the operation above that makes the call}}
    sync: {{source owner · trigger or cadence · acceptable staleness}}

---

## {{AnotherContext}} | {{owner}}

{{Repeat — every aggregate from the bounded-context map appears here or is marked `Unresolved`.}}
