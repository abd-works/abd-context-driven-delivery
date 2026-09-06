---
name: stories-story_map
description: "Provide guidance for creating story maps, scenarios, and acceptance tests."
disable-model-invocation: true
---

Run the action on stories at story_map fidelity through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: context_tools.stories.stories:Stories
context:
  fidelity: story_map
action: generate
```
.\tools.ps1 run -
