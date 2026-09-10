---
name: handoff
description: "Compact the current session into a handoff document under the session working folder so a fresh agent can continue. Tailor the doc to {{next_focus}} when provided."
disable-model-invocation: true
---

Compact the current session into a handoff document under the session working folder so a fresh agent can continue. Tailor the doc to {{next_focus}} when provided.

If a work session is already open, open a turn for this handoff. Do not open a session.

Use MCP tool: `handoff.handoff_session(destination: 'str', next_focus: 'str' = '') -> 'str'`
