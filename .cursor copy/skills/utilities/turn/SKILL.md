---
name: turn
description: "Commit the current checkout with skill lineage (/turn)."
disable-model-invocation: true
---

Commit the current checkout with skill lineage (/turn).

        Fill context_tool, action, and utility from the skills/commands/prompts
        you used (best guess when unknown). Subject: a few folders or files —
        not an exhaustive list. Message: short description of what changed.

Use MCP tool: `turn.turn(*, context_tool: 'str' = '', action: 'str' = '', utility: 'str' = '', subject: 'str' = '', message: 'str' = '', root: 'str' = '', commit_message: 'str' = '') -> 'TurnCommit | None'`
