---
name: agent-bdd
description: "Agent BDD generator - write agent specs against the agent() harness, composing vanilla bdd."
disable-model-invocation: true
---

# AgentBdd

Run the manifest to load tools, actions, and instructions:

```
python -m tools manifest agent_bdd.agent_bdd:AgentBdd
```

Follow `response.instructions` before doing anything else. Invoke tools by writing
the request to a YAML file (e.g. `_req.yaml`) and running:

```
python -m tools run _req.yaml
```

Delete the file after the call. Request format — `toolset` is the classname from
the manifest step above:

```yaml
toolset: agent_bdd.agent_bdd:AgentBdd
context:
  key: value      # constructor params (fidelity, path, session, …)
tool: <tool_name>   # or action: <action_name>
arguments:
  key: value
```

Read `examples/` before guessing any field shape.
