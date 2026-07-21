<!--
  Bounded Context Map — matches contexts/ddd/examples/examples.md

  One artifact. Aggregates are direct children of the context (no Aggregates
  wrapper). Building-blocks = CE compact classes + stereotypes as #### under
  each ### aggregate. Dependencies name a concrete integrate call site.
-->

# Bounded Context Map — {{project_name}}

## {{ContextName}}

- **Owning team:** {{team_name}}
- **Scope:** {{what this context owns}}
- **Implementation:** {{monolith module | microservice | shared library | legacy system | external vendor}}

### {{AggregateRoot}}

- **Root:** {{Entity}}
- **Boundary members:** {{member}} — {{why inside}}
- **Protected invariants:** {{business rule that requires atomic change}}
- **Cross-aggregate refs:** {{OtherRoot}} (by ID) — consistency: {{immediate | eventual | snapshot}}; rule: {{what happens when this changes}}

#### **{{AggregateRoot}}** <<Aggregate Root>> <<Entity>>

+ {{AggregateRoot}}({{ctor params}})
------
+ << identifier >> {{id_property}}: {{IdType}}
+ << composition >> {{owned}}: list[{{Part}}]
+ << association >> {{ref}}: {{OtherId}} | None
+ {{plain}}: {{Type}}
	Invariant: {{business rule}}
----
+ {{operation}}({{params}}): {{Return}}
	Invariant: {{rule}}
- _{{private_helper}}({{params}}): {{Return}}

#### **{{Part}}** <<Value Object>>

+ {{Part}}({{params}})
------
+ {{property}}: {{Type}}
	Invariant: {{rule — e.g. immutable: replace, do not update in place}}
----
+ {{operation}}({{params}}): {{Return}}

#### **{{AggregateRoot}}Repository** <<Repository>>

+ {{AggregateRoot}}Repository()
------
----
+ add({{root}}: {{AggregateRoot}}): None
+ remove({{root}}: {{AggregateRoot}}): None
+ update({{root}}: {{AggregateRoot}}): None
+ find_by_{{criteria}}({{params}}): {{AggregateRoot}} | None

#### **{{SomethingHappened}}** <<Domain Event>>

+ {{SomethingHappened}}({{payload fields}})
------
+ {{field}}: {{Type}}
	Invariant: Raised when {{trigger}}.
	Invariant: Consumers are {{who}}.
----

## {{AnotherContext}}

- **Owning team:** {{team_name}}
- **Scope:** {{what this context owns}}
- **Implementation:** {{implementation type}}

### {{AggregateRoot}}

- **Root:** {{Entity}}
- **Boundary members:** {{members}}
- **Protected invariants:** {{rules}}
- **Cross-aggregate refs:** {{OtherRoot}} (by ID) — consistency: {{immediate | eventual | snapshot}}; rule: {{…}}

## Dependencies

### {{SourceContext}} → {{TargetContext}}

- **Direction:** {{Source is upstream; Target is downstream | mutual — what flows each way}}
- **What crosses:** {{concepts + translation}}
- **How they integrate:** {{concrete mechanism + call site — e.g. Synchronous call — at `add_item`, Sales reads `Catalog.Product.unit_price` and stores a snapshot}}
- **Relationship pattern:** {{Shared Kernel | Customer/Supplier | Conformist | Anticorruption Layer | Open Host/Published Language | Separate Ways}}
- **Rationale:** {{why; trade-offs}}
