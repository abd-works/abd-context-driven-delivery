---
name: bdd
description: "BDD generator — multi-fidelity behavior skeletons and development."
disable-model-invocation: true
---

# Bdd

Run the manifest to load tools, actions, and instructions:

```
python -m tools manifest bdd.bdd:Bdd
```

Follow `response.instructions` before doing anything else. Invoke tools via:

```
python -m tools run -
```
