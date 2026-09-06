---
name: turn
description: "Commit the current checkout with skill lineage (/turn)."
disable-model-invocation: true
---

Commit the current checkout with skill lineage (/turn).

Fill context_tool, action, and utility from the skills/commands/prompts
you used (best guess when unknown). Subject: a few folders or files —
not an exhaustive list. Message: short description of what changed.

through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: workspace.workspace:Turn
tool: turn
```
.\tools.ps1 run -
