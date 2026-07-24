# Partition

Orchestrate a thin partition of source material using this context's lens.

**Parameters**

- `context` — path to the corpus (markdown and/or code).
- `mode` — `one_go` (default) | `pause` | `index_only`.
- `out_root` — optional override for the index/segment root. **Default = the generator `session` resource** (index lands under `{session.path}/.context/`; chunks under `{session.path}/{module}/.context/`). Use `out_root` only for true sandbox forks — see **Multi-pass**.

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

1. Resolve output root: `out_root` if set, else the toolset **`session`** resource.
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
