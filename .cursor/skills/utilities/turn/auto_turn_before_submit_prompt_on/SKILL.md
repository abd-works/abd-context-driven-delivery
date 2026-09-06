---
name: auto_turn_before_submit_prompt_on
description: "Enable `auto_turn` hook on `beforeSubmitPrompt` (before submit prompt) for Turn."
disable-model-invocation: true
---

Enable the `auto_turn` hook on Cursor event `beforeSubmitPrompt`.

Flag file: `.context/hooks/turn/auto_turn_before_submit_prompt.enabled`

Create the flag file (empty is fine). The hook dispatcher runs `auto_turn` when this flag exists.
