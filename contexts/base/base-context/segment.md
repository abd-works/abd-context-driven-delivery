# Segment

Turn index guidance into **named segment files** under each **module folder’s `.context/`** by **extracting source chunks** — not synthesizing summaries, APIs, or generate-shaped notes.

Chunks share the **same directory tree** as later generate output (`{session.path}/{module}/`), parked as module-local docs under `.context/`.

## Additive rule (hard)

If module folders already have `*-segment.md` chunks for this corpus:

- **Do not** delete, empty, or rewrite existing `*-segment.md` files.
- **Do not** re-extract the whole corpus into a parallel tree for a new lens (Stories / UX / BDD / CE).
- **Do** leave existing chunks as the source of truth and let the **index** map new lens labels onto them.
- **Do** create **new** segment files only for **uncovered** spans the current lens needs (additive gap-fill).

Repartition-from-scratch of chunks requires an **explicit** user request.

## Steps

1. Resolve output root: `out_root` if set, else the generator **`session`** resource.
2. Read the index file (`{session.path}/.context/{subject}-index.md` for the corpus, or the path the user / caller gave). `{subject}` is the corpus basename — not the skill/toolset name.
3. If chunks already cover the needed spans, **skip extract** for those rows; ensure the index points at the existing paths (and any new lens columns map to them). Stop here for covered material.
4. Open the **same source corpus** the index describes. Use **contexts** and **partition guidance** only to interpret **which uncovered spans** still need a chunk — do not deepen into a full generate.
5. For each **new** chunk to create, write under the **module path** from the index row:
   - Default: `{session.path}/{module}/.context/{leaf}-segment.md` (or `{out_root}/{module}/.context/…` when `out_root` is set).
   - **`{module}`** = index row path (`checks`, `powers/attack`, …).
   - **`{leaf}`** = last path segment (`checks`, `attack`, …).
   - **Flat row** `checks` → `{session.path}/checks/.context/checks-segment.md`
   - **Nested row** `powers/attack` → `{session.path}/powers/attack/.context/attack-segment.md` (create parent folders as needed)
   - Later-lens gap fills use the same naming rules for the unit being chunked (module / epic / screen / subject) — never overwrite a different lens’s existing file.
6. **Body = verbatim source.** Copy the contributing handbook/code prose for that row — **full text of those spans**, not a paraphrase, principle list, or rough-API write-up. A short header (path + span labels / line or heading anchors) is fine; the payload must be the chunked source.
7. When one source span contributes to **several** index units, either copy into each new chunk **or** (preferred once a chunk exists) point multiple index mappings at the **same** existing chunk. Prefer whole heading sections over torn mid-paragraph cuts.
8. **Create the module folder + `.context/`** as needed to hold the chunk. Do **not** generate code, APIs, or module-context prose here — only the extracted `*-segment.md`. Later generate owns source layouts inside `{session.path}/{module}/`.
9. Optional thin TODOs at the end (missing span, ambiguous cut) are fine. Do **not** replace the extract with invented participants/flow/API sections — that is generate territory.
10. **Update the index so chunk-bearing units point at chunk paths.** After any new segments exist, refresh `{session.path}/.context/{subject}-index.md`: chunk column/links for new or existing files; **preserve** all prior columns. Hard fail if a previously valid chunk link was removed or a required new chunk path is missing on disk.
