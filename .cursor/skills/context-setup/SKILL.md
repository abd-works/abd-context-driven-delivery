---
name: context-setup
description: "ContextIndex — embed segments into a FAISS index and answer questions with citations."
disable-model-invocation: true
---

# ContextIndex

Run the manifest to load tools, actions, and instructions:

```
python -m tools manifest context_setup.context_index:ContextIndex
```

Follow `response.instructions` before doing anything else. Invoke tools by writing
the request to a YAML file (e.g. `_req.yaml`) and running:

```
python -m tools run _req.yaml
```

Delete the file after the call. Request format — `toolset` is the classname from
the manifest step above:

```yaml
toolset: context_setup.context_index:ContextIndex
context:
  key: value      # constructor params (fidelity, path, session, …)
tool: <tool_name>   # or action: <action_name>
arguments:
  key: value
```

Read `examples/` before guessing any field shape.
