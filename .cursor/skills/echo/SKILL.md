---
name: echo
description: "Echo — print an action's wrapped instructions inside a DO-NOT-FOLLOW fence for inspection."
disable-model-invocation: true
---

# Echoer

Run the manifest to load tools, actions, and instructions:

```
python -m tools manifest echo.echo:Echoer
```

Follow `response.instructions` before doing anything else. Invoke tools via:

```
python -m tools run -
```
