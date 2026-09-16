---
name: ask
description: "Answer question using the FAISS index at index_path, citing sources."
disable-model-invocation: true
---

Answer question using the FAISS index at index_path, citing sources.
        question={question}, index_path={index_path}.

Step 1 — Derive a semantic query:
        Read question and formulate a concise search phrase that captures the core intent.
        No tool fires during this step.

Step 2 — call search(query, index_path) to retrieve the top ranked chunks.

Use MCP tool: `context_index.ask(question: 'str', index_path: 'str') -> 'str'`
