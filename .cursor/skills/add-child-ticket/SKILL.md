---
name: add-child-ticket
description: "Create a project ticket and attach it as a direct child of a parent issue. Follow the repo workflow rules (read_ticket_rules)."
disable-model-invocation: true
---

Create a project ticket and attach it as a direct child of a parent issue. Follow the repo workflow rules (read_ticket_rules).

through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: workflow.workflow:Workflow
tool: add_child_ticket
```
.\tools.ps1 run -
