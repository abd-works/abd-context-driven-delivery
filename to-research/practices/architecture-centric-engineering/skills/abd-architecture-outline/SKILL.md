---
catalog_garden_tier: practice
catalog_garden_order: 10
name: abd-architecture-outline
catalogue_one_liner: >-
  First fidelity of src/architecture-context.md — system context with all connecting systems, packages, mechanisms catalogue with explicit deviation justification, rules, and decisions.
description: >-
  Produce the first fidelity of src/architecture-context.md — system context (complete surrounding-systems table), packages, mechanisms, rules, and outline-stage ADRs. Use when starting architecture on a new or unfamiliar system, onboarding, or preparing for review.
context-perspective: architecture
context-fidelity:
  - level: shaping
    mode: system-context
---
# abd-architecture-outline

## Purpose

Establish the shared canonical picture of a system — what systems exist, how they connect, what packages organise cross-cutting concerns, what mechanisms impose code shape, and what rules constrain every future decision — so the team starts deeper architecture work from agreed facts, not assumptions.

---

## Agent Instructions

**MANDATORY:** [`common/reference/skill-workflow.md`](../../../../common/reference/skill-workflow.md) — read in full; complete § Bootstrap and § Read-gates before generating or validating.

## Bootstrap

§ Bootstrap — [`common/reference/skill-workflow.md`](../../../../common/reference/skill-workflow.md).

## Read

§ Read-gates — all of [`rules/`](rules/), [`reference/`](reference/), [`templates/`](templates/).

## Input traps

[`reference/input-traps.md`](reference/input-traps.md) — pre-flight in every run, not grill-only.

## Grill me

[`reference/grill-me.md`](reference/grill-me.md) — only when the invocation includes "grill me".

## Generate

[`reference/generate.md`](reference/generate.md).

## Validate

[`common/reference/rule-checklist.md`](../../../../common/reference/rule-checklist.md).

## Diagram workflow

[`reference/diagram-workflow.md`](reference/diagram-workflow.md).
