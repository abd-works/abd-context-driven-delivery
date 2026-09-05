---
name: model
description: "Set the preferred IDE/CLI model for this work session (slash ``/model``)."
disable-model-invocation: true
---

Set the preferred IDE/CLI model for this work session (slash ``/model``).

Persist under ``.context/sessions/{session}/model``. When no session is open,
use the root-repo ``sessions/default`` folder. CliAgent and SubAgent read this
value when present. Never set disable-model-invocation.

through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: workspace.workspace:Workspace
action: model
```
.\tools.ps1 run -
