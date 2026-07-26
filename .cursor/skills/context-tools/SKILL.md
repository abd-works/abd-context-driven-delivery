---
name: context-tools
description: "Build or patch Context domains — scaffold @base_context_tool toolsets via CreateContextTool."
disable-model-invocation: true
---

# Context

From the repo root, set `PYTHONPATH` so category packages resolve (hybrid imports):

```powershell
$env:PYTHONPATH = "$PWD;$PWD\primitives;$PWD\utilities;$PWD\context_tools"
```

Run the manifest to load tools, actions, and instructions:

```
python -m tools manifest context_tools.base.create_context_tool.create_context_tool:CreateContextTool
```

Follow `response.instructions` before doing anything else. Invoke tools via:

```
python -m tools run -
```
