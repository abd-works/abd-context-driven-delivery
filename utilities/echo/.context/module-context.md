# echo — module context

## Purpose
Renders action instructions inside a clearly labelled DO-NOT-FOLLOW fence so that the instructions can be inspected by the user without being executed. `Echo` is a **utility** (`utilities/echo`), not a lifecycle action. It is a standalone toolset with a `fence` tool (pure wrap) and an `echo_session` `@prompt` that captures every instruction the agent received, passes them to `fence`, and emits the fenced block as chat output — nothing more.

## Seam
`Echo`

## Dependencies
`primitives.actions`, `tools.tool`

## Mechanism
Two-step fence pattern: `_fenced` composes the header/footer delimiters around a body string; `echo_session` short-circuits normal execution by instructing the agent to collect its received instructions, call `fence`, and stop.

## Seam
`Echo`

## Dependencies
`primitives.actions`, `tools.tool`

## Mechanism
Two-step fence pattern: `_fenced` composes the header/footer delimiters around a body string; `echo_session` (an `@action`) short-circuits normal execution by instructing the agent to collect its received instructions, call `fence`, and stop.
