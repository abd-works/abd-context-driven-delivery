# grill_context — module context

## Purpose
`GrillContext` drives the codebase-aware interview loop used by sketch, iterate, and any other stage that needs to ground design decisions in existing context files. It scans a directory tree for context-named files and `.context/` folders, reads them on demand, and persists each resolved insight immediately to `grill-answers.md` under the session folder. The `grill_with_context` action enforces a strict prove-read gate: options are never presented until the relevant context files have been read and cited.

## Seam
`GrillContext`

## Dependencies
`primitives.actions`, `tools.tool`, `sessions`

## Mechanism
Prove-read gate — every question turn must name the context file(s) read and ground options in concrete terms from them before asking; skimming titles or relying on memory is treated as a defect.
