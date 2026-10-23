---
name: actions-render
description: >-
  Convert already-generated content into format. Returns one result per guidance. After the conversion returns, follow place_rendered.
  format: the target channel, such as python, markdown, or drawio.
  paths: a file, a list of files, or a folder. Required on every call. Pass paths so this action reads locally. Do not pass the document body in content on MCP.
  content: in-process text when paths is empty. Leave this empty on an MCP call.
  source: the format content is already in. Use sketch for a sketch file. Otherwise markdown, python, typescript, java, javascript, json, or drawio. md is markdown. Omit source when content is already the current format.
  
  guidance: the slugs you type, such as stories, clean-engineering-model, or bdd-behavior. A list runs this action once per slug. A module:Class ref is that slug after lookup. Any other string is text this action runs once.
---

Convert already-generated content into format. Returns one result per guidance. After the conversion returns, follow place_rendered.
format: the target channel, such as python, markdown, or drawio.
paths: a file, a list of files, or a folder. Required on every call. Pass paths so this action reads locally. Do not pass the document body in content on MCP.
content: in-process text when paths is empty. Leave this empty on an MCP call.
source: the format content is already in. Use sketch for a sketch file. Otherwise markdown, python, typescript, java, javascript, json, or drawio. md is markdown. Omit source when content is already the current format.

guidance: the slugs you type, such as stories, clean-engineering-model, or bdd-behavior. A list runs this action once per slug. A module:Class ref is that slug after lookup. Any other string is text this action runs once.

Use MCP tool: `render.render(guidance: 'GuidanceArg', format: 'str', paths: 'list[str] | str', content: 'str' = '', source: 'str | None' = None)`
