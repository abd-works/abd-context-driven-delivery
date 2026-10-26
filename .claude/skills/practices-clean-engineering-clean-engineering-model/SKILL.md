---
name: practices-clean-engineering-clean-engineering-model
description: >-
  #### Overview
  
  **Other formats:** markdown for a language model and `drawio` through `model/drawio` for a class diagram. The same classes, operations, and relationships must appear in every selected representation.
  
  Design the object model — the classes, what they remember and do, and how they relate.
---

overview

Guide this action so the output conforms to this schema.

[module | package]

module:
  fidelity: modules
  id: dotPath
  name: string
  stereotypes?: [string]
  participants: [module | package | class | operation]
  dependsOn?: [module]
  usedBy?: [epic]
  where:
    - id is the name slugs from the root module to this module, joined by dots
    - name is a domain noun or a path
    - a nested module shares a base seam or is a sub-system
    - at most 40% of classes are public
    - dependencies flow one way, with no cycle
    - seam terms are what a caller types
    - purpose opens with the job a caller hires it for
  rules:
    - vocabulary-traces-to-source
    - do-not-invent-terms
    - do-not-invent-parallel-object-models
    - domain-nouns-only
    - named-seam-and-constraint
    - high-cohesion
    - no-module-per-class
    - single-boundary
    - deep-module
    - abstraction-focus
    - purpose-before-mechanism
    - public-seam-only
    - use-typed-signatures
    - general-purpose-surface
    - temporal-independence
    - one-way-deps
    - extensions-live-with-the-domain
    - low-coupling
    - layer-separation
    - missing-module-context
    - language-modules-one-section
    - modules-not-model-blocks

package:
  fidelity: modules
  id: dotPath
  name: string
  belongsTo: module
  participants: [class | package | module]
  where:
    - id is the module id, then this package name, joined by dots
    - a package groups classes inside a module

class:
  fidelity: model
  id: dotPath
  name: string
  belongsTo: module
  stereotypes?: [string]
  baseClass?: class
  dependsOn?: [class]
  relationships?: [relationship]
  demonstratedThrough?: [example | observation]
  participants: [operation | property]
  where:
    - id is the module id, then this class name, joined by dots
    - a class exists when a property, an instance, and a subtype do not fit
    - a subtype works wherever the base is used
    - collaborators arrive through the constructor
    - behavior sits on the object that owns the invariant
    - one reason to change
  rules:
    - model-modules-follow-the-partition
    - class-not-property-instance-or-subtype
    - no-prototype-swapping
    - keep-classes-single-responsibility
    - shape-classes-around-resources
    - put-logic-on-the-owning-resource
    - hide-inner-details
    - use-explicit-dependencies
    - external-system-interface-is-one-way
    - use-intention-revealing-names
    - use-consistent-naming
    - eliminate-duplication
    - one-canonical-model-document
    - no-redundant-relationship-paths
    - missing-module-context
    - language-modules-one-section
    - modules-not-model-blocks

relationship:
  fidelity: model
  id: dotPath
  kind: "composition" | "aggregation" | "association"
  target: class
  cardinality?: string
  where:
    - id is the class id, then kind, then the target class name, joined by dots
    - composition when the part has no identity outside the owner
    - aggregation when members keep their own identity
    - association when both sides stay independent
    - one canonical link per participant

operation:
  fidelity: model
  id: dotPath
  name: string
  belongsTo: class
  parameters: [parameter]
  returnType: class | string
  body?: string
  invokes: [operation | property]
  invokedBy?: [step | observation]
  invariants?: [invariant]
  where:
    - id is the class id, then this operation name, joined by dots
    - 0..3 parameters on a domain operation (self not counted)
    - one job
    - body under 20 statements
    - a state change returns the record or a failure named after the rejected rule
    - interactions call a named public operation on a collaborator
  rules:
    - keep-operations-single-responsibility
    - limit-operation-parameters
    - avoid-vague-parameter-names
    - errors-out-of-existence
    - state-change-returns-record-or-named-failure
    - domain-exception-carries-context
    - write-invariants
    - write-interactions
    - prefer-class-operations
    - prefer-instance-operations
    - keep-operations-small-focused
    - simplify-control-flow
    - use-exceptions-properly
    - never-swallow-exceptions
    - limit-comments
    - provide-meaningful-context
    - no-legacy-api-after-refactor

property:
  fidelity: model
  id: dotPath
  name: string
  belongsTo: class
  type: string
  value?: string
  hasType?: class
  invokes?: [operation | property]
  invariants?: [invariant]
  where:
    - id is the class id, then this property name, joined by dots
    - a derived property takes no owner or state parameter
    - a relationship stereotype on the property copies onto relationship.kind
  rules:
    - use-property-not-accessor
    - hide-inner-details

parameter:
  fidelity: model
  id: dotPath
  name: string
  belongsTo: operation
  type: string
  where:
    - id is the operation id, then this parameter name, joined by dots
    - the name says what the caller supplies
  rules:
    - avoid-vague-parameter-names
    - use-typed-signatures
    - use-intention-revealing-names

invariant:
  fidelity: model
  id: dotPath
  text: string
  belongsTo: [operation | property]
  where:
    - id is the owner id, then this text slug, joined by dots
    - a must, never, always, before, or after about this object's own state
  rules:
    - write-invariants
    - limit-comments

Use MCP tool: `clean-engineering-model()`
