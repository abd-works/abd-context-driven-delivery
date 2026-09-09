---
name: tickets
description: "Manage project tickets from {{request}}."
disable-model-invocation: true
---

Manage project tickets from {{request}}.

Start by calling read_ticket_rules and follow every rule it returns; the repo's
rules override defaults. Display each available ticket tool name and purpose
before acting. Then review ticket statuses so board state and left-to-right
column order are known. Then call only the tool needed to move a ticket, add a
child ticket, merge a completed child into its parent, update a ticket, update
labels, align children to parent, or report board status. Never infer a ticket
number when the request is ambiguous.

through the tools cli

Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: workflow.workflow:Workflow
action: manage_tickets
```
.\tools.ps1 run -
