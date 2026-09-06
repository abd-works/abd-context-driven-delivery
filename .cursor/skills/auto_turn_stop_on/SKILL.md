---
name: auto_turn_stop_on
description: "Enable `auto_turn` hook on `stop` (stop) for Turn."
disable-model-invocation: true
---

Enable the `auto_turn` hook on Cursor event `stop`.

Flag file: `.context/hooks/turn/auto_turn_stop.enabled`

Create the flag file (empty is fine). The hook dispatcher runs `auto_turn` when this flag exists.

On `stop`, auto-turn stages all changes under the repo root (including new untracked files) and commits in one step.
