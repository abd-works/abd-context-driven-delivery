---
name: finish-turn
description: "finish_turn — close the hanging turn, or commit the current checkout if no work session."
disable-model-invocation: true
---

finish_turn — close the hanging turn, or commit the current checkout if no work session.

through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: workspace.workspace:Turn
tool: finish_turn
```
.\tools.ps1 run -
