---
name: embed
description: "Read every segment markdown file listed in segments_paths, embed using the embedding provider,"
disable-model-invocation: true
---

Read every segment markdown file listed in segments_paths, embed using the embedding provider,
        and write a FAISS index to out_path/index.faiss with a metadata sidecar at out_path/meta.json.
        segments_paths — absolute paths to *-segment.md files produced by context tool partitions.
        out_path — directory where index.faiss and meta.json are written (created if absent).
        Returns EmbedResult with index_path, segment_count, and views_covered.

Use MCP tool: `context_index.embed(segments_paths: 'list[str]', out_path: 'str') -> 'EmbedResult'`
