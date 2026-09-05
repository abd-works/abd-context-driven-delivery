---
name: abd-architecture-code
description: >-
  Generate tests and production code by resolving the per-folder architecture-context.md for the mechanism in scope and copying-and-renaming the matching template package per story. Use when a story has both a specification and a runnable template package and needs executable code.
context-perspective: architecture
context-fidelity:
  - level: engineering
    mode: production-code
---
# abd-architecture-code

## Purpose

Turn architecture decisions into running code — so the per-folder `architecture-context.md` design and the runnable template package it embodies are an enforced reality in every layer and test tier for every story.

---

## Agent Instructions

**MANDATORY:** [`common/reference/skill-workflow.md`](../../../../common/reference/skill-workflow.md) — read in full; complete § Bootstrap and § Read-gates before generating or validating.

## Bootstrap

§ Bootstrap — [`common/reference/skill-workflow.md`](../../../../common/reference/skill-workflow.md).

## Read

§ Read-gates — read in this order:

- **[`reference/concepts.md`](reference/concepts.md)** — defines the two inputs this skill consumes (`<context-file>` for the design, `<spec-root>` for the embodiment), how `<spec-root>` resolves to a template package under `docs/architecture/templates/`, and the orchestration of downstream skills.
- **[`../../reference/architecture-context-model.md`](../../reference/architecture-context-model.md)** — practice-level model; centralized documents + per-folder context files + template packages.
- **[`reference/generate.md`](reference/generate.md)** — step-by-step workflow (input resolution → context read → test layout inventory → progress checklist → generation → validation).
- **[`reference/input-traps.md`](reference/input-traps.md)** — pre-flight in every run; route back to `abd-architecture-specification` or `abd-architecture-template` when gates fail.
- **[`reference/grill-me.md`](reference/grill-me.md)** — interview questions when inputs are incomplete; mechanics in [`common/reference/grill-me-with-practice-skill.md`](../../../../common/reference/grill-me-with-practice-skill.md).
- **All files in [`rules/`](rules/)** — DO / DO NOT contract per rule; every generated file is validated against this set plus `<spec-root>/rules/` and `<context-file>` § Rules.

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
