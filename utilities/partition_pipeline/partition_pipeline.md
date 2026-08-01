# Partition

Orchestrate a thin partition of source material using this context's lens.

**Parameters**

- `context` — path to the corpus (markdown and/or code).
- `mode` — `one_go` (default) | `pause` | `index_only`.
- `out_root` — optional override for the index/segment root. **Default = the generator `active` resource** (index lands under `{active.path}/.context/`; chunks under `{active.path}/{module}/.context/`). Use `out_root` only for true sandbox forks — see **Multi-pass**.

**Session layout**

- Index (+ durable diagrams at session scope) → `{session.path}/.context/`
- Partitioned chunks → `{session.path}/{module}/.context/{leaf}-segment.md` (same tree as generated modules)
- Later generate puts code under `{session.path}/{module}/` — segment may create the module / `.context/` folders for chunks only.

**Flow (first pass that creates chunks)**

```
partition
    -> index      (lens rows + contributing span labels → {session.path}/.context/{subject}-index.md)
    -> segment    (verbatim chunks under {session.path}/{module}/.context/ … unless mode skips)
    -> verify_segment_completeness   (call the tool on new/repaired catalog chunks)
    -> index      (refresh: every chunk-bearing row points at its chunk path)
```

After segmenting, **call tool `verify_segment_completeness`**. Span-length match alone is a
false PASS. Completeness FAIL blocks story inventory until the chunk is repaired.

`{subject}` = corpus basename from the `context` path (file stem or directory name), **not** the skill/toolset name
(e.g. session `sandbox`, corpus `sandbox/HeroesHandbook.md` → `sandbox/.context/HeroesHandbook-index.md`).

1. Resolve output root: `out_root` if set, else the toolset **`active`** resource.
2. Run **index** on the given `context` (writes or updates `{session.path}/.context/{subject}-index.md`).
3. Then by `mode`:
   - **`one_go`** (default) — continue immediately to **segment** when new chunks are needed.
   - **`pause`** — stop after index; wait for the user before running **segment**.
   - **`index_only`** — stop after index; do not segment.
4. When segmenting, follow **segment** — extract/copy contributing source into **`{session.path}/{module}/.context/`**. Do not substitute paraphrased notes or API sketches for source text.
5. After new chunks exist, the index must **point at them** (chunk paths). Partition is incomplete while new chunk rows only cite corpus TOC labels.

Base behavior: read code or markdown. Guidance is `partition.md` in the context folder when present; otherwise determine top-level structure from user suggestion, context, skill-provided material, etc.

**Hard fail (lens):** when domain `partition.md` and/or `{domain}.md` § Contexts exist, that lens’s artifacts (epics / screens / subjects / modules / …) **must** appear correctly in the index. Mirroring corpus chapters, TOC, files, or types is a failed partition — stop and regroup.

---

## Multi-pass / multi-lens (hard) — ADD, do not replace

Partition is **cumulative**. Later passes (another skill, another lens, a refinement) **add** to the shared index and chunk set. They do **not** wipe the previous partition.

### Hard fails

| Forbidden | Required |
|-----------|----------|
| Delete or overwrite `{subject}-index.md` and rewrite from scratch | **Open the existing index** and **add** columns / mapping sections for the new lens |
| Delete, rename-away, or re-chunk existing `{module}/.context/*-segment.md` files | **Leave existing chunks intact**; map new lens labels **onto** those chunk paths |
| Replace a CE module index with a Stories-only index (or UX/BDD-only) | Keep prior columns (e.g. Module, Chunk, Role, Deps) and **add** Epic / Screen / Subject columns |
| Recopy the whole corpus into a second parallel chunk tree for the new lens | Prefer **many→one / one→many maps** from new artifacts → **existing** chunks |
| Use a new `out_root` just to avoid colliding with another skill | Default is **one** `{session.path}/.context/{subject}-index.md` + chunks under `{session.path}/{module}/.context/`; `out_root` only for true sandbox forks |

### What a later pass does

1. **Detect existing partition:** if `{session.path}/.context/{subject}-index.md` and/or module `*-segment.md` chunks already exist, treat this as an **additive** pass.
2. **Apply the current lens** (Stories epics, UX screens, BDD subjects, CE modules, …) per that domain’s `partition.md`.
3. **Update the index by addition:**
   - Add column(s) for the new lens (e.g. `Epic`, `Mid-epic` / grounding stories, `Screen`, `Subject`).
   - Map each new label to **already-partitioned chunk path(s)** (and/or prior lens row ids). One chunk may map to several epics/screens/subjects; one epic may span several chunks.
   - Preserve all prior columns and links.
4. **Segment only gaps:** create new `*-segment.md` files **only** for source spans the new lens needs that are **not** already covered by an existing chunk. Never rewrite an existing chunk’s body unless the user explicitly asked to repair that chunk.
5. **Done-check:** prior chunk links still resolve; new lens columns are populated; no prior row/column was removed for convenience.

### Example (CE then Stories)

After Clean Engineering, the index has Module + Chunk (+ role/deps). A later **Stories** pass **adds** columns — it does not replace modules with epics:

| Module | Chunk | Epic | Mid-epic / grounding stories |
|--------|-------|------|------------------------------|
| `checks` | `checks/.context/checks-segment.md` | `Resolve Check` | `Make Trait Check`, … |
| `character` | `character/.context/character-segment.md` | `Create Hero` | `Spend Power Points`, … |
| `powers/attack` | `powers/attack/.context/attack-segment.md` | `Use Power` | `Make Attack Effect`, … |

Same pattern for **UX** (add `Screen` / transitions mapped to chunks) and **BDD** (add `Subject` / `that`·`with` hints mapped to chunks).

### First pass vs additive pass

| Situation | Behavior |
|-----------|----------|
| No index and no module `*-segment.md` chunks yet | Full first pass: create index rows for this lens, extract chunks, point index at chunks |
| Index/chunks already exist | **Additive only** — new lens columns + maps; segment only uncovered spans |
| User explicitly says “repartition from scratch” | Only then may replace index/chunks (ask if ambiguous) |

# Index

Build or **extend** a thin sections index over the source at the given `context` path — enough to ground partitions, not a full exploration.

1. Read the source as **code or markdown** (no separate channel required).
2. Resolve output root: `out_root` if set, else the generator **`active`** resource. Docs go under `{active.path}/.context/`.
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
11. **Config (project-specific completeness knobs)** — put corpus/layout noise in the index, never in the partition kit. Under a `## Config` section include a machine block:

```markdown
## Config

<!-- partition-config
non-entry-headers:
  - NAME
  - COST
  - DESCRIPTION
short-body-pattern: \bRANKS?\b|\bPOINT
min-body-chars: 120
-->
```

- `non-entry-headers` — ALL-CAPS lines that are layout/table noise, **not** named entry headers
- `short-body-pattern` — optional regex; short bodies still count when it matches
- `min-body-chars` — optional completeness threshold (default 120)

`verify_segment_completeness` reads this from the partition root index next to the segment.

Keep depth thin: epic/module/BC/screen/subject ground only — not full stories, full APIs, or deep BDD.

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

1. Resolve output root: `out_root` if set, else the generator **`active`** resource.
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

11. **When done segmenting catalog chunks, call `verify_segment_completeness`** on each new or repaired `*-segment.md` that has a cost table / option list / feature catalog.
    - Put expected names in the segment (`<!-- expected-entries … -->`) or pass them as `expected_names`.
    - Project layout noise (`non-entry-headers`, `short-body-pattern`, `min-body-chars`) lives in the partition root index `<!-- partition-config -->` block — see `index.md` **Config**. Never hardcode project headers into the kit.
    - **Span length alone is a false PASS.** Completeness FAIL = hard fail — repair the chunk before story inventory.
