# Index

Build a **thin** sections index over the source at the given `context` path — enough to ground partitions, not a full exploration.

1. Read the source as **code or markdown** (no separate channel required).
2. Apply **contexts** plus **partition guidance** (`partition.md` in this context folder, or the base default when missing). Guidance names only **top-level artifacts**.
3. Infer a guiding structure from that lens. TODOs and rough names are fine.
4. Write **one** index file at `.context/{{self.toolset_name}}-index.md`
   (e.g. `.context/stories-index.md`, `.context/clean_engineering-index.md`).
   - If `out_root` is set, use `{out_root}/.context/{{self.toolset_name}}-index.md`.
5. Do **not** write segment files. Index produces only that one file.
6. Multiple contexts may each index the same corpus; filenames must not collide.

Keep depth thin: epic/module/BC (or equivalent) ground only — not full stories, full APIs, or deep BDD.
