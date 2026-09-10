---
name: add-child-ticket
description: "Create a project ticket and attach it as a direct child of a parent issue. Follow the repo workflow rules (read_ticket_rules)."
disable-model-invocation: true
---

Create a project ticket and attach it as a direct child of a parent issue. Follow the repo workflow rules (read_ticket_rules).

Use MCP tool: `workflow.add_child_ticket(parent: 'str', title: 'str', body: 'str' = '', workspace: 'str' = '', project_status: 'str' = 'Backlog', theme: 'str' = '', category: 'str' = '') -> 'dict[str, str | int]'`
