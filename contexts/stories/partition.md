# Partition guidance — stories

**Hard fail** if the index/segments ignore this file **or** `stories.md` § Contexts (canonical model + shared rules). Soft “we mirrored the source TOC” is not allowed.

**Hard fail (multi-pass):** if an index/chunks already exist (e.g. from clean_engineering), **do not** replace them with a Stories-only index or re-chunk the corpus into epic-named files. **Add** Stories columns mapped to existing chunks — see base `partition.md` **Multi-pass / multi-lens**.

## Top-level artifacts (this lens)

**Epics** (+ thin mid-level grounding stories) — verb–noun capability activities (`StoryMap` → `Epic` → `SubEpic` → `Story` → `Scenario` per `stories.md`).

Not a source chapter, file, bookmark, handbook section, or CE module name used as an epic title.

## Must follow (read before indexing)

1. **`stories.md` § Contexts** — canonical model, verb–noun names, 4–9 children, behavioral outcomes, vocabulary traces to domain language; **`branch-on-mechanical-uniqueness`** and **`read-all-source-context-in-full`** (read segments in full; branch only on mechanical uniqueness — not catalog/requirements bullets).
2. **This file** — epic / mid-epic ground; source spans and **existing chunks** are evidence.
3. **`base-context/index.md`** + **`base-context/partition.md` Multi-pass** — shared `{subject}-index.md`; additive columns.

## Index

### First pass (no index/chunks yet)

1. Skim corpus; list candidate activities/capabilities stakeholders care about.
2. **Regroup under Stories lens:** name **epics** (verb–noun). Source chapters/files **contribute to** epics (many→one or one→many).
3. Under each epic, list thin grounding stories (verb–noun; TODOs OK) — not full scenarios yet.
4. Write `.context/{subject}-index.md` with Epic (+ mid-epic) as the primary rows; later segment creates chunks and the index points at them.

### Additive pass (index/chunks already exist — default after CE, UX, BDD, …)

1. **Open the existing** `.context/{subject}-index.md`. Keep every prior column (Module, Chunk, Role, Deps, Screen, Subject, …).
2. **Add** Stories columns, e.g. `Epic`, `Mid-epic` / grounding stories — **mapped to existing chunk paths** (and/or module rows). Example: `checks` chunk → Epic `Resolve Check`; several `powers/*` chunks → Epic `Use Power`.
3. Do **not** delete module/chunk rows to “make room” for epics. Epics overlay the partition; they do not replace it.
4. Only note a gap (and optionally gap-fill segment) when an epic needs source not covered by any existing chunk.

### Done-check — fail if any box fails

- [ ] Stories lens applied (`stories.md` cited).
- [ ] Epic and story names are **verb–noun**; actor not in the name; stakeholder-observable outcomes.
- [ ] Epic count ≠ chapter / major-heading count (mirrored TOC = hard fail).
- [ ] No “1:1 with chapters” rationalization.
- [ ] **If a prior partition existed:** prior columns and chunk links still present and valid; Stories data was **added**, not substituted.
- [ ] Every epic maps to ≥1 existing chunk path **or** a new gap-fill chunk (explicit).

### Anti-patterns (do not ship)

| Anti-pattern | Instead |
|--------------|---------|
| Wipe CE index; write epics-only | Add `Epic` / `Mid-epic` columns on the shared index |
| Re-chunk handbook into `create-hero-segment.md` when `character/.context/character-segment.md` exists | Map `Create Hero` → existing `character` chunk |
| One epic per chapter | Merge/split by **user activity / capability** |
| Epic name = “Chapter 2: Secret Origins” | Verb–noun epic, e.g. `Create Hero`, `Advance Hero` |
| Stories named after section headings | Verb–noun stories under the epic |

## Segment

Follow base `segment.md` (verbatim extract; **additive**).

- **Additive (chunks exist):** usually **no new files** — index maps epics → existing chunks. Gap-fill only for uncovered spans.
- **First pass only:** one segment per epic (`{epic-slug}-segment.md`) with verbatim contributing source; then index points at those chunks.
- Done-check: hierarchy language matches `stories.md`; chapters only as evidence; existing chunks untouched unless explicit repair.
