---
name: car-trip_outline
description: "Provide guidance for in-character road stories at the current fidelity."
disable-model-invocation: true
---

Run the action on car at trip_outline fidelity through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: context_tools.car.car:Car
context:
  fidelity: trip_outline
action: generate
```
.\tools.ps1 run -
