---
name: generator
description: "Build or patch Generator domains — scaffold @generator toolsets."
disable-model-invocation: true
---

# Generator

Run the manifest to load tools, actions, and instructions:

```
python -m tools manifest generator.generator:Generator
```

Follow `response.instructions` before doing anything else. Invoke tools via:

```
python -m tools run -
```
