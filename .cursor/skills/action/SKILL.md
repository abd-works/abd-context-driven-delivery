---
name: action
description: "AgentWithActions generator — scaffold @toolset classes with @action recipes, bdd spec, and agent bdd spec."
disable-model-invocation: true
---

# AgentWithActions

Run the manifest to load tools, actions, and instructions:

```
python -m tools manifest action.agent_with_actions:AgentWithActions
```

Follow `response.instructions` before doing anything else. Invoke tools via:

```
python -m tools run -
```
