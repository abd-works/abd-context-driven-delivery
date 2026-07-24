---
name: iterate
description: "Iterate on formal generate output through a grill loop with validate + one fix pass."
disable-model-invocation: true
---

# Iterator

Run the manifest to load tools, actions, and instructions:

```
python -m tools manifest iterate.iterate:Iterator
```

Follow `response.instructions` before doing anything else. Invoke tools via:

```
python -m tools run -
```
