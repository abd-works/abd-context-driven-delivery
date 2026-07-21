---
name: contexts
description: "Build or patch Context domains — scaffold @context toolsets."
disable-model-invocation: true
---

# Context

From the repo root, set `PYTHONPATH` so category packages resolve (hybrid imports):

```powershell
$env:PYTHONPATH = "$PWD;$PWD\primitives;$PWD\utilities;$PWD\contexts"
```

Run the manifest to load tools, actions, and instructions:

```
python -m tools manifest contexts.base.context:Context
```

Follow `response.instructions` before doing anything else. Invoke tools via:

```
python -m tools run -
```
