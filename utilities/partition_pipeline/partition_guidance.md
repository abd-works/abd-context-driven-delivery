**Hard fail** if the index/segments ignore this file **or** `{{domain_slug}}.md` § Contexts. Soft "we mirrored the source TOC / file list" is not allowed.

Multi-pass: see partition_pipeline.md § Multi-pass / multi-lens — add {{index_columns}} columns, do not replace or re-chunk.

## Must follow (read before indexing)

Read in this order — each shapes what the next means:

1. **`{{domain_slug}}.md` § Contexts** — learn the lens: what counts as a {{primary_artifact}}, naming rules, hierarchy, and key constraints. This determines what you are looking *for* before you touch the corpus.
2. **`templates/{{domain_slug}}-sketch.md`** — calibrate output fidelity: know how thin or rich each {{primary_artifact}} entry should be before you start writing.
3. **All source context in full** — read the whole corpus before naming anything; spans that belong together must not be split mid-concept.
4. **Existing index and chunks (if any)** — establish ground state: treat the open index as additive evidence; existing chunk paths are already-extracted segments, not candidates for re-cut.

Each {{primary_artifact}} must represent a mechanically distinct concept — not a chapter, heading, or TOC row.

## Index

### First pass (no index/chunks yet)

1. Skim corpus for **{{primary_artifact}}s** — {{skim_focus}}.
2. Name **{{primary_artifact}}s** ({{artifact_naming_rule}}). Source chapters/files **contribute to** {{primary_artifact}}s (many→one or one→many).
3. Under each **{{primary_artifact}}**, list thin {{secondary_artifact}} (TODOs OK).
4. Write `.context/{subject}-index.md` with **{{primary_artifact}}** as the primary rows; later segment creates chunks and the index points at them.

**Additive pass:** see partition_pipeline.md § Multi-pass / what a later pass does — open existing index, add {{index_columns}} columns mapped to existing chunks, do not delete prior columns.

### Done-check — fail if any box fails

- [ ] {{lens_name}} lens applied (`{{domain_slug}}.md` cited).
- [ ] {{primary_artifact}} count ≠ chapter / major-heading count (mirrored TOC = hard fail).
- [ ] No "1:1 with chapters" rationalization.
{{partition_done_checks}}

## Segment

Follow partition_pipeline.md § Segment (verbatim extract; additive). Hierarchy language must match `{{domain_slug}}.md`; chapters are evidence only.
