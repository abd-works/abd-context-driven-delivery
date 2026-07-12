---
fidelity: [engineering]
---

# Story Tests

Story tests are the **automated checks that prove each story scenario is real** — one test method per scenario, executing the interaction from the outside through observable outcomes.

The scenarios written at specification (`Given / When / Then / And / But`) map directly onto the test: `Given` steps become setup, `When` becomes the action, `Then` / `And` / `But` become assertions.

## Shape of a story test

Each **story** becomes a **test class**; each **scenario** becomes a **test method**. Additions go into the existing class; new stories get their own class.

- Class: `Test<ExactStoryName>`
- Method: `test_<scenario_outcome_snake_case>`

Where the class lives on disk is a layout decision (Expanded or Flat), not a story-test concept.

## Orchestrator pattern

**Test methods orchestrate; helpers do the work.**

The test method shows the `Given / When / Then` shape of the scenario by calling helpers. The helpers hold the setup, action, and assertion logic. Helpers are named after the step vocabulary so the test method reads as executable scenario prose: `given_cart_with_items(...)`, `when_order_is_submitted(...)`, `then_order_is_confirmed(...)`.

Helpers are parameterized to prevent sprawl. Where `create_order_pending` and `create_order_confirmed` would sit side by side, a single `create_order(status)` covers both. Helpers shared across sub-epic test files are extracted into an epic-level helper module.

Sizing: test method under 20 lines, helper under 20 lines, test class under 300 lines.

## TDD cycle

**RED → GREEN → REFACTOR.** A failing test comes first. The minimum production code follows to make it pass. Refactoring happens with tests green.

A test that passes on the first run proves nothing — the RED step is what defines what needs to be built.
