---
name: move-ticket
description: "Move a ticket to an exact board state, or to its next/previous state. Follow the repo workflow rules (read_ticket_rules)."
disable-model-invocation: true
---

Move a ticket to an exact board state, or to its next/previous state. Follow the repo workflow rules (read_ticket_rules).

through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: workflow.workflow:Workflow
tool: move_ticket
```
.\tools.ps1 run -
