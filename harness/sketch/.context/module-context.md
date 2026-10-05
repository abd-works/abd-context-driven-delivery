# sketch

## Purpose

Read a sketch document for one practice: find that practice's section and hand back its tree as indented lines, whatever heading depth the author used to write it.

## Seam (terms)

`SketchOutline`, `SketchLens`

## Constraint

A caller asks for one practice's section and reads the indented body it already understands. Callers do not reach for heading depths, fence markers, or section boundaries themselves — a second reader is a second notation, and the two drift.

## Dependencies (one-way)

none — a sketch is read from its own text

## Public API

- `SketchOutline(text, nesting_indent)` — the sketch, read at the indent width that practice's notation nests by.
- `SketchOutline.holds(lens)` — whether the sketch has a section for that practice.
- `SketchOutline.body_for(lens)` — that section as indented lines: each heading one level deeper than the heading above it, fenced detail keeping its own relative indentation under the heading that owns it. A sketch that names no lens is a single section, so the whole document is its body.
- `SketchLens.stories`, `.clean_engineering`, `.domain_driven_design`, `.user_experience`, `.behavior_driven_development`, `.every` — the practice sections a sketch can hold, each answering to its short marker (`ce:`) and its spelled-out heading (`clean engineering:`).
