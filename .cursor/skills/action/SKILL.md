---
name: action
description: "AgentWithActions generator — scaffold @toolset classes with @action recipes, bdd spec, and agent bdd spec."
disable-model-invocation: true
---

# AgentWithActions

From the repo root, set `PYTHONPATH` so category packages resolve (hybrid imports):

```powershell
$env:PYTHONPATH = "$PWD;$PWD\primitives;$PWD\utilities;$PWD\concepts"
```

Run the manifest to load tools, actions, and instructions:

```
python -m tools manifest primitives.actions.agent_with_actions:AgentWithActions
```

Follow `response.instructions` before doing anything else. Invoke tools via:

```
python -m tools run -
```
