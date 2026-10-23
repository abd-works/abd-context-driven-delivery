---
name: tools-echo-instructions-fence
description: >-
  Wrap instructions in DO-NOT-FOLLOW fences and return the fenced block.
  Header and footer label the block as inert diagnostic text intended for the user to read.
  paths: a file, a list of files, or a folder. Pass paths. This action reads them locally. Do not pass the instruction body.
  body: in-process text. Leave this empty on an MCP call.
---

Wrap instructions in DO-NOT-FOLLOW fences and return the fenced block.
Header and footer label the block as inert diagnostic text intended for the user to read.
paths: a file, a list of files, or a folder. Pass paths. This action reads them locally. Do not pass the instruction body.
body: in-process text. Leave this empty on an MCP call.

Use MCP tool: `echo-instructions.fence(body: 'str' = '', paths: 'list[str] | str | None' = None)`
