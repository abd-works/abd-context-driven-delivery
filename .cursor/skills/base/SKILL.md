---
name: base
description: "Build or patch Context domains — scaffold @context toolsets (class Context + @context)."
disable-model-invocation: true
---

# Context

Run the manifest to load tools, actions, and instructions:

```
python -m tools manifest context_tools.base.context:Context
```

Follow `response.instructions` before doing anything else. Invoke tools via:

```
python -m tools run -
```
