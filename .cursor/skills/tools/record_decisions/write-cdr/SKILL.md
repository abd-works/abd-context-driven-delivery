Write one Context Decision Record to {root}/.context/cdr/{NNNN}-{slug}.md.
NNNN is the next sequential number under .context/cdr/. Creates the directory lazily.
content: full markdown following CDR-FORMAT.md (title + 1-3 sentence body; optional sections only when valuable).
slug: kebab-case short name (e.g. 'event-sourced-orders').
Returns the resolved path. Call immediately when a qualifying decision crystallises - do not batch.

Use MCP tool: `record-decisions.write_cdr(root: 'str', slug: 'str', content: 'str')`
