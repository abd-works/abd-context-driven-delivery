---
fidelity: [exploration, specification]
---

# Story Scenarios

Story scenarios are **the exact interactions and results between the user and the system** that a story represents — what the user does, what the system does back, what becomes true, what must not happen.

The happy path is the first walk-through of the interaction — one path, enough to prove the story is real and align on what "done" looks like.

Beyond the happy path lie every path that matters — errors, boundaries, alternate flows — captured with concrete values and any preconditions needed to make them runnable.

## How an interaction is described

An interaction is a short sequence of steps.

The starting state is named with `Given` — the data, state, and setup that must be true before the trigger makes sense. Preconditions chain with `And` the same way outcomes do.

The trigger is written with `When` — the action or event that starts a beat. The observable result follows as `Then`. Further outcomes from the same trigger continue with `And`, not a new `When`. A new `When` appears only when the actor or trigger genuinely changes and the next beat begins.

The negative — something that must not happen, an error prevented, no write, no state change — is named explicitly with `But`, so it is visible in the scenario rather than implied.

## Scenarios

An interaction is captured as a **named scenario**. The name describes the path (`Happy path`, `Payment declined`, `Cart empty at checkout`), so readers can find the one they care about at a glance.

At exploration there is exactly one scenario, named `Happy path`. No error scenarios, no boundary scenarios, no alternates. When a second scenario feels necessary, the story is either not shaped right or the work has already moved to specification.

At specification there is one named scenario per path that matters — `Happy path` plus each error, boundary, and alternate flow that changes the outcome. Every step, `Given` through `Then`, carries concrete examples, so the whole interaction has real values a test can run against.
