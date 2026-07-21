---
name: handoff
description: "Handoff — compact the current session so a fresh agent can continue."
disable-model-invocation: true
---

# Handoff

Run the manifest to load tools, actions, and instructions:

```
python -m tools manifest handoff.handoff:Handoff
```

Follow `response.instructions` before doing anything else. Invoke tools via:

```
python -m tools run -
```
