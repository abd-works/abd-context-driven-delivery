# grill_context — module context

## Purpose
`GrillContext` drives the codebase-aware interview loop used by sketch, iterate, and any other stage that needs to ground design decisions in existing context files. It scans a directory tree for context-named files and `.context/` folders, reads them on demand, and persists each resolved insight immediately to `grill-answers.md` under the session folder. The `grill_with_context` action enforces a strict prove-read gate: options are never presented until the relevant context files have been read and cited. `grill(tools)` is the host grill body (open, record decisions, grill_with_context, generate) run once per passed context tool via inherited `AgenticToolset.context_tools`. `/grill` invokes this toolset — not each context tool's host `grill`.

## Seam
`GrillContext`

## Dependencies
`primitives.actions`, `tools.tool`, `sessions`

## Public API
- `explore_context_files`, `read_context_file`, `write_grill_answer`
- `grill_with_context(plan)`
- `grill(tools)` — host grill body once per passed context tool

## Mechanism
Prove-read gate — every question turn must name the context file(s) read and ground options in concrete terms from them before asking; skimming titles or relying on memory is treated as a defect.
