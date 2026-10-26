---
name: actions-partition
description: >-
  Split the given context into an index plus verbatim segments for each listed guidance. Fail if any new chunk misses a named entry the index required.
  paths: a file, a list of files, or a folder. Pass paths. This action reads them locally. Do not pass the corpus in context.
  context: in-process text. Leave this empty on an MCP call.
  mode: one_go, or the named partition mode.
  out_root: folder for the index and segments. Omit it to use the session path.
  
  guidance: the slugs you type, such as stories, clean-engineering-model, or bdd-behavior. A list runs this action once per slug. A module:Class ref is that slug after lookup. Any other string is text this action runs once.
---

Split the given context into an index plus verbatim segments for each listed guidance. Fail if any new chunk misses a named entry the index required.
paths: a file, a list of files, or a folder. Pass paths. This action reads them locally. Do not pass the corpus in context.
context: in-process text. Leave this empty on an MCP call.
mode: one_go, or the named partition mode.
out_root: folder for the index and segments. Omit it to use the session path.

guidance: the slugs you type, such as stories, clean-engineering-model, or bdd-behavior. A list runs this action once per slug. A module:Class ref is that slug after lookup. Any other string is text this action runs once.

Use MCP tool: `partition.partition(guidance: 'GuidanceArg', context: 'str' = '', mode: 'str' = 'one_go', out_root: 'str | None' = None, paths: 'list[str] | str | None' = None)`
