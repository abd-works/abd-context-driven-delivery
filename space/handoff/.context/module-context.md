# space/handoff
*Handoff* is a compact account of a session — what it achieved, what was learned, and where the next agent starts — so a fresh agent can continue the work without rereading the whole chat. Each handoff is a new `handoff-{timestamp}.md` in the session's folder, and `Session.latest_handoff` finds the newest.

`Handoff.for_session(session)` is the handoff for the session called `session`, such as a board ticket's; a blank name means the open session of the project the call names (`.sessions/main/` when that project has none). The MCP instructions `handoff.handoff_session(next_focus, session)` draft the handoff, and the MCP tool `handoff.write_handoff(session, paths)` writes the drafted file into the session's folder.

- **Purpose:** Hand a session's work to the next agent as one file in the session's folder.
- **Seam (terms):** Handoff, `Handoff.for_session`, `handoff.handoff_session`, `handoff.write_handoff`
- **Dependencies (one-way):** `space/session`, `space/repo`, `harness/agent_tools`, `harness/installation`, `harness/mcp`, `harness/guidance_actions` (`load_document`)

## Constraint

Draft the handoff to a file and pass its path in `paths`; do not put the handoff body on an MCP call. A handoff asked for a named session is written into that session's folder, never into whichever session the chat has open, because a chat can be asked for another ticket's handoff. A name the project has no session for raises `SessionNotFoundError` instead of writing elsewhere.
