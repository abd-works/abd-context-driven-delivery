# handoff — module context

## Purpose
Compacts an agent session into a structured handoff document so a fresh agent can resume without re-reading the full chat. `Handoff` (`space/handoff`) writes `handoff-{timestamp}.md` into the folder of the session the handoff is for. It does not open a session.

## Seam
`Handoff`. Its `@tool_subject` loader `Handoff.for_session(session)` makes a handoff for the session called `session`, such as a board ticket's, read through `Repo.current().session_named(session)`; a blank name means the current session of the project the call names (`.sessions/main/` when that project has no named session). The MCP tools are `handoff.write_handoff(session, content, paths)` and the instructions `handoff.handoff_session(next_focus, session)`.

## Constraint
A handoff asked for a named session is written into that session's folder, never into whichever session the chat has open, because a chat can be asked for another ticket's handoff. A name the project has no session for raises `SessionNotFoundError` instead of writing elsewhere.

## Dependencies
`harness.agent_tools`, `harness.guidance_actions.load_document`, `space.repo` (`Repo.session_named`), `space.session` (`Session.new_handoff_path`)

## Mechanism
`handoff_session` expands into the structure of a handoff (Outcome, Progress, Key Learnings, Approach for Next Agent, Correction trend) and tells the agent to write it to a file and call `write_handoff` with that file in `paths` and the same `session`. `write_handoff` reads the file and writes it to `Session.new_handoff_path()`, one timestamped file per call; `Session.latest_handoff` finds the newest.
