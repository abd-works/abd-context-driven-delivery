---
name: align-child-tickets-to-parent
description: "Align child tickets so no child is in a board column prior to its parent. Follow the repo workflow rules (read_ticket_rules)."
disable-model-invocation: true
---

Align child tickets so no child is in a board column prior to its parent. Follow the repo workflow rules (read_ticket_rules).

Use MCP tool: `workflow.align_child_tickets_to_parent(parent: 'str' = '', workspace: 'str' = '') -> 'dict[str, object]'`
