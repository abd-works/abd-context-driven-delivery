---
name: move-ticket
description: "Move a ticket to any Project Status column, or to next/previous. Follow the repo workflow rules (read_ticket_rules)."
disable-model-invocation: true
---

Move a ticket to any Project Status column, or to next/previous. Follow the repo workflow rules (read_ticket_rules).

Use MCP tool: `workflow.move_ticket(ticket: 'str', destination: 'str', workspace: 'str' = '', align_children: 'bool' = True) -> 'dict[str, object]'`
