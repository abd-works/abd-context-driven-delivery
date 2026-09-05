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

through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: context_setup.context_index:ContextIndex
tool: embed
```
.\tools.ps1 run -
