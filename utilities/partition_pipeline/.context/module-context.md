# PartitionPipeline

**Purpose:** Thin, additive partition of source corpora into index + verbatim segments, with named-entry completeness on catalog chunks.

**Primary use case:** Call `partition` / `index` / `segment`; hard-fail new catalog chunks via `verify_segment_completeness`.

**Rationale:** Durable artifacts are resources — `PartitionIndex` (root index + project config) and `Segment` / `SegmentEntry` (chunks). Project-specific completeness knobs live in the index config block, never hardcoded in the kit.

**Seam:** `PartitionPipeline`, `PartitionIndex`, `Segment`, `SegmentEntry`

**Constraint:** Do not treat span length alone as completeness PASS. Do not hardcode corpus/project header lists in kit code — put them in `{subject}-index.md` `<!-- partition-config -->`. Later lenses must add to the shared index/chunks — they must not wipe or re-chunk existing segments.

## Public API

- `PartitionPipeline` — `partition`, `index`, `segment`, `verify_segment_completeness`, `partition_guidance`
- `PartitionIndex` — props: `path`, `text`, `completeness`; ops: `from_text`, `resolve_near`
- `SegmentCompletenessConfig` — `min_body_chars`, `non_entry_headers`, `short_body_pattern` (from index `<!-- partition-config -->`)
- `Segment` — props: `path`, `text`, `config`, `expected_names`, `has_expected_names`, `is_complete`; ops: `from_text`, `entries`, `completeness_report`
- `SegmentEntry` — props: `name`, `body`, `body_chars`, `status`, `is_complete`

**Dependencies:** (none)

**Mechanism:** Concrete mergeable kit (one test tier — no I*/impl split). Completeness loads nearby `PartitionIndex` config, then asks `Segment` for its report.
