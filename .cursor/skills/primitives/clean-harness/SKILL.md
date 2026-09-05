---
name: clean-harness
description: "Remove this Harness type's deploy files only — not the other IDE."
disable-model-invocation: true
---

Remove this Harness type's deploy files only — not the other IDE.

Required context params with no value: type. AskQuestion to collect each missing value before running.

through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: harness.harness:Harness
context:
  type: 
tool: clean
```
.\tools.ps1 run -
