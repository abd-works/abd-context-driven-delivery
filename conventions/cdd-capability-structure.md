---
description: Every CDD capability must have a .cdd-config.json, an agentic surface {capability}.md, and an API surface {capability}.py (or equivalent).
globs: **
---

A CDD capability is a folder that contains:

```
{capability}/
  .cdd-config.json       ← presence identifies this as a CDD capability
  {capability}.md        ← agentic surface: what it does, how to use it (section per action)
  {capability}.py        ← API surface: importable code (or .ts, .js, …)
```

The `{capability}.md` must follow the enforce pattern — one section per action, each pointing to a sub-file with `read in full →`.

A capability may contain sub-capabilities. Each sub-folder with its own `.cdd-config.json` is an independent capability.

See `cdd-capability/cdd-capability.md` for a concrete example.
