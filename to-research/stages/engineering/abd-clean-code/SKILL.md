---
name: abd-clean-code
catalog_garden_tier: practice
catalog_garden_family: architecture-centric-engineering
catalog_garden_order: 60
catalogue_one_liner: >-
  Production code that matches story behavior: clean structure, domain language, scanner-backed quality bars (Python/JS).
description: >-
  Write production code that implements story behavior using domain language,
  clean functions, explicit dependencies, and observable design. This skill
  covers the full quality bar for implementation code: single-responsibility
  functions and classes, intention-revealing names, explicit constructor
  injection, guard-clause control flow, domain exceptions, encapsulation, and
  DRY structure. Use it when writing any production module from scratch,
  reviewing code for quality, driving the GREEN phase of a TDD cycle, or
  refactoring to clean up debt. Produces Python or JavaScript/ES module output
  from templates and validates against embedded scanner-backed rules.
context-perspective: stage
context-fidelity:
  - level: engineering
    mode: quality-gate
---
# abd-clean-code

## Purpose

Write production code that implements story behavior using **domain language**, **clean functions**, **explicit dependencies**, and **observable design**.

This skill produces real, runnable production modules — in Python or JavaScript — from whatever context is available: a story, acceptance criteria, a failing test, or a description of the behavior to implement. The output follows a consistent layout: one module per sub-epic area, one class per domain entity, functions under 20 lines, and all dependencies injected through the constructor.

---

## Output file

**Deliverables folder:** see `../common/reference/skill-workflow.md` — Output file resolution.

**File name:** `<domain_entity_snake_case>.py` or `<domainEntity>.js`. One file per domain entity.

---

## Agent Instructions

> **MANDATORY — read `../common/reference/skill-workflow.md` before starting. It defines read-gates, output file resolution, and the per-rule verdict format.**

### 1. Read context

Read these files:
- **`reference/concepts.md`** — what clean code is, domain language, function discipline, dependency injection, class design, properties, error handling, and the shape of good production code.
- **`reference/examples.md`** — a worked Python example showing a complete Cart/Order domain module.

### 2. Generate

Read every file in **`rules/`**; author to those rules.

**Produce output from every template:**

| Template | What to produce |
| --- | --- |
| `templates/clean-code.py` | Python production module with domain entities, constants, exceptions, and behavior |
| `templates/clean-code.js` | JavaScript/ES module equivalent |

**Generation steps:**
1. Confirm language and framework — default to Python (stdlib) or JavaScript (ES modules).
2. Identify the story, then declare names — state domain entity and responsibilities before coding.
3. Pick the matching template; emit code only (omit template instructions).
4. Build — one module per sub-epic area, one class per domain entity, functions under 20 lines, explicit constructor injection.

### 3. Validate

Run the scanners:

```bash
python skills/common/scripts/run_scanners.py \
  --skill-root skills/abd-clean-code \
  --workspace <path-to-output>
```

Then emit per-rule verdicts per `../common/reference/skill-workflow.md`.

---

## Validate

**Goal:** Inspect what was built — read the artifacts as reviewers.

- **Functions do one thing** — no mixing business logic with I/O or mutations in the same function.
- **Functions under 20 lines** — complex logic extracted into named helpers.
- **Clear parameters** — 0–2 parameters preferred; no boolean flags.
- **Guard clauses** — flat structure, maximum 2 levels of nesting.
- **Intention-revealing names** — named constants for every magic number; no abbreviations.
- **Consistent naming** — one word per concept across the codebase.
- **No duplication** — repeated logic extracted into reusable functions.
- **Separated concerns** — pure calculations separate from side effects.
- **Abstraction levels maintained** — no raw SQL mixed with business logic.
- **Domain exceptions** — never return None to signal failure; never swallow.
- **Explicit dependencies** — all via constructor; no hidden globals.
- **Encapsulation** — private attributes with `_` or `#`; expose behavior, not data.
- **Single-responsibility classes** — each class has one reason to change.
- **Domain language** — no Manager, Handler, process(), execute().
- **No useless comments** — only WHY, not WHAT; no commented-out code.
- **No bundle markers** — `SKILL.md` has no `<!-- execute_rules:bundle_rules -->` markers.

---
