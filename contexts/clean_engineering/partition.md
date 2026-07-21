# Partition guidance — clean_engineering

Top-level artifacts: **modules** (rough public API; obvious mechanisms and their role).

Use **abd-code-research** (not raw file scraping) when the corpus is code.

## Index (Pass 1 — Explorer)

1. Run code-research **Pass 1** (Explorer): research paths + source notes.
2. Apply the CE lens: **group and name modules** — index rows are modules, not 1:1 research paths.
3. Research paths **contribute to** modules (many paths may feed one module). Record that mapping in the index.
4. Write the index at the usual path: `.context/clean_engineering-index.md` (same naming as every concept — do not rename to `research-paths.md`).

Keep it thin: module list, contributing paths/evidence hints, rough public API / obvious mechanisms. TODOs fine.

## Segment (Pass 2 — Deep Dive)

1. For each module in the index, run code-research **Pass 2** depth on the paths that contribute to that module.
2. Write **one** segment file per module in Pass 2 deep-dive shape (principles/patterns, file structure, participants, flow, walkthrough) — not a raw markdown extract of source.
3. File **naming** is the same as every concept: named from the guiding structure (e.g. `{module}-segment.md`). Nothing CE-special.
