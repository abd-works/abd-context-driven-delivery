---
name: ux-mockup
description: "Provide guidance for creating IA, mockups, and front-end code."
disable-model-invocation: true
---

Run the action on ux at mockup fidelity through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: context_tools.ux.ux:Ux
context:
  fidelity: mockup
action: generate
```
.\tools.ps1 run -
