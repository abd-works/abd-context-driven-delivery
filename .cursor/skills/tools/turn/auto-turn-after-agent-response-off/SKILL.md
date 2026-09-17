---
name: auto-turn-after-agent-response-off
description: "Disable `auto_turn` hook on `afterAgentResponse` (after agent response) for Turn."
disable-model-invocation: true
---

Disable the `auto_turn` hook on Cursor event `afterAgentResponse`.

Set `@hooks(disabled=True)` on `Turn` in `tools/workspace/workspace.py` so the hook server skips `auto_turn`.
