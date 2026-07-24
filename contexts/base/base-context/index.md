# Index

Build or **extend** a thin sections index over the source at the given `context` path — enough to ground partitions, not a full exploration.

1. Read the source as **code or markdown** (no separate channel required).
2. Resolve output root: `out_root` if set, else the generator **`session`** resource. Docs go under `{session.path}/.context/`.
3. **If `{session.path}/.context/{subject}-index.md` already exists, open it and ADD — do not replace.** See base `partition.md` **Multi-pass / multi-lens**. Prior columns, chunk links, and rows stay unless the user explicitly asked to repartition from scratch.
4. Apply **contexts** plus **partition guidance** (`partition.md` in this context folder, or the base default when missing). Guidance names this lens’s **top-level artifacts**.
   - **Hard fail:** if the domain has `{domain}.md` § Contexts and/or `partition.md`, that lens’s artifacts **must** appear in the index (as rows on a first pass, or as **added columns / maps** on a later pass). Ignoring the lens or mirroring the corpus TOC/chapters/files is a failed partition — do not ship.
5. Infer guiding structure from that **lens** — not from the corpus TOC. Source chapters/files/paths (and existing **chunk paths**) are **evidence that contributes to** lens artifacts; artifacts are **not** 1:1 with chapters, files, or bookmarks.
6. Write **one** shared index at `{session.path}/.context/{subject}-index.md`, where **`{subject}` is the corpus basename** — **not** the context skill / toolset name.
   - Examples: session `sandbox`, corpus `sandbox/HeroesHandbook.md` → `sandbox/.context/HeroesHandbook-index.md`.
   - If `out_root` is set, use `{out_root}/.context/{subject}-index.md` (sandbox fork only — not the default way to run a second skill).
7. Do **not** write segment files here. On a first pass, **segment** creates chunks under `{session.path}/{module}/.context/`. On an additive pass, prefer mapping new lens labels to **existing** chunk paths; only call for new segments when spans are uncovered (see `segment.md`).
8. The skill lens lives in the index **content** (columns / sections), not a separate filename per skill. Multiple lenses share one `{subject}-index.md`.
9. **Anti-mirror check:** if this lens’s new artifact count equals the number of major source sections (chapters / top-level folders), regroup under the lens before writing. Do not justify mirrors with “the source seams already match.”
10. After chunks exist (first or gap fill), ensure the index **points at chunk paths** for every chunk-bearing unit. Later lenses add columns that **reference those same paths**.

Keep depth thin: epic/module/BC/screen/subject ground only — not full stories, full APIs, or deep BDD.
