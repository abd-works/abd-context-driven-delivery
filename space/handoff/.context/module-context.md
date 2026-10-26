# handoff — module context

## Purpose
Compacts the current agent session into a structured handoff document so a fresh agent can resume without re-reading the full chat. `Handoff` (`space/handoff`) writes `handoff-{timestamp}.md` into the project's current session folder, `{CDD_PROJECT}/.sessions/{session}/` (the session saved in that project's `.sessions/session.json`), or `.sessions/default/` when the project has no named session; cwd stands in when `CDD_PROJECT` is unset. It does not open a session.

## Seam
`Handoff`

## Dependencies
`workspace`, `harness.agent_tools`, `tools.tool`

## Mechanism
`collect_session_state` assembles live state from the working folder (sketches, named artifacts, CDD sketch summary, grill-answer headings) and returns it as JSON. `preview_handoff` collects and renders that markdown without writing files or closing a sprint. `write_handoff` resolves the archive slug (`handoff-YYYY-MM-DD[-focus]`), persists content to both the archive and latest paths, and optionally closes the sprint session. `handoff_session` wraps a turn only when `workspace.current_work_session` is already set. `/backlog` uses `preview_handoff` so the GitHub issue body is canonical.
