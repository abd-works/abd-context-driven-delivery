---
name: stories-scenarios
description: "Provide guidance for creating story maps, scenarios, and acceptance tests."
disable-model-invocation: true
---

Run the action on stories at scenarios fidelity through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: context_tools.stories.stories:Stories
context:
  fidelity: scenarios
action: generate
```
.\tools.ps1 run -
