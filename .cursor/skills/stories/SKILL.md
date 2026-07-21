---
name: stories
description: "Stories generator — multi-fidelity story maps and acceptance tests."
disable-model-invocation: true
---

# Stories

Run the manifest to load tools, actions, and instructions:

```
python -m tools manifest contexts.stories.stories:Stories
```

Follow `response.instructions` before doing anything else. Invoke tools via:

```
python -m tools run -
```
