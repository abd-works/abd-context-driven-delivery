---
name: context-setup-capture-from-documents
description: >-
  Capture documents from folder_path, partition through selected context tools, embed into one FAISS index.
  folder_path={folder_path}, indexers={indexers}, first={first}.
  Collaborators (compile-time references): Partition, ContextIndex.
---

Capture documents from folder_path, partition through selected context tools, embed into one FAISS index.
folder_path={folder_path}, indexers={indexers}, first={first}.
Collaborators (compile-time references): Partition, ContextIndex.

Use MCP tool: `context-setup.capture_from_documents(folder_path: 'str', indexers: 'Optional[list[str]]' = None, first: 'str' = '')`
