---
name: turn
description: "Commit the current checkout with context-tool, action, utility, subject, and message (/turn)."
disable-model-invocation: true
---

Commit the current checkout with skill lineage. Call this when a slice of work is done — there is no separate open step.

Fill in what you know from the skills, commands, or prompts you used (best guess when unknown):

- **context_tool** — context-tool skill (e.g. `stories`, `bdd`, `clean_engineering`)
- **action** — action skill (e.g. `generate`, `grill`, `sketch`, `validate`)
- **utility** — utility skill when one ran (e.g. `sub-agent`, `cli-agent`, `workflow`) — omit when none
- **subject** — a few folders or files touched (e.g. `sandbox/courier/.context`, `utilities/workspace`) — not every file
- **message** — short plain description of what changed

through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: workspace.workspace:Turn
tool: turn
arguments:
  context_tool: <skill slug>
  action: <skill slug>
  utility: <optional skill slug>
  subject: <few folders or files>
  message: <what changed>
```
.\tools.ps1 run -
