---
name: agent-bdd
description: "Agent BDD generator — write agent specs against the agent() harness, composing vanilla bdd."
disable-model-invocation: true
---

# AgentBdd

Run the manifest to load tools, actions, and instructions:

```
python -m tools manifest agent_bdd.agent_bdd:AgentBdd
```

Follow `response.instructions` before doing anything else. Invoke tools via:

```
python -m tools run -
```
