---
name: space-handoff-write-handoff
description: >-
  Write a handoff into the current session folder, .sessions/{session}/handoff-{timestamp}.md (.sessions/default/ with no named session).
  Returns the absolute path of the written file.
  paths: a file, a list of files, or a folder. Pass paths. This action reads them locally. Do not pass the handoff body in content.
  content: in-process text. Leave this empty on an MCP call.
---

Write a handoff into the current session folder, .sessions/{session}/handoff-{timestamp}.md (.sessions/default/ with no named session).
Returns the absolute path of the written file.
paths: a file, a list of files, or a folder. Pass paths. This action reads them locally. Do not pass the handoff body in content.
content: in-process text. Leave this empty on an MCP call.

Use MCP tool: `handoff.write_handoff(content: 'str' = '', paths: 'list[str] | str | None' = None)`
