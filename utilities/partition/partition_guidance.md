{{scaffold}}

Each primary artifact must represent a mechanically distinct concept — not a chapter, heading, or TOC row from source.

## Must follow (read before indexing)
1. Read all **source context** in full.
2. Read **`{{slug}}.md` § Contexts** — artifact model; top-level structure, sub-groupings, and key rules.
3. Read **`templates/{{slug}}-sketch.md`** — sketch at the active fidelity.
4. Read **This file** — existing chunks and source spans are evidence.

## Index

### First pass (no index/chunks yet)

1. Skim corpus for the primary artifact described in the scaffold above.
2. Name them per the naming rules in the scaffold. Source chapters/files **contribute to** artifacts (many→one or one→many).
3. Under each, list thin secondary artifacts (TODOs OK).
4. Write `.context/{subject}-index.md` with the primary artifact as the primary rows; later segment creates chunks and the index points at them.

**Additive pass:** see partition_pipeline.md § Multi-pass / what a later pass does — open existing index, add columns per the scaffold hierarchy, do not delete prior columns.

### Done-check — fail if any box fails

- [ ] `{{slug}}.md` cited.
- [ ] Primary artifact count ≠ chapter / major-heading count (mirrored TOC = hard fail).
- [ ] No "1:1 with chapters" rationalization.

## Segment

Follow partition_pipeline.md § Segment (verbatim extract; additive). Hierarchy language must match `{{slug}}.md`; chapters are evidence only.
