# iterate — module context

## Purpose
`Iterator` enforces a disciplined grill-then-generate loop over formal output, producing only one small, scanner-validated slice per tick. It wraps `GrillContext.grill_with_context` and applies a hard gate before each generate step: the last two or three grill answers must name a concrete slice boundary grounded in a prove-read of the relevant context files. After each generate, it runs validate and applies one fix pass before returning to the grill. Dumping a whole artifact in a single tick is explicitly a defect.

## Seam
`Iterator`

## Dependencies
`grill_context.grill_context`, `primitives.actions`, `tools.tool`

## Mechanism
Tick discipline — each cycle is grill → mark_iterate_tick → generate one slice → validate → one fix pass → stop; the loop never chains ticks or pre-authors output while grilling.
