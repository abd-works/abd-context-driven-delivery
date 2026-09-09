---
name: ticket-rules
description: "Read the repo's workflow rules that govern every ticket action."
disable-model-invocation: true
---

Read the repo's workflow rules that govern every ticket action.

through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: workflow.workflow:Workflow
tool: read_ticket_rules
```
.\tools.ps1 run -
