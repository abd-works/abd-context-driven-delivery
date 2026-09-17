---
name: worksession-chat
description: "worksession-chat — list chat transcript paths attached to a work session."
disable-model-invocation: true
---

worksession-chat — list chat transcript paths attached to a work session.

        Reads the append-only annotated tag ``chat/session/{name}``. Omit ``name`` to
        use the current work session (or this session). Pass the kebab session name or
        ``session/...`` branch when looking up a closed session from another chat.

Use MCP tool: `work_session.worksession_chat(tools: 'list[Any] | None' = None, name: 'str' = '') -> 'list[str]'`
