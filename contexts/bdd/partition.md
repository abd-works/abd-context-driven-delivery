# Partition guidance — bdd

**Hard fail** if the index/segments ignore this file **or** `bdd.md` § Contexts (hierarchy shape + shared rules). Soft “we mirrored the source TOC / class list” is not allowed.

**Hard fail (multi-pass):** if an index/chunks already exist, **do not** replace them with a BDD-only index or re-chunk into subject-named files. **Add** Subject / `that`·`with` columns mapped to existing chunks — see base `partition.md` **Multi-pass / multi-lens**.

## Top-level artifacts (this lens)

**Subjects** — domain things, states, or observable conditions (top-level `describe`s per `bdd.md`). Thin: subject + candidate `that` / `with` + TODOs. Not full `it should` suites.

A subject is **never** a manager, hub, runner, service, decorator symbol, package, chapter, file, or CE module path used as a describe title.

## Must follow (read before indexing)

1. **`bdd.md` § Contexts** — hierarchy shape; plain-English subjects; usage order; `state-not-when`; nest-by-enabling-events.
2. **`sketch-template.md`** — usage-order subjects before implementation detail.
3. **This file** + **`base-context/partition.md` Multi-pass** — shared `{corpus}-index.md`; additive columns. (`{corpus}` = corpus basename, not a BDD describe subject.)

## Index

### First pass (no index/chunks yet)

1. Skim for **observable domain behaviors**, not chapter/type names.
2. Name top-level **subjects** in **usage order**; optional `that` / `with` candidates.
3. Write `.context/{corpus}-index.md`. Later segment creates chunks and the index points at them.

### Additive pass (index/chunks already exist)

1. **Open the existing** index; keep prior columns (Module, Chunk, Epic, Screen, …).
2. **Add** `Subject` (+ `that` / `with` hints) **mapped to existing chunk path(s)**.
3. Do not delete prior lens data. Gap-fill segment only for uncovered spans.

### Done-check — fail if any box fails

- [ ] BDD lens applied (`bdd.md` cited).
- [ ] Subjects are plain-English domain observables — no internals/`@…`.
- [ ] Order is a usage story, not TOC/package order; nest hints use `that`/`with`, never `when`.
- [ ] Subject count ≠ chapter / major-heading / top-level-type count.
- [ ] **If a prior partition existed:** prior columns/chunk links intact; BDD data was **added**, not substituted.
- [ ] Every subject maps to ≥1 existing chunk **or** an explicit gap-fill chunk.

### Anti-patterns (do not ship)

| Anti-pattern | Instead |
|--------------|---------|
| Wipe shared index for subjects-only | Add Subject columns mapped to existing chunks |
| Re-chunk whole corpus per subject when chunks exist | Map subjects → existing `{module}/.context/*-segment.md` |
| One subject per chapter or class | Subject = **what is observed** |
| `SessionLog` / `@log marker` | Plain-English subject |

## Segment

Follow base `segment.md` (verbatim; **additive**). Chunks exist → map subjects to them; first pass only → `{subject-slug}-segment.md` extracts. Existing chunks untouched unless explicit repair.
