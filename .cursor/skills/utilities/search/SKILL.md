---
name: search
description: "Embed query and search the FAISS index at index_path."
disable-model-invocation: true
---

Embed query and search the FAISS index at index_path.
query — natural-language question or search phrase.
index_path — directory containing index.faiss and meta.json written by embed().
top_k — maximum number of chunks to return (default 5).
Returns SearchResult with chunks ordered from most to least relevant.

through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: context_setup.context_index:ContextIndex
tool: search
```
.\tools.ps1 run -
