# Partition guidance — ux

**Hard fail** if the index/segments ignore this file **or** `ux.md` § Contexts (canonical model + shared rules). Soft “we mirrored the source TOC / screen list in the PDF” is not allowed.

**Hard fail (multi-pass):** if an index/chunks already exist, **do not** replace them with a UX-only index or re-chunk into screen-named files. **Add** Screen / Interaction / Transition columns mapped to existing chunks — see base `partition.md` **Multi-pass / multi-lens**.

## Top-level artifacts (this lens)

- **Screens** (domain / user language)
- **Interactions and transitions** (list only)

UxMap ground per `ux.md` — not chapters, files, bookmarks, or CE module names used as screen titles.

## Must follow (read before indexing)

1. **`ux.md` § Contexts** — canonical model; `tab-states-are-separate-screens`; `screen-names-use-domain-terms`; `screen-story-budget`.
2. **This file** — screens + interaction/transition lists only at partition depth.
3. **`base-context/index.md`** + **`base-context/partition.md` Multi-pass** — shared index; additive columns.

## Index

### First pass (no index/chunks yet)

1. Skim corpus for user-facing goals, places, and moves — not chapter titles.
2. Name **screens**; list **transitions** and key **interactions**. Source chapters contribute to screens.
3. Write `.context/{subject}-index.md` (IA-thin). Later segment creates chunks and the index points at them.

### Additive pass (index/chunks already exist)

1. **Open the existing** index; keep prior columns (Module, Chunk, Epic, Subject, …).
2. **Add** `Screen` (+ interaction/transition lists or columns) **mapped to existing chunk path(s)**.
3. Do not delete prior lens data. Gap-fill segment only for uncovered spans.

### Done-check — fail if any box fails

- [ ] UX lens applied (`ux.md` cited).
- [ ] Screen names use domain / user language; not chapter titles.
- [ ] Tab-like alternate states are separate screens when implied.
- [ ] Screen count ≠ chapter / major-heading count.
- [ ] No control/region detail beyond named screens.
- [ ] **If a prior partition existed:** prior columns/chunk links intact; UX data was **added**, not substituted.
- [ ] Every screen maps to ≥1 existing chunk **or** an explicit gap-fill chunk.

### Anti-patterns (do not ship)

| Anti-pattern | Instead |
|--------------|---------|
| Wipe shared index for screens-only | Add Screen columns mapped to existing chunks |
| Re-chunk whole corpus per screen when chunks exist | Map screens → existing `{module}/.context/*-segment.md` |
| One screen per chapter | Screens = **places users work** |
| Transition list = TOC order | Transitions = **user navigation** |

## Segment

Follow base `segment.md` (verbatim; **additive**). Chunks exist → map screens to them; first pass only → `{screen}-segment.md` extracts. Existing chunks untouched unless explicit repair.
