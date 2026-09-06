---
name: auto_turn_after_agent_response_on
description: "Enable `auto_turn` hook on `afterAgentResponse` (after agent response) for Turn."
disable-model-invocation: true
---

Enable the `auto_turn` hook on Cursor event `afterAgentResponse`.

Flag file: `.context/hooks/turn/auto_turn_after_agent_response.enabled`

Create the flag file (empty is fine). The hook dispatcher runs `auto_turn` when this flag exists.

On `afterAgentResponse`, auto-turn stages all changes under the repo root (including new untracked files) and commits after each agent reply.
