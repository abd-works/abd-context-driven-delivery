---
name: grill-context
description: "Grill a plan against codebase context — relentless interview with context-aware exploration."
disable-model-invocation: true
---

# GrillContext

Run the manifest to load tools, actions, and instructions:

```
python -m tools manifest grill_context.grill_context:GrillContext
```

Follow `response.instructions` before doing anything else. Invoke tools via:

```
python -m tools run -
```
