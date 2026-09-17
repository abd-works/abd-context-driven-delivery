---
name: update-ticket
description: "Update a ticket title and/or body; omitted values remain unchanged. Follow the repo workflow rules (read_ticket_rules)."
disable-model-invocation: true
---

Update a ticket title and/or body; omitted values remain unchanged. Follow the repo workflow rules (read_ticket_rules).

Use MCP tool: `workflow.update_ticket(ticket: 'str', title: 'str | None' = None, body: 'str | None' = None, workspace: 'str' = '') -> 'dict[str, str | int]'`
