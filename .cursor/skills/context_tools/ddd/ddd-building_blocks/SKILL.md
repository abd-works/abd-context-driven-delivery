---
name: ddd-building_blocks
description: "Provide guidance for creating bounded contexts, building blocks, and tactics."
disable-model-invocation: true
---

Run the action on ddd at building_blocks fidelity through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: context_tools.ddd.ddd:Ddd
context:
  fidelity: building_blocks
action: generate
```
.\tools.ps1 run -
