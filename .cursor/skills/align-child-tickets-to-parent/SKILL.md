---
name: align-child-tickets-to-parent
description: "Align child tickets so no child is in a board column prior to its parent. Follow the repo workflow rules (read_ticket_rules)."
disable-model-invocation: true
---

Align child tickets so no child is in a board column prior to its parent. Follow the repo workflow rules (read_ticket_rules).

through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: workflow.workflow:Workflow
tool: align_child_tickets_to_parent
```
.\tools.ps1 run -
