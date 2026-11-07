# cdd_guidance/actions/partition
*Partition* splits a large source — a document set or a codebase — into an *index* and verbatim *segments*, so later work reads exactly the part of the source it needs instead of a summary. The index, `{subject}-index.md`, names every segment and the entries each must hold; a segment, `*-segment.md`, is one verbatim chunk of source, and it is complete only when every entry the index named for it is present with a body. Each practice partitions through its own lens: `partition.partition(guidance, paths)` (slash `/partition`) runs once per listed Guidance, guided by the practice's `partition.md` or its Overview.

The MCP tools `partition.index`, `partition.segment`, and `partition.verify_segment_completeness` write the index, write the segments, and fail a segment that drops a named entry.

- **Purpose:** Turn a large source into an index plus verbatim chunks that every later stage can cite, with a hard check that no named entry was lost.
- **Seam (terms):** Partition, `partition.partition`, `partition.index`, `partition.segment`, `partition.verify_segment_completeness`
- **Dependencies (one-way):** `harness/guidance_actions` (*GuidanceAction*, *GuidanceArg*), `harness/markdown` (`@markdown`), `harness/agent_tools`, `harness/installation`, `harness/mcp`

## Constraint

Pass the source by path; never put the corpus on an MCP call. Index by the practice's lens, not by the source's own table of contents. Judge a segment complete by its named entries, never by its length. Put project-specific completeness settings in the index's `<!-- partition-config -->` block, not in code. A later practice adds its columns to the shared index and segments; it never wipes or re-chunks what an earlier practice wrote.
