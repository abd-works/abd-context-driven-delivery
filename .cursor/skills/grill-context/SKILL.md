---
name: grill-context
description: "Grill a plan against codebase context - relentless interview with context-aware exploration."
disable-model-invocation: true
---

# GrillContext

Run the manifest to load tools, actions, and instructions:

```
python -m tools manifest grill_context.grill_context:GrillContext
```

Follow `response.instructions` before doing anything else. Invoke tools by writing
the request to a YAML file (e.g. `_req.yaml`) and running:

```
python -m tools run _req.yaml
```

Delete the file after the call. Request format — `toolset` is the classname from
the manifest step above:

```yaml
toolset: grill_context.grill_context:GrillContext
context:
  key: value      # constructor params (fidelity, path, session, …)
tool: <tool_name>   # or action: <action_name>
arguments:
  key: value
```

Read `examples/` before guessing any field shape.
