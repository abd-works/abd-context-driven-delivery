# handoff — module context

## Purpose
Compacts the current agent session into a structured handoff document so a fresh agent can resume without re-reading the full chat. `Handoff` is a **utility** (`utilities/handoff`), not a lifecycle action. It does **not** open a work session. If a work session is already open, it opens and finishes a turn; otherwise it just writes the files.

## Seam
`Handoff`

## Dependencies
`workspace`, `primitives.actions`, `tools.tool`

## Mechanism
`collect_session_state` assembles live state from the working folder (sketches, named artifacts, CDD sketch summary, grill-answer headings) and returns it as JSON. `write_handoff` resolves the archive slug (`handoff-YYYY-MM-DD[-focus]`), persists content to both the archive and latest paths, and optionally closes the sprint session. `handoff_session` wraps a turn only when `workspace.current_work_session` is already set.
