# handoff — module context

## Purpose
Compacts the current agent session into a structured handoff document so a fresh agent can resume without re-reading the full chat. `Handoff` collects generator state, grilling progress, and CDD sketch summaries from the session folder, then writes two files: a date-stamped archive under `handoffs/` and a stable `handoff-latest.md` pointer at the docs root. When the destination is a named sprint under `sessions/`, it also closes the `Session` record.

## Seam
`Handoff`

## Dependencies
`sessions`, `primitives.actions`, `tools.tool`

## Mechanism
`collect_session_state` assembles live state from the working folder (sketches, named artifacts, CDD sketch summary, grill-answer headings) and returns it as JSON. `write_handoff` resolves the archive slug (`handoff-YYYY-MM-DD[-focus]`), persists content to both the archive and latest paths, and optionally closes the sprint session.
