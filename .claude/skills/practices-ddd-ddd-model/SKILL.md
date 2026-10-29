---
name: practices-ddd-ddd-model
description: >-
  #### Overview
  
  Draw the core domain and nothing else: each aggregate's root, the entities and values it owns, the repository that keeps it, the domain operations the business performs on it, and how aggregates depend on one another inside a context and across contexts. Strip out everything technical, so the domain can be discussed, modelled, and simplified as far as it will go before any implementation detail lands on it.
  
  The notation is Clean Engineering's class model. DDD adds three things to it: bounded contexts and aggregates drawn as containers, a stereotype on each class, and the root's repository drawn **in the root's card** below its domain operations.
  
  **Produce:** `domain-model.md` (artifact `ce-domain-model`) from `templates/model.md`, which extends `practices/clean_engineering/templates/class-model.md`; render to `drawio` for the aggregate view. Keep `bounded-context-map.md` contexts, aggregates, and integrations in step. Call clean_engineering at **model**.
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

Use MCP tool: `ddd-model()`
