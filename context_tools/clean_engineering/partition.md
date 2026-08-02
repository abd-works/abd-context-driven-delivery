CE often runs first; if CE runs **after** another lens, add columns only — do not delete Epic/Screen/Subject columns.

## Top-level artifacts (this lens)

**Modules** (rough public API; obvious mechanisms and their role) — including **nested** modules when a shared base exists (`clean_engineering.md` § Nested modules).

**Partition vs modules generate:** Partition owns the **initial module cut** (index rows + chunks) and **thin dependency notes**. The **modules** generate fidelity (next) owns the formal **one-way dependency graph**, **build order**, physical module folders, and thin term/class names — it **does not re-cut** or wipe this index.

A **module** is a CE boundary you could **pull out and implement independently** with a short seam and minimal dependencies — named with a **domain noun** (path form `parent/child` when nested). Not a handbook chapter, file, TOC row, or "everything that changes together in the book."

Key rules: `one-way-deps` — dependencies flow one direction only; no cycles; `domain-nouns-only` — module names are domain nouns or paths, never action verbs or `*Model`/`*Runtime` suffixes.

Use **abd-code-research** (not raw file scraping) when the corpus is code.

### Sizing grain (hard)

Ask for every candidate row: **Could a team implement this behind its seam while sibling modules are stubs?** (Depend on a **parent base** when nested — not on siblings.)

| Too small | Right | Too big |
|-----------|-------|---------|
| Pass-through / no independent lifecycle | One independently shippable seam | Blob that forces unrelated rules to land together |
| Exists only because a chapter/heading exists | Short API; thin deps listed | Flat megamodule when children should nest under a shared base |

**Prefer split + nest** when parts don't need each other's implementation but **do** share a base (e.g. effect types under `powers/` with `powers/effect`).
**Prefer flat** when there is no shared parent seam (`checks`, `abilities`).
**Prefer merge** only when there is no meaningful independent seam (not merely "same chapter").

Domain nouns / paths: `checks`, `powers/attack`, `conflicts/turns` — not `check_resolution`, `power_composition`.

## Index

### First pass (CE additions to base steps)

**Before step 1:** Run code-research **Pass 1** (Explorer): research paths + source notes. (Markdown corpora: skim structure + evidence spans; still do all steps.)

**After step 2:** Detect shared bases — if candidates duplicate mechanics, add a **parent path** and a **base child** (e.g. `powers/effect`) then nest specializations (`powers/attack`, …). Record **thin dependency** notes (parent base vs stubs); formal one-way deps wait for **modules** generate.

**Step 4 (extended):** List nested module paths (`powers/movement`); keep existing lens columns and add {{index_columns}}.

### Anti-patterns (do not ship)

| Anti-pattern | Instead |
|---|---|
| Flat `attack`, `movement`, … with duplicated effect rules | `powers/effect` + `powers/attack\|movement\|…` |
| Empty parent folder with no shared seam | Don't nest — keep flat |
| Child depends on sibling child | Depend on parent base only |
| Single `conflicts` / `gear` blob | `conflicts/turns\|actions\|conditions`; `gear/equipment\|…` |
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

## Segment (domain)

Chunks exist → map modules to them; first pass only → one segment per module.

For each **module path** in the index, write one segment under the module folder's `.context/`:
- Flat: `{module}/.context/{module}-segment.md`
- Nested: `{parent}/{child}/.context/{child}-segment.md`
- Parent base: `{parent}/{base}/.context/{base}-segment.md`

Shared base prose lands in the **parent-base** segment once; children get their specialization spans. Duplicate a span only when the index maps it to multiple modules. Refresh the index: each module row's **chunk** column/path points at its segment file.

Segment done-check: every new module chunk is a non-empty extract; no synthesized stubs; existing chunk files not rewritten unless explicit repair.
