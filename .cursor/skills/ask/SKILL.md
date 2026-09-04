---
name: ask
description: "Answer question using the FAISS index at index_path, citing sources."
disable-model-invocation: true
---

Answer question using the FAISS index at index_path, citing sources.
question={question}, index_path={index_path}.

through the tools cli

Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: context_setup.context_index:ContextIndex
action: ask
```
.\tools.ps1 run -
