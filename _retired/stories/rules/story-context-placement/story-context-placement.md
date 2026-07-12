---
rule: story-context-placement
kind: shape
fidelity: [shaping, discovery, exploration, specification, engineering]
artifact: story-context.md
scanner: story-context-placement-scanner.py
---

# story-context-placement

`story-context.md` is an on-request folder-level aggregate that sits at the top
of a story map (or at the top of a sub-epic being expanded). It stitches the
stories below it into one human-readable narrative that complements the
machine-readable spec files. It is not a default artifact in every folder and
must never appear at a leaf/story folder — a leaf has nothing left below it to
aggregate.

## The rule

Every `story-context.md` MUST:

1. Live at a folder that has at least one child sub-folder (epic root or
   sub-epic root — never a story-level leaf folder).
2. Start with an H1 title (typically the epic or sub-epic verb–noun).
3. Include a `**Status:**` line describing expansion state.
4. Include a `**Stories in scope:**` label followed by at least one bulleted
   entry naming a story below it.

## DO

- Place `story-context.md` at the epic root by default (top of the story map).
- Place it at a sub-epic root only when expanding just that branch in depth.
- Enumerate the stories it consolidates under `**Stories in scope:**`.

## DON'T

- Do not place `story-context.md` inside a leaf/story folder — the aggregate
  needs children below it.
- Do not omit the H1 title, `**Status:**`, or `**Stories in scope:**` labels.
- Do not treat it as a default per-folder artifact; it exists only where a
  human-readable roll-up is useful.
