---
name: practices-bdd
description: >-
  ## Overview
  
  Behavior-driven development turns domain vocabulary into passing tests. Every BDD artifact is an indented hierarchy. Sketch that shape first (`templates/bdd-sketch.md`).
  
  **Tooling & Idioms:** Refer to [`cdd_guidance/rules/language-tools.md`](../../rules/language-tools.md) for language-specific tool recommendations and idiomatic patterns.
---

overview

Guide this action so the output conforms to this schema.

[spec]

spec:
  fidelity: behavior
  id: dotPath
  name: string
  descriptions: [description]
  where:
    - id is this spec name slug
    - the outermost describe is the subject
    - order follows the usage story
  rules:
    - observable-behavior
    - domain-practice-alignment
    - usage-order-behaviors
    - shared-describe-subject
    - full-surface-coverage
    - framework-syntax

description:
  fidelity: behavior
  id: dotPath
  text: string
  order: number
  belongsTo: [spec | description]
  alignsWith?: class
  contexts?: [context]
  descriptions?: [description]
  observations?: [observation]
  where:
    - id is the text slugs from the spec through each parent description to this one, joined by dots
    - plain-English subject, state, or observable condition
    - sibling describes are mutually exclusive
    - reading this describe through each nested that and with to it should is one sentence
  rules:
    - describe-is-subject-not-internal
    - describe-is-plain-english
    - domain-practice-alignment

context:
  fidelity: behavior
  id: dotPath
  text: string
  order: number
  belongsTo: [description | context]
  kind: "that" | "with"
  contexts?: [context]
  observations?: [observation]
  examples?: [example]
  where:
    - id is the parent id, then this text slug, joined by dots
    - that names an enabling event or condition already true
    - with names a standing condition
    - a nested context is a precondition of the observations under it
    - setup under the label establishes the state the label names
    - examples are the shared arrange state for the observations here
  rules:
    - state-not-when
    - nest-by-enabling-events
    - context-setup-expresses-state
    - context-sharing

observation:
  fidelity: behavior
  id: dotPath
  text: string
  order: number
  belongsTo: [context | description]
  examples?: [example]
  demonstrates?: class
  invokes?: [operation | property]
  specifies?: scenario
  where:
    - id is the parent context or description id, then this text slug, joined by dots
    - one observable outcome a stakeholder can verify
    - behavior fidelity is a signature with no assertion body
    - examples are the concrete cases for this outcome
    - demonstrates is the class whose public effect this observation proves
    - invokes is the operation or property the call surface exercises
    - specifies is the story scenario this observation makes executable
  rules:
    - observable-behavior
    - full-surface-coverage
    - no-implementation
    - hierarchy-preservation
    - one-assertion-per-test
    - one-signature-at-a-time
    - red-then-green
    - minimum-green
    - code-minimalism
    - layer-isolation
    - oo-api-design
    - honors-documented-surface-contracts
    - scan-fixture-pair

behavior — Define BDD signatures — describe/it names for every observation, no test bodies.

Use MCP tool: `bdd-behavior()`

realization — Expand each agreed `it should` into the domain call graph that executes that observation — sketch fidelity only (signatures and collaborator calls, no bodies). Notation matches `@clean_engineering` **model** interactions (`->` outbound, `<-` return). This fidelity does not restate GWT scenarios; it traces the describe/`that`/`with` tree already fixed at **behavior**.

Use MCP tool: `bdd-realization()`

development — Implement BDD tests with production code.

Use MCP tool: `bdd-development()`
