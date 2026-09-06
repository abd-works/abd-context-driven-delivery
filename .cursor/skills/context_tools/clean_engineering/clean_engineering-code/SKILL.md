---
name: clean_engineering-code
description: "Provide guidance for creating OO modules, models, and code."
disable-model-invocation: true
---

Run the action on clean_engineering at code fidelity through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
context:
  fidelity: code
action: generate
```
.\tools.ps1 run -
