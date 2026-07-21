# Segment

Turn an approved (or just-written) index into **named segment files** — no folder tree for partitions.

1. Read the index file (`.context/{{self.toolset_name}}-index.md`, or the path the user / caller gave as the index).
2. Use **contexts** and **partition guidance** only to interpret top-level names in the index — do not deepen into a full generate.
3. For each top-level entry in the guiding structure, write a file named from that structure, e.g. `epic-context-segment.md`, `ordering-module-segment.md`.
   - Place files under `out_root` when that argument is set; otherwise next to the index.
4. Do **not** create module/epic/BC folder trees — filenames carry the structure.
5. Fill each segment only enough to hold the sourced span / notes for that partition; TODOs are fine.
