# echo — module context

## Purpose

Renders action instructions inside a clearly labelled DO-NOT-FOLLOW fence so that the instructions can be inspected by the user without being executed. `Echo` is a **utility** (`utilities/echo`), not a lifecycle action. It is a standalone toolset with a `fence` tool (pure wrap) and an `echo_session` `@prompt` that captures every instruction the agent received, passes them to `fence`, and emits the fenced block as chat output — nothing more.

## Seam

`Echo`

## Public API

- `fence` — wrap a body in the DO-NOT-FOLLOW delimiters
- `echo_session` — collect received instructions, call `fence`, and stop

## Extend

Compose `fence` around any instruction body the agent should display without following. Do not treat delimiter helpers as a separate seam.

## Dependencies

`primitives.actions`, `tools.tool`
