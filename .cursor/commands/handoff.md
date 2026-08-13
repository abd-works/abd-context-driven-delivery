# Handoff

A context-tool skill/session is already in play. Run this companion toolset in
that frame (same path / session / workspace as the context tool):

```
python -m tools manifest handoff.handoff:Handoff
```

Follow `response.instructions`. Invoke via `_req.yaml` + `python -m tools run`:

```yaml
toolset: handoff.handoff:Handoff
context:
  path: <active context-tool path>
  session: <active session name>
action: <action from this companion's manifest>
```

Delete the request file after the call. Read `examples/` before guessing field shape.
