# iterate — module context

## Purpose
`Iterator` enforces a disciplined grill-then-generate loop over formal output, producing only one small, scanner-validated slice per tick. It wraps `GrillContext.grill_with_context` and applies a hard gate before each generate step: the last two or three grill answers must name a concrete slice boundary grounded in a prove-read of the relevant context files. After each generate, it runs validate and applies one fix pass before returning to the grill. Dumping a whole artifact in a single tick is explicitly a defect. `iterate(tools)` is the host iterate body (open, record decisions, iterate_session, generate) run once per passed context tool. `/iterate` invokes this toolset — not each context tool's host `iterate`. A tools item may be an instance, a toolset path string, or `{toolset, context}`.

## Seam
`Iterator`

## Dependencies
`grill_context.grill_context`, `primitives.actions`, `tools.tool`

## Public API
- `mark_iterate_tick`
- `iterate_session(plan)`
- `iterate(tools)` — host iterate body once per passed context tool

## Mechanism
Tick discipline — each cycle is grill → mark_iterate_tick → generate one slice → validate → one fix pass → stop; the loop never chains ticks or pre-authors output while grilling.
