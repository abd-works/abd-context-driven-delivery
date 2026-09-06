---
name: auto_turn_after_agent_response_off
description: "Disable `auto_turn` hook on `afterAgentResponse` (after agent response) for Turn."
disable-model-invocation: true
---

Disable the `auto_turn` hook on Cursor event `afterAgentResponse`.

Flag file: `.context/hooks/turn/auto_turn_after_agent_response.enabled`

Remove the flag file so the dispatcher skips this handler.
