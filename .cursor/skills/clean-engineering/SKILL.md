---
name: clean-engineering
description: "Clean Engineering generator - multi-fidelity OO design and implementation."
disable-model-invocation: true
---

# CleanEngineering

Run the manifest to load tools, actions, and instructions:

```
python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
```

Follow `response.instructions` before doing anything else. Invoke tools by writing
the request to a YAML file (e.g. `_req.yaml`) and running:

```
python -m tools run _req.yaml
```

Delete the file after the call. Request format — `toolset` is the classname from
the manifest step above:

```yaml
toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
context:
  key: value      # constructor params (fidelity, path, session, …)
tool: <tool_name>   # or action: <action_name>
arguments:
  key: value
```

Read `examples/` before guessing any field shape.
