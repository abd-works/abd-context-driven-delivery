---
name: cdd-engineer
description: "Provide guidance for orchestrating CDD stages across stories, ddd, ux, clean_engineering, and bdd."
disable-model-invocation: true
---

Run the action on cdd at engineer fidelity through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: context_tools.cdd.cdd:Cdd
context:
  fidelity: engineer
action: generate
```
.\tools.ps1 run -
