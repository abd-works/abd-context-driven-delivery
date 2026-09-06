---
name: abd-story-acceptance-criteria
catalog_garden_tier: practice
catalog_garden_order: 30
catalogue_one_liner: >-
  State exactly what must be true for a story to be done — so everyone agrees on 'finished'.
description: >-
  Write When/Then/And/But behaviors that define done for each story. Use when writing or reviewing exploration-phase behavior for stories.
context-perspective: stories
context-fidelity:
  - level: exploration
    mode: acceptance-criteria
---
# abd-story-acceptance-criteria

## Purpose

State exactly what must be true for a story to be done — so everyone agrees on "finished" before coding starts.

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

[`rules/`](rules/) + [`templates/`](templates/).

**Output format:** AC are written as structured `as const` objects in `*-stories.ts`, not decorator or annotation syntax. Each story is an `export const` with `story`, `actor`, `acceptance_criteria` (array of step-object arrays), `domain_terms`, `evidence`, and one named scenario object per AC. See [`reference/concepts.md`](reference/concepts.md) § Code format and [`templates/stories.ts`](templates/stories.ts) for the exact shape.

The `acceptance-criteria.md` template is the **design artifact** for exploration. The `stories.ts` template is the **code artifact** — use it when writing AC directly into code or when reviewing generated output.

## Validate

[`common/reference/rule-checklist.md`](../../../../common/reference/rule-checklist.md).

## Diagram workflow

[`reference/diagram-workflow.md`](reference/diagram-workflow.md).
