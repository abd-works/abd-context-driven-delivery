---
name: practices-ddd
description: >-
  ## Overview
  
  Build the solution around how the business actually works, in the words the business already uses. When the software mirrors the business, it holds the business's logic and knowledge where that understanding actually lives; when it mirrors a database, a framework, or a screen layout, every business conversation has to be re-translated and what the business knows ends up scattered wherever the technology happened to put it.
  
  **`clean_engineering`** owns OO structure, one skill per fidelity: **`clean_engineering-modules`** shapes the module boundaries and seams when **`bounded_context`** draws the map; **`clean_engineering-model`** types the classes, operations, and relationships when **`building_blocks`** classifies concepts with stereotypes; **`clean_engineering-code`** implements the seams when **`tactics`** wires repositories, events, and factories. Do not restate module or class analysis here. DDD adds the domain layer on top: where the language changes, which clusters protect which rules, and what each concept actually is.
  
  ---
---

overview

Guide this action so the output conforms to this schema.

# DDD extends Clean Engineering (practices/clean_engineering/model/schema.yaml).
# Each ``is:`` line names the CE supertype (or a DDD type that itself extends CE):
#   module → Module (BoundedContext, Aggregate)
#   class → OoadClass (Entity, ValueObject, Repository, …)
#   property → Property (DomainEvent)
# Tactical markers: model/sketch use <<Repository>>; code may use @repository / @entity on the class.
# Python nodes in nodes.py subclass the same CE model types; graph rules inherit from schema.
# Pattern overlays may use ``is: ddd.entityRoot`` to extend a DDD type.
# Top: a collection of bounded contexts or aggregates is required. Everything below is a def or sub-def.
[boundedContext | aggregate]
boundedContext:
  - fidelity: bounded_context
  - is: module
  - name: string
  - [boundedContext | aggregate]
  - mappedTo:
    [
      - contextMapping:
          - local: aggregate
          - remote: aggregate
          - pattern: "shared kernel" | "customer-supplier" | "published language" | "conformist" | "separate ways"
    ]
aggregate:
  - fidelity: bounded_context
  - is: module
  - name: string
  - root: entityRoot
  - participants:
    [
      entity | valueObject | class | repository | domainEvent | domainService | factory | specification
    ]
  - entityRoot:
      - fidelity: building_blocks
      - is: entity
      - name: string
      - belongsTo: aggregate
      - associates: [entity]
      - identity: property
      - path: "{aggregate}"
  - valueObject:
      - fidelity: building_blocks
      - is: class
      - name: string
      - belongsTo: aggregate
      - path: "{aggregate}"
  - entity:
      - fidelity: building_blocks
      - is: class
      - name: string
      - belongsTo: aggregate
      - associates: [entity]
      - path: "{aggregate}"
  - repository:
      - fidelity: building_blocks
      - is: class
      - name: string
      - belongsTo: aggregate
      - accesses: entityRoot
      - path: "{aggregate}"
  - domainEvent:
      - fidelity: building_blocks
      - is: property
      - name: string
      - belongsTo: aggregate
      - path: "{aggregate}"
  - domainService:
      - fidelity: building_blocks
      - is: class
      - name: string
      - belongsTo: aggregate
      - path: "{aggregate}"
  - factory:
      - fidelity: building_blocks
      - is: class
      - name: string
      - belongsTo: aggregate
      - path: "{aggregate}"
  - specification:
      - fidelity: building_blocks
      - is: class
      - name: string
      - belongsTo: aggregate
      - path: "{aggregate}"

# Tactical DDD rules (CE rules still inherited via is: above).
entityRoot:
  rules:
    - building-blocks-fidelity-requires-tactical-stereotype
    - domain-concepts-not-technical-names
    - private-method-naming
    - flaccid-data-object-no-behavior
    - no-orphaned-objects
    - screen-interface-not-a-domain-object
entity:
  rules:
    - building-blocks-fidelity-requires-tactical-stereotype
    - domain-concepts-not-technical-names
    - private-method-naming
    - flaccid-data-object-no-behavior
    - no-orphaned-objects
    - screen-interface-not-a-domain-object
valueObject:
  rules:
    - building-blocks-fidelity-requires-tactical-stereotype
    - domain-concepts-not-technical-names
    - private-method-naming
    - no-orphaned-objects
    - screen-interface-not-a-domain-object
repository:
  rules:
    - building-blocks-fidelity-requires-tactical-stereotype
    - domain-concepts-not-technical-names
    - private-method-naming
    - repository-is-collection-lifecycle
    - load-with-identity-in-hand
domainService:
  rules:
    - building-blocks-fidelity-requires-tactical-stereotype
    - domain-concepts-not-technical-names
    - private-method-naming
    - service-is-homeless
factory:
  rules:
    - building-blocks-fidelity-requires-tactical-stereotype
    - domain-concepts-not-technical-names
    - private-method-naming
specification:
  rules:
    - building-blocks-fidelity-requires-tactical-stereotype
    - domain-concepts-not-technical-names
    - private-method-naming

bounded_context — Draw where language changes — at the level of **business areas, organizational departments, and systems** (or collections of systems that share one model) — then the aggregates that protect invariants inside each context, and the dependency arcs between contexts. A bounded context sits **above** aggregates; it is not one box per aggregate. Names and boundaries are cheap to change here; they are expensive once building blocks, stories, and code hang off them.

Use MCP tool: `ddd-bounded-context()`

building_blocks — Classify each concept on the map — entity, value, repository, event, service — and shape the classes that carry them.

Use MCP tool: `ddd-building-blocks()`

tactics — Decide one implementation pattern for each building block the model uses, then implement the domain against it — preserving every name and boundary from upstream.

Use MCP tool: `ddd-tactics()`
