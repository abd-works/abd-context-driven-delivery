---
name: space-record-decisions-write-cdr
description: >-
  Write one Context Decision Record to the current session workpath .context/cdr/{NNNN}-{slug}.md.
  NNNN is the next sequential number under .context/cdr/. Creates the directory lazily.
  paths: a file, a list of files, or a folder. Pass paths. This action reads them locally. Do not pass the record body in content.
  content: in-process text. Leave this empty on an MCP call.
  slug: kebab-case short name (e.g. 'event-sourced-orders').
  Returns the resolved path. Call immediately when a qualifying decision crystallises - do not batch.
---

Write one Context Decision Record to the current session workpath .context/cdr/{NNNN}-{slug}.md.
NNNN is the next sequential number under .context/cdr/. Creates the directory lazily.
paths: a file, a list of files, or a folder. Pass paths. This action reads them locally. Do not pass the record body in content.
content: in-process text. Leave this empty on an MCP call.
slug: kebab-case short name (e.g. 'event-sourced-orders').
Returns the resolved path. Call immediately when a qualifying decision crystallises - do not batch.

Use MCP tool: `record-decisions.write_cdr(slug: 'str', content: 'str' = '', paths: 'list[str] | str | None' = None)`
