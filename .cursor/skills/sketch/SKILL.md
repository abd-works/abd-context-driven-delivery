---
name: sketch
description: "Sketch a solution interactively before generating the formal artifact."
disable-model-invocation: true
---

# Sketcher

Run the manifest to load tools, actions, and instructions:

```
python -m tools manifest sketch.sketch:Sketcher
```

Follow `response.instructions` before doing anything else. Invoke tools via:

```
python -m tools run -
```
