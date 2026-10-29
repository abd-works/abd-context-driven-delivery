---
name: practices-ddd-ddd-bounded-context
description: >-
  #### Overview
  
  Draw where language changes — at the level of **business areas, organizational departments, and systems** (or collections of systems that share one model) — then the aggregates that protect invariants inside each context, and the dependency arcs between contexts. A bounded context sits **above** aggregates; it is not one box per aggregate. Names and boundaries are cheap to change here; they are expensive once the model, stories, and code hang off them.
  
  **Produce:** `bounded-context-map.md` from `templates/bounded-context.md`. Call clean_engineering at **modules**.
---

overview

Guide this action so the output conforms to this schema.

# DDD extends Clean Engineering (practices/clean_engineering/model/schema.yaml).
# Each ``is:`` line names the CE supertype (or a DDD type that itself extends CE):
#   module → Module (BoundedContext, Aggregate)
#   class → OoadClass (Entity, ValueObject, Repository, …)
#   property → Property (DomainEvent)
# Fidelity: model draws entityRoot, entity, valueObject, and repository (the aggregate view);
# tactics adds domainEvent, domainService, factory, and specification.
# Stereotype markers: model/sketch use <<Repository>>; code may use @repository / @entity on the class.
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
      - fidelity: model
      - is: entity
      - name: string
      - belongsTo: aggregate
      - associates: [entity]
      - identity: property
      - path: "{aggregate}"
  - valueObject:
      - fidelity: model
      - is: class
      - name: string
      - belongsTo: aggregate
      - path: "{aggregate}"
  - entity:
      - fidelity: model
      - is: class
      - name: string
      - belongsTo: aggregate
      - associates: [entity]
      - path: "{aggregate}"
  - repository:
      - fidelity: model
      - is: class
      - name: string
      - belongsTo: aggregate
      - accesses: entityRoot
      - path: "{aggregate}"
  - domainEvent:
      - fidelity: tactics
      - is: property
      - name: string
      - belongsTo: aggregate
      - path: "{aggregate}"
  - domainService:
      - fidelity: tactics
      - is: class
      - name: string
      - belongsTo: aggregate
      - path: "{aggregate}"
  - factory:
      - fidelity: tactics
      - is: class
      - name: string
      - belongsTo: aggregate
      - path: "{aggregate}"
  - specification:
      - fidelity: tactics
      - is: class
      - name: string
      - belongsTo: aggregate
      - path: "{aggregate}"

# Tactical DDD rules (CE rules still inherited via is: above).
entityRoot:
  rules:
    - every-class-carries-ddd-stereotype
    - domain-concepts-not-technical-names
    - private-method-naming
    - flaccid-data-object-no-behavior
    - no-orphaned-objects
    - screen-interface-not-a-domain-object
entity:
  rules:
    - every-class-carries-ddd-stereotype
    - domain-concepts-not-technical-names
    - private-method-naming
    - flaccid-data-object-no-behavior
    - no-orphaned-objects
    - screen-interface-not-a-domain-object
valueObject:
  rules:
    - every-class-carries-ddd-stereotype
    - domain-concepts-not-technical-names
    - private-method-naming
    - no-orphaned-objects
    - screen-interface-not-a-domain-object
repository:
  rules:
    - every-class-carries-ddd-stereotype
    - domain-concepts-not-technical-names
    - private-method-naming
    - repository-is-collection-lifecycle
    - load-with-identity-in-hand
domainService:
  rules:
    - every-class-carries-ddd-stereotype
    - domain-concepts-not-technical-names
    - private-method-naming
    - service-is-homeless
factory:
  rules:
    - every-class-carries-ddd-stereotype
    - domain-concepts-not-technical-names
    - private-method-naming
specification:
  rules:
    - every-class-carries-ddd-stereotype
    - domain-concepts-not-technical-names
    - private-method-naming

Use MCP tool: `ddd-bounded-context()`
