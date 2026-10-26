---
name: practices-ddd-ddd-tactics
description: >-
  #### Overview
  
  Decide one implementation pattern for each building block the model uses, then implement the domain against it — preserving every name and boundary from upstream.
  
  **Produce:** Implementation under the project layout; call clean_engineering at **code**. When that build creates folders for bounded contexts and aggregates, write `.context/bounded-context.md` in each context folder.
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

Use MCP tool: `ddd-tactics()`
