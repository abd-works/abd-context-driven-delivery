---
name: capture-from-documents
description: "Capture documents from folder_path, partition through selected context tools, embed into one FAISS index."
disable-model-invocation: true
---

Capture documents from folder_path, partition through selected context tools, embed into one FAISS index.
        folder_path={folder_path}, indexers={indexers}, first={first}.
        Collaborators (compile-time references): Stories, CleanEngineering, Ddd, Ux, Partition.

Step 1 — call convert(folder_path) to convert every document to markdown.
        Inspect the returned structure_notes.  If any note shows heading_depth=0 and
        word_count > 200, note it for the user — the document may need a semantic re-pass
        before partitioning gives useful results (do not block; continue to Step 2).

Use MCP tool: `context_setup.capture_from_documents(folder_path: 'str', indexers: 'Optional[list[str]]' = None, first: 'str' = '') -> 'str'`
