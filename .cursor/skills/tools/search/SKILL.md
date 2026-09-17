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

Use MCP tool: `context_index.search(query: 'str', index_path: 'str', top_k: 'int' = 5) -> 'SearchResult'`
