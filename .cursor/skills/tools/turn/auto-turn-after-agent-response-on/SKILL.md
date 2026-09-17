---
name: auto-turn-after-agent-response-on
description: "Enable `auto_turn` hook on `afterAgentResponse` (after agent response) for Turn."
disable-model-invocation: true
---

Enable the `auto_turn` hook on Cursor event `afterAgentResponse`.

Set `@hooks(disabled=False)` (or drop `@hooks(disabled=True)`) on `Turn` in `tools/workspace/workspace.py`. The hook server runs `auto_turn` when the class is not disabled.

On `afterAgentResponse`, auto-turn stages all changes under the repo root (including new untracked files) and commits after each agent reply.
