---
name: record-decisions
description: "Offer and write Context Decision Records (CDRs) in .context/cdr/ as decisions crystallise."
disable-model-invocation: true
---

# RecordDecisions

Run the manifest to load tools, actions, and instructions:

```
python -m tools manifest record_decisions.record_decisions:RecordDecisions
```

Follow `response.instructions` before doing anything else. Invoke tools by writing
the request to a YAML file (e.g. `_req.yaml`) and running:

```
python -m tools run _req.yaml
```

Delete the file after the call. Request format — `toolset` is the classname from
the manifest step above:

```yaml
toolset: record_decisions.record_decisions:RecordDecisions
context:
  key: value      # constructor params (fidelity, path, session, …)
tool: <tool_name>   # or action: <action_name>
arguments:
  key: value
```

Read `examples/` before guessing any field shape.
