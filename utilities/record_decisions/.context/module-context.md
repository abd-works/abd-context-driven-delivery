# record_decisions — module context

## Purpose
`RecordDecisions` manages Context Decision Records (CDRs) — short, durable markdown files that capture design choices that are hard to reverse, surprising without context, and represent a real trade-off. It resolves sequential four-digit numbers automatically, writes CDRs to `.context/cdr/` under a workspace root, and gates every offer against those three criteria so CDRs are never batched or invented. The `CDR-FORMAT.md` template file co-located with the module defines the canonical structure.

## Seam
`RecordDecisions` is composed on the work session — not an IDE skill. Do not deploy a `record_decisions` skill. CDR helpers stay `@agent_tool`. `record_decisions_session` is `@prompt(name="record-decisions-session")` plus `@agent_instructions` so `/record-decisions-session` is the slash command.

## Dependencies
`primitives.actions`, `tools.tool`

## Mechanism
Three-criteria gate — a CDR is offered only when all three hold: hard to reverse, surprising without context, genuine trade-off. Any missing criterion means skipping the CDR entirely.
