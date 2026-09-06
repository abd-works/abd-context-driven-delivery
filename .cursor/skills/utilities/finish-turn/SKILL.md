---
name: finish-turn
description: "Legacy alias — use /turn instead."
disable-model-invocation: true
---

**Use `/turn` instead.** This skill remains for older recipes that still call `finish_turn`.

through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: workspace.workspace:Turn
tool: turn
arguments:
  context_tool: <skill slug>
  action: <skill slug>
  utility: <optional skill slug>
  subject: <few folders or files>
  message: <what changed>
```
.\tools.ps1 run -
