# space/record_decisions
*Context Decision Record* (CDR) is a short, numbered markdown file that records a design choice a later reader would otherwise question: one that is hard to reverse, surprising without its context, and a real trade-off. Records live in `.context/cdr/{NNNN}-{slug}.md` under the workpath of the session they belong to, and `CDR-FORMAT.md` beside this module is their template.

*RecordDecisions* offers and writes those records while an action runs. `RecordDecisions.for_session(session)` is the records of the session called `session`, such as a board ticket's; a blank name means the open session of the project the call names. The MCP tools are `record-decisions.read_cdr_format`, `record-decisions.list_cdrs(session)`, and `record-decisions.write_cdr(session, slug, paths)`; the MCP instructions `record-decisions.record_decisions_session(session)` wrap an action's turn.

- **Purpose:** Keep the reasons behind hard-to-reverse design choices next to the work they shaped, one record per decision.
- **Seam (terms):** RecordDecisions, `RecordDecisions.for_session`, `record-decisions.read_cdr_format`, `record-decisions.list_cdrs`, `record-decisions.write_cdr`, `record-decisions.record_decisions_session`
- **Dependencies (one-way):** `space/session`, `space/repo`, `harness/agent_tools`, `harness/installation`, `harness/mcp`, `harness/guidance_actions` (`load_document`)

## Constraint

Offer a record only when all three criteria hold, write it as soon as the decision is made, and never invent or batch decisions. Draft the record to a file and pass its path in `paths`. A record for a named session goes under that session's workpath, never under whichever session the chat has open; a name the project has no session for raises `SessionNotFoundError`.
