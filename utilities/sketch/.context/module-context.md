# sketch — module context

## Purpose
`Sketcher` produces a rough, persisted draft of a formal artifact through an interactive grill loop before any generate step runs. It locates a sketch template via tiered discovery (caller-supplied → agent-dir convention → built-in default), writes interim `{slug}-sketch.md` files to the session docs dir after every two or three grill answers, and overwrites the same path on each refinement. Leaving a sketch only in chat is treated as a defect; the file under the docs dir is the working record.

## Seam
`Sketcher`

## Dependencies
`grill_context.grill_context`, `primitives.actions`, `tools.tool`, `sessions`

## Mechanism
Persist-on-draft cadence — `save_sketch` is called immediately on the first draft and again after every subsequent pair of grill answers; `find_template` uses tiered discovery so host toolsets can supply a domain-specific template alongside their module.
