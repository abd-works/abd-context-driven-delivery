---
name: auto_turn_stop_off
description: "Disable `auto_turn` hook on `stop` (stop) for Turn."
disable-model-invocation: true
---

Disable the `auto_turn` hook on Cursor event `stop`.

Flag file: `.context/hooks/turn/auto_turn_stop.enabled`

Remove the flag file so the dispatcher skips this handler.
