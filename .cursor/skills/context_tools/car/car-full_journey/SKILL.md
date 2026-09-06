---
name: car-full_journey
description: "Provide guidance for in-character road stories at the current fidelity."
disable-model-invocation: true
---

Run the action on car at full_journey fidelity through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: context_tools.car.car:Car
context:
  fidelity: full_journey
action: generate
```
.\tools.ps1 run -
