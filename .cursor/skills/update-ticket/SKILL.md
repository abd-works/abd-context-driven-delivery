---
name: update-ticket
description: "Update a ticket title and/or body; omitted values remain unchanged. Follow the repo workflow rules (read_ticket_rules)."
disable-model-invocation: true
---

Update a ticket title and/or body; omitted values remain unchanged. Follow the repo workflow rules (read_ticket_rules).

through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: workflow.workflow:Workflow
tool: update_ticket
```
.\tools.ps1 run -
