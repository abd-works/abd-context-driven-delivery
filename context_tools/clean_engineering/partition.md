# Partition guidance — clean_engineering

Top-level artifacts: **modules** (rough public API; obvious mechanisms and their role) — including **nested** modules when a shared base exists (`clean_engineering.md` Nested modules).

**Partition vs modules generate:** Partition owns the **initial module cut** (index rows + chunks) and **thin dependency notes**. The **modules** generate fidelity (next) owns the formal **one-way dependency graph**, **build order**, physical module folders, and thin term/class names — it **does not re-cut** or wipe this index.

A **module** is a CE boundary you could **pull out and implement independently** with a short seam and minimal dependencies — named with a **domain noun** (path form `parent/child` when nested). Not a handbook chapter, file, TOC row, or “everything that changes together in the book.”

Use **abd-code-research** (not raw file scraping) when the corpus is code.

**Multi-pass:** CE often runs first and owns module rows + chunk files. Later Stories/UX/BDD passes **add columns** mapped to those chunks — they must not wipe this index. If CE runs **after** another lens, **add** Module / Chunk / Role / Deps columns (and gap-fill module chunks only for uncovered seams); do **not** delete Epic/Screen/Subject columns. See base `partition.md` **Multi-pass / multi-lens**.

## Sizing grain (hard)

Ask for every candidate row: **Could a team implement this behind its seam while sibling modules are stubs?** (Depend on a **parent base** when nested — not on siblings.)

| Too small | Right | Too big |
|-----------|-------|---------|
| Pass-through / no independent lifecycle | One independently shippable seam | Blob that forces unrelated rules to land together |
| Exists only because a chapter/heading exists | Short API; thin deps listed | Flat megamodule when children should nest under a shared base |

**Prefer split + nest** when parts don’t need each other’s implementation but **do** share a base (e.g. effect types under `powers/` with `powers/effect`).  
**Prefer flat** when there is no shared parent seam (`checks`, `abilities`).  
**Prefer merge** only when there is no meaningful independent seam (not merely “same chapter”).

Domain nouns / paths: `checks`, `powers/attack`, `conflicts/turns` — not `check_resolution`, `power_composition`.

## Index (Pass 1 — Explorer)

1. Run code-research **Pass 1** (Explorer): research paths + source notes. (Markdown corpora: skim structure + evidence spans; still do steps 2–6.)
2. Apply the CE lens: name modules by independent seams — **not** 1:1 research paths/chapters.
3. **Detect shared bases:** if several candidates duplicate the same mechanics, add a **parent path** and a **base child** (e.g. `powers/effect`) then nest specializations (`powers/attack`, …).
4. Research paths **contribute to** modules (many→one or one→many). Record mapping + **thin dependency** notes (parent base vs stubs). Formal one-way deps + topological build order wait for **modules** generate.
5. Write or **extend** `.context/{subject}-index.md` (`{subject}` = corpus basename). List nested modules with path names (`powers/movement`). If the index already has other lens columns, **keep them** and add Module / Chunk / Role / Deps.
6. **Done-check (fail if any fail):**
   - [ ] Every module row is an independently implementable domain-noun seam (path OK).
   - [ ] Shared mechanics appear **once** under a parent base — not copy-pasted into every sibling.
   - [ ] Nested children depend on **parent base**, not on sibling children.
   - [ ] Each module row states rough public API and thin deps (hints only — modules generate formalizes).
   - [ ] Module count ≠ chapter/major-heading count (mirrored TOC = fail).
   - [ ] No “1:1 with chapters” rationalization.
   - [ ] No flat megamodule that should be a nest (`powers`, `conflicts`, `gear` without children).
   - [ ] **If a prior partition existed:** prior lens columns/links intact; CE data was **added** or first-created, not substituted by wiping others.

Keep it thin: module list (nested paths), contributing paths, rough API, deps, TODOs.

### Anti-patterns (do not ship)

| Anti-pattern | Instead |
|--------------|---------|
| Flat `attack`, `movement`, … with duplicated effect rules | `powers/effect` + `powers/attack|movement|…` |
| Empty parent folder with no shared seam | Don’t nest — keep flat |
| Child depends on sibling child | Depend on parent base only |
| Single `conflicts` / `gear` blob | `conflicts/turns|actions|conditions`; `gear/equipment|…` |
| Action-named or `*Model`/`*Runtime` labels | Domain nouns / paths |

### Example (rules handbook)

```
powers/effect          shared rank/duration/descriptors/activate
powers/attack|control|defense|movement|sensory|general
powers/extras|flaws
conflicts/turns|actions|conditions
gear/equipment|headquarters|vehicles
checks                 flat — no shared parent needed
```

## Segment (Pass 2 — extract chunks)

**Segment is chunking, not generate.** Follow base `segment.md`: copy contributing **source text** into each module’s segment file.

1. For each **module path** in the index, locate the contributing spans recorded in the index (heading ranges / files / symbols).
2. Write one segment under the **module folder’s `.context/`** (same tree as generate):
   - Flat: `{module}/.context/{module}-segment.md` (e.g. `checks/.context/checks-segment.md`)
   - Nested: `{parent}/{child}/.context/{child}-segment.md` (e.g. `powers/attack/.context/attack-segment.md`)
   - Parent base: `{parent}/{base}/.context/{base}-segment.md` (e.g. `powers/effect/.context/effect-segment.md`)
3. **Markdown (or other prose) corpora:** paste the **verbatim** contributing sections into the segment (short header OK). Do **not** replace them with principles / participants / flow / rough-API deep-dives — those belong to later **generate**.
4. **Code corpora:** still extract the contributing source (files or contiguous symbol blocks) into the segment. Use abd-code-research only to **find** spans; the segment body remains the sourced text (plus minimal anchors), not a rewritten design note.
5. Shared base prose (e.g. effect cost/activate protocol) lands in the **parent-base** segment once; children get their specialization spans. Duplicate a span into multiple segments only when the index maps it to multiple modules.
6. Segment done-check: every **new** module chunk is a non-empty extract; nested child files hold child spans (not sibling catalogs); no synthesized stubs; **existing** chunk files not rewritten unless explicit repair.
7. **Refresh the index:** each module row’s **chunk** column/path points at its segment file under `{module}/.context/` (flat or nested). Preserve other lens columns. Fail if the index still only lists chapter labels with no chunk paths for module rows.
8. Additive later lenses map onto these chunk paths — CE must not require exclusive ownership of the index file.
