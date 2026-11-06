# record_decisions — module context

## Purpose
`RecordDecisions` manages Context Decision Records (CDRs) — short, durable markdown files that capture design choices that are hard to reverse, surprising without context, and represent a real trade-off. It numbers records with four sequential digits, writes them to `.context/cdr/` under the workpath of the session the records are for, and gates every offer against those three criteria so CDRs are never batched or invented. The `CDR-FORMAT.md` template file co-located with the module defines the canonical structure.

## Seam
`RecordDecisions`. Its `@tool_subject` loader `RecordDecisions.for_session(session)` makes the records of the session called `session`, such as a board ticket's, read through `Repo.current().session_named(session)`; a blank name means the current session of the project the call names. The MCP tools are `record-decisions.read_cdr_format`, `list_cdrs`, and `write_cdr(session, slug, content, paths)`, each taking `session` first; `record_decisions_session(session)` is the instructions that wrap a turn.

## Constraint
A record for a named session goes under that session's workpath, never under whichever session the chat has open. A name the project has no session for raises `SessionNotFoundError`.

## Dependencies
`harness.agent_tools`, `harness.guidance_actions.load_document`, `space.repo` (`Repo.session_named`), `space.session`

## Mechanism
Three-criteria gate — a CDR is offered only when all three hold: hard to reverse, surprising without context, genuine trade-off. Any missing criterion means skipping the CDR entirely.
