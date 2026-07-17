---
name: diagnose
description: "Diagnose toolset — launch the disciplined bug-fixing loop as a non-blocking sub-agent."
disable-model-invocation: true
---

# Diagnose

Run the manifest to load tools, actions, and instructions:

```
python -m tools manifest diagnose.diagnose:Diagnose
```

Follow `response.instructions` before doing anything else. Invoke tools via:

```
python -m tools run -
```
