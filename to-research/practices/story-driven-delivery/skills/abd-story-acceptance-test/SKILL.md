---
name: abd-story-acceptance-test
catalog_garden_tier: practice
catalog_garden_order: 50
catalogue_one_liner: >-
  Prove each behavior works before writing production code — tests drive what gets built.
description: >-
  Generate executable acceptance tests from scenarios using the orchestrator pattern. Use when turning behavioral specs into test code or driving implementation test-first.
context-perspective: stories
context-fidelity:
  - level: engineering
    mode: acceptance-tests
---
# abd-story-acceptance-test

## Purpose

Generate executable test files from specification scenarios, acceptance criteria, stories, or rough descriptions using the project's language and framework. Follow RED-GREEN-REFACTOR: write a failing test that expresses expected behavior, implement production code until it passes — one class per story, one method per scenario, Given-When-Then helpers doing the work.

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

## Output

[`reference/output.md`](reference/output.md).

## Validate

[`common/reference/rule-checklist.md`](../../../../common/reference/rule-checklist.md).
