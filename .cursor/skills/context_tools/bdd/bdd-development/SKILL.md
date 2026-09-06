---
name: bdd-development
description: "Provide guidance for creating behavior skeletons and development tests."
disable-model-invocation: true
---

Run the action on bdd at development fidelity through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: context_tools.bdd.bdd:Bdd
context:
  fidelity: development
action: generate
```
.\tools.ps1 run -
