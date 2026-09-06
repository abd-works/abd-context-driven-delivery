---
name: ux-front_end_code
description: "Provide guidance for creating IA, mockups, and front-end code."
disable-model-invocation: true
---

Run the action on ux at front_end_code fidelity through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: context_tools.ux.ux:Ux
context:
  fidelity: front_end_code
action: generate
```
.\tools.ps1 run -
