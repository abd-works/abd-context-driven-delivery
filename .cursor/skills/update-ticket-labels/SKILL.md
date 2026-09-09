---
name: update-ticket-labels
description: "Update ticket labels: add and/or remove comma-separated labels."
disable-model-invocation: true
---

Update ticket labels: add and/or remove comma-separated labels.

through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: workflow.workflow:Workflow
tool: update_ticket_labels
```
.\tools.ps1 run -
