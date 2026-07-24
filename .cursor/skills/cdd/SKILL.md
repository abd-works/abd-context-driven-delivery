---
name: cdd
description: "CDD orchestrator — stage menu across stories, ddd, ux, clean_engineering, bdd."
disable-model-invocation: true
---

# Cdd

Run the manifest to load tools, actions, and instructions:

```
python -m tools manifest context_tools.cdd.cdd:Cdd
```

Follow `response.instructions` before doing anything else. Invoke tools via:

```
python -m tools run -
```
