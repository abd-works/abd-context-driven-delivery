---
name: review-ticket-statuses
description: "List project tickets by board columns from left to right, optionally filtered. Follow the repo workflow rules (read_ticket_rules)."
disable-model-invocation: true
---

List project tickets by board columns from left to right, optionally filtered. Follow the repo workflow rules (read_ticket_rules).

through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: workflow.workflow:Workflow
tool: review_ticket_statuses
```
.\tools.ps1 run -
