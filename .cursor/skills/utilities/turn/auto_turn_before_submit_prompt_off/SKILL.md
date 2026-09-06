---
name: auto_turn_before_submit_prompt_off
description: "Disable `auto_turn` hook on `beforeSubmitPrompt` (before submit prompt) for Turn."
disable-model-invocation: true
---

Disable the `auto_turn` hook on Cursor event `beforeSubmitPrompt`.

Flag file: `.context/hooks/turn/auto_turn_before_submit_prompt.enabled`

Remove the flag file so the dispatcher skips this handler.
