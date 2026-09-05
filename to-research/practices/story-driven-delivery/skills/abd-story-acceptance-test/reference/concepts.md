# Acceptance Test-Driven Development — Core Concepts

**Domain sources first.** Read [`../../../reference/domain-input-priority.md`](../../../reference/domain-input-priority.md) before writing tests — fixtures and names trace to domain vocabulary and spec examples.

## What is acceptance test-driven development?

**Acceptance test-driven development (ATDD)** is a practice where **automated tests** are written from behavioral context — in whatever form is available — before (or alongside) production code. Tests validate that the system does what the behavior says it should do — from the outside, through observable outcomes.

The richer the input, the more direct the translation: **spec-by-example scenarios** give you Given/When/Then steps to encode directly; **acceptance criteria** give you WHEN/THEN pairs to convert; **stories with notes** give you intent to derive from; **unstructured context** gives you behaviors to discover and make concrete.

In this skill's approach:
- **Tests drive design** — tests are written against the real expected API first; they must fail before implementation begins.
- **RED before GREEN** — a test that passes immediately proves nothing; a failing test defines exactly what to build.
- **Orchestrator pattern** — test methods show the Given-When-Then flow by calling helper functions; helpers handle the detail.
- **Domain language** — test and class names, method names, and helper names use the same vocabulary as the domain context being tested.
- **Any context works** — the quality of the output scales with the specificity of the input, but the practice applies regardless.

---

## Test organization

Tests mirror the story hierarchy as a folder structure. You navigate down through epics and sub-epics as nested folders until you reach the lowest-level sub-epic — that becomes the **file**. The story inside it becomes the **class**. Each scenario on that story becomes a **method**.

```
tests/
  <epic>/
    <epic>_helper.py              ← shared Given/When/Then helpers for this epic
    <sub_epic>/
      <sub_epic>/
        ...
          <lowest_sub_epic>/
            <lowest_sub_epic>.py  ← FILE  (named after the lowest-level sub-epic)
              class Test<Story>   ← CLASS (named after the story)
                def test_<scenario>  ← METHOD (named after the scenario)
```

The epic-level helper file (`<epic>_helper.py`) sits at the epic folder and contains only reusable `given_*` / `when_*` / `then_*` helper methods — no test methods. Sub-epic test files inherit from it when they share helpers.

**The most common mistake** is naming the file after the story instead of the lowest-level sub-epic. The story is always the class, never the file.

**Before writing any code, declare the structure explicitly:**
- Story Path: `[Epic] → [Sub-Epic] → ... → [Lowest Sub-Epic] → [Story]`
- File: `tests/<epic>/.../<lowest_sub_epic>/<lowest_sub_epic>.py`
- Class: `Test<ExactStoryName>`
- Method: `test_<scenario_outcome_snake_case>`
- Existing: yes / no — add to existing file; do not create a duplicate

## Orchestrator pattern

Test methods **orchestrate** the flow; **helper functions** handle the details.

- Test method: under 20 lines, shows Given/When/Then structure by calling helpers.
- Helper function: under 20 lines, reusable setup/action/assertion logic.
- Test class: under 300 lines, one class per story.

**Helper naming** — name helpers using the step vocabulary: `given_cart_with_items(...)`, `when_order_is_submitted(...)`, `then_order_is_confirmed(...)`. Test methods read as executable scenarios.

**Helper discipline** — parameterize to prevent sprawl. If `create_order_pending` and `create_order_confirmed` appear side by side, merge them into `create_order(status)`. When helpers are shared across multiple sub-epic test files, extract them into an epic-level base class.

## TDD cycle

**RED → GREEN → REFACTOR.** Write a failing test first (RED). Implement the minimal code to make it pass (GREEN). Improve code quality while keeping tests green (REFACTOR). Tests must fail before any production code exists — a test that passes immediately proves nothing.

## Domain language

Use the same vocabulary as the domain model, stories, and acceptance criteria in:
- Class names → domain entities (`GatherContextAction`, `BotConfig`)
- Method names → domain responsibilities (`inject_questions_and_evidence`, `load_trigger_words`)
- Test names → observable behavior (`test_agent_loads_configuration_when_file_exists`)

---

## New system vs existing system

**Determine new system vs existing system before writing tests.** If writing tests for an existing system, you MUST read the extracted context (ARIA snapshots, screenshots) and controller decorators before writing `then_*` assertions. Tests must pass against the running system; when a test fails, the test is likely wrong — not the code. See [`../../../reference/new-vs-existing-system.md`](../../../reference/new-vs-existing-system.md) for the shared discipline and evidence sources.
