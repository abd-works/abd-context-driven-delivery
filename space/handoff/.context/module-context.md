# handoff — module context

## Purpose
Compacts the current agent session into a structured handoff document so a fresh agent can resume without re-reading the full chat. `Handoff` (`space/handoff`) writes `handoffs/handoff-{timestamp}.md` under `Session.current().session_path`. It does not open a session.

## Seam
`Handoff`

## Dependencies
`workspace`, `harness.agent_tools`, `tools.tool`

## Mechanism
`collect_session_state` assembles live state from the working folder (sketches, named artifacts, CDD sketch summary, grill-answer headings) and returns it as JSON. `preview_handoff` collects and renders that markdown without writing files or closing a sprint. `write_handoff` resolves the archive slug (`handoff-YYYY-MM-DD[-focus]`), persists content to both the archive and latest paths, and optionally closes the sprint session. `handoff_session` wraps a turn only when `workspace.current_work_session` is already set. `/backlog` uses `preview_handoff` so the GitHub issue body is canonical.
